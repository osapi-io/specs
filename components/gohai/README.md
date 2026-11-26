# gohai

gohai collects system facts. It is an SDK first, which you import at
`pkg/gohai`. It also ships a CLI over the same collectors. The entry point of
the CLI is `main.go`, and its commands are under `cmd/`. The first sentence of
its README calls it SDK first. Thus its consumers are programs, not people. A
program that depends on a shape with no documentation breaks without a signal
when the shape changes.

It has 62 collector packages and 10 categories. It has 314 Go files, and 205 of
them are not tests.

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

`Collect` can return nil when a platform does not support what the collector
reads. That is a normal result, not an error. Thus a caller that checks for nil
handles the ordinary case.

`DefaultEnabled` keeps large and privileged collectors off until a caller asks
for them. The interface names the cases: ssh host keys, the full package
inventory and the full service list. A consumer who expects one of those in a
default run gets nothing and no error.

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

The warning of the interface is more important than the mechanism. `prior`
always has each collector that you declared, and it **can** have more upstream
collectors. Thus a collector that reads an undeclared collector works until the
schedule changes. Then it does not work. Declare what you read.

## The registry (`internal/collector/registry.go`)

A caller uses eight exported functions, and nothing more.

```
NewRegistry  Register  Get  Names  NamesInCategory  Selected  SelectedWith  Run
```

The registry adds the declared dependencies, and runs the collectors in
topological levels. The order comes from `Dependencies`. It never comes from the
order of registration or of the request. Thus a caller cannot put work in order
with the order of a list. `expandWithDeps` and `topoLevels` do this.

`pkg/gohai/gohai.go` registers all 62 collector packages, in one location. If a
collector exists and is not registered there, nobody can use it, and nothing
reports it.

## Output

The collectors give facts as Go values. `FromFacts` in `pkg/gohai/ocsf` changes
them to an OCSF form. It converts what gohai already collected. It is not a
second collection path.

`schemas/gohai.schema.json` describes the fact output. The code under
`schemas/gen` generates it. Thus the next run removes a change that you make by
hand.

## Counting collectors

There are two numbers. Each one is correct for a different question.

**62 implemented.** `ls -d pkg/gohai/collectors/*/ | wc -l`.

**65 in the catalog.** These are the 62 implemented rows, each with a link to a
page, and three entries that are deliberately not implemented: `rackspace`,
`softlayer` and `eucalyptus`. They have no link, a tombstone marker and no
package.

```sh
grep -cE '^\| (\[|[a-z])' docs/collectors/README.md   # 65, both kinds of row
grep -c '^| \[' docs/collectors/README.md             # 62, the linked ones
```

That pair is in a code block, not in a table. A command with a regex alternation
cannot stay correct in a markdown table cell. The table writes a pipe as a
backslash and a pipe, and so does the alternation. Thus nothing can tell them
apart after that.

The move out of the table was not sufficient alone. The second command kept the
escape of the table and read `'^\| \['`. Basic grep reads `\|` as the
alternation operator, not as a pipe. Thus the pattern means "an empty string or
a bracket", each line matches, and it returned 180, not 62. The fix is a pipe
without the escape. A code block needs no escape, and the two conventions use
the same two characters for opposite meanings.

A reader who compares `ls` with the catalog, and knows only one of the numbers,
thinks that something is broken. Nothing is broken. The catalog gives the two
numbers and what each counts. It did not do this until gohai#201.

## What is in the repository

There are 62 collector packages in 10 categories, and 205 Go files that are not
tests.

## Known limitations

There are three. In the first two, nothing reports the error. A built-in
collector that does not register makes `gohai.New` panic, and a test in
`pkg/gohai` checks that each built-in collector has a `Facts` field that
`Facts.set` fills.

**An undeclared dependency works until it does not.** `prior` always has what a
collector declared. It **can** also have upstream collectors that it did not
declare. A read of one of those works now. It breaks when the schedule changes,
and nothing warns before that. Declare what you read.

**A default run does not include the large collectors, and says nothing.**
`DefaultEnabled` returns false for ssh host keys, the full package inventory and
the full service list. A consumer who expects one of those in a default run gets
no value and no error. A collector that finds nothing gives the same result.

**`schemas/gohai.schema.json` is generated.** The next run of `schemas/gen`
removes a change that you make by hand.

## Not covered here

What each collector reads. There are 62, and the catalog lists what each
returns. [Its own document](collectors.md) has the rule that all 62 obey. This
page does not describe the 62 instances.

The CLI flags, other than the `--collector.<name>` form that the catalog
describes.

The OCSF field mapping in `schemas/field-mapping.md`.

The test conventions of gohai. They are in its own `CONTRIBUTING.md`.

______________________________________________________________________

Written from the gohai repository.
