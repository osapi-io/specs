# gohai

gohai collects system facts. It is an SDK first, which you import at
`pkg/gohai`. It also ships a CLI over the same collectors. The entry point of
the CLI is `main.go`, and its commands are under `cmd/`. The first sentence of
its README calls it SDK first. Thus its consumers are programs, not people. A
program that depends on a shape with no documentation breaks without a signal
when the shape changes.

Each fact is one collector package under `pkg/gohai/collectors/`, and each
collector has one category. `ls pkg/gohai/collectors` lists them.

## Where it sits

gohai is the read layer of osapi: what osapi detects or reads on a host comes
from gohai, and a read that osapi needs and gohai lacks goes into gohai.
[How they fit together](../../ARCHITECTURE.md) has the decision and where the
move is now. osapi imports gohai for the family of a host, and its other reads
follow.

One more connection exists, and no `go.mod` records it. The build of gohai gets
the `go`, `just` and `md` modules from `osapi-justfiles` with `curl`. Thus a
change there gets to the next CI run of gohai.

## Read about it

| Subject                                        | What it answers                                                                                     |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| [How a collector gathers facts](collectors.md) | The sources a collector reads through, what it reads, what a field is called, and `gohai collector` |

## The collector contract (`internal/collector/collector.go`)

The interface has five methods, and nothing more.

```go
type Collector interface {
    Name() string
    Category() Category
    DefaultEnabled() bool
    Dependencies() []string
    Collect(ctx context.Context, prior PriorResults) (any, error)
}
```

What `Collect` returns sets the status of the collector in the facts. The status
is in `_status` of the output, and in `Facts.Status`:

| `Collect` returns        | Status        |
| ------------------------ | ------------- |
| the fact and no error    | `ok`          |
| nil and no error         | `absent`      |
| nil and `ErrUnsupported` | `unsupported` |
| nil and an error         | `failed`      |
| the fact and an error    | `partial`     |

`absent` means that the host has nothing to report. `unsupported` means that the
platform has nothing to read, such as the macOS variant of a Linux-only
collector. Neither is an error of the run, and neither goes into `_errors`. A
`partial` collector keeps what it read before the error, and its error goes into
`_errors`. Thus one failed read does not remove the other facts of a collector.
`StatusOf` in `collector.go` makes this decision, and `Absent` tells a source
that is not on the host from a read that failed.

Two more helpers in `collector.go` keep the status correct. `Result` changes a
nil pointer to an untyped nil. A typed nil `*Info` in an `any` is not nil, so
without `Result` the output has a `null` fact. `Cancelled` tells a read that
stopped because the run was cancelled or ran out of time. Then the collector
gives no fact, also when earlier reads worked, because the run did not finish.

`DefaultEnabled` keeps a collector off until a caller asks for it. A default run
has 21 of the 64 collectors, and the `DEFAULT` column of `gohai collector list`
names them. The large and privileged collectors are off, such as ssh host keys,
the full package inventory and the full service list. Each cloud collector, and
many hardware and Linux collectors, are off too. A collector that is off still
runs when a selected collector depends on it: `shard` is on and depends on
`dmi`, so a default run has 22 statuses. A consumer who expects a collector that
is off gets nothing and no error.

`Category` returns one of ten values. Constants close the set. A convention does
not.

```
system  hardware  network  cloud  virtualization
security  software  users  linux  misc
```

One or more collectors use each of the ten. To add an eleventh, add a constant.
Do not give a new string.

### Dependencies between collectors

`Dependencies` declares what must run first. `PriorResults` has the typed output
of the collectors that completed. The generic `GetDep[T]` gets one result with
its type.

`prior` has each declared collector that returned a fact, with the status `ok`
or `partial`. A declared collector that is `absent` or `unsupported` is not in
`prior`, and the dependent runs without it. A declared collector that `failed`
stops the dependent: it does not run, its error wraps `ErrDependencyFailed`, and
its status is `failed`. Thus the dependents of that dependent do not run either.

`prior` has each collector that finished before this one started. Thus it
**can** also have collectors that you did not declare. An undeclared collector
is in `prior` only when it finished first, and that can change from one run to
the next. Declare what you read.

## The registry (`internal/collector/registry.go`)

A caller uses seven exported functions, and nothing more.

```
NewRegistry  Register  Get  Names  NamesInCategory  SelectedWith  Run
```

`Names` and `NamesInCategory` return sorted names. `Register` refuses a
duplicate name, and a collector that `CheckSources` refuses: a field with a
source name such as `FS` or `Exec`, and another type.

`Run` takes `Hooks`, with three optional callbacks. `OnError` gets the error of
each collector that failed or was partial. `OnComplete` gets the time of each
collector. `OnStatus` gets the status and the error of each collector that ran,
or that a failed dependency stopped. A collector that panics gives a
`*PanicError`, which has the stack. Thus one collector does not stop the process
that runs gohai.

The registry adds the declared dependencies of each requested collector
(`expandWithDeps`). It starts a collector when each of its dependencies has
finished. It does not wait for a level of collectors to finish. Thus a dependent
does not wait for a slow collector that it does not need, and collectors with no
path between them run at the same time. `topoLevels` finds a dependency cycle
and the collectors with no dependency, which start first. It does not set when
the other collectors start.

The order comes from `Dependencies`. It never comes from the order of
registration or of the request. Thus a caller cannot put work in order with the
order of a list. After a context is cancelled, no collector starts, and `Run`
returns the facts that finished with the error of the context.

