# The CLI

`osapi client ...` is a thin shell over the SDK. It parses flags, calls one SDK
method, and renders the answer. No command connects to the controller directly.
No command has logic that the SDK does not have.

That is the purpose. A command that decides something is a second location for
the decision. The SDK is the location that consumers other than the CLI already
use.

[Commands](commands.md) plans a DSL that makes each command of the binary from a
definition. This page has the rules that each command obeys, whatever makes it.

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
`install` and `uninstall`, `retry`, `export`, `upload`, `accept` and `reject`,
and `validate`. A paired action keeps its pair. `undeploy` is not `delete`,
because the file stays.

A command is `<resource> <verb>`. A noun that is used as a command becomes a
filter on `list`, or a resource with its own verbs under it: `file stale list`,
`package list --updates`, `log source list`, `user password update`,
`facts keys list`. Do not use synonyms. Use `delete`, never `remove` or `rm`.
Use `create`, never `add` or `new`. Use `get`, never `describe` or `show`.

A command directly under `osapi` that does one thing for the tool itself, such
as `osapi version` or `osapi init`, is not a resource and a verb. Each command
line tool has these, as `kubectl version` and `git init` are. Its word is one of
`command.Roots`, a short list that a person adds to as a decision, because the
root is the first thing a person reads. `TestCommandShape` holds each command of
the root to that list.

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
| `client file stale`                         | `client file stale list`                    |
| `client node package updates`               | `client node package list --updates`        |
| `client node log unit --name`               | `client node log query --unit`              |
| `client node log source`                    | `client node log list-sources`              |
| `--job-id`, `--audit-id`                    | `--id`                                      |
| `--interface-name`                          | `--interface`                               |
| `client job retry --target-hostname`        | `client job retry -T, --target`             |

### Renamed on 17 November 2026

The endpoint groups moved to `<resource> <verb>`, and these commands moved with
them. `TestCommandShape`, in `cmd/help_style_test.go`, fails on a command under
`osapi client` whose last word is not a CRUD verb or a listed action:

| Was                                    | Now                                       |
| -------------------------------------- | ----------------------------------------- |
| `client agent pending`                 | `client agent pending list`               |
| `client agent remove`                  | `client agent delete`                     |
| `client node log query`                | `client node log list`                    |
| `client node log list-sources`         | `client node log source list`             |
| `client node container docker inspect` | `client node container docker get`        |
| `client node container docker pull`    | `client node container docker image pull` |
| `client node user set-password`        | `client node user password update`        |

### Moved to admission on 18 November 2026

Admission of a machine became its own group, keyed by the machine ID
([admission](admission.md)):

| Was                              | Now                                     |
| -------------------------------- | --------------------------------------- |
| `client agent pending list`      | `client admission list --state pending` |
| `client agent accept --hostname` | `client admission admit --machine-id`   |
| `client agent reject --hostname` | `client admission reject --machine-id`  |
| `client agent delete --hostname` | `client admission revoke --machine-id`  |
| `client agent key fingerprint`   | `agent admission`, on the machine       |

### Renamed on 19 November 2026

`token` moved to the [command DSL](commands.md), and its verb rule applies to
local groups too:

| Was           | Now                |
| ------------- | ------------------ |
| `token roles` | `token roles list` |

### Required flags

`MarkFlagRequired` marks a required flag. `--help` and the CLI page show
"(required)" from it, so a flag's help does not say it. The same test fails on a
flag whose help says it.

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

## Output comes from the output type

