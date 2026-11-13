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

## Command and flag names

Every command and flag is named by the same rules, so a reader who knows one
domain can guess the next. They came from an audit of all 136 commands on 13
November 2026, which found the core already consistent (`get` 23 times, `list`
18, `update` 14, `delete` 13, `create` 11) and the exceptions spread thin.

### Verbs

One verb per meaning:

| Verb                         | Means                             |
| ---------------------------- | --------------------------------- |
| `list`                       | many of a resource                |
| `get`                        | one, by its identifier            |
| `create`, `update`, `delete` | change a resource                 |
| `status`                     | the health of a running component |

An action that is not one of those keeps the verb that says what it does:
`start` and `stop`, `enable` and `disable`, `deploy` and `undeploy`, `drain` and
`undrain`, `exec`, `shell`, `ping`, `reboot`, `shutdown`, `signal`, `pull`,
`install` and `uninstall`, `retry`, `export`, `upload`, `query`, `inspect`,
`validate`. A paired action keeps its pair; `undeploy` is not `delete`, because
the file stays.

A command is a verb. A noun used as one (`stale`, `updates`, `source`,
`password`) becomes a verb or a filter on `list`: `file list --stale`,
`package list --updates`, `log list-sources`, `user set-password`. Synonyms are
not used: `delete`, never `remove` or `rm`; `create`, never `add` or `new`;
`get`, never `describe` or `show`.

Following the verbs cost one natural name: `user ssh-key add` became `create`,
which reads less well than "add a key". It was taken anyway, because one verb
set is what lets the generator enforce it.

### Identifier flags

| Flag     | For                                                      |
| -------- | -------------------------------------------------------- |
| `--name` | a thing with a name: a user, a service, a behavior       |
| `--id`   | an opaque identifier: a job, an audit entry, a container |
| `--key`  | a keyed value, such as a sysctl parameter                |

A flag does not repeat its command's noun: `job get --id`, not `--id`.

### Other flags

- One concept, one flag, everywhere: `--interface`, not `--interface`;
  `-T, --target` for where a node command runs, never `--target`.
- Every list that can grow takes `--limit` and `--offset`.
- Flags are kebab-case, and a boolean is named for what it turns on.

### Renamed on 12 November 2026

The audit's renames, made without aliases because nothing depended on the old
names yet:

| Was                                         | Now                                         |
| ------------------------------------------- | ------------------------------------------- |
| `behavior describe`                         | `behavior get`                              |
| `client node container docker remove`       | `client node container docker delete`       |
| `client node container docker image-remove` | `client node container docker image delete` |
| `client node user ssh-key add`              | `client node user ssh-key create`           |
| `client node user password`                 | `client node user set-password`             |
| `client file stale`                         | `client file list --stale`                  |
| `client node package updates`               | `client node package list --updates`        |
| `client node log unit --name`               | `client node log query --unit`              |
| `client node log source`                    | `client node log list-sources`              |
| `--job-id`, `--audit-id`                    | `--id`                                      |
| `--interface-name`                          | `--interface`                               |
| `client job retry --target-hostname`        | `client job retry -T, --target`             |

### Behaviors follow them by construction

A behavior's commands are generated from its method names, and
`osapi behavior validate` rejects a method named with a synonym (`remove`,
`add`, `describe`, `show`, `rm`, `ls`, `new`, `destroy`) and names the verb to
use instead. A read is `list`, `get` or `status`.

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

## Rendering is shared helpers, not per-command formatting

They live in `internal/cli`, and a command prints through them rather than with
`fmt`:

| Helper              | For                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------- |
| `PrintHeading`      | the heading every block sits under, in the next logo color                                  |
| `PrintKV`           | labelled values; the block is buffered and printed aligned by `FlushKV`                     |
| `PrintJobID`        | the job a result came from, printed gray at the end of the summary line                     |
| `PrintCompactTable` | rows, including the broadcast result table, with an empty section's `Empty` hint as "None." |
| `PrintErrors`       | skipped and failed hosts, under Details, with the outcome word                              |
| `PrintRawOutput`    | output that is already text, such as a log tail                                             |

Every printer calls `FlushKV` before it prints, and `Execute` calls it when a
command returns, so a key-value block is never left unprinted. `PrintNote`
remains for the few commands that print a line where no table belongs; an empty
list is a table section with `Empty` set, not a note.

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

Cobra's own errors, an unknown command or flag, a missing required flag or wrong
arguments, are printed by `cli.PrintError` from `Execute` in `cmd/root.go`: the
error, then the command's usage in the theme, as cobra prints it, so the reader
sees what was wrong and how to call it in one place. Cobra's "Did you mean"
suggestion is kept. A runtime error prints no usage, because the call was right
and something else failed.

This replaces the first version, which printed only a muted
`Run 'osapi <cmd> --help' for usage.` hint and never the usage, until 13
November 2026. Sending the reader to run a second command to learn the flags
they had just got wrong was the wrong trade.

Under `--json` an error is one JSON document on stderr, from
`internal/cli/errors.go`, and nothing else is printed:

```json
{"error": "insufficient permissions", "code": "forbidden", "status": 403}
```

