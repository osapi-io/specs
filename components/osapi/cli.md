# The CLI

`osapi client ...` is a thin shell over the SDK. It parses flags, calls one SDK
method, and renders the answer. No command connects to the controller directly.
No command has logic that the SDK does not have.

That is the purpose. A command that decides something is a second location for
the decision. The SDK is the location that consumers other than the CLI already
use.

## One command per endpoint

A domain gets a parent command and one subcommand for each endpoint. The file
names come from the path that they serve: `cmd/client_node_sysctl_get.go` serves
`GET /api/node/{hostname}/sysctl`. There were 156 such files in October 2026.

The file layout is the routing table. A reader who wants to know what
`osapi client node sysctl get` does finds it by name, and does not search.

## Values arrive as flags, never as positional arguments

An identifier is a named flag, marked required. It is not the first word after
the subcommand:

```
osapi client node sysctl get --key net.ipv4.ip_forward
```

One positional argument is easy to read. Two are not. The parser can make a flag
required, and nobody must write a length check. A required flag is declared.
Thus the error when you forget it comes from the parser, and it is the same in
each command.

`get` takes its identifier as a required flag and shows one thing. `list` shows
all of them. `config get --key controller.api.port` is one setting.
`config list` is each setting. `config get` alone is a usage error, not a list
of all settings.

A group refuses a word that it does not know. Cobra checks for an unknown
subcommand only at the root. Thus below the root, `osapi config lst` printed the
help of the group and exited 0, and a typo looked like success.
`cli.GuardGroups` runs in `Execute`. It gives each group a run function. That
function returns a usage error for an unknown word, and prints the help when you
run the group alone. `help --json` still reports that the group does not run.

## Command and flag names

The same rules name each command and flag. Thus a reader who knows one domain
can guess the next. The rules came from an audit of all 136 commands on 13
November 2026. The audit found that the core was already consistent (`get` 23
times, `list` 18, `update` 14, `delete` 13, `create` 11), with a small number of
exceptions.

### Verbs

There is one verb for each meaning:

| Verb                         | Means                             |
| ---------------------------- | --------------------------------- |
| `list`                       | many of a resource                |
| `get`                        | one, by its identifier            |
| `create`, `update`, `delete` | change a resource                 |
| `status`                     | the health of a running component |

An action that is not one of those keeps the verb that tells what it does:
`start` and `stop`, `enable` and `disable`, `deploy` and `undeploy`, `drain` and
`undrain`, `exec`, `shell`, `ping`, `reboot`, `shutdown`, `signal`, `pull`,
`install` and `uninstall`, `retry`, `export`, `upload`, `query`, `inspect` and
`validate`. A paired action keeps its pair. `undeploy` is not `delete`, because
the file stays.

A command is a verb. A noun that is used as a command (`stale`, `updates`,
`source`, `password`) becomes a verb, or a filter on `list`:
`file list --stale`, `package list --updates`, `log list-sources`,
`user set-password`. Do not use synonyms. Use `delete`, never `remove` or `rm`.
Use `create`, never `add` or `new`. Use `get`, never `describe` or `show`.

The verbs cost one natural name. `user ssh-key add` became `create`, which is
less natural than "add a key". The change was made anyway, because one verb set
lets the generator enforce it.

### Identifier flags

| Flag     | For                                                      |
| -------- | -------------------------------------------------------- |
| `--name` | a thing with a name: a user, a service, a behavior       |
| `--id`   | an opaque identifier: a job, an audit entry, a container |
| `--key`  | a keyed value, such as a sysctl parameter                |

A flag does not repeat the noun of its command: `job get --id`, not `--job-id`.

### Other flags

- One concept has one flag in each command: `--interface`, not
  `--interface-name`. `-T, --target` is where a node command runs, never
  `--target-hostname`.
- Each list that can grow takes `--limit` and `--offset`.
- Flags are kebab-case. A boolean has the name of what it turns on.

### Renamed on 12 November 2026

The audit made these renames without aliases, because nothing depended on the
old names yet:

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

osapi generates the commands of a behavior from its method names.
`osapi behavior validate` refuses a method with a synonym as its name (`remove`,
`add`, `describe`, `show`, `rm`, `ls`, `new`, `destroy`), and names the verb to
use. A read is `list`, `get` or `status`.

## Two flags every command inherits

`--json`, `-j` is global. The root command declares it one time.

`client node` declares `--target`, `-T` one time, with the default `_all`. It
accepts a hostname, the reserved values `_any` and `_all`, or a label selector
such as `group:web.dev`. No domain declares it again. Thus its meaning cannot
become different between domains.

## JSON returns before anything is formatted

