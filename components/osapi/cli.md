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
    fmt.Println(string(resp.RawJSON()))
    return
}
```

What a script sees is therefore what the API sent, not a reconstruction of it. A
field added to a response reaches `--json` consumers without any command
changing.

## Rendering is four shared helpers, not per-command formatting

They live in `internal/cli`:

| Helper              | For                                             |
| ------------------- | ----------------------------------------------- |
| `PrintKV`           | a single labelled value, such as the job ID     |
| `PrintCompactTable` | rows, including the broadcast result table      |
| `PrintErrors`       | per-row errors beneath the rows                 |
| `PrintRawOutput`    | output that is already text, such as a log tail |

`BuildBroadcastTable` turns `[]ResultRow` into headers and rows, so a one-host
answer and a forty-host answer render through the same path. A domain that
formatted its own table would be the one that looks different.

## Errors go through one handler

`cli.HandleError` unwraps an `APIError`, logs the status code and message, and
exits non-zero. 120 of the commands call it, which is every command that can
fail.

A command does not decide what an error means or print its own message. The
status code the API declared is the status code the user is told about.

## Where this connects

What the CLI calls, and the envelope every method returns, is [the SDK](sdk.md).

What `_any`, `_all` and a label selector resolve to is
[the job system](job-system.md).

What a contributor adds when a new domain needs commands, alongside the seven
other artifacts, is [building a domain](domains.md).

______________________________________________________________________

Written from `cmd/client_*.go` and `internal/cli/`.
