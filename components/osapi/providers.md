# Providers

A provider is the layer that actually does something to a host. It runs **in the
agent process**, not the controller, which is why an API request becomes a
queued job instead of a function call.

Every provider implements one operation set for its domain. Where a domain is a
collection of resources, that set is list, get, create, update, delete, and
every method takes a context first.

## What an operation returns

Three things: the resource's identity, **whether anything changed**, and a
per-resource error when one occurred.

The per-resource error is reported *in* the result rather than replacing it, so
one failing host does not hide the others. A broadcast to twenty machines where
one fails returns twenty rows, nineteen of them useful.

`changed` is what makes conditional work possible for a caller. It is also what
makes the idempotency rule below expressible.

## The idempotency rule

The bus delivers at-least-once, so an operation may run twice. These three
outcomes are what make that harmless:

| Operation                             | Outcome                 |
| ------------------------------------- | ----------------------- |
| create a resource that already exists | no change, **no error** |
| delete a resource that is absent      | no change, **no error** |
| update a resource that is absent      | **error**               |

The asymmetry is deliberate. Create and delete describe a desired end state, and
the end state is already true. Update describes a change to something, and there
is nothing to change.

## osapi owns the state, so drift gets overwritten

A change made to a managed resource outside osapi is drift, and the next
operation overwrites it. osapi is what the resource is supposed to look like,
and an edit by hand does not change that.

Overwriting drift means seeing it, and a provider cannot see it by consulting
its own record. The record says what osapi last wrote, which is exactly what
drift makes untrue. So the decision is made by reading the resource: hash the
file on disk and compare it with the content to deploy, read the file's actual
uid and gid rather than the owner the record names.

The record is written, not read. It serves status, staleness and audit, and it
does not decide.

Getting this backwards does not look like a bug. It looks like an operation that
succeeds and reports no change, on the one host that needed the change.

Two consequences, both easy to miss:

A name the host does not know fails the operation rather than passing silently.
The requested owner and group resolve on the host first, and a numeric id is
accepted as itself, which is what a container image with no `passwd` entry
needs.

A platform that cannot answer the question gets the work applied rather than
assumed. If ownership cannot be read, the `chown` runs.

This is the one place the filesystem abstraction is not enough. Reading a file's
uid and gid needs the stat structure it does not carry, so that read goes to the
operating system behind an injectable seam. The abstraction cannot answer the
question, and the question has to be answered from the resource.

## Unsupported is not failure, and not no-change

An operation that the host's OS family does not support returns the shared
**unsupported outcome**, and the agent records it as `skipped`.

That is a third answer, distinct from both `ok` with no change and `failed`. A
caller can tell "this does not apply here" from "this applies and did nothing"
from "this broke", and conflating the first two is how a fleet report starts
lying.

`internal/provider/errors.go` declares it; `internal/agent/handler.go` turns it
into the skip.

## The four implementation patterns

A new provider is one of these four. Recognising which one you are writing tells
you what you owe.

**A direct provider runs commands.** `internal/provider/node/process` is the
example. Nothing else mediates; the provider is responsible for its own argument
handling.

**A provider that delegates file writes to the file deployer** gains change
tracking, idempotency and template rendering by doing so. `cron`, `service`,
`certificate` and `user` all work this way. If a provider writes a file and is
not using the deployer, that is a decision it needs to justify.

**A provider that manages its own configuration files** marks them with a
reserved filename prefix, so a managed file is distinguishable from one somebody
wrote by hand. `sysctl` is the example, and the prefix is the whole mechanism
preventing it from clobbering an operator's work.

**A provider that calls an external API** has no platform variants and
establishes availability when it is constructed rather than on first use.
`internal/provider/container` is the example.

## Platform selection happens outside the provider

A provider does not decide whether it applies. `pkg/sdk/platform`'s `Detect` and
`IsContainer` choose by OS family and by whether the process is containerised,
and `cmd/agent_setup.go` wires the result.

**Families a domain does not implement are present as stubs rather than
absent.** So the selection always finds something, and the something returns the
unsupported outcome. A missing platform is a compile-time gap rather than a
runtime nil.

