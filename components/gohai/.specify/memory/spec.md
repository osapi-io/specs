# gohai

gohai collects system facts. It is an SDK first, importable at `pkg/gohai`, and
it ships a CLI over the same collectors with its entry point at `main.go` and
commands under `cmd/`. Its README calls it SDK first in its own first sentence,
so consumers are programs rather than people, and a program that depends on an
undocumented shape breaks quietly when the shape changes.

62 collector packages, 10 categories, 314 Go files of which 205 are not tests.

## Where it sits

No Go dependency runs in either direction. Nothing in the organization imports
gohai, and gohai's `go.mod` names one `osapi-io` path, its own module line. That
is why `system`'s repository map uses it as the worked example. You can read this
document without holding another repository in your head.

One edge exists and no `go.mod` records it. gohai's build fetches the `go`, `just`
and `md` modules from `osapi-justfiles` by `curl` from `main` rather than from a
release, so a change there reaches gohai's next CI run with nothing recording
which version built it.

Isolation is not the same as doing a different job. gohai and `osapi` read system
facts from the same upstream library at the same pinned version, independently,
which is a fact between repositories and so lives in
[how they fit together](../../../../system/.specify/memory/architecture.md). What
matters for anybody working here: osapi is not a consumer of gohai and will not
break if a collector changes.

## Read about it

| Subject                                             | What it answers                                                      |
| --------------------------------------------------- | -------------------------------------------------------------------- |
| [How a collector gathers facts](architecture/collectors.md) | Which library to wrap, what an extension may do, and what a field is called |

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
grep -c '^| \[' docs/collectors/README.md             # 62, the linked ones
```

That pair sits in a code block rather than in the table below because a command
holding a regex alternation cannot survive a markdown table cell. The table
escapes a pipe as a backslash-pipe and so does the alternation, so nothing can
tell them apart afterwards.

Moving it out was not enough on its own. The second command carried the table's
escaping with it and read `'^\| \['`, where basic grep treats `\|` as the
alternation operator rather than a literal pipe. The pattern then means "an empty
string or a bracket", every line matches, and it returned 180 instead of 62. The
fix is the pipe unescaped, since a code block needs no escaping
and the two conventions mean opposite things by the same two characters.

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

## Known limitations

Five, and the first four are cases where nothing reports the mistake.

**The registration error is discarded, and the test it defers to does not
exist.** `registerBuiltins` in `pkg/gohai/gohai.go` calls `_ = reg.Register(c)`
for each of the 62, with a comment saying a duplicate or empty name "would only
occur from programmer bugs ... which are caught by tests". The test that exists
checks that `Register` rejects a duplicate on a fresh registry. Nothing exercises
`registerBuiltins`, and the whole assertion on the built-in registry is that it
contains one name:

```sh
grep -rn 'registerBuiltins\|builtinCollectors' --include='*_test.go' .   # nothing
grep -A2 'func.*TestNewRegistry' pkg/gohai/registry_public_test.go
```

So a duplicate name among the 62 drops one collector silently, and the
justification for discarding the error is a test nobody wrote.

**The registered count does not check registration.** The
`Registered collectors` row above counts `collectors/<name>` paths in
`pkg/gohai/gohai.go`, which is source text. It catches a collector that exists and
was never added to that file, which is the failure it was written for, and it
cannot catch a collector that is in the file and did not register. Those are
different failures and only the first has a check.

**An undeclared dependency works until it does not.** `prior` always carries what
a collector declared and **may** carry upstream siblings it did not. Reading one
of those works today and breaks whenever scheduling changes, with nothing in
between to warn. Declare what you read.

**A default run omits the heavy collectors and says nothing.** `DefaultEnabled`
returns false for ssh host keys, full package inventory and full service list. A
consumer expecting one of those in a default run gets no value and no error, which
is indistinguishable from the collector finding nothing.

**`schemas/gohai.schema.json` is generated.** Editing it by hand is lost on the
next run of `schemas/gen`.

## Not covered here

What any individual collector reads. There are 62 of them and the catalogue lists
what each returns. The rule all 62 follow is
[its own document](architecture/collectors.md); what stays out here is the 62
instances of it.

The CLI's flag surface beyond the `--collector.<name>` form the catalogue
documents.

The OCSF field mapping in `schemas/field-mapping.md`.

gohai's testing conventions, which are its own `CONTRIBUTING.md`'s.

______________________________________________________________________

Traced to `specs/001-gohai-baseline/`, amended twice on 2026-09-30 to add the
dependency section and the page classification the shape requires. The limitations
above were found by reading the code rather than carried from that baseline, which
still has no section naming this repository's gaps. It is owed one, and what it
owes is now written down here rather than nowhere.