A command does not write its own output. The command layer prints the output of
a method from its Go type, by the [output style](#output-style) below. Thus two
commands with the same shape of answer look the same, and a new command looks
right with no code. osapi-io/osapi#903 built it.

| The output                                      | Prints as                                                                     |
| ----------------------------------------------- | ----------------------------------------------------------------------------- |
| a list: `Items []T` with `TotalItems`, or `[]T` | a heading with the count, then a table with one column for each field of `T`  |
| a list with fewer items than `TotalItems`       | the count as `(3 of 120)`                                                     |
| an empty list                                   | the heading with `(0)`, then `None.` and the hint of the list, if it has one  |
| one object                                      | a heading, then an aligned key-value block                                    |
| an object in an object                          | a section under the key-value block                                           |
| a list in an object                             | a table under the key-value block, with its count                             |
| an object with one field                        | the value of that field: the envelope is not shown                            |
| no body (204)                                   | one line: the key of the input and what occurred, such as `[ok] m-1 admitted` |

These rules have no options:

- The columns and the keys have the order of the fields. To change the order,
  change the order of the fields.
- A field with `omitempty` and no value is not shown.
- A `bool` is `yes` or `no`. A `[]string` is its values, joined with `, `. A
  `float32` or `float64` has two decimals, such as `0.00`, so a column lines up.
- A label is the json name in sentence case: `last_seen` is `Last seen`. A
  column header is the json name in capitals: `LAST SEEN`.
- A table leaves out a column that has no value in any row, except a column with
  a `none` tag. `agent list` always has CONDITIONS, with `-` when no condition
  is true.
- A field tagged `render:"body"` is the whole output, as it is, such as the text
  of a skill that `skill get` prints. The other fields are only in `--json`.
- A list tagged `table:"blocks"` prints each item as a block, not a row: its
  first field on a line, then each other field as a wrapped paragraph with its
  label. A field tagged `label:"-"` is a paragraph with no label. It is for a
  list of long text, such as the terms of a DSL, which the cells of a table cut.
- A list tagged `table:"sections"` prints each item as a section: the value of
  its first field is the heading, and the rest of the item prints under it as an
  object does. A section that is only one list prints that list under the
  heading. `spec get` is a section for each kind of the DSL, with a block for
  each term. Both tags are opt-in: a list of rows that hold lists, such as
  `agent list`, stays a table.
- A row whose type has a list of its own type has a tree: the items print as
  rows under it, with `├─` and `└─`. Each component of `health status` has its
  sub-components under it.
- In a table cell, an object is its values, with a space between them, such as
  `Ubuntu 24.04`. A list of objects is the first field of each, with commas,
  such as `HighLoad, DiskPressure`.
- The heading is the name of the group in sentence case, plural for a list.
- In a table cell, an object leaves out its `table:"-"` fields. The `operation`
  of a job is its type.
- A list's fields other than its items and its count print after the table, such
  as the count of each status of `job list`.
- A field of `any`, or of a map of `any`, prints as a section of its keys, each
  with its value. A value with more in it is a count, and `--json` has all of
  it. The `result` of a job prints so.

A field changes its own output with tags:

| Tag                 | Effect                                                            |
| ------------------- | ----------------------------------------------------------------- |
| `render:"-"`        | the field is not shown                                            |
| `render:"bytes"`    | a size, such as `3.4 GB`                                          |
| `render:"age"`      | the time since a `time.Time` or a number of seconds, such as `3s` |
| `render:"time"`     | a time in the one time format of the CLI                          |
| `render:"duration"` | a duration; `render:"duration=ms"` for an integer of milliseconds |
| `render:"status"`   | a status word, in its color                                       |
| `render:"short=N"`  | in a table, the first N characters, with `...`; a block shows all |
| `label:"..."`       | a different label and header                                      |
| `none:"..."`        | the text for a field with no value, such as `never` for a time    |
| `empty:"..."`       | on a list: the hint after `None.`                                 |
| `prefix:"..."`      | text in front of each value, such as `@fact.`                     |
| `table:"-"`         | not in a table; the key-value block of a get shows it             |
| `title:"..."`       | on the field `_ struct{}`: a different heading                    |

A 204 says the past tense of the method, such as `admitted` for `admit`. A
method whose result is a state, not a past tense, names it: `.Says("draining")`.
With `--json`, a 204 prints the key and the result, such as
`{"machine_id":"m-1","result":"admitted"}`. A behavior prints its table of
results for each host, which the behavior runtime gives.

**No command writes its own output.** A command that prints a different shape
from its data changes its data. `token roles list` was a matrix of each
permission against each role. It is now a table of the roles, and
`token roles get` shows what one role grants. `audit export` wrote a file. It
now prints the entries, and `--json > audit.json` keeps them.

The DSL had a renderer, `command.Render(...).Because("...")`, for a shape that
no output type gave. Each response that needed one changed instead, the last
when the controller began to answer the span tree of a trace
(osapi-io/osapi#904). The renderer had no user, and it is removed
(osapi-io/osapi#913). A tree is a list of the row's own type.

`osapi cli command spec` teaches the tags. With `--json`, a command prints its
output, and nothing renders it.

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

Three groups have them today. The behavior group has `osapi behavior spec get`
and `osapi behavior validate`. The endpoint group has
`osapi controller endpoint spec get` and `osapi controller endpoint validate`.
The config group has `osapi config list` and `config get` in place of `spec`,
and `osapi config validate`. A workflow DSL in osapi-orchestrator gets the same
commands, from `guide` in a public package, in osapi-io/osapi#764.

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

The help has one style too. The one line of a command, and the help of each
flag, start with a capital letter and have no period at the end, as the lines of
cobra have none. The long help is sentences. A test of each command holds this,
for the commands that a person writes and the ones that a definition makes.

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
the full contract of a behavior. It prints from its output type, as each command
does:

```text
Behavior:
  Name:         sysctl
  Placement:    node
  Internal:     no
  API:          yes
  CLI:          yes
  Platforms:    debian
  Sudo:         sysctl
  Uses:         managedfile
  Used by:      none

Methods (5):
  NAME    VERB   HTTP  ROUTE                                   PERMISSION    DESCRIPTION
  list    read   GET   /api/next/node/{hostname}/sysctl        sysctl:read   List the kernel's parameters ...

Types (5):
  NAME    INPUT                         OUTPUT
  list    ListInput { prefix }          []Entry { key, value, managed }
  create  CreateInput { key*, value* }  MutationResult { key, changed }

Settings (1):
  KEY                   AGENT FLAG    TYPE    DEFAULT
  behaviors.sysctl.dir  --sysctl-dir  string  /etc/sysctl.d

Telemetry:
  Span:             behavior.sysctl.<method>
  Child spans:      behavior.managedfile.<method>, exec sysctl, file.write, ...
  Recorded inputs:  key (get, create, update, delete)
```

- **Types.** Each method shows its input and output by their Go type names, with
  the fields in braces. A required input field has a `*`. A list output is `[]`
  and its element.
- **Chains.** `Uses` is the behaviors that this one requires, through
  `Requires`. `Used by` is the behaviors that require this one. A behavior that
  uses none says `none`.
- **Telemetry.** What each call of the behavior records: the span, the spans
  under it, the three metrics and the attributes that each method gets. Then the
  input fields that each method records, and the methods that record each. A
  method records the field that `.Key` names, and each field with the tag
  `telemetry:"attr"`. The names come from `internal/behavior`. Thus the block
  cannot be different from what osapi records.

`osapi behavior method get --name <behavior> --method <method>` shows one method
in full: its route, permission and command, each input field with its type,
constraints and description, the fields of its output, and its examples as input
and output pairs. It is a command of its own because it prints a different thing
from `get`.

`--json` of `get` has the same content, with `uses` and `used_by` as lists of
names, and the command, route and permission of each method. `--json` of
`method get` adds the input and the output of the method as JSON Schema, with
the Go type name of each, and its examples and refusals.

### Empty lists

An empty list keeps its heading with `(0)`, and tells what to do next:
`None. Upload one with osapi client file upload.` A header row with no rows
under it is incorrect. A heading with nothing under it is also incorrect.

### Values

- Times are local, `2026-11-12 18:15:13`. With `--json`, they are RFC 3339.
  `cli.FormatTime` prints a time that comes as text, and `cli.LocalTime` a
  `time.Time`. A command does not call `Format` on a time of its own: the audit
  list did, and printed the zone that the controller stored, not the local zone
  (osapi-io/osapi#864).
- Durations are rounded to a useful precision: `6ms`, `1.2s`, `3m4s`.
- Sizes have one decimal and their unit: `3.4 GB used of 7.7 GB`.
- A percentage is a whole number with `%`, such as `67%` of packet loss or `45%`
  of a disk. A CPU percentage has one decimal, `12.3%`, because it is often
  below 1%.
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
