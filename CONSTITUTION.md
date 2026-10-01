# Constitution

The rules binding every repository in this organization. One file, because there
are seven repositories and a rule stated seven times is seven things to keep in
agreement.

Each rule below is here because the organization got it wrong first. A rule
invented to fill out a document is noise, so the evidence is named where there
is any.

## Documentation

A repository states in full the conventions binding it. A reference to guidance
held elsewhere does not stand in place of stating them: a reviewer reading a
pull request in a browser, a contributor working offline, and an agent with a
single checkout each see only that repository.

Where a convention binds several repositories, each states it in the same words,
so a difference in wording means a difference in rule.

A rule a tool already enforces is never restated as prose. The configuration is
the statement of record; documentation names where it lives. Prose describing a
tool's settings is maintained by hand and checked by nothing, so it drifts while
continuing to read as authoritative.

## Verification

A claim about the codebase is measured, not inspected. Reading code and
concluding is a hypothesis; running something that would fail if the claim were
false is a result.

Completion is reported with the output that demonstrates it. "Tests pass" is a
claim; the command and its output are evidence.

Where a check can be automated it is automated. A rule enforced only by review
is a rule that holds until someone is busy.

## Tooling

A tool a repository invokes is declared where the repository declares its tools.
A tool resolved from whatever the developer happens to have installed is not the
same tool across machines, and is not what continuous integration runs.

Both provisioning paths resolve to the same version. Where nothing maintains a
version automatically, both track the latest release so they move together;
where something does, both pin it and that mechanism moves both. A version
pinned in one path and floating in the other guarantees divergence.

A tool whose output is committed is pinned, so the committed artifact does not
change under whoever runs the generator.

## The language version

A tool version and a language version are different promises. The tool version
is what this repository builds with. The language version in `go.mod` is a
floor: the oldest release a consumer may build with, and the only one of the two
that binds somebody else.

A repository supports the two most recent Go minor releases, so the directive
names the older of them. Naming the newest drops support for the one before it,
which is the opposite of the rule. Tool provisioning still tracks the latest
release, because building with a newer toolchain than the floor is always
allowed and surfaces new vet findings early.

The floor is built in continuous integration, not only declared. A repository
testing one version while promising two has not tested the promise, and the day
a newer standard library call compiles locally is the day the floor breaks for
every consumer with nothing reporting it. The job building the floor reads the
version from `go.mod` rather than repeating it, so moving the directive moves
the build with it.

Which release is current is not recorded here. It is what the toolchain list
returns, for the same reason the repository list is not recorded either.

## Correction

When applying a rule shows the rule is wrong, work stops and the rule is
corrected first, in its own change. Correcting the rule and the code together
produces a rule written to describe what was already done, and buries the
correction where nobody reviews it as a change of rule.

Write a requirement from evidence the repository already carries: its
configuration, its history, a failure it has had. A standard invented to fill a
template creates noise rather than a constraint, and is non-conformant from the
day it is written.

## Repositories

The repositories in this organization are what
`gh repo list osapi-io --no-archived --visibility public` returns. No document
holds a copy of that list.

A written list is correct when written and wrong after the next repository is
added, and nothing marks the moment it turns. Work spanning repositories takes
the set from the command each time, and narrows it at the point of use rather
than by keeping a second list.

What a command can produce is not recorded. A record of it is a cache that
nothing refreshes and nothing checks, and it reads as current for exactly as
long as nobody measures.

## Tracking

An issue records that something should change. The page records what changing it
means. These are stages of one piece of work rather than two records of it, and
an issue is closed by the pull request that makes its page true.

An issue exists so an intent survives being put down. Work under way is tracked
wherever it is being done, and copying that into issues produces a second list
that drifts from the first and is read by whoever finds it first.

Open one when the work is larger than the change in hand, and fix it directly
when it is not. An inconsistency found while doing something else is the case
this rule is for: widening the change buries the fix in a diff about something
unrelated, and saying nothing loses it. Neither is tracking.

An issue carries the evidence that found it, with the command that reproduces
it, for the same reason a page does.

An issue is opened in the repository the change lands in, never in the design
record, because that is where the reader of the code looks. Work spanning the
organization therefore reads issues alongside pull requests and alerts, and an
intent nobody wrote down as one is work nobody can find.

Something exploitable is never an issue. An issue is public the moment it is
opened, so it is reported as a draft advisory on the repository it affects.

