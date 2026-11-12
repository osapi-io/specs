# The CLI

`osapi client ...` is a thin shell over the SDK. It parses flags, calls one SDK
method, and renders the answer. No command talks to the controller directly, and
no command holds logic the SDK does not.

That thinness is the point. A command that decided anything would be a second
place the decision lives, and the SDK is the one consumers other than the CLI
already use.

## One command per endpoint

A domain gets a parent command and one subcommand per endpoint, in files named
after the path they serve: `cmd/client_node_sysctl_get.go` serves
`GET /api/node/{hostname}/sysctl`. There were 156 such files in October 2026.

The file layout is the routing table. A reader looking for what
`osapi client node sysctl get` does finds it by name rather than by searching.

## Values arrive as flags, never as positional arguments

An identifier is a named flag, marked required, not the first bare word after
the subcommand:

```
osapi client node sysctl get --key net.ipv4.ip_forward
```

Positional arguments read fine with one of them and stop reading at two, and a
flag can be made required by the parser rather than by a length check somebody
has to write. Required-ness is declared, so the error for omitting it is the
parser's and is the same everywhere.

## Two flags every command inherits

`--json`, `-j` is global, declared once on the root command.

`--target`, `-T` is declared once on `client node` and defaults to `_all`. It
accepts a hostname, the reserved values `_any` and `_all`, or a label selector
such as `group:web.dev`. Nothing per-domain redeclares it, which is why its
meaning cannot drift between domains.

## JSON returns before anything is formatted

When `--json` is set, the command prints the response's raw JSON and returns. It
does not render a table and then serialize it.

```go
if jsonOutput {
    cli.PrintJSON(resp.RawJSON())
    return
}
```

What a script sees is therefore what the API sent, not a reconstruction of it. A
field added to a response reaches `--json` consumers without any command
changing.

## Rendering is five shared helpers, not per-command formatting

They live in `internal/cli`, and a command prints through them rather than with
`fmt`:

| Helper              | For                                                      |
| ------------------- | -------------------------------------------------------- |
| `PrintKV`           | a single labelled value, such as the job ID              |
| `PrintCompactTable` | rows, including the broadcast result table               |
| `PrintErrors`       | per-row errors beneath the rows                          |
| `PrintRawOutput`    | output that is already text, such as a log tail          |
| `PrintNote`         | a line where a table would be, such as "No files found." |

`BuildBroadcastTable` turns `[]ResultRow` into headers and rows, so a one-host
answer and a forty-host answer render through the same path. A domain that
formatted its own table would be the one that looks different.

## Errors go through one handler

`cli.HandleError` unwraps an `APIError` and prints the status code and message
as `✗ api error (403): …`, then exits non-zero. 120 of the commands call it,
which is every command that can fail. `cli.LogFatal` does the same for a config
that will not load, with the details muted beneath.

A command does not decide what an error means or print its own message. The
status code the API declared is the status code the user is told about.

Cobra's own errors, an unknown command or a missing required flag, are printed
by `cli.PrintError` from `Execute` in `cmd/root.go`. A bad invocation gets a
muted `Run 'osapi <cmd> --help' for usage.` beneath it, and cobra's "Did you
mean" suggestion is kept. No error prints the usage dump.

Under `--json` none of this is styled. `HandleError` and `LogFatal` write the
same structured log lines as before, and a cobra error is a plain `Error:` line,
so a program reading stderr sees no color or decoration.

## Output style

One theme, defined in `internal/cli/theme.go` and nowhere else. Nothing in
`cmd/` imports lipgloss or names a color, and a new command looks like the rest
because it prints through the helpers above.

```sh
grep -rlE 'lipgloss\.(Color|NewStyle)' --include='*.go' cmd internal | grep -v _test | grep -v internal/cli/theme.go
```

The colors come from the README logo, `asset/logo-dark.svg`, and each has one
job:

| Role                                          | Style                                                   |
| --------------------------------------------- | ------------------------------------------------------- |
| The logo, above the root help only            | its own palette, drawn in full blocks at the SVG's grid |
| Help headings and output titles               | bold, each a different logo color                       |
| Command and flag names, table headers, labels | bold, in the terminal's own color                       |
| Descriptions and values                       | the terminal's own color                                |
| Flag types, defaults, hints, durations        | the logo's gray, `#8a8a8a`                              |
| ok, skipped, failed                           | the web UI's green, amber and red, on status only       |

The heading colors are cyan, magenta, yellow and green, shuffled once per run,
and each heading takes the next. No two headings in one output share a color
until all of them are used, and a fifth heading gets the logo's blue lifted to
`#6b5cff`, because `#2300fd` is nearly invisible on a dark terminal. Red is
never a heading, because it means an error.

Only headings are colored. When names were colored as well, every line carried a
color and the headings stopped standing out.

The logo is drawn one grid row per terminal line, each cell two columns of `█`.
A terminal cell is about twice as tall as it is wide, so two columns make the
square cells the SVG has. Half blocks, two rows to a line, came out twice as
wide as tall.

With `NO_COLOR` set, or output that is not a terminal, help is cobra's default
text with the same structure and the logo is not drawn. Renderers bind to the
writer they print to, so stderr and stdout are judged separately.

## Where this connects

What the CLI calls, and the envelope every method returns, is [the SDK](sdk.md).

What `_any`, `_all` and a label selector resolve to is
[the job system](job-system.md).

What a contributor adds when a new domain needs commands, alongside the seven
other artifacts, is [building a domain](domains.md).

______________________________________________________________________

Written from `cmd/client_*.go` and `internal/cli/`.
