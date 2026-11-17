# osapi-orchestrator

`osapi-orchestrator` describes ordered work across a fleet, and runs it. It is a
Go library over the SDK of [osapi](../osapi/README.md). It has one package at
`pkg/orchestrator`, and no binary. A consumer imports it, describes what must
occur, and calls `Run`.

```go
o := orchestrator.New(client)

o.PackageInstall("_all", "nginx").Named("install")
o.ServiceRestart("_all", "nginx").After("install").OnlyIfChanged()
o.HealthCheck().After("install").When(orchestrator.OS("debian"))

result, err := o.Run(ctx)
```

Each operation returns a `*Step`. Guards and order attach to the step. Thus the
same vocabulary works on all 101 operations.

## What it adds over calling the SDK directly

It adds four things. Without them, the library has no reason to exist.

**Order.** `After` declares that one step comes after a different step. Thus the
engine uses the declaration for the order, not the order of the calls in the
code.

**Conditional execution.** A step can depend on the result of earlier work, or
on what a host is. These are different questions with different vocabularies,
below.

**Retry.** Put `Retry` on a step. The consumer does not need a loop.

**Results from many hosts.** One step that targets twenty machines returns
twenty results. Each one succeeded, failed, changed or was skipped
independently.

## Guards ask what happened; predicates ask what a host is

There are two kinds of condition. What each one examines separates them. People
often confuse the two.

The code and `docs/features/guards.md` call all of these "guards". This page
separates them because the two kinds fail in different ways. The code does not
separate them.

**Guards** examine earlier work. There are eight:

```
OnlyIfChanged          OnlyIfFailed
OnlyIfAllChanged       OnlyIfAnyHostFailed
OnlyIfAnyHostSkipped   OnlyIfAllHostsFailed
OnlyIfAnyHostChanged   OnlyIfAllHostsChanged
```

The variants for each host exist because a step on twenty machines has twenty
results. "Any host failed" and "all hosts failed" need different next steps.

A host failed when its `Status` is `failed`. It also failed when it has an
`Error` and its `Status` is not `skipped` (`pkg/orchestrator/step.go`). A
skipped host with an error is not a failure. Thus `OnlyIfAnyHostFailed` does not
start for it.

**Host predicates** examine the machine. There are ten. They get to a step
through `When` and `WhenFact`. The code counts these two methods as guards. This
page does not.

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

`MatchAll` joins predicates. `FactEquals` reads a fact that the agent collected.
Thus a step can depend on something that osapi found, not only on something that
the consumer already knew.

## The rest of the step vocabulary

`Named` gives a step an identity, so that `After` can refer to it. `Retry` sets
the attempts. `OnError` and `ContinueOnError` decide if a failure stops the
plan, or if the engine records it and continues. `Step` has fifteen methods.

## Two layers, and a plan between them

`pkg/orchestrator` is the vocabulary that a consumer writes in.
`internal/engine` runs the work. A plan is the boundary: the public package
makes a plan, and the engine runs it.

```
pkg/orchestrator/     ops.go, step.go, predicate.go, result.go, orchestrator.go, …
internal/engine/      plan.go, task.go, runner.go, bridge.go, result.go
```

**`internal/engine` imports the SDK of osapi directly**, in `bridge.go`,
`plan.go` and `task.go`. Thus the engine uses the generated types of osapi, not
an abstraction. The word `internal` controls visibility. It does not make the
engine independent. Refer to the limitations below.

## Where it sits

It depends on [osapi](../osapi/README.md). **Nothing in the organization depends
on it.** Thus it is the only component with an incoming Go connection and no
outgoing connection.

It pins a released tag of osapi. Thus an SDK change does not get here until
somebody updates the pin. A rename in osapi passes there and fails here at the
pin update.

Its build gets [osapi-justfiles](../osapi-justfiles/README.md) through a
justfile recipe, from `main`. No `go.mod` shows that connection.

[The architecture of the system](../../ARCHITECTURE.md) shows the full
organization.

## The contract

The contract is the exported API of `pkg/orchestrator`: 16 functions, 13 types
and 127 methods. 101 of the methods are the operations. Nothing under
`internal/` is part of the contract, **also the parts that import the SDK of
osapi.**

`pkg/orchestrator` declares **no interfaces.** `nats-client` and `nats-server`
each declare exactly one. Each uses it to replace what it wraps in tests. This
package can replace nothing. Thus a consumer cannot replace the SDK under it,
and the tests of the repository use the generated client of osapi directly.

## Documentation coverage is exact, and nothing keeps it that way

There are 140 pages and 81 Go files. Thus there is more documentation than code.
**101 operation pages map one to one to 101 operation methods.** No page is
without a method, and no method is without a page.

A check of the headings in the two directions found this. A comparison of the
totals is not sufficient: two totals of 101 do not show that they are the same
101\. To do the check again:

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

It is the only documentation set in the organization where the two agree.
**Nothing enforces it.** That is the limitation below.

## How big it is

There are 101 operation methods, and 140 documentation pages for 81 Go files.

To count them, do not match on `) *Step {`. Most signatures wrap, and that
pattern returns 2.

## Known limitations

**The engine is not isolated from the SDK of osapi.** Four files in
`internal/engine` import it. This repository exists to use that dependency, so
maybe an abstraction is not necessary. But no document states the decision, and
a consumer cannot find it.

**No interface means no seam.** A consumer who wants to replace the client of
osapi cannot do it.

**Nothing verifies the documentation mapping.** It is true now, and a person
checked it by hand. Somebody can add the 102nd operation without a page, and no
gate reports it. Thus no mechanism protects the repository with the best
documentation coverage in the organization.

## Not covered here

What each of the 101 operations does. Each has its own page under
`docs/operations/`. The shape that they share is above.

What the SDK of osapi does. [The osapi page](../osapi/README.md) covers that.

The 14 feature pages, the `dist/` build output, and the contributor conventions
of the repository.

If eight guards and ten predicates are the correct eight and ten.

______________________________________________________________________

Written from `pkg/orchestrator/` and `internal/engine/`.
