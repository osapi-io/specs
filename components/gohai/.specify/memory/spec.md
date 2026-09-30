# gohai

gohai collects system facts. It is an SDK first, importable at `pkg/gohai`, and
it ships a CLI over the same collectors with its entry point at `main.go` and
commands under `cmd/`. Its README calls it SDK first in its own first sentence,
so consumers are programs rather than people, and a program that depends on an
undocumented shape breaks quietly when the shape changes.

62 collector packages, 10 categories, 314 Go files of which 205 are not tests.

## Where it sits

Nothing in the organization depends on gohai, and gohai depends on nothing in the
organization. It is the only component with no edge in either direction, which is
why `system`'s repository map uses it as the worked example: you can read this
document without holding another repository in your head.

Its build fetches `osapi-justfiles` through a justfile recipe, from `main` rather
than from a release. That edge is in no `go.mod`.

## The collector contract (`internal/collector/collector.go`)

Five methods. That is the whole of what a collector implements.

```go
type Collector interface {
    Name() string
    Category() Category
    DefaultEnabled() bool
    Dependencies() []string
    Collect(ctx context.Context, prior PriorResults) (any, error)
}
```

`Collect` may return nil when a platform does not support what the collector
gathers. That is a normal outcome, not an error, so a caller checking for nil is
handling the ordinary case.

`DefaultEnabled` keeps heavy and privileged collectors off until a caller asks
for them. The interface names the cases: ssh host keys, full package inventory,
full service list. A consumer who expected one of those in a default run gets
nothing and no error.

`Category` returns one of ten, and the set is closed by constants rather than by
convention.

```
system  hardware  network  cloud  virtualization
security  software  users  linux  misc
```

All ten are in use by at least one collector. Adding an eleventh means adding a
constant, not passing a new string.

### Dependencies between collectors

`Dependencies` declares what must run first. `PriorResults` carries the typed
output of what finished, and the generic `GetDep[T]` pulls one out with its type
intact.

The interface's own caveat matters more than the mechanism. `prior` always
includes everything the collector declared, and it **may** include additional
upstream siblings. So a collector that reads a sibling it never declared works,
until the day scheduling changes and it does not. Declare what you read.

## The registry (`internal/collector/registry.go`)

Eight exported functions are the whole of what a caller drives.

```
NewRegistry  Register  Get  Names  NamesInCategory  Selected  SelectedWith  Run
```

The registry expands declared dependencies and runs collectors in topological
levels. Ordering comes from `Dependencies`, never from the order a caller
registered or requested them, so a caller cannot sequence work by listing it in
sequence. `expandWithDeps` and `topoLevels` do this.

All 62 collector packages are registered in one place, `pkg/gohai/gohai.go`. A
collector that exists and is not registered there is unreachable, and nothing
reports that.

## Output

Facts come out as Go values from the collectors. `FromFacts` in `pkg/gohai/ocsf`
converts them to an OCSF representation, and it is a conversion of what was
already collected rather than a second collection path.

`schemas/gohai.schema.json` describes the fact output. It is generated, by the
code under `schemas/gen`, so editing it by hand is lost on the next run.

## Counting collectors

Two numbers, and both are right about different questions.

**62 implemented.** `ls -d pkg/gohai/collectors/*/ | wc -l`.

**65 catalogued.** The 62 implemented rows, which link to a page each, plus three
deliberately unimplemented entries that do not: `rackspace`, `softlayer` and
`eucalyptus`. They carry a tombstone marker and have no package.

```sh
grep -cE '^\| (\[|[a-z])' docs/collectors/README.md   # 65, both kinds of row
grep -c '^\| \[' docs/collectors/README.md             # 62, the linked ones
```

That pair sits in a code block rather than in the table below because a command
holding a regex alternation cannot survive a markdown table cell. The table
escapes a pipe as a backslash-pipe and so does the alternation, so nothing can
tell them apart afterwards.

A reader who compares `ls` against the catalogue and has been told only one of
the figures concludes something is broken. Nothing is. The catalogue documents
both figures and what each counts, which it did not do until gohai#201.

## What was measured

At the baseline, 2026-09-29.

| Measurement              | Value | Command                                                                              |
| ------------------------ | ----: | ------------------------------------------------------------------------------------ |
| Go files                 |   314 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                 |
| Go files excluding tests |   205 | `find . -name '*.go' -not -path './.git/*' -not -name '*_test.go' \| wc -l`           |
| Implemented collectors   |    62 | `ls -d pkg/gohai/collectors/*/ \| wc -l`                                             |
| Registered collectors    |    62 | `grep -oE 'collectors/[a-z_]+' pkg/gohai/gohai.go \| sort -u \| wc -l`               |
| Collector methods        |     5 | `awk '/^type Collector interface/,/^}/' internal/collector/collector.go \| grep -cE '^\t[A-Z]'` |
| Category constants       |    10 | `grep -cE '^\tCategory[A-Za-z]+ +=' internal/collector/collector.go`                 |
| Categories in use        |    10 | `grep -rhoE 'collector\.Category[A-Za-z]+' pkg/gohai/collectors/ \| sort -u \| wc -l` |
| Documentation pages      |    68 | `find docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                        |

Registered and implemented both return 62, and they are separate commands
checking separate things. A collector can exist without being registered, and
that is the failure the pair catches.

## What the baseline found in gohai's own prose

Both are fixed in gohai now, by gohai#201. They are kept here because they
explain why a count in this document carries its command.

The README said "65 collectors across 9 categories" and the catalogue said
"across 9 categories". Ten constants are declared and all ten are in use, so nine
was wrong rather than differently scoped.

Reconciling 65 against 62 meant reading the catalogue's legend, which defined
`✅` twice: once as implemented and tested, once as planned. 62 of its 65 rows are
ticks, so the Implemented column could not be read. Nobody was looking for that
and the count is what surfaced it.

## Not covered here

How any individual collector gathers its facts. There are 62 of them and they
share one contract, which is stated above; the catalogue lists them.

The CLI's flag surface beyond the `--collector.<name>` form the catalogue
documents.

The OCSF field mapping in `schemas/field-mapping.md`.

gohai's testing conventions, which are its own `CONTRIBUTING.md`'s.

______________________________________________________________________

Traced to `specs/001-gohai-baseline/`. That baseline predates the seven section
shape `system`'s 002 fixes and carries no dependency section or architecture
section of its own, which 002 records as an amendment still owed.
