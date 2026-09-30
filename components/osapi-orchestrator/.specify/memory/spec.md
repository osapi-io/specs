# osapi-orchestrator

`osapi-orchestrator` describes ordered work across a fleet and runs it. It is a Go
library over [osapi](../../../osapi/.specify/memory/spec.md)'s SDK, one package at
`pkg/orchestrator`, no binary. A consumer imports it, describes what should happen,
and calls `Run`.

```go
o := orchestrator.New(client)

o.PackageInstall("_all", "nginx").Named("install")
o.ServiceRestart("_all", "nginx").After("install").OnlyIfChanged()
o.HealthCheck().After("install").When(orchestrator.OS("debian"))

result, err := o.Run(ctx)
```

Every operation returns a `*Step`. Guards and ordering attach to the step, so the
same vocabulary works on all 101 of them.

## What it adds over calling the SDK directly

Four things, and if the wrapping did not add them the library would have no reason
to exist.

**Ordering.** `After` declares that one step follows another, so the engine
sequences from the declaration rather than from the order a consumer wrote the
calls.

**Conditional execution.** A step can depend on what earlier work did, or on what
a host is. Those are different questions and have different vocabularies, below.

**Retry.** `Retry` on a step, rather than a loop in the consumer.

**Multi-host result handling.** One step targeting twenty machines returns twenty
results, each of which succeeded, failed, changed or was skipped independently.

## Guards ask what happened; predicates ask what a host is

Conflating these is the most likely mistake, so they are named separately.

**Guards** look at earlier work. Eight of them:

```
OnlyIfChanged          OnlyIfFailed
OnlyIfAllChanged       OnlyIfAnyHostFailed
OnlyIfAnyHostSkipped   OnlyIfAllHostsFailed
OnlyIfAnyHostChanged   OnlyIfAllHostsChanged
```

The per-host variants exist because a step spanning twenty machines has twenty
outcomes, and "any host failed" and "all hosts failed" want different follow-up.

**Host predicates** look at the machine. Ten of them, reaching a step through
`When` and `WhenFact`:

```
OS      Arch          MinMemory    MinCPU      HasLabel
Healthy FactEquals    HasCondition NoCondition MatchAll
```

`MatchAll` combines them. `FactEquals` reads a fact the agent gathered, which is
what lets a step depend on something osapi discovered rather than something the
consumer already knew.

## The rest of the step vocabulary

`Named` gives a step an identity for `After` to refer to. `Retry` sets attempts.
`OnError` and `ContinueOnError` decide whether a failure stops the plan or is
recorded and passed. Fifteen methods on `Step` in total.

## Two layers, and a plan between them

`pkg/orchestrator` is the vocabulary a consumer writes in. `internal/engine`
executes. The boundary is a plan: the public package builds one, the engine runs
it.

```
pkg/orchestrator/     ops.go, step.go, predicate.go, result.go, orchestrator.go, …
internal/engine/      plan.go, task.go, runner.go, bridge.go, result.go
```

**`internal/engine` imports osapi's SDK directly**, in `bridge.go`, `plan.go` and
`task.go`. So the engine works on osapi's generated types rather than on an
abstraction, and the word `internal` describes visibility rather than
independence. See the limitations below.

## Where it sits

It depends on [osapi](../../../osapi/.specify/memory/spec.md). **Nothing in the
organisation depends on it**, which makes it the only component with an incoming
Go edge and no outgoing one.

It pins osapi by pseudo-version commit rather than tag, so an SDK change does not
reach here until somebody bumps it. A rename in osapi lands green there and fails
here at the bump.

Its build fetches
[osapi-justfiles](../../../osapi-justfiles/.specify/memory/spec.md) through a
justfile recipe, from `main`. That edge is in no `go.mod`.

