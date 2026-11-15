# Workflows

This is a proposal. Nobody built it yet. A workflow is a named, ordered set of
behavior calls across hosts. You write it as a file. osapi checks it before it
runs, and a second run gives the same result. This page records the design, so
that people can read it and argue with it before anybody writes code. When the
feature is built, the content moves into a subject page, as
[behavior-migration](behavior-migration.md) will.

## Why

A behavior is one typed operation on one host. A second run reports
`changed: false`. Real work is a sequence of behaviors, for example:

1. Set a kernel parameter.
2. Restart the service that reads it, but only on the hosts where it changed.

Now, a person types the commands, or a Go developer writes code against
[osapi-orchestrator](../osapi-orchestrator/README.md). Only a Go developer can
write that code.

swamp shows a good shape. You build its behaviors one time, and its workflows
put them together. A second run takes the same path. Thus the difficult thinking
occurs when you write the workflow, not each time that it runs. A person who
does not use swamp must also get this from osapi.

## The idea: a workflow is data, and the binary already knows the vocabulary

The osapi binary has all of the behaviors in it: the name, the input type, the
validation rules, the permission and the docs of each method.
`osapi behavior get --json` prints them. Thus a workflow does not need to be
code. It can be a file that names methods:

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

The registry is the vocabulary. Thus osapi can check a workflow before it runs,
as `behavior validate` checks a definition:

- Each `run` names a registered behavior method.
- Each `with` decodes into the input type of that method, and passes its
  validate tags. The API makes the same check before it queues a job.
- Each `after` names a step, and the steps make no cycle.
- Each `when` uses the guard vocabulary below.
- The token of the caller has the permission of each step. The API checks this.
  The runner does not assume it.

## Where it runs

| Place                    | Decision                                                                                                                                                                                                                         |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The controller           | No, for now. A server-side engine must store workflow state, continue after a restart, and schedule. That makes the scope of the controller approximately two times larger. Examine it again for "keep this applied every hour". |
| A separate binary        | No. It needs a second copy of the behavior registry, and an agent has a second tool to learn.                                                                                                                                    |
| osapi's CLI, client side | Yes. `osapi workflow new`, `validate` and `run`. Each step is an ordinary job through the current API. Thus the controller does not change, and permissions, audit and telemetry apply to each step as now.                      |

On the client side, the run continues only while the process that started it
runs. A workflow that must continue after the operator closes a laptop is the
controller case above. It is out of scope until there is a reason.

## Running and rerunning

The runner puts the steps in order by `after`. It sends each step to its target,
and records the result of each host: ok with `changed`, skipped, failed or timed
out.

- **Guards ask what occurred.** `changed(step)`, `failed(step)` and
  `succeeded(step)` apply to each host. A step with the guard
  `changed(forwarding)` runs only on the hosts where `forwarding` changed
  something.
- **Predicates ask what a host is.** `os(debian)`, a label or a fact. These come
  from the vocabulary of the orchestrator, and they stay.
- **Retry** applies to each step, with a count and a backoff.

The first run reports what changed. A second run of the same file reports
`changed: false` on each host. Each write is idempotent, and the fake host
enforces that for each behavior. A `changed: true` on a later run is drift:
something changed the host after the last run. This property is valuable. It
comes from the behaviors. Nobody builds it for workflows.

## For agents

Workflows get the same three layers as behaviors:

- **The CLI explains itself.** `workflow validate` names the step and the field
  that is incorrect. `behavior get` tells what each step accepts.
- **A skill**, `build-a-workflow`, has the procedure and the decisions. It tells
  when the request is a workflow and not a new behavior, when a step needs a
  guard, and how to select targets.
- **Evals** in a new session: "write a workflow that tunes the web hosts".
  `workflow validate` scores the result, and so does a run against fake hosts.
  The second run must report `changed: false`.

If a workflow needs an operation that no behavior has, build that behavior
first. The current skill does that.

## What happens to osapi-orchestrator

Its order, guards, retries and results for each host become the logic of the
runner, and move into osapi. After that, there are two possible directions. The
decision is still open:

- **A thin Go wrapper.** It stays for programs that put workflows in Go. Its
  steps come from the behavior definitions, not from 101 hand-written steps.
  Thus a new behavior is a step with no code.
- **Retired.** When the CLI runs workflow files, and if nobody needs the Go API.

A new name, for example `osapi-workflows`, waits for that decision. If the
runner moves into osapi, the repository becomes the wrapper or goes away.

## Open questions

- Can a step give its output to the input of a different step? How much
  expression language does that need before it becomes a programming language?
- Does `run` get a plan mode, which reports what will change and does not change
  it? Each write must then answer "will this change?", and behaviors do not
  declare that yet.
- Where does run history go, if anywhere? The results of a run are already jobs.
  Thus a history can be a query on the job store, not a new store.
- Do workflow files go in a directory that the CLI finds? Do they have their own
  docs pages, as behaviors do?

## Order of work

This work starts after the sysctl cutover, because the steps of a workflow name
`/api` routes:

1. `osapi workflow validate`: the file format, checked against the registry.
2. `osapi workflow run`: order, guards, retry and results for each host. This is
   the logic of the orchestrator, moved in.
3. The `build-a-workflow` skill and its evals.
4. The decision about osapi-orchestrator.
