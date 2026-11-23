# Providers

A provider is the layer that does the work on a host. It runs **in the agent
process**, not in the controller. That is why an API request becomes a queued
job and not a function call.

[Behaviors](behaviors.md) replace providers, one domain at a time. sysctl is the
first. What this page says about results, idempotency and drift applies to the
two.

Each provider implements one set of operations for its domain. When a domain is
a collection of resources, the set is list, get, create, update and delete. Each
method takes a context first.

## What an operation returns

An operation returns three things: the identity of the resource, **if anything
changed**, and an error for each resource that had an error.

The error of a resource is *in* the result. It does not replace the result. Thus
one failed host does not hide the others. A broadcast to twenty machines where
one fails returns twenty rows, and nineteen are useful.

With `changed`, a caller can do conditional work. `changed` also lets osapi
express the idempotency rule below.

## The idempotency rule

The bus delivers at least one time, so an operation can run two times. These
three results make that safe:

| Operation                             | Outcome                 |
| ------------------------------------- | ----------------------- |
| create a resource that already exists | no change, **no error** |
| delete a resource that is absent      | no change, **no error** |
| update a resource that is absent      | **error**               |

The difference is deliberate. Create and delete describe a necessary end state,
and the end state is already true. Update describes a change to something, and
there is nothing to change.

## The not-found rule

A get, an update or an action on an item that is not on the host returns
`ErrNotFound`, wrapped with `%w`. Examples are a package that is not installed,
a user, a unit, a container and a PID. A delete of an item that is not there
returns no change and no error, as the idempotency rule says.

**A command that says "not found" gave an answer. It did not fail.** Many
commands tell that an item is absent with an exit code or with output that does
not look like an error. Read that answer, and return `ErrNotFound`. Do not
return the exit status:

| Command              | For an absent item                               |
| -------------------- | ------------------------------------------------ |
| `dpkg-query -W`      | exits 1, and prints `no packages found matching` |
| `systemctl show`     | exits 0, with `LoadState=not-found`              |
| `systemctl start`    | exits 5                                          |
| `userdel`, `usermod` | exit 6                                           |

A raw exit status tells the user only that something failed. On 19 November
2026, `package get` on a host without nginx answered `exit status 1`, and
`systemctl show` made an `inactive` service from a unit that did not exist.

**The sentinel is how the API knows.** The agent names the cause of a failure as
a code (`classifyProviderError`): `not_found`, `not_managed`, `not_installed` or
`unsupported`. The code goes in the stored response, and the job client makes it
`job.ErrNotFound` again. Then a handler answers 404 (`apierr.IsMissing`). An
error that does not wrap a sentinel becomes a 500. Until 19 November 2026 the
stored response did not keep the code, so each missing item answered 500.

## osapi owns the state, so drift gets overwritten

A change to a managed resource outside osapi is drift. The next operation writes
over it. osapi defines how the resource must look, and an edit by hand does not
change that.

To write over drift, the provider must see it. The provider cannot see it in its
own record. The record says what osapi wrote last, and drift makes exactly that
untrue. Thus the provider reads the resource to decide:

- It calculates the hash of the file on disk and compares it with the content to
  deploy.
- It reads the real uid and gid of the file, not the owner that the record
  names.

The provider writes the record, but does not read it to decide. The record is
for status, staleness and audit.

If you do this in the opposite way, it does not look like a bug. It looks like
an operation that succeeds and reports no change, on the one host that needed
the change.

Two results are easy to miss:

- A name that the host does not know fails the operation. It does not pass
  without a signal. The provider finds the requested owner and group on the host
  first. It accepts a numeric id as it is. A container image with no `passwd`
  entry needs that.
- If a platform cannot answer the question, the provider applies the work. It
  does not assume. If it cannot read the ownership, the `chown` runs.

This is the one location where the filesystem abstraction is not sufficient. To
read the uid and gid of a file, you need the stat structure, and the abstraction
does not have it. Thus that read goes to the operating system through a seam
that a test can replace. The abstraction cannot answer the question, and the
resource must answer it.

## Unsupported is not failure, and not no-change

If the OS family of the host does not support an operation, the operation
returns the shared **unsupported outcome**. The agent records it as `skipped`.

That is a third answer. It is different from `ok` with no change, and from
`failed`. A caller can tell these three apart:

- "this does not apply here"
- "this applies and did nothing"
- "this broke"

If you confuse the first two, the fleet report starts to give false data.

`internal/provider/errors.go` declares it. `internal/agent/handler.go` changes
it into the skip.

## The four implementation patterns

A new provider is one of these four. When you know which one you write, you know
what it must do.

**A direct provider runs commands.** `internal/provider/node/power` is the
example. Nothing else is between them. The provider must handle its own
arguments.

**A provider that gives file writes to the file deployer.** It gets change
tracking, idempotency and template rendering from the deployer. `cron`,
`service`, `certificate` and `user` work this way. If a provider writes a file
and does not use the deployer, it must have a reason.

**A provider that manages its own configuration files.** It marks them with a
reserved filename prefix. Thus you can tell a managed file from a file that a
person wrote by hand. `sysctl` is the example. Only the prefix prevents it from
writing over the work of an operator.

