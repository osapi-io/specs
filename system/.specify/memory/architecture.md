# How the osapi-io repositories fit together

Six components, one product. osapi is the thing an operator runs; everything else
either supports it or drives it.

A seventh repository, `specs`, holds this documentation and is not a component. It
matters once below, because it consumes `osapi-justfiles` like the others do, which
is why the blast radius of a justfiles change is seven and not six.

```
      nats-client ─┐
                   ├─→ osapi ──→ osapi-orchestrator
      nats-server ─┘

      gohai                    (standalone)

      osapi-justfiles          (build, all seven, by fetch)
```

| Repository                                                       | Is                                            | Read it to learn                             |
| ---------------------------------------------------------------- | --------------------------------------------- | -------------------------------------------- |
| [osapi](../../../components/osapi/.specify/memory/spec.md)        | The API and the agent                         | how a request becomes work on a host         |
| [osapi-orchestrator](../../../components/osapi-orchestrator/.specify/memory/spec.md) | A declarative layer over osapi's SDK | how ordered work across hosts is described |
| [nats-client](../../../components/nats-client/.specify/memory/spec.md) | A wrapper over the NATS client            | what osapi's transport gives it              |
| [nats-server](../../../components/nats-server/.specify/memory/spec.md) | A NATS server embedded in its consumer    | how osapi runs its own bus                   |
| [gohai](../../../components/gohai/.specify/memory/spec.md)        | A system fact collection library               | how facts are gathered, if you need them     |
| [osapi-justfiles](../../../components/osapi-justfiles/.specify/memory/spec.md) | Shared `just` recipes            | why every repository's `just test` is the same |

## Where to start

**Start with osapi.** Five of the six either feed it or consume it, so its
document is the one that makes the others legible. Read its
[job system](../../../components/osapi/.specify/memory/architecture/job-system.md)
next, because the queue is the mechanism the whole product is built on.

**gohai is the exception.** It has no edge in either direction, so it reads
standalone and is the right place to start if you want to see the documentation
shape without holding another repository in your head.

## What crosses a boundary

### The transport

osapi embeds a NATS server through `nats-server` and talks to it through
`nats-client`. **Neither of those repositories knows about the other**, and
neither knows about osapi. They wrap opposite ends of the same upstream library,
and osapi is the only thing that holds both.

Two things about that pairing matter and are stated in neither wrapper alone.
`nats-client` adds no reconnection policy, so a dropped connection is handled by
whatever the upstream library does by default and osapi is not notified.
`nats-server` forces debug and trace logging on and attaches its logger after the
server is already running, so osapi's own startup logging from the bus goes
somewhere else. **osapi's memory mentions neither**, and an operator debugging a
transport problem needs both.

### The SDK surface

`pkg/sdk/client` is the contract between osapi and its orchestrator. A change to
it is the widest-reaching code change in the organisation after a justfile change.

The orchestrator pins osapi by **pseudo-version commit rather than tag**, so the
break is delayed rather than absent: a rename lands green in osapi and fails in
the orchestrator at whatever later moment somebody bumps the pin. **Land a rename
and its bump together** is the rule that follows, and it is the only coordination
rule in this organisation that spans repositories.

The coupling reaches further than the layer built for it. The orchestrator's
`internal/engine` imports osapi's SDK directly, so `internal` there describes
visibility rather than independence, and it declares no interface that would have
insulated it.

### The build

Every repository fetches `osapi-justfiles` through a justfile recipe, from
`refs/heads/main`. Nothing is pinned, nothing records which version a build used,
and `.just/` is gitignored everywhere.

`md` reaches all seven consumers, `just` six, `go` five, and `react` and
`docusaurus` one each. So **`md.just` is the widest change available in the
organisation.** The specs repository, whose `just test` gates every corpus change,
is downstream of it.

## What no single repository states

Three facts live between repositories and belong here because no component's
memory owns them.

**The dependency graph has one hub and one terminal.** osapi is the only
repository with edges in both directions. osapi-orchestrator has an incoming Go
edge and no outgoing one. gohai has neither.

**A change's blast radius is not proportional to the repository's size.**
`osapi-justfiles` has no Go at all and reaches seven repositories. `nats-server`
has twelve Go files and forces a logging decision on the largest one.

**Two repositories wrap the same upstream library from opposite ends**, and the
facts a consumer needs about reconnection and logging are split between them.

## What is not here

How any one repository works. That is its own document, linked above.

Anything about `specs` or `.github`, which are the organisation's own repositories
rather than components. `specs` is where components are described; `.github` holds
shared configuration and has no justfile.

______________________________________________________________________

The graph is re-derived rather than trusted:

```sh
grep -oE "osapi-io/[a-z-]+" */go.mod    # the Go edges
grep -ln justfiles */justfile           # the build edge, which is in no go.mod
```

Run them from the directory holding the clones. The second command is the one that
matters: the build edge appears in no module graph, so a reader who ran only the
first would conclude `osapi-justfiles` has no dependents.
