# How the osapi-io repositories fit together

**The product makes a Linux host operate like an appliance.** You install one
binary and give it a config file. You then get a REST API and a CLI that read
and change the system configuration: hostname, DNS, disk, memory, load,
packages, services and users.

You configure an appliance through an interface. You do not log in and edit
files. The design comes from the need to do this on a fleet, not on one machine:

- osapi queues the work, so that the API does not wait for twenty machines.
- The results come back for each host.
- An agent must prove its identity before a job can target it.

There is one product. An operator runs osapi. Each other repository supports
osapi or controls it.

The `specs` repository has this documentation and is not a component. It is
important in one location below, because it uses `osapi-justfiles` like the
other repositories. Thus a change to the justfiles has an effect on eight
repositories, not seven.

```
      nats-client ─┐
      nats-server ─┼─→ osapi ──→ osapi-orchestrator
      gohai ───────┘           (osapi's read layer: moving to it)

      osapi-lab                (runs a checkout of osapi on real hosts)

      osapi-justfiles          (build, all eight, by fetch)
```

| Repository                                                    | Is                                     | Read it to learn                               |
| ------------------------------------------------------------- | -------------------------------------- | ---------------------------------------------- |
| [osapi](components/osapi/README.md)                           | The API and the agent                  | how a request becomes work on a host           |
| [osapi-orchestrator](components/osapi-orchestrator/README.md) | A declarative layer over osapi's SDK   | how to describe ordered work across hosts      |
| [nats-client](components/nats-client/README.md)               | A wrapper over the NATS client         | what the transport of osapi gives it           |
| [nats-server](components/nats-server/README.md)               | A NATS server embedded in its consumer | how osapi runs its own bus                     |
| [gohai](components/gohai/README.md)                           | A system fact collection library       | how gohai collects facts, if you need them     |
| [osapi-justfiles](components/osapi-justfiles/README.md)       | Shared `just` recipes                  | why `just test` is the same in each repository |
| [osapi-lab](components/osapi-lab/README.md)                   | A fleet of real machines running osapi | how to try a branch on hosts before a release  |

## Where to start

**Start with osapi.** Each of the other six repositories gives data to it, uses
it or runs it. Thus its document makes the others clear. Read the
[job system](components/osapi/job-system.md) of osapi next, because the full
product uses the queue.

## What crosses a boundary

### The transport

osapi embeds a NATS server through `nats-server` and connects to it through
`nats-client`. **Neither of these repositories knows about the other**, and
neither knows about osapi. They wrap the two ends of the same upstream library.
osapi is the only thing that uses the two.

Two facts about that pair are important, and neither wrapper states them alone:

- `nats-client` adds no reconnection policy. The default of the upstream library
  handles a dropped connection, and osapi gets no notification.
- `nats-server` always turns on debug and trace logging. It attaches its logger
  after the server starts. Thus the startup log of the bus does not go to the
  log of osapi.

[The message bus](components/osapi/transport.md) has the two facts. A person who
debugs the transport looks there.

**osapi calls NATS only through the methods of `nats-client`.** It keeps no
JetStream handle, and it does not call `nats.go` or `jetstream` itself. Each
method takes `ctx` first and the name of the bucket or the stream. Thus each
call to NATS is in the traces and the metrics of osapi, because `nats-client`
makes the span and the metric in one place.

When osapi needs a call that `nats-client` does not have, add the method to
`nats-client`, with its span and its metric. Do not add a direct call in osapi.
A direct call is not in a trace, and nothing tells the person who reads the
trace that a call is not there.

`nats-client` returns concrete types and declares no interface for its own
methods. Each osapi package declares the interface of the methods that it uses,
and makes its mocks from that interface. A bucket goes into a package as its
name, not as a handle.

### The SDK surface

`pkg/sdk/client` is the contract between osapi and its orchestrator. After a
justfile change, a change to it has the widest effect of all code changes in the
organization.

The orchestrator pins a **released tag of osapi**. Thus a break comes later, but
it comes. A rename passes in osapi. It then fails in the orchestrator when
somebody updates the pin. The rule is: **merge a rename and its version update
together**. This is the only coordination rule in this organization that applies
to more than one repository.

The connection goes further than the layer for it. The `internal/engine` of the
orchestrator imports the SDK of osapi directly. Thus `internal` there controls
visibility, but it does not make the engine independent. The engine declares no
interface that can isolate it.

### The build

Each repository gets `osapi-justfiles` through a justfile recipe, at the commit
that `main` is at when the recipe runs. The recipe writes that commit to
`.just/remote/VERSION`, and prints it. No repository asks for a different
commit, so a merge gets to each repository at its next `fetch`. Each repository
ignores `.just/` in git.

`md` goes to all eight consumers, `just` to seven, `go` to five, and `react`,
`docusaurus` and `ansible` to one each. Thus **a change to `md.just` has the
widest effect in the organization.** The specs repository uses it. Its
`just test` checks each change to these documents.

### Continuous integration of the Go repositories

The five Go repositories are gohai, nats-client, nats-server, osapi and
osapi-orchestrator. Each has `.github/workflows/go.yml`, and each workflow runs
the checks that `just test` runs on a laptop. Thus a check that passes on a
laptop passes in CI.

Each workflow keeps the cache of golangci-lint between runs. An `actions/cache`
step restores `~/.cache/golangci-lint` before the lint:

```yaml
key: golangci-${{ hashFiles('go.sum', '.golangci.yml') }}-${{ github.sha }}
restore-keys: golangci-${{ hashFiles('go.sum', '.golangci.yml') }}-
```