**A provider that calls an external API.** It has no platform variants. It
checks availability when osapi makes it, not on the first use. No provider does
this now: `internal/provider/container`, which called the Docker Engine API, was
deleted when the container behaviors replaced it (osapi-io/osapi#994).

## Platform selection happens outside the provider

A provider does not decide if it applies. gohai's `family.Detect` selects by OS
family, and the `InContainer` of gohai's virtualization collector by whether the
process is in a container: docker, podman, lxc, nspawn and the others of Ohai's
cascade, not only `/.dockerenv`. `agent.Setup` in `internal/agent/setup.go`
reads them one time, and the methods of `hostEnv` in
`internal/agent/providers.go` select the provider.

**A read is not selected by family.** gohai reads the host on every Linux family
and on macOS, so an operation that only reads, such as disk usage, memory, load
or the process list, comes from gohai on each of them. Fedora, RHEL and Arch get
the same reads as Debian. The family selects only an operation that changes the
host, such as a package or a service. When gohai does not have a read that an
operation needs, and the read is a fact about the host, it goes into gohai
first: the process list's CPU and memory shares did (osapi-io/osapi#960). The
live state of a service that a domain manages, such as NTP sync or package
updates, stays in that domain's provider, next to its writes, and also runs on
each family (osapi-io/osapi#964).

**A family that a domain does not implement has a stub. It is not missing.**
Thus the selection always finds something, and that thing returns the
unsupported outcome. A missing platform is a compile-time gap, not a runtime
nil.

## Facts

**gohai collects the facts, not the providers.** `writeFacts` in
`internal/agent/facts.go` makes one gohai call with the kernel, hostname, cpu,
init, package_mgr, network and virtualization collectors. It changes the result
into `job.FactsRegistration` and writes it to the facts bucket. A new fact is a
new gohai collector, or a new field of one. It is never a method of a provider
(osapi-io/osapi#962). When gohai does not have a read, the change goes into
gohai first, as the macOS routes did (osapi-io/gohai#301).

A provider gets these host attributes in three steps:

1. It embeds the shared facts holder.
2. It asserts the setter contract at compile time.
3. osapi registers it.

Registration causes the injection. **A provider that osapi makes but never
registers has no facts.** An operation that needs facts then fails when you call
it, not at startup. That is the worse time to learn about it.
`internal/provider/facts.go` has all three parts.

## Three rules about the boundary

Each of these rules was broken somewhere first, and each has an advisory.

### Validation on the request path does not discharge the provider's

The **provider** validates each value that becomes a filesystem path, a filename
or a command argument, before it uses it.

The request path validated the value one time, at that time. Work that runs from
storage is a second caller. It comes later, and the rules can be new since osapi
stored the value. GHSA-7fjw-v3g9-326g was the cost of that error.

### A secret never appears in a command's arguments

Treat arguments as logged and public, because they are. They are in the process
table, and `internal/exec/exec.go` logs them.

A secret goes to a command through stdin, with the variant in `internal/exec`
for that purpose. GHSA-6gc6-px2x-q95j is the advisory.

### A caller's value is never parsed as an option

If a value starts with a dash and gets to a command without a guard, it becomes
a flag. The provider must make sure that this cannot occur.

## What a provider goes through, not around

**Filesystem access goes through the virtual filesystem abstraction.** It never
uses the standard library directly, and never a replacement. Thus you can test a
provider in memory, and with injected failures.

**Commands go through the shared exec manager.** A provider does not start them
directly.

**The deployer does not write a file in place.** A configuration file with only
part of its content is worse than no write. Thus the deployer writes a new file
and moves it.

## How an error reads

The error of a provider gets to a job result, the audit log and the screen of a
CLI user. Thus its words are an interface, not only a debugging aid.

The shape is **`<domain> <verb>: what went wrong`**.

```
sysctl create: key must not be empty
schedule delete: not managed by osapi
file deploy: execute template: no such template
```

With that order, you can sort and grep errors. It reads the same when the error
is alone, and when three callers above it wrap it.

Do not do these two things. The code already has both.

**An error does not say that it failed.** A caller almost always wraps
`failed to execute template`. Thus the reader sees "deploy schedule entry:
failed to execute template: ...". The words "failed to" add nothing to the
context. Name the attempted operation, and let the wrap give the rest.

**An error names the operation, not the command.** `chpasswd failed` shows the
implementation in a message that a CLI user reads. It becomes untrue when the
implementation changes. `user set password` stays true.

The four sentinels are the exception. They stay exactly as they are, because
callers compare them with `errors.Is`. Nobody reads them:

```go
ErrUnsupported  = errors.New("operation not supported on this OS family")
ErrNotFound     = errors.New("not found")
ErrNotManaged   = errors.New("not managed by osapi")
ErrNotInstalled = errors.New("not installed")
```

On each path that has a cause, wrap with `%w`. This is necessary. If an error
loses its cause, a caller cannot match it, and the sentinels exist for that
match.

## What a provider does not touch

A provider does not use the bus, the job store, the audit log or the HTTP layer.
It gets a request and returns a result. How the request arrived is not its
concern.

Thus you can test a provider without other services. You can also read one alone
and understand it.

## What its tests owe

Tests have these obligations. They make the coverage gate possible to pass.

Test each platform variant alone, also the variant that the test machine is not.
A suite on a Mac does not run a Debian implementation. Thus each variant has its
own file.

Test the idempotency rules as results, not as code paths. Create on a resource
that exists asserts no change and no error. Delete on a resource that is not
there asserts the same. Update on a resource that is not there asserts the
error.

Test the unsupported outcome where a platform declares it. If a provider returns
a plain error in its place, a skip becomes a failure in the fleet report.

Test filesystem operations in memory and with injected failures. The abstraction
exists for this.

## Where this connects

[The job system](job-system.md) tells how work gets to a provider, what occurs
when the same job comes two times, and what the four result statuses mean.

[Behaviors](behaviors.md) tells what a contributor writes for a new behavior,
and what osapi generates from its definition.

______________________________________________________________________

Written from `internal/provider/`.
