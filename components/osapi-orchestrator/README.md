# osapi-orchestrator

`osapi-orchestrator` describes ordered work across a fleet and runs it. It is a
Go library over [osapi](../osapi/README.md)'s SDK, one package at
`pkg/orchestrator`, no binary. A consumer imports it, describes what should
happen, and calls `Run`.

```go
o := orchestrator.New(client)

o.PackageInstall("_all", "nginx").Named("install")
o.ServiceRestart("_all", "nginx").After("install").OnlyIfChanged()
o.HealthCheck().After("install").When(orchestrator.OS("debian"))

result, err := o.Run(ctx)
```

Every operation returns a `*Step`. Guards and ordering attach to the step, so
the same vocabulary works on all 101 of them.

## What it adds over calling the SDK directly

Four things, and if the wrapping did not add them the library would have no
reason to exist.

**Ordering.** `After` declares that one step follows another, so the engine
sequences from the declaration rather than from the order a consumer wrote the
calls.

**Conditional execution.** A step can depend on what earlier work did, or on
what a host is. Those are different questions and have different vocabularies,
below.

**Retry.** `Retry` on a step, rather than a loop in the consumer.

**Multi-host result handling.** One step targeting twenty machines returns
twenty results, each of which succeeded, failed, changed or was skipped
independently.

## Guards ask what happened; predicates ask what a host is

Two kinds of condition, split by what each one inspects. Mixing them up is the
usual mistake.

Note the code and `docs/features/guards.md` both call all ten of these "guards".
This page splits them because the two kinds fail differently, not because the
code does.

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
`When` and `WhenFact`, the two methods the code counts as guards and this
distinction does not:

```
OS      Arch          MinMemory    MinCPU      HasLabel
Healthy FactEquals    HasCondition NoCondition MatchAll
```

```sh
grep -cE '^func \(s \*Step\) OnlyIf' pkg/orchestrator/step.go   # 8 guards
grep -cE '^func \(s \*Step\) When' pkg/orchestrator/step.go     # 2, the predicate route
grep -cE '^func \(s \*Step\) [A-Z]' pkg/orchestrator/step.go    # 15 methods on Step
grep -cE '^func [A-Z][A-Za-z]*\(' pkg/orchestrator/predicate.go  # 10 predicates
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

**`internal/engine` imports osapi's SDK directly**, in `bridge.go`, `plan.go`
and `task.go`. So the engine works on osapi's generated types rather than on an
abstraction, and the word `internal` describes visibility rather than
independence. See the limitations below.

## Where it sits

It depends on [osapi](../osapi/README.md). **Nothing in the organization depends
on it**, which makes it the only component with an incoming Go edge and no
outgoing one.

It pins osapi by pseudo-version commit rather than tag, so an SDK change does
not reach here until somebody bumps it. A rename in osapi lands green there and
fails here at the bump.

Its build fetches [osapi-justfiles](../osapi-justfiles/README.md) through a
justfile recipe, from `main`. That edge is in no `go.mod`.

The organization-wide picture is [system's architecture](../../ARCHITECTURE.md).

## The contract

The exported surface of `pkg/orchestrator`: 16 functions, 13 types, 127 methods,
of which 101 are the operations. Everything under `internal/` is not the
contract, **including the parts of it that import osapi's SDK.**

`pkg/orchestrator` declares **no interfaces at all.** `nats-client` and
`nats-server` each declare exactly one and use it as the seam for substituting
what they wrap; this substitutes nothing, so a consumer cannot replace the SDK
underneath it and the repository's own tests reach osapi's generated client
directly.

## Documentation coverage is exact, and nothing keeps it that way

140 pages against 81 Go files, more documentation than code. **101 operation
pages map one to one onto 101 operation methods**, with no orphan page and no
undocumented method.

That was checked by iterating headings in both directions rather than by
comparing totals, because 101 and 101 agreeing says nothing about whether they
are the same 101. Reproduce it:

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

It is the only documentation set in the organization that reconciles. **Nothing
enforces it**, which is the limitation below.

## How big it is

101 operation methods, and 140 documentation pages against 81 Go files.

```sh
grep -cE '^func \(o \*Orchestrator\) [A-Z]' pkg/orchestrator/ops.go   # 101
```

Do not match on `) *Step {` to count those: most signatures wrap and it returns
2\.

## Known limitations

**The engine is not insulated from osapi's SDK.** Four files in
`internal/engine` import it. There may be no reason to abstract a dependency
this repository exists to consume, but the decision is stated nowhere and a
consumer cannot infer it.

**No interface means no seam.** Even a consumer who wanted to substitute osapi's
client could not.

**Nothing verifies the documentation mapping.** It holds today and was checked
by hand. The 102nd operation can be added without a page and no gate will say
so, so the repository with the best documentation coverage in the organization
has no mechanism protecting it.

## Not covered here

What each of the 101 operations does. Each has its own page under
`docs/operations/`, and the shape they share is above.

What osapi's SDK does, which is [osapi's](../osapi/README.md).

The 14 feature pages, the `dist/` build output, and the repository's own
contributor conventions.

Whether eight guards and ten predicates are the right eight and ten.

______________________________________________________________________

Written from `pkg/orchestrator/` and `internal/engine/`.