A run restores the newest cache with the same `go.sum` and `.golangci.yml`, and
saves its own cache at the end. Thus golangci-lint examines only the packages
that changed. On osapi, a run with no cache takes 60 to 110 seconds, and a run
with the cache takes about 2 seconds. A change to `go.sum` or `.golangci.yml`
starts with no cache. A pull request reads the caches of `main` and of its own
branch, not those of a different pull request.

Each workflow has the same four jobs, and the shared `go` module of
osapi-justfiles has their recipes:

- A plan job runs `just go-ci-checks` and `just go-unit-plan`. Their output is
  the matrix of the other jobs.
- Check jobs. `go-test` runs the checks of two lists, `go_quick_checks` and
  `go_slow_checks`, and `go-ci-checks` prints the same lists. The quick checks
  share one job, and each slow check is a job. A repository adds its own checks
  to the lists. Thus a check that is added to a list runs on a laptop and in CI.
- Unit jobs. `go-unit-plan` weighs each package by its lines of test code, and
  gives each package to the lightest shard, the heaviest package first. It makes
  one shard for each `go_shard_weight` lines, 20,000 by default, up to ten.
  osapi sets 13,000: its test code fell to about 133,000 lines as behaviors
  moved to generated tests, and 20,000 gave seven shards. Each shard is a job,
  and `go-unit-shard` runs it with the race detector. Thus a new package goes
  into a shard with no change to the workflow.
- A coverage job. `go-cover-merge` joins the profiles of the shards, and fails
  below the target. Each shard also checks its own profile against the target
  (`go-unit-shard`). With a target of 100 that gives the same answer, because
  the total is 100% only when each package is. gohai has no coverage job: each
  shard sends its own profile to Codecov, which joins them
  ([gohai#288](https://github.com/osapi-io/gohai/pull/288)). The other four
  repositories still have the coverage job.

`.github/actions/setup` in each repository has its own setup. In osapi it also
installs Node.js and Bun (input `js`), because some checks run Prettier through
Bun. CI does not bundle the UI. Only the job of the UI checks installs its
packages (input `ui`), and `go_quick_checks` lints and type-checks it with
`react-lint` and `react-typecheck` (`tsc -b`, no emit). Each job puts a
placeholder in `ui/dist`: the embed needs a file there, and no Go test reads the
built UI. The unit shards also skip Node.js and Bun. A release bundles the UI in
the `before` hook of goreleaser. The bundle took most of the 87 seconds of setup
in each shard (osapi-io/osapi#1353).

The five repositories have the same jobs so that they stay the same, not for
speed. Each job starts a runner, checks out the code and restores the caches
before it does work, about 30 to 45 seconds. A repository with a run of 1 or 2
minutes gets almost nothing from parallel jobs, and a repository with two
packages gets one shard. GitHub runs about 20 jobs at a time for a public
repository. A workflow with more jobs than that waits for a runner. Thus a quick
check goes in `go_quick_checks`, so that the shards have runners.

The smallest part of a shard is one package. Thus the package with the most
tests, or the slowest tests, sets the minimum time of the slowest shard. In
osapi that is `internal/dslcheck`, about 53 seconds, because it type-checks each
package. The planner weighs by lines, so it does not see this.

## Facts that span repositories

There are four. Each is true of a pair, or of the full set. Thus the page of one
repository is not the correct location.

**The dependency graph has one center and one end.** osapi is the only
repository with connections in the two directions. osapi-orchestrator has an
incoming Go connection and no outgoing connection. gohai will have one outgoing
connection, to osapi, as the next paragraph tells.

**The effect of a change does not follow the size of the repository.**
`osapi-justfiles` has no Go code, and it goes to eight repositories.
`nats-server` has twelve Go files, and it forces a logging decision on the
largest repository.

**Two repositories wrap the two ends of the same upstream library.** The facts
about reconnection and logging that a consumer needs are in the two. osapi is
the only consumer of either repository. It now has the two facts in one
location: [the message bus](components/osapi/transport.md).

Before, only this page had those facts. That was a correct finding in the
incorrect repository. A new contributor needed them and did not find them where
a contributor looks.

**gohai is the read layer of osapi.** gohai was written for osapi. What osapi
detects or reads on a host comes from gohai: the platform and its family first,
then memory, CPU, load, disk and the facts. osapi does not keep a copy of a
gohai table, and does not call `gopsutil` itself. When osapi needs a read that
gohai does not have, or an API of gohai does not fit, the change goes into gohai
first, and osapi then uses it.

gohai exports the family of a host (`pkg/gohai/family`), as Ohai names it, and
osapi's agent and behaviors use it: osapi no longer detects the family itself.
The collectors of gohai take their sources (a filesystem, a command runner, a
clock and the family) from the caller, and gohai does not use `gopsutil`
(osapi-io/gohai#292). Thus a behavior of osapi can call a collector with the
sources of `host.Host`, and its example runs on the fake host. osapi does not
use `gopsutil`: its facts, its host, disk, memory, load and process reads, and
the process metrics of its heartbeats come from gohai, on each Linux family and
on macOS (osapi-io/osapi#960). The node-read behaviors call gohai's collectors
with `host.Host.Sources()`: the host's filesystem, its commands through
`RunCmd`, its clock, its platform as the family, and its resolver. The adapter
is in osapi, and gohai knows nothing of osapi (osapi-io/osapi#965).

## What is not here

How one repository works. Each repository has its own document, with a link
above.

`specs` and `.github`. They are the repositories of the organization, not
components. `specs` describes the components. `.github` has shared configuration
and has no justfile.

______________________________________________________________________

Written from the `go.mod` and justfile of each repository.
