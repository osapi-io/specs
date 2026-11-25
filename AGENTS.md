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
URL that `.lab/config/cli.yaml` of osapi-lab names. For each flow that the
change touches, add its methods as steps on the Plans page, run them, and look
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

## Make a change

**Work in a worktree from a new `origin/main`.** Rebase it onto `origin/main`
again just before you open the pull request, and again before the merge. When
the owner wants to see each edit as you make it, for example in the Docusaurus
dev server, work on a branch in the main checkout. Never leave changes behind in
a checkout after the work merged or moved.

**Put changes that edit the same files in sequence.** Changes that edit the same
registration lists or generated files cannot all stay mergeable at the same
time. Each merge makes the others conflict. Open one, merge it, then start the
next. Give parallel agents only work in different files. On 22 and 23 November
2026, 13 parallel migration pull requests each needed a rebase and a new
generation, many of them two times.

**Decide a choice that a rule of the project answers.** Make it, and write it in
the description of the pull request. Ask the owner only about a choice that no
rule answers, or that changes the design. Give a recommendation with the
question.

**Do not keep backward compatibility.** Nobody but the owner uses osapi, its
SDK, its CLI or its API. When a change makes something old or inconsistent,
change it or delete it everywhere, in the same change. Do not add a deprecated
flag, a field for old callers, or a note about compatibility.

**Read a host through gohai.** osapi reads and detects facts through gohai. When
gohai does not have a read that osapi needs, or its API does not fit, change
gohai first. Merge and release gohai, then use it in osapi. Do not copy the read
into osapi.

**Generate test doubles.** A double of an interface of the organization is a
`mockgen` mock in a `mocks` package. Do not write a fake by hand. The exceptions
are in the Test doubles section of each CONTRIBUTING.md.

**Remove a plan when its work is built.** A plan page, such as a migration plan,
is temporary. Move each part that you build into the page of its subject, and
delete the plan when the work is complete.

**Change a shared convention in each repository at the same time.** The Go
repositories of osapi-io have the same sections of CONTRIBUTING.md, in the same
order. The `.github/` directory of each repository has the same configuration
files. Change a convention in each repository and in `templates/CONTRIBUTING.md`
together. Do not add a configuration file in a different location: a root
`codecov.yml` replaces `.github/codecov.yml`, and nothing fails.

## Check a change

Run only the checks that can find a problem in your change. CI runs the full
suite on the pull request. The full suite of osapi takes approximately ten
minutes. Do not run it, and do not run a test of a full directory tree. In this
repository, `just test` is fast, and it is the gate.

Do not run checks while you edit. Run them one time, before the commit:

- `go test -cover` on each package that you changed.
- The format checks on the files that the branch changes against `origin/main`:
  `gofumpt -l` and the `golines` dry run on Go files, and `md-fmt-check`,
  `docs-fmt-check` and `react-fmt-check` for the other files. Run
  `go tool golangci-lint run` on the changed packages. CI found unformatted
  files that an edit script changed on osapi #710, #718, #721 and #887.
- When you move or delete a route or a command in osapi, record the
  `internal/apicontract` golden file again. Then search `docs/docs/sidebar`,
  `test/integration` and `ui/` for the old path, the old API page and the old
  command words. Run `go test ./cmd/` too.
- When you add or change a gohai collector field, run `go generate ./...`, which
  writes `schemas/gohai.schema.json`, and `just md-fmt`.

## Open a pull request

Open the pull request when the change is complete and its checks pass. Do not
ask first.

- Open it ready, never as a draft. When something is not tested, say so in the
  description.
- A change to a component has a specs pull request. Open the specs pull request
  first. Put `Specs: <url>` in the description of the component pull request
  when you create it, and link back from the specs pull request.
- Put `Closes #<n>` in the description for each issue that it completes.
- Before you push to a branch again, make sure that its pull request did not
  merge. A squash merge orphans a commit that you push after it.
- Do not wait on CI after you open a pull request. Start the next work.

When the owner asks to close out the work, merge each pull request when its
checks pass: the specs pull request first, then the component pull request.
Rebase a pull request that conflicts, generate again, and push. After you push a
fix, watch the new run. Do not leave a green pull request unmerged.

## Close an issue

Close an issue only when each item that it waits on is closed: its sub-issues,
and the issues that it names as a part or as a block. Tick its task boxes when
it closes. Each item of a tracker that is not complete has its own issue, as a
sub-issue of the tracker.

An issue about current behavior does not wait on a design that nobody decided.
Move each such part to a `decision` issue in the repository where it would be
built, write a comment on the original issue, and close the original on the
current work.

A security finding that somebody can exploit, in a public repository, is a
private draft security advisory, not an issue. An issue is public when it opens.

## Report to the owner

- Give the full URL of each issue, pull request, commit and run. Do not use link
  text, and do not give a number without its URL.
- After you open or change pull requests, list each one that is still open from
  the work, one URL on each line, with what it does and what it waits on. List
  only the pull requests that you opened.

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