## Facts

A provider gets host attributes by embedding the shared facts holder, asserting
the setter contract at compile time, and being registered.

Registration is what causes injection. **A provider that is constructed but
never registered has no facts**, and a fact-dependent operation then fails when
it is called rather than at startup, which is the worse place to find out.
`internal/provider/facts.go` holds all three pieces.

## Three rules about the boundary

Each of these was got wrong somewhere first, and each has an advisory behind it.

### Validation on the request path does not discharge the provider's

Any value that becomes a filesystem path, a filename or a command argument is
validated **in the provider**, before use.

The request path validated it once, at the time. Work executed from storage is a
second caller, arriving later, possibly under rules that did not exist when the
value was stored. GHSA-7fjw-v3g9-326g is what that cost.

### A secret never appears in a command's arguments

Arguments are treated as logged and publicly visible, because they are: they
appear in the process table and `internal/exec/exec.go` logs them.

A secret reaches a command through stdin, using the variant in `internal/exec`
built for it. GHSA-6gc6-px2x-q95j is the advisory.

### A caller's value is never parsed as an option

A value that starts with a dash and reaches a command unguarded becomes a flag.
The provider is responsible for making sure it cannot.

## What a provider goes through, not around

**Filesystem access goes through the virtual filesystem abstraction**, never the
standard library directly and never a substitute. That is what makes a provider
testable in memory and testable with injected failures.

**Commands go through the shared exec manager** rather than being spawned
directly.

**A file is not written in place.** A partially written configuration file is
worse than no write at all, so the deployer writes and moves.

## How an error reads

A provider's error reaches a job result, the audit log and a CLI user's screen,
so its wording is an interface rather than a debugging aid.

The shape is **`<domain> <verb>: what went wrong`**.

```
sysctl create: key must not be empty
schedule delete: not managed by osapi
file deploy: execute template: no such template
```

That ordering sorts and greps usefully, and it reads the same whether the error
arrives alone or wrapped by three callers above it.

Two habits to avoid, because both are already in the tree.

**An error does not announce that it failed.** `failed to execute template` is
almost always wrapped, so the reader sees "deploy schedule entry: failed to
execute template: ...", where the words carry nothing the context did not
already. Name what was being attempted and let the wrapping supply the rest.

**An error names the operation, not the command.** `chpasswd failed` leaks the
implementation into a message a CLI user reads, and it stops being true the day
the implementation changes. `user set password` survives that.

The four sentinels are the exception and stay exactly as they are, because they
are compared with `errors.Is` rather than read:

```go
ErrUnsupported  = errors.New("operation not supported on this OS family")
ErrNotFound     = errors.New("not found")
ErrNotManaged   = errors.New("not managed by osapi")
ErrNotInstalled = errors.New("not installed")
```

Wrapping with `%w` on any path that carries a cause is not optional. An error
that loses its cause cannot be matched by a caller, which is what the sentinels
exist for.

## What a provider does not touch

A provider does not reach the bus, the job store, the audit log or the HTTP
layer. It is handed a request and returns a result, and everything about how
that request arrived is somebody else's problem.

That is what makes one testable without standing anything up, and it is why a
provider can be read on its own and understood.

## What its tests owe

Three obligations, and they are the reason the coverage gate is survivable
rather than cruel.

Every platform variant is tested on its own, including the one the test machine
is not. A Debian implementation is not exercised by running the suite on a Mac,
so each variant carries its own file.

The idempotency outcomes are tested as outcomes, not as code paths. Create
against an existing resource asserts no change and no error. Delete against an
absent one asserts the same. Update against an absent one asserts the error.

The unsupported outcome is tested where a platform declares it, because a
provider returning a plain error instead is the failure that turns a skip into a
red fleet report.

Filesystem behaviour is tested in memory and with injected failures, which is
what the abstraction is for.

## Where this connects

How work reaches a provider, what happens when the same job arrives twice, and
what the four result statuses mean is [the job system](job-system.md).

What a contributor adds when a new domain needs a provider, and the seven other
artifacts that come with it, is [building a domain](domains.md).

______________________________________________________________________

Written from `internal/provider/`.
