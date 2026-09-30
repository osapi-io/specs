# nats server Constitution

<!-- [F] global/documentation SECTION -->

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

<!-- [F] global/verification SECTION -->

## Verification

A claim about the codebase is measured, not inspected. Reading code and
concluding is a hypothesis; running something that would fail if the claim were
false is a result.

Completion is reported with the output that demonstrates it. "Tests pass" is a
claim; the command and its output are evidence.

Where a check can be automated it is automated. A rule enforced only by review
is a rule that holds until someone is busy.

<!-- [F] global/tooling SECTION -->

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

### The language version

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

<!-- [F] global/correction SECTION -->

## Correction

When applying a rule shows the rule is wrong, work stops and the rule is
corrected first, in its own change. Correcting the rule and the code together
produces a rule written to describe what was already done, and buries the
correction where nobody reviews it as a change of rule.

Write a requirement from evidence the repository already carries: its
configuration, its history, a failure it has had. A standard invented to fill a
template creates noise rather than a constraint, and is non-conformant from the
day it is written.

<!-- [F] global/workflow SECTION -->

## Workflow

One workflow governs specification, planning, and implementation, and it is Spec
Kit: `speckit-specify` and `speckit-clarify` settle what a change must do,
`speckit-plan` and `speckit-tasks` settle how, `speckit-implement` carries it
out, and `speckit-archive-run` consolidates the result. A second workflow over
that same ground gives two answers to which artifact is authoritative, and the
answer that loses is the one nobody reads.

Design output is written where the workflow that reads it looks: a feature under
the project's `specs/`, consolidated into `.specify/memory/` when it merges. A
planning artifact written anywhere else is not durable knowledge, whatever it
contains, because nothing reaches it again.

The superpowers plugin is not used, and nothing it produces is committed. Its
planning skills cover ground Spec Kit already owns, and its `docs/superpowers/`
tree is a second planning record that drifts from the first.

<!-- [F] global/repositories SECTION -->

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

<!-- [F] global/tracking SECTION -->

## Tracking

An issue records that something should change. A specification records what
changing it means, and a task list records the order it is built in. These are
stages of one piece of work, not three records of it: an issue is closed by the
pull request that implements the specification it became, and a task is never
mirrored into an issue, which is why `speckit-taskstoissues` is not used.

An issue exists so an intent survives being put down. Work under way is tracked
by its task list, which is authoritative while it runs; copying it into issues
produces a second list that drifts from the first and is read by whoever finds
it first.

An issue is opened in the repository the change lands in, never in the design
record, because that is where the reader of the code looks. Work spanning the
organization therefore reads issues alongside pull requests and alerts, and an
intent nobody wrote down as one is work nobody can find.

Something exploitable is never an issue. An issue is public the moment it is
opened, so it is reported as a draft advisory on the repository it affects.

<!-- [F] global/baseline SECTION -->

## Baseline

A repository's memory states what the repository is before it states what was
decided about it. What it is, where it sits among the others, how it is built,
what a consumer may depend on, what was measured and the command that measures
it again, where its own prose and its code disagree, and what the inventory
leaves out.

Memory filled only by archived features records a sequence of changes. It
answers what was decided and never what the thing is, so a reader arriving at it
learns how one mechanism works before learning what the repository is for. That
is the state osapi's memory was in after five features: 1,840 lines, no
statement of purpose, no dependency, no architecture.

A count is written with the command that produces it. A number alone is a claim
that was true when somebody typed it, and nothing marks the moment it stops
being true.

Memory is documentation, written in the voice of somebody explaining a system to
somebody who has to work on it. Not a specification: no requirement identifiers
in the body, no "MUST", no user stories, no acceptance scenarios, no success
criteria. Those belong to the feature that produced the knowledge, where a
reviewer reads them once. Memory is read repeatedly by somebody learning the
system, and the formalism that serves the first reader obstructs the second.

A heading names the thing, with its path where a path helps. A statement is made
in the present tense and stated once. A design decision carries its reason, in a
sentence, the first time it appears — why the liveness probe checks nothing
belongs beside the liveness probe. What never appears is commentary about the
document: how a fact was found, that a fact is important, which requirement
obliged it, or what an earlier version said. A reader who wants that reads the
feature it came from.

Show the thing where showing it is shorter than describing it. A configuration
block, a directory tree, a response shape and a command are documentation; a
paragraph about the shape of a configuration block is not.

Memory is a tree, not a file. `spec.md` says what the repository is and links to
the subjects. A subject with enough in it to explain gets its own document beside
it, and a repository small enough to explain in one document keeps one.

Archiving a feature places its content in the subject it belongs to. A change to
how work is queued lands in the document about queuing work, beside what is
already there, and `spec.md` gains a link at most. Appending every feature to one
document produces a file that answers everything and explains nothing, which is
what one repository's memory became after seven features: five subjects in 266
lines, saying something about each and enough about none.

The consolidation is the work. Two statements about the same mechanism become one
statement, and the one that survives carries what both said. A document that grew
by appending is a record of how it was written rather than a description of what
is true.

Memory is written in a human voice and checked for the tells that mark machine
prose. Em dashes, bold labels that restate the line after them, title case
headings, "serves as" where "is" would do, rule-of-three lists that were not
three things to begin with. A document a reader cannot finish is not
documentation, whatever it contains.


---

**Version**: 1.4.0 | **Ratified**: 2026-09-02 | **Last Amended**: 2026-09-30