When `--json` is set, the command prints the raw JSON of the response and
returns. It does not render a table and then serialize it.

```go
if jsonOutput {
    cli.PrintJSON(resp.RawJSON())
    return
}
```

Thus a script sees what the API sent, not a reconstruction of it. A field that
is added to a response gets to `--json` consumers, and no command changes.

## Rendering is shared helpers, not per-command formatting

The helpers are in `internal/cli`. A command prints through them, not with
`fmt`:

| Helper              | For                                                                                         |
| ------------------- | ------------------------------------------------------------------------------------------- |
| `PrintHeading`      | the heading every block sits under, in the next logo color                                  |
| `PrintKV`           | labelled values; the block is buffered and printed aligned by `FlushKV`                     |
| `PrintJobID`        | the job a result came from, printed gray at the end of the summary line                     |
| `PrintCompactTable` | rows, including the broadcast result table, with an empty section's `Empty` hint as "None." |
| `PrintErrors`       | skipped and failed hosts, under Details, with the outcome word                              |
| `PrintRawOutput`    | output that is already text, such as a log tail                                             |

Each printer calls `FlushKV` before it prints. `Execute` calls it when a command
returns. Thus a key-value block always prints. `PrintNote` stays for the few
commands that print a line where no table fits. An empty list is a table section
with `Empty` set, not a note.

`BuildBroadcastTable` changes `[]ResultRow` into headers and rows. Thus an
answer from one host and an answer from forty hosts render through the same
path. A domain that formats its own table looks different from the others.

## Errors go through one handler

`cli.HandleError` unwraps an `APIError`, prints the status code and message as
`✗ api error (403): …`, and exits with a value that is not zero. 120 of the
commands call it. That is each command that can fail. `cli.LogFatal` does the
same for each error that stops a command from starting, for example a config
that does not load, with the details in gray below it. Only `cmd/` calls it.
Code in `internal/` returns the error, and the command calls `LogFatal`.

A command does not decide what an error means, and does not print its own
message. The user sees the status code that the API declared.

Cobra makes its own errors: an unknown command or flag, a missing required flag,
or incorrect arguments. `cli.PrintError` prints them from `Execute` in
`cmd/root.go`. It prints the error, then the usage of the command in the theme,
as cobra prints it. Thus the reader sees what was incorrect and how to call the
command, in one location. The "Did you mean" suggestion of cobra stays. A
runtime error prints no usage, because the call was correct and something else
failed.

This replaces the first version, which printed only a gray
`Run 'osapi <cmd> --help' for usage.` hint and never the usage, until 13
November 2026. It was a bad decision to make the reader run a second command to
learn the flags that they had just used incorrectly.

With `--json`, an error is one JSON document on stderr, from
`internal/cli/errors.go`. Nothing else prints:

```json
{"error": "insufficient permissions", "code": "forbidden", "status": 403}
```

| `code`                                                                                               | When                                                                             |
| ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `usage_error`                                                                                        | an unknown command or flag, or a missing required flag                           |
| `fatal`                                                                                              | the command could not start, such as a config that will not load, with `details` |
| `invalid_request`, `unauthorized`, `forbidden`, `not_found`, `conflict`, `server_error`, `api_error` | the API's answer, by status code                                                 |
| `error`                                                                                              | anything the CLI cannot name more precisely                                      |

A program matches on `code`. The message can change between releases. The exit
code is 2 for a usage error, and 1 for each other failure. Thus a script can
tell "I called it incorrectly" from "it ran and failed" without stderr.

## Help as JSON, for agents

`--json` on any help prints the command as JSON, not as text. It comes from
`cli.HelpJSON` in `internal/cli/helpjson.go`:

```sh
osapi help client node sysctl get --json
osapi client node sysctl get --help --json
```

The document has the path, usage, description and example of the command. It has
each flag with its type, its default, if it is required and if it is inherited.
It also has the subcommands. It lists subcommands by name and description only.
Thus an agent asks for the next one that it needs, and does not read 120
commands at one time.

The document of the root also has the contract that all commands share. Errors
under `--json` are `{"error", "code"}` on stderr. The exit codes are 0 for
success, 1 for an error and 2 for a usage error.

It reads `--json` from the persistent flag of the root, not from the variable
that the flag binds. Cobra prints help before it runs the initializers that set
that variable.

## Commands that teach, for agents

An agent learns what to write from the binary, not from a skill or a page that
can be out of date. Each command group for something that an agent writes has
the same commands:

| Command                   | Tells                                                                     |
| ------------------------- | ------------------------------------------------------------------------- |
| `<group> spec`            | each part of the DSL or format, what it makes osapi do and when to use it |
| `<group> validate`        | the problems, each with its rule and its fix                              |
| `<group> validate --help` | each rule, what it requires and its fix, before the agent breaks one      |
| `<group> list`, `get`     | what exists already                                                       |

Each one takes `--json`. The terms and the rules are tables in Go, of the types
in `internal/guide`: `guide.Spec` and `guide.Checks`. The command, the help and
each problem read the same table. A test fails on a part of the DSL or a rule
without an entry. Thus what the command tells cannot be different from what the
code does.

Two groups have them today. The behavior group has `osapi behavior spec` and
`osapi behavior validate`. The config group has `osapi config list` and
`config get` in place of `spec`, and `osapi config validate`. A workflow DSL in
osapi-orchestrator gets the same commands, from `guide` in a public package, in
osapi-io/osapi#764.

A skill keeps only judgment: what to ask the person, and which way to select. It
sends the agent to these commands for each fact.

## Output style

The output of each command obeys these rules. Thus a reader who knows the output
of one command can read each other command. The rules came from an audit of the
CLI on 13 November 2026. The audit ran 63 read-only commands against a Linux
agent, and read the code of the 71 commands that change a host. Root help is the
reference, and the rest copies it.

There is one theme, in `internal/cli/theme.go` and nowhere else. Nothing in
`cmd/` imports lipgloss or names a color. A new command obeys these rules
because it prints through the helpers above.

```sh
grep -rlE 'lipgloss\.(Color|NewStyle)' --include='*.go' cmd internal | grep -v _test | grep -v internal/cli/theme.go
```

### Layout

- Each block is under a heading. A heading is at the left margin with a colon.
  Its block is indented two spaces below it.
- Exactly one blank line separates blocks. Nothing prints above the first
  heading.
- The one exception is a one-line verdict, `✓ 1 behavior valid` or the `✗ ...`
  of an error. It is alone at the left margin.
- A table of results for each host with no title of its own gets the heading
  `Results:`.

The audit found that 58 of 63 outputs printed something before their first
heading. Most often, a `Job ID:` line was above `Results:`. That, more than any
color, made commands look like they were at different levels.

### Color