The organisation-wide picture is
[system's architecture](../../../../system/.specify/memory/architecture.md).

## The contract

The exported surface of `pkg/orchestrator`: 16 functions, 13 types, 127 methods,
of which 101 are the operations. Everything under `internal/` is not the contract,
**including the parts of it that import osapi's SDK.**

`pkg/orchestrator` declares **no interfaces at all.** `nats-client` and
`nats-server` each declare exactly one and use it as the seam for substituting
what they wrap; this substitutes nothing, so a consumer cannot replace the SDK
underneath it and the repository's own tests reach osapi's generated client
directly.

## Documentation coverage is exact, and nothing keeps it that way

140 pages against 81 Go files, more documentation than code. **101 operation pages
map one to one onto 101 operation methods**, with no orphan page and no
undocumented method.

That was checked by iterating headings in both directions rather than by comparing
totals, because 101 and 101 agreeing says nothing about whether they are the same
101. Reproduce it:

```sh
# every page has a method
for p in $(find docs/operations -name '*.md' -not -name 'README.md'); do
  grep -q "func (o \*Orchestrator) $(head -1 "$p" | sed 's/^# //')(" pkg/orchestrator/ops.go || echo "NO METHOD: $p"
done
# every method has a page
for m in $(grep -oE '^func \(o \*Orchestrator\) [A-Z][A-Za-z]*' pkg/orchestrator/ops.go | sed 's/.*) //'); do
  grep -rqx "# $m" docs/operations --include='*.md' || echo "NO PAGE: $m"
done
```

It is the only documentation set in the organisation that reconciles. **Nothing
enforces it**, which is the limitation below.

## What was measured

At `727ab40`, 2026-09-30.

| Measurement                          | Value | Command                                                                                                             |
| ------------------------------------ | ----: | ------------------------------------------------------------------------------------------------------------------- |
| Go files                             |    81 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                                                |
| Go files excluding tests             |    59 | `find . -name '*.go' -not -path './.git/*' -not -name '*_test.go' \| wc -l`                                          |
| Non-test files in `pkg/orchestrator` |    12 | `find pkg/orchestrator -maxdepth 1 -name '*.go' -not -name '*_test.go' \| wc -l`                                    |
| Operation methods                    |   101 | `grep -cE '^func \(o \*Orchestrator\) [A-Z]' pkg/orchestrator/ops.go`                                               |
| Exported functions                   |    16 | `find pkg/orchestrator -maxdepth 1 -name '*.go' -not -name '*_test.go' -exec grep -hE '^func [A-Z]' {} + \| wc -l`   |
| Exported types                       |    13 | `find pkg/orchestrator -maxdepth 1 -name '*.go' -not -name '*_test.go' -exec grep -hE '^type [A-Z]' {} + \| wc -l`   |
| Interfaces                           |     0 | `find pkg/orchestrator -maxdepth 1 -name '*.go' -not -name '*_test.go' -exec grep -hE '^type [A-Z][A-Za-z]* interface' {} + \| wc -l` |
| Documentation pages                  |   140 | `find docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                                       |
| Operation pages                      |   101 | `find docs/operations -name '*.md' -not -name 'README.md' \| wc -l`                                                   |
| Directory indexes                    |    24 | `find docs/operations -name 'README.md' \| wc -l`                                                                    |
| Feature pages                        |    14 | `find docs/features -name '*.md' \| wc -l`                                                                           |
| README lines                         |   119 | `wc -l README.md`                                                                                                   |

One measurement needs care.
`grep -cE '^func \(o \*Orchestrator\) [A-Z].*\) \*Step \{$'` returns **2**, not
101, because most signatures span three lines and the return type sits on its own.
That command looks more careful than the one above it and is wrong by two orders
of magnitude.

## Known limitations

**The engine is not insulated from osapi's SDK.** Four files in `internal/engine`
import it. There may be no reason to abstract a dependency this repository exists
to consume, but the decision is stated nowhere and a consumer cannot infer it.

**No interface means no seam.** Even a consumer who wanted to substitute osapi's
client could not.

**Nothing verifies the documentation mapping.** It holds today and was checked by
hand. The 102nd operation can be added without a page and no gate will say so, so
the repository with the best documentation coverage in the organisation has no
mechanism protecting it.

## Not covered here

What each of the 101 operations does. Each has its own page under
`docs/operations/`, and the shape they share is above.

What osapi's SDK does, which is
[osapi's](../../../osapi/.specify/memory/spec.md).

The 14 feature pages, the `dist/` build output, and the repository's own
contributor conventions.

Whether eight guards and ten predicates are the right eight and ten.

______________________________________________________________________

Traced to `specs/001-orchestrator-baseline/`.