| `code`                                                                                               | When                                                                             |
| ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `usage_error`                                                                                        | an unknown command or flag, or a missing required flag                           |
| `fatal`                                                                                              | the command could not start, such as a config that will not load, with `details` |
| `invalid_request`, `unauthorized`, `forbidden`, `not_found`, `conflict`, `server_error`, `api_error` | the API's answer, by status code                                                 |
| `error`                                                                                              | anything the CLI cannot name more precisely                                      |

A program matches on `code`; the message can change between releases. The exit
code is 2 for a usage error and 1 for every other failure, so a script can tell
"I called it wrong" from "it ran and failed" without reading stderr.

## Help as JSON, for agents

`--json` on any help prints the command as JSON instead of text, from
`cli.HelpJSON` in `internal/cli/helpjson.go`:

```sh
osapi help client node sysctl get --json
osapi client node sysctl get --help --json
```

The document has the command's path, usage, description and example, every flag
with its type, default, whether it is required and whether it is inherited, and
its subcommands. Subcommands are listed by name and description only, so an
agent asks for the one it needs next instead of reading 120 commands at once.
The root's document also carries the contract every command shares: errors under
`--json` as `{"error", "code"}` on stderr, and exit codes 0 for success, 1 for
an error and 2 for a usage error.

It reads `--json` from the root's persistent flag rather than from the variable
the flag binds, because cobra prints help before it runs the initializers that
set that variable.

## Output style

Every command's output follows these rules, so a reader who has learned one
command's output can read any other. They came from an audit of the CLI on 13
November 2026: 63 read-only commands run against a Linux agent, and the 71 that
change a host read from their code. Root help is the reference, and the rest is
written to look like it.

One theme, defined in `internal/cli/theme.go` and nowhere else. Nothing in
`cmd/` imports lipgloss or names a color, and a new command follows these rules
because it prints through the helpers above.

```sh
grep -rlE 'lipgloss\.(Color|NewStyle)' --include='*.go' cmd internal | grep -v _test | grep -v internal/cli/theme.go
```

### Layout

- Everything is under a heading. A heading sits at the left margin with a colon;
  its block is indented two spaces beneath it.
- Exactly one blank line separates blocks. Nothing prints above the first
  heading.
- The one exception is a one-line verdict, `✓ 1 behavior valid` or an error's
  `✗ ...`, which sits at the left margin on its own.
- A table of per-host results with no title of its own is headed `Results:`.

The audit found 58 of 63 outputs printing something before their first heading,
most often a `Job ID:` line floating above `Results:`. That, more than any
color, is why commands looked to sit at different levels.

### Color

Four tiers. Nothing outside them takes a hue:

| Tier   | Color                                          | Only for                                                                      |
| ------ | ---------------------------------------------- | ----------------------------------------------------------------------------- |
| Vivid  | a logo color, a different one for each heading | headings                                                                      |
| Tint   | a dark tint of that block's heading color      | the block's table headers and key-value labels                                |
| Status | green `#67ea94`, amber `222`, red `#ef4444`    | state: status words, set conditions, outcome counts above zero                |
| Gray   | the logo's `#8a8a8a`                           | IDs, times, units, URLs, `{params}`, zeroes, tree branches, the job ID, hints |

Data is in the terminal's own color. Bold marks what a reader scans for: names,
hostnames, `TYPE`, HTTP verbs, and writes. Headers and labels are tinted but not
bold, so bold is never spent on a label.

The heading colors are cyan, magenta, yellow, green, and the logo's blue lifted
to `#6b5cff`, because `#2300fd` is nearly invisible on a dark terminal. They are
shuffled once per run and each heading takes the next, so no two headings in one
output share a color until all five are used. Red is never a heading, because it
means an error. A heading is never the color of the text under it: `Details:`
lists skips in amber and failures in red, so it passes over the logo's yellow
and green, and the color it passes over is swapped into the next place.

Status colors mean state and nothing else. An HTTP `POST` is not green and a
write is not amber, because green already says "ok" and amber says "skipped". A
kind of thing is told apart by weight, not hue. `statusStyles` maps status words
to their colors, `cli.Count` colors a count by what it counts, and `renderCell`
holds the per-column rules, all in `internal/cli/theme.go`.

### Key-value blocks

One pair per line, label then colon, and the values line up within the block.
Labels are spelled out in sentence case: `Service manager`, `Primary interface`,
`Updated`, not `Service Mgr` or `Updated At`.

### Tables

- Headers are capitals with spaces, never underscores: `UTC OFFSET`.
- A header names its column once in a table. `service list` had two `STATUS`
  columns, the host's result and the service's state; the second is `STATE`.
- A cell never holds truncated JSON. It holds a summary, `12 packages`, and
  `--json` gives the whole value.

### Counts

A list's count is in its heading, `Files (6):`, or `Audit entries (3 of 88):`
when it is paginated. A breakdown goes on a summary line beneath the table, in
the form a result already uses: `30 jobs: 28 completed, 2 skipped`. There is no
separate `Total:` line and no summary block.

### Results across hosts