The web UI uses the same palette.
[Color in the UI](ui.md#color-one-palette-with-the-cli) tells how it maps these
tiers to its tokens. A change to a color changes both.

There are four tiers. Nothing outside them gets a color:

| Tier   | Color                                          | Only for                                                                      |
| ------ | ---------------------------------------------- | ----------------------------------------------------------------------------- |
| Vivid  | a logo color, a different one for each heading | headings                                                                      |
| Tint   | a dark tint of that block's heading color      | the block's table headers and key-value labels                                |
| Status | green `#67ea94`, amber `222`, red `#ef4444`    | state: status words, set conditions, outcome counts above zero                |
| Gray   | the logo's `#8a8a8a`                           | IDs, times, units, URLs, `{params}`, zeroes, tree branches, the job ID, hints |

Data is in the default color of the terminal. Bold marks what a reader looks
for: names, hostnames, `TYPE`, HTTP verbs and writes. Headers and labels have a
tint, but are not bold. Thus a label never uses bold.

The heading colors are cyan, magenta, yellow, green, and a lighter form of the
blue of the logo, `#6b5cff`. The original `#2300fd` is almost invisible on a
dark terminal. osapi mixes their order one time for each run, and each heading
takes the next. Thus no two headings in one output have the same color until all
five are used. Red is never a heading, because it means an error.

A heading never has the color of the text under it. `Details:` lists skips in
amber and failures in red. Thus it skips the yellow and green of the logo, and
the skipped color moves into the next position.

Status colors mean state and nothing else. An HTTP `POST` is not green, and a
write is not amber, because green already means "ok" and amber means "skipped".
Weight tells kinds of things apart, not color. `statusStyles` maps status words
to their colors. `cli.Count` colors a count by what it counts. `renderCell` has
the rules for each column. All three are in `internal/cli/theme.go`.

### Key-value blocks

Each line has one pair: the label, a colon, then the value. The values align in
the block. Labels are full words in sentence case: `Service manager`,
`Primary interface`, `Updated`. Not `Service Mgr` or `Updated At`.

### Tables

- Headers are capitals with spaces, never underscores: `UTC OFFSET`.
- A header names its column one time in a table. `service list` had two `STATUS`
  columns: the result of the host, and the state of the service. The second is
  now `STATE`.
- A cell never has cut JSON. It has a summary, `12 packages`, and `--json` gives
  the full value.
- If a listing is too wide for one table, it splits into one headed table for
  each top-level group. The key-value block above says the rule that each row
  shares, one time. `config list` has a table for each config section, and its
  block tells how a key becomes an environment variable.

### Counts

The count of a list is in its heading: `Files (6):`, or
`Audit entries (3 of 88):` when it has pages. A breakdown goes on a summary line
below the table, in the form that a result already uses:
`30 jobs: 28 completed, 2 skipped`. There is no separate `Total:` line and no
summary block.

### Results across hosts

One renderer prints each result for each host. The same command looks the same
on one host and on forty.

- The table always has a `HOSTNAME` column, also for one host. Thus more hosts
  only add rows.
- A host that returned data is a row. A host that was skipped or failed is not a
  row. It is listed one time under `Details:`: its name, what occurred
  (`skipped` in amber or `failed` in red), then why.
- When all hosts were skipped or failed, there is no empty table. The summary
  comes after `Results:`, and then `Details:`.
- A list from many hosts is in groups by host. The hostname is bold on the first
  row of a host and gray on the others. Thus the rows of each host read as a
  block.
- Hosts sort by name. Thus a fleet prints in the same order on each run.
- The summary counts each host and ends with the job ID in gray:
  `3 hosts: 2 changed, 1 skipped   job 0d485436-...`. A command with no summary
  line shows the job ID as the first pair of its block.

The generated docs page for each behavior method renders its example two times
through the real renderer: one time for one host, and one time for three hosts
with one skipped. Thus each page shows the shape for many hosts, and nobody
learns it in production.

### Showing a behavior

`osapi behavior get --name <behavior>` is the one location where a reader sees
the full contract of a behavior. Thus its layout is fixed:

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
  the fields in braces. A required input field has a `*`. A list output is `[]`
  and its element. The type name is gray and the fields are data. Thus the shape
  is clear before the names. `--method` shows all the fields of one method, with
  the type, constraints and description of each field. It also shows the
  examples of the method as input and output pairs.
- **Chains.** `Uses:` is the tree of behaviors that this one requires, through
  `Requires`, each with the method that it calls and why. `Used by:` is the
  behaviors that require this one. A behavior that uses none says `None.`. The
  heading stays, so that a reader can tell "none" from "not shown". The tree
  uses the same gray branches as the components of health status.
- **Telemetry.** What each call of the behavior records: the span, the three
  metrics and the attributes that each method gets. Then the input fields that
  each method records, and the methods that record each. A method records the
  field that `.Key` names, and each field with the tag `telemetry:"attr"`. The
  names come from `internal/behaviors/telemetry.go`. Thus the block cannot be
  different from what osapi records.
- **Surfaces.** `API` and `CLI` show where osapi serves each one, or `none` when
  the behavior does not have that surface.

`--json` has the same content: `uses` and `used_by` as nested lists,
`telemetry`, and the input and output of each method as JSON Schema, with the Go
type name next to it.

### Empty lists

An empty list keeps its heading with `(0)`, and tells what to do next:
`None. Upload one with osapi client file upload.` A header row with no rows
under it is incorrect. A heading with nothing under it is also incorrect.

### Values

- Times are local, `2026-11-12 18:15:13`. With `--json`, they are RFC 3339.
- Durations are rounded to a useful precision: `6ms`, `1.2s`, `3m 4s`.
- Sizes have one decimal and their unit: `3.4 GB used of 7.7 GB`.
- The noun of a count agrees with it: `1 key`, `2 keys`.

### JSON

Human output never has raw JSON. A nested object shows as key-value pairs, with
a note that `--json` prints all of it. `osapi version` prints a key-value block,
as each other command does. It prints JSON only with `--json`.

### The logo, and plain output

The logo shows above the root help only. Each grid row is one terminal line, and
each cell is two columns of `█`. A terminal cell is approximately two times as
tall as it is wide. Thus two columns make the square cells that the SVG has.

With `NO_COLOR` set, or when the output is not a terminal, all output prints
with the same layout and no color, and the logo does not show. Renderers bind to
the writer that they print to. Thus osapi examines stderr and stdout separately.

### Kept from earlier versions

The first version of the theme gave a color only to headings, and printed table
headers and labels in bold white. Status got colors when the output was changed
to look like help. The tiers above replaced the bold white headers on 12
November 2026, after the audit.

## Where this connects

[The SDK](sdk.md) tells what the CLI calls, and the envelope that each method
returns.

[The job system](job-system.md) tells what `_any`, `_all` and a label selector
resolve to.

[Building a domain](domains.md) tells what a contributor adds when a new domain
needs commands, together with the seven other artifacts.

______________________________________________________________________

Written from `cmd/client_*.go` and `internal/cli/`.
