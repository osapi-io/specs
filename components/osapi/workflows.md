# Workflows

A proposal, not built. A workflow is a named, ordered set of behavior calls
across hosts, written as a file, checked before it runs, and run again with the
same result. This page records the design so it can be read and argued with
before anything is written; it moves into a subject page when it is built, as
[behavior-migration](behavior-migration.md) will.

## Why

A behavior is one typed operation on one host, and running it twice reports
`changed: false` the second time. Real work is several of them in order: set a
kernel parameter, then restart the service that reads it, only on the hosts
where it changed. Today that is either a person typing commands or Go code
against [osapi-orchestrator](../osapi-orchestrator/README.md), which only a Go
developer can write.

swamp shows the shape worth copying. Its behaviors are built once, its workflows
compose them, and a rerun takes the same deterministic path, so the expensive
thinking happens when the workflow is written, not every time it runs. Someone
who does not run swamp should still get that from osapi.

## The idea: a workflow is data, and the binary already knows the vocabulary

The osapi binary has every behavior compiled in: each method's name, input type,
validation rules, permission and docs. `osapi behavior get --json` prints them.
So a workflow does not need to be code. It can be a file that names methods:

```yaml
name: web-tuning
target: role:web
steps:
  - id: forwarding
    run: sysctl.update
    with: { key: net.ipv4.ip_forward, value: "1" }
  - id: restart
    run: service.restart
    with: { name: nginx }
    after: [forwarding]
    when: changed(forwarding)
```

Because the vocabulary is the registry, a workflow can be checked before it
runs, the way `behavior validate` checks a definition:

- every `run` names a registered behavior method
- every `with` decodes into that method's input type and passes its validate
  tags, the same check the API makes before queuing a job
- every `after` names a step, and the steps form no cycle
- every `when` uses the guard vocabulary below
- the caller's token holds each step's permission, checked against the API
  rather than assumed

## Where it runs

| Place                    | Decision                                                                                                                                                                                                         |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The controller           | No, for now. A server-side engine has to store workflow state, resume after a restart, and schedule, which roughly doubles the controller's scope. Revisit for "keep this applied every hour".                   |
| A separate binary        | No. It would carry a second copy of the behavior registry, and an agent would have a second tool to learn.                                                                                                       |
| osapi's CLI, client side | Yes. `osapi workflow new`, `validate` and `run`. Each step is an ordinary job through the existing API, so the controller does not change, and permissions, audit and telemetry apply per step as they do today. |

Client side means the run lasts as long as the process that started it. A
workflow that must survive the operator's laptop closing is the controller case
above, and is out of scope until there is a reason.

## Running and rerunning

The runner sequences steps by `after`, fans each out to its target, and records
each host's result: ok with `changed`, skipped, failed or timed out.

- **Guards ask what happened.** `changed(step)`, `failed(step)`,
  `succeeded(step)`, per host: a step guarded by `changed(forwarding)` runs only
  on the hosts where `forwarding` changed something.
- **Predicates ask what a host is.** `os(debian)`, a label, a fact. These are
  the orchestrator's vocabulary, kept.
- **Retry** is per step, with a count and a backoff.

The first run reports what changed. A second run of the same file reports
`changed: false` everywhere, because every write is idempotent and the fake host
enforces that for every behavior. A `changed: true` on a later run is drift:
something moved the host since. That is the property worth having, and it falls
out of the behaviors rather than being built for workflows.

## For agents

The same three layers behaviors have:

- **The CLI explains itself.** `workflow validate` names the step and the field
  that is wrong; `behavior get` says what each step accepts.
- **A skill**, `build-a-workflow`, holds the procedure and the judgment: when
  the request is a workflow rather than a new behavior, when a step needs a
  guard, how to target.
- **Evals** in a fresh session: "write a workflow that tunes the web hosts",
  scored by `workflow validate` and by a run against fake hosts that must report
  `changed: false` the second time.

A workflow that needs an operation no behavior has is a behavior to build first,
which is the existing skill's job.

## What happens to osapi-orchestrator

Its ordering, guards, retries and per-host results become the runner's logic,
moved into osapi. Two ways to go after that, still open:

- **A thin Go wrapper.** It stays for programs that embed workflows in Go, with
  its steps built from the behavior definitions instead of 101 hand-written
  ones, so a new behavior is a step with no code.
- **Retired**, once the CLI runs workflow files, if nobody needs the Go surface.

Renaming it, to `osapi-workflows` or similar, waits for that choice: if the
runner moves into osapi, the repository either becomes the wrapper or goes.

## Open questions

- Whether a step can pass one step's output into another's input, and how much
  expression language that needs before it becomes a programming language.
- Whether `run` gets a plan mode, reporting what would change without changing
  it. That needs each write to answer "would this change?", which behaviors do
  not yet declare.
- Where run history lives, if anywhere: a run's results are jobs already, so a
  history may be a query over the job store rather than a new store.
- Whether workflow files live in a directory the CLI discovers, and whether they
  carry their own docs pages the way behaviors do.

## Order of work

After the sysctl cutover, since a workflow's steps name `/api` routes:

1. `osapi workflow validate`: the file format, checked against the registry.
2. `osapi workflow run`: sequencing, guards, retry and per-host results, the
   orchestrator's logic moved in.
3. The `build-a-workflow` skill and its evals.
4. The decision on osapi-orchestrator.