The `Facts` struct in `pkg/gohai/facts.go` is the one list of the collectors.
`pkg/gohai/gen` reads it and writes `pkg/gohai/builtins.gen.go`, which holds the
registration of each collector package and the cases of `Facts.set`. Thus a
registration, a `Facts` field and a `set` case cannot disagree. To add a
collector, add its field to `Facts` and run `just generate`. Do not edit
`builtins.gen.go`, because the next `go generate` writes over it.

`registerBuiltins` returns the error of a collector that does not register, and
`gohai.New` and `gohai.NewRegistry` return it. `TestBuiltinCollectors` in
`pkg/gohai` checks the lists that the generator does not write. It fails when a
collector has no `Facts` field that `Facts.set` fills, when a field of `Facts`
has no collector, or when a collector has no description in `Collectors()`, no
schema property or no page under `docs/collectors`. It also fails when a source
field of a collector does not get the source that the caller gave.

## The SDK API (`pkg/gohai`)

A program uses `New` with options such as `WithCollectors` and `WithSources`,
then `Collect`, which returns `Facts`. `Facts` has a typed field for each
collector, `Errors` (`_errors`), `Status` (`_status`) and, with `WithTimings`,
`Timings`.

`New` returns an error when the caller disables a collector that a selected
collector depends on, directly or through a different dependency. The registry
adds each dependency to a run, so without this error the disabled collector
runs. The error names the two collectors, and tells the caller to enable the
first or to disable the second too. Thus `gohai collect --no-collector.dmi`
fails, because the default `shard` depends on `dmi`.

`Facts.Err(name)` returns the error value of a collector, and `Errors` has its
text. `Err` is not nil for each collector with the status `failed` or `partial`.
For a collector that panicked, or whose dependency panicked, the error is a
`*gohai.PanicError`, with the stack. Use `errors.As` to get it. `Facts` that a
caller reads back from JSON have only `Errors`, so `Err` is nil for them. When
the context is cancelled, `Collect` returns the error and the `Facts` of the
collectors that finished.

`Collectors`, `CollectorSpec`, `Field` and `Reads` describe each collector: its
fields, how a caller builds it and what it reads on each platform. osapi reads
them, so they stay public. `NewRegistry` returns a `Registry` interface: the
sorted names of the collectors and their categories. The CLI uses it for its
flags.

The rules of a collector are not in the SDK. `internal/spec` has them, and only
`gohai collector validate` uses them.

Each collector package exports a `Collector` interface that embeds the contract
of `internal/collector`. Thus a public type names internal types. Nobody outside
gohai builds a collector, and gohai#624 records the decision about this.

## Output

The collectors give facts as Go values. `FromFacts` in `pkg/gohai/ocsf` changes
them to an OCSF form. It converts what gohai already collected. It is not a
second collection path.

`schemas/gohai.schema.json` describes the fact output, with `_errors`, `_status`
and `_timings`. The code under `schemas/gen` generates it. Thus the next run
removes a change that you make by hand.

## Counting collectors

There are two numbers. Each one is correct for a different question.

**64 implemented.** `ls -d pkg/gohai/collectors/*/ | wc -l`.

**67 in the catalog.** These are the 64 implemented rows, each with a link to a
page, and three entries that are deliberately not implemented: `rackspace`,
`softlayer` and `eucalyptus`. They have no link, a tombstone marker and no
package.

```sh
grep -cE '^\| (\[|[a-z])' docs/collectors/README.md   # 67, both kinds of row
grep -c '^| \[' docs/collectors/README.md             # 64, the linked ones
```

That pair is in a code block, not in a table. A command with a regex alternation
cannot stay correct in a markdown table cell. The table writes a pipe as a
backslash and a pipe, and so does the alternation. Thus nothing can tell them
apart after that.

The move out of the table was not sufficient alone. The second command kept the
escape of the table and read `'^\| \['`. Basic grep reads `\|` as the
alternation operator, not as a pipe. Thus the pattern means "an empty string or
a bracket", each line matches, and it returned 180, not the count of the linked
rows. The fix is a pipe without the escape. A code block needs no escape, and
the two conventions use the same two characters for opposite meanings.

A reader who compares `ls` with the catalog, and knows only one of the numbers,
thinks that something is broken. Nothing is broken. The catalog gives the two
numbers and what each counts. It did not do this until gohai#201.

## What is in the repository

Each collector is a package under `pkg/gohai/collectors/`, with its variants for
each family and its public test suite.

## Known limitations

There are four.

**An undeclared dependency works only some of the time.** `prior` **can** have
collectors that a collector did not declare. A read of one of those works only
when that collector finished first. Which collector finishes first can change
from one run to the next, and nothing warns about it. Declare what you read.

**A default run has 21 of the 64 collectors, and says nothing about the
others.** `DefaultEnabled` returns false for the other 43, such as ssh host
keys, the full package inventory, the full service list and each cloud
collector. A consumer who expects one of those in a default run gets no value
and no error. Those collectors did not run, so they have no status.

**`schemas/gohai.schema.json` is generated.** The next run of `schemas/gen`
removes a change that you make by hand.

**A program cannot add its own collectors.** The contract is in `internal/`, and
`Facts` has a field only for each built-in collector. Extensions are planned,
not built: gohai#391 asks for them, and gohai#566 records the design, a small
public `Extension` interface that a program implements and registers.

## Not covered here

What each collector reads. There are 64, and the catalog lists what each
returns. [Its own document](collectors.md) has the rule that all 64 obey. This
page does not describe the 64 instances.

The CLI flags, other than the `--collector.<name>` form that the catalog
describes.

The OCSF field mapping in `schemas/field-mapping.md`.

The test conventions of gohai. They are in its own `CONTRIBUTING.md`.

______________________________________________________________________

Written from the gohai repository.