## The documents

A repository's page states what the repository is before it states anything that
was decided about it: what it is, where it sits among the others, how it is
built, what a consumer may depend on, what was measured and the command that
measures it again, where its own prose and its code disagree, and what it leaves
out.

Documentation that grows only by appending records a sequence of changes. It
answers what was decided and never what the thing is, so a reader arriving at it
learns how one mechanism works before learning what the repository is for. That
is the state osapi's was in after five changes: 1,840 lines, no statement of
purpose, no dependency, no architecture.

A count is written with the command that produces it. A number alone is a claim
that was true when somebody typed it, and nothing marks the moment it stops
being true.

A page explains a system to somebody who has to work on it. It is not a
specification: no requirement identifiers, no "MUST", no user stories, no
acceptance scenarios. A page is read repeatedly by somebody learning the system,
and the formalism that serves a reviewer once obstructs that reader every time.

A heading names the thing, with its path where a path helps. A statement is made
in the present tense and stated once. A design decision carries its reason, in a
sentence, the first time it appears: why the liveness probe checks nothing
belongs beside the liveness probe. What never appears is commentary about the
document: how a fact was found, that a fact is important, or what an earlier
version said.

Show the thing where showing it is shorter than describing it. A configuration
block, a directory tree, a response shape and a command are documentation; a
paragraph about the shape of a configuration block is not.

The documentation is a tree. A component's `README.md` says what the repository
is and links to its subjects. A subject with enough in it to explain gets its
own page beside it, and a repository small enough to explain in one page keeps
one.

A change lands in the subject it belongs to. Something about how work is queued
goes in the page about queuing work, merged with what is already there, and the
README gains a link at most. Appending everything to one page produces a file
that answers everything and explains nothing, which is what one repository's
documentation became after seven changes: five subjects in 266 lines, saying
something about each and enough about none.

The merging is the work. Two statements about the same mechanism become one, and
the one that survives carries what both said. A page that grew by appending is a
record of how it was written rather than a description of what is true.

A page is written in a human voice and checked for the tells that mark machine
prose: em dashes, bold labels that restate the line after them, title case
headings, "serves as" where "is" would do, rule-of-three lists that were not
three things to begin with.

## What the repositories agree on

These bind more than one repository, so they live here rather than in whichever
one noticed first.

### The repository list is a command, not a document

The repositories in this organization are what this returns:

```sh
gh repo list osapi-io --no-archived --visibility public
```

**No document holds a copy of that list.** A written list is correct when
written and wrong after the next repository is added, and nothing marks the
moment it turns. So work spanning repositories takes the set from the command
each time and narrows it at the point of use.

`--no-archived` matters. Archived repositories hold Dependabot pull requests
that can never merge, and a search across the organization counts them.

This rule started as a deletion. A hand-maintained list of the repositories held
a hand-maintained dependency graph, and the graph was already derivable from
`go.mod` files and justfiles. It went, and the rule that replaced it is
`global/repositories` in every constitution.

**It has been broken since, which is the useful part.** `osapi-justfiles`' own
baseline listed six consumers. The command returns seven, because `specs`
fetches justfile modules too, and the list was written from the six *components*
rather than from what the command returns. **It was wrong when written, not
stale.** Ageing was never the failure mode; the writer's frame was.

### A count carries the command that produces it

A number alone is a claim that was true when somebody typed it, and nothing
marks the moment it stops being true.

A count is written with the command that produces it, so a reader can run the
repository it describes. Getting there fixed seven counts nobody could have
checked: six written as "the same, plus `-not -name '*_test.go'`", which is a
shortcut for whoever wrote the table and cannot be run by anything.

Each command has to stand alone for that reason.

### A rule a document states is reachable from the repository it binds

Where these docs state a rule somebody must follow, the repository they are
working in states it too, in one line. The reasoning lives here and stays here;
what this asks is that the rule be reachable from one checkout.

Measured at `osapi` on 2026-09-30: ten rules a contributor must follow, two of
them stated in `osapi`'s own documentation and eight not. Two of the eight carry
security advisories, so the rules this organization learned the hardest were
among those a checkout could not show you.

```sh
cd ~/git/osapi-io/osapi
grep -ilE 'consistent across all layers' CONTRIBUTING.md   # stated
grep -ilE 'upsert' CONTRIBUTING.md                          # was not
```
