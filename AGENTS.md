# AGENTS.md

Test: `just test` | Format: `just md-fmt`

Read [CONTRIBUTING.md](CONTRIBUTING.md) first. Then read
[CONSTITUTION.md](CONSTITUTION.md). This file has only the rules that are
specific to agents. They apply to each coding agent.

## Run tools

Run tools through `mise`, not from your path:

```bash
mise exec -- just test
```

`mise` is active in the shell of a person. It supplies the versions that
`.mise.toml` declares. The shell of an agent does not activate `mise`. Thus a
bare `just` runs the version that is installed globally. That version is usually
older.

The symptom is a check that fails here but passes in CI, on a file that nobody
changed. If this occurs, find the version that ran. Do this before you accept
the failure as real.

## Use the lab

[The lab](components/osapi-lab/README.md) runs osapi on a Mac hub and on Linux
and macOS VMs. An agent can deploy the lab with no person present. The hub and
the VMs have passwordless sudo, so no recipe asks for a password.

Deploy the lab when a change needs a real host: to run the integration tests, or
to see that a read or a write operates on Linux and on macOS.

- `just lab-session <name> "<commands>"` in osapi-lab holds the lab for your
  deploy and your tests, and gives it back at the end, also when a step fails.
  Use the issue as the name, such as `osapi-1139`. Other agents wait for it.
- `just deploy` in osapi-lab copies your osapi build to the hub and the running
  VMs. Run it in your session, with `LAB_SESSION` set.
- `just ssh <vm>` opens a shell on a VM. Remove each file that you copy to a VM
  when you finish.
- `just go-unit-int` in osapi runs the integration tests against the lab when
  `OSAPI_INTEGRATION_OSAPIFILE` and `OSAPI_INTEGRATION_TARGET` point at it.

A test in the lab includes the UI. The controller of the hub serves it, at the
URL that `.lab/config/client.yaml` of osapi-lab names. For each flow that the
change touches, open its block on the Configure page, run each method, and look
at the result: the fields that it asks for, the rows that it shows, and a
refusal. Then report the UI results with the CLI and integration results. A
passing type check of the UI is not a test of it. On 21 November 2026 a route
change went to review with the UI only type-checked, and a person had to ask for
the click-through. The UI is not on a local host. Thus an agent does not type a
token into it: a person signs in, then the agent continues. Remove the blocks
that you add, and anything that the flows wrote on a VM, when you finish.

Ask a person before `just teardown`, and before a change to the security
settings of the lab, such as its firewall or its sudo rules.

## Read the documents before you change them

Read the page of the component under `components/`, and the subjects that it
links. That page is the current description of how the component operates. It is
more current than other prose about the component.

Read [ARCHITECTURE.md](ARCHITECTURE.md) when the work has an effect on how the
repositories fit together. The page of a component describes only its own
operation. Thus it does not have an agreement between components. If the page
does not have an agreement, that is not evidence that the agreement does not
exist.

Nothing here permits work that the constitution forbids. If you cannot obey a
request and the constitution together, say so. Do not select one and say
nothing.

## What you find during the work

Record an inconsistency. Do not make the change larger, and do not ignore the
inconsistency. Open an issue on the repository where the fix goes, with the
command that found it, and label it `side-finding`, its type and its component.
Then continue your work. [Issues](CONTRIBUTING.md#issues) has the rule, and
[Labels](CONTRIBUTING.md#labels) has the labels. Agents most often make the
change larger.

A page that does not agree with the code is the same situation. Say so. Fix the
page in its own change. Do not write around the error.

Work that you agree to do later is also an issue, in the repository where the
change goes. Open it when you agree to the work, with its labels. Work that
waits on a different issue is `blocked`, with a blocked-by link to that issue.
Your task list, your memory and the text of the session are not records. They
stop when the session stops, and nobody else can read them. Use a task list only
for the steps of the change that you do now.
[Tracking](CONSTITUTION.md#tracking) has the rule.

## Write a page

**Run `unslop` on all text that you write.** It applies to prose here as
`mdformat` applies to the format. The sign that it finds most often is the em
dash.

**Use `/document`. Do not write a page by hand.** It has the voice, puts the
subject in the correct location and runs `unslop`.

**Write sentences in Simplified Technical English.** The constitution requires
STE for the pages of each repository, not only these pages. `/ste-100` writes
and checks them. Use it here, and when you change the docs of a different
repository from this one. The voice decides what a page says. STE decides how
each sentence says it.

**Put content in the page of its subject.** The README of a component is an
index. It tells what the repository is, and has a table of links to its
subjects. Text about how osapi queues work goes in the page about the queue.
Merge it with the text that is there. Do not add it at the end.

## Commit trailer

When an agent writes a commit, end the commit message with a trailer that names
the agent. Use the trailer that the documentation of the agent gives.

The skills are in `.claude/skills`. `.agents/skills` is a link to that
directory. Thus each coding agent uses the same skills.