One renderer prints every per-host result, and the same command looks the same
on one host as on forty.

- The table always has a `HOSTNAME` column, even for one host, so more hosts
  only add rows.
- A host that returned data is a row. A host that was skipped or failed is not;
  it is listed once under `Details:`: its name, what happened (`skipped` in
  amber or `failed` in red), then why.
- When every host was skipped or failed, there is no empty table: `Results:` is
  followed by the summary, then `Details:`.
- A list from several hosts is grouped by host. The hostname is bold on a host's
  first row and gray on the rest, so each host's rows read as a block.
- Hosts sort by name, so a fleet prints in the same order every run.
- The summary counts every host and ends with the job ID in gray:
  `3 hosts: 2 changed, 1 skipped   job 0d485436-...`. A command with no summary
  line shows the job ID as the first pair of its block.

The generated docs page for every behavior method renders its example twice
through the real renderer, once for one host and once for three with one
skipped, so the multi-host shape is on every page rather than discovered in
production.

### Showing a behavior

`osapi behavior get --name <behavior>` is the one place a behavior's contract is
read whole, so its layout is fixed:

```text
Behavior:
  Name:        sysctl
  Placement:   node
  API:         /api/next
  CLI:         osapi client next

Uses:
  sysctl
  └─ file.write        writes /etc/sysctl.d/osapi-<key>.conf
     └─ file.read

Used by:
  None.

Methods (5):
  NAME    VERB   ROUTE                                   PERMISSION
  list    read   GET /api/next/node/{hostname}/sysctl    sysctl:read
  create  write  POST /api/next/node/{hostname}/sysctl   sysctl:write

Types (5):
  NAME    INPUT                         OUTPUT
  list    ListInput                     []Entry { key, value }
  create  CreateInput { key*, value* }  MutationResult { key, changed }

Telemetry:
  Span:             behavior.sysctl.<method>
  Metrics:          osapi_behavior_calls_total, osapi_behavior_duration_seconds, osapi_behavior_changes_total
  Attributes:       osapi.behavior.name, osapi.behavior.method, osapi.behavior.verb, ...
  Recorded inputs:  key (get, create, update, delete)
```

- **Types.** Each method shows its input and output by their Go type names, with
  the fields in braces and a required input field marked `*`. A list output is
  `[]` and its element. The type name is gray and the fields are data, so the
  shape reads before the names. `--method` shows one method's fields in full,
  with each field's type, constraints and description, and its examples as input
  and output pairs.
- **Chains.** `Uses:` is the tree of behaviors this one is built on, through
  `Requires`, each with the method it calls and why, and `Used by:` is the
  behaviors built on this one. A behavior that uses none says `None.` rather
  than leaving the heading out, so a reader can tell "none" from "not shown".
  The tree uses the same gray branches as the health status components.
- **Telemetry.** What every call of the behavior records: the span, the three
  metrics and the attributes every method gets, then the input fields this
  behavior tags with `telemetry:"attr"` and the methods that record each. The
  names come from `pkg/behavior/telemetry.go`, so the block cannot disagree with
  what is recorded.
- **Surfaces.** `API` and `CLI` show where each is served, or `none` when the
  behavior has no such surface.

`--json` carries the same: `uses` and `used_by` as nested lists, `telemetry`,
and each method's input and output as JSON Schema with the Go type name beside
it.

Chains need `Requires`, which is not built yet, so `Uses:` and `Used by:` read
`None.` for every behavior today.

### Empty lists

An empty list keeps its heading with `(0)` and says what to do next:
`None. Upload one with osapi client file upload.` A header row with no rows
under it, and a heading with nothing under it, are both wrong.

### Values

- Times are local, `2026-11-12 18:15:13`. With `--json` they are RFC 3339.
- Durations are rounded to what a reader can use: `6ms`, `1.2s`, `3m 4s`.
- Sizes have one decimal and their unit: `3.4 GB used of 7.7 GB`.
- A count's noun agrees with it: `1 key`, `2 keys`.

### JSON

Human output never contains raw JSON. A nested object is shown as key-value
pairs, with a note that `--json` prints all of it. `osapi version` prints a
key-value block like everything else, and JSON only with `--json`.

### The logo, and plain output

The logo is drawn above the root help only, one grid row per terminal line, each
cell two columns of `█`. A terminal cell is about twice as tall as it is wide,
so two columns make the square cells the SVG has.

With `NO_COLOR` set, or output that is not a terminal, everything prints with
the same layout and no color, and the logo is not drawn. Renderers bind to the
writer they print to, so stderr and stdout are judged separately.

### Kept from earlier versions

The first version of the theme colored only headings, and printed bold white
table headers and labels. Status took color when the output was made to read
like help, and the tiers above replaced bold white headers on 12 November 2026,
after the audit.

## Where this connects

What the CLI calls, and the envelope every method returns, is [the SDK](sdk.md).

What `_any`, `_all` and a label selector resolve to is
[the job system](job-system.md).

What a contributor adds when a new domain needs commands, alongside the seven
other artifacts, is [building a domain](domains.md).

______________________________________________________________________

Written from `cmd/client_*.go` and `internal/cli/`.
