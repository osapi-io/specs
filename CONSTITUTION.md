# Constitution

These are the rules for each repository in this organization. They are in one
file because there are seven repositories. If you write a rule seven times, you
must keep seven copies the same.

Each rule is here because the organization made the error first. A rule that
somebody adds only to fill a document is noise. Thus each rule names its
evidence, where there is evidence.

## Documentation

A repository states all of the conventions that apply to it. A reference to
guidance in a different location does not replace that statement. These readers
see only the one repository:

- a reviewer who reads a pull request in a browser
- a contributor who works offline
- an agent with one checkout

When a convention applies to more than one repository, each repository states it
in the same words. Thus a different word means a different rule.

Do not write a rule as prose if a tool already enforces it. The configuration is
the statement of record. The documentation says where the configuration is.
People must update prose about the settings of a tool by hand, and no check
finds an error in it. Thus the prose becomes incorrect, but it continues to look
correct.

## Verification

Measure a claim about the codebase. Do not only examine the code. If you read
the code and make a conclusion, that is a hypothesis. If you run a check that
fails when the claim is false, that is a result.

When you report that work is complete, give the output that shows it. "Tests
pass" is a claim. The command and its output are evidence.

If a check can be automatic, make it automatic. A rule that only a review
enforces stays true only until the reviewer is busy.

## Tooling

Declare each tool that a repository runs in the location where the repository
declares its tools. A tool that comes from the installation of each developer is
not the same tool on each machine. It is also not the tool that continuous
integration runs.

The two provisioning paths use the same version. If nothing updates a version
automatically, the two paths use the latest release, so that they change
together. If a mechanism updates the version, the two paths pin it, and that
mechanism changes the two. If one path pins a version and the other path does
not, the two versions become different.

Pin a tool when you commit its output. Then the committed file does not change
when a different person runs the generator.

Pin a GitHub Action from outside the organization by its full commit SHA. Put
its version in a comment at the end of the line:

```yaml
uses: actions/checkout@<40-character sha> # v7.0.0
```

The owner of an action can move a tag. A workflow that pins a tag runs the code
that the tag points to today. That is how the tj-actions/changed-files
compromise got to its users. Nobody can move a SHA. Dependabot reads the comment
and changes the SHA and the comment together. Thus the pin needs no maintenance.

Each workflow declares the token permissions that it needs in a `permissions:`
block. Put the block at the top of the workflow or on each job. The default
token of the repository is read-only:

```yaml
permissions:
  contents: read
```

Without a block, the workflow gets the default of the repository setting. On an
older repository, that default is write access to all things, which includes the
approval of pull requests. A workflow that declares nothing gets that default.
Thus each third-party action that it runs can push to the default branch.

A declared block also tells the purpose of a workflow. A workflow that labels
stale issues asks for `issues: write`, and a reader can see why. If a workflow
needs write access and does not declare it, it fails without a clear error. A
stale-issue job on a read-only default fails in this way.

## The language version

A tool version and a language version are different promises. The tool version
is the version that this repository builds with. The language version in
`go.mod` is a minimum. It is the oldest release that a consumer can build with.
Of the two versions, only the language version applies to other people.

A repository supports the two most recent Go minor releases. Thus the directive
names the older of the two. If the directive names the newest release, the
repository stops support for the release before it. That is the opposite of the
rule. Tool provisioning still uses the latest release. A toolchain that is newer
than the minimum is always permitted, and it shows new vet findings early.

Continuous integration builds the minimum version. A declaration alone is not
sufficient. A repository that tests one version and promises two did not test
the promise. A day can come when a newer standard library call compiles locally.
On that day, the build of the minimum version breaks for each consumer, and
nothing reports it. The job that builds the minimum reads the version from
`go.mod`. It does not write the version again. Thus a change to the directive
also changes the build.

This file does not record the current release. The toolchain list gives it. The
reason is the same as the reason that this file does not record the repository
list.

## Correction

If a rule is incorrect when you apply it, stop the work. Correct the rule first,
in its own change. If you correct the rule and the code together, the rule only
describes what you already did. Also, the correction is in a place where no
reviewer examines it as a change of rule.

Write a requirement from evidence that the repository already has: its
configuration, its history, or a failure that occurred. A standard that you
invent to fill a template is noise, not a constraint. The repository does not
obey it from the first day.

## Repositories

The repositories in this organization are the result of
`gh repo list osapi-io --no-archived --visibility public`. No document keeps a
copy of that list.

A written list is correct when you write it. It is incorrect after somebody adds
the next repository, and nothing shows that change. Work on more than one
repository gets the set from the command each time. To use fewer repositories,
make the set smaller when you use it. Do not keep a second list.

Do not record what a command can give. Such a record is a cache that nothing
updates and nothing checks. It looks current until somebody measures it.

## Tracking

An issue records that something must change. The page records the result of that
change. These are two stages of one piece of work, not two records of it. The
pull request that makes the page true closes the issue.

An issue keeps an intent when nobody works on it. Track work in progress where
you do it. If you copy it into issues, you make a second list. That list becomes
different from the first, and a reader can find the incorrect list first.

Open an issue when the work is larger than the current change. When the work is
not larger, fix it directly. This rule applies most to an inconsistency that you
find during a different task. If you make the change larger, the fix is hidden
in a diff about a different subject. If you say nothing, the fix is lost.
Neither result is tracking.

Work that you agree to do later is an issue from the time that you agree to it.
This includes a next step that you name at the end of a change, a candidate that
you give with other candidates, and each step of a plan page that nobody has
started. Before you open the issue, look for an issue that has the work. A plan
page tells the order and the design. Thus the issue links to its section and
does not copy it.

The task list of an agent, its memory and the text of a session are not records.
They stop when the session stops, and nobody else can read them. An agent can
use a task list for the steps of the change that it does now. Each item that is
not done when the change merges becomes an issue, or the agent deletes it.

An issue has the evidence that found it, with the command that shows the problem
again. The reason is the same as for a page.

Open an issue in the repository where the change goes. Do not open it in the
design record, because the reader of the code looks in the repository. Thus work
across the organization reads issues together with pull requests and alerts. If
nobody writes an intent as an issue, nobody can find that work.

Do not open an issue for a problem that an attacker can use. An issue is public
when you open it. Report the problem as a draft advisory on the repository that
it affects.

## The documents

The page of a repository tells what the repository is before it tells what
people decided about it. In this order, it tells:

1. what the repository is
2. where it is among the other repositories
3. how to build it
4. what a consumer can depend on
5. what somebody measured, and the command that measures it again
6. where its prose and its code do not agree
7. what it does not include

Documentation that only grows at the end records a sequence of changes. It tells
what people decided, and never what the thing is. A new reader learns how one
mechanism works before the reader learns the purpose of the repository. The
osapi documentation was in that state after five changes: 1,840 lines, no
statement of purpose, no dependency and no architecture.

A page explains a system to a person who must work on it. It is not a
specification. It has no requirement identifiers, no "MUST", no user stories and
no acceptance scenarios. A person who learns the system reads a page many times.
The formal style helps a reviewer one time, and it makes the page more difficult
for that reader each time.

A heading names the thing. Add its path if the path helps. Write a statement in
the present tense, and write it one time. A design decision gives its reason in
one sentence, at the first location where it occurs. For example, the reason
that the liveness probe checks nothing goes next to the liveness probe.

A page has no comments about the document itself. It does not tell how somebody
found a fact, that a fact is important, or what an earlier version said.

If it is shorter to show a thing than to describe it, show it. A configuration
block, a directory tree, a response shape and a command are documentation. A
paragraph about the shape of a configuration block is not documentation.

The documentation is a tree. The `README.md` of a component tells what the
repository is and links to its subjects. A subject that needs an explanation
gets its own page next to the README. A repository that one page can explain
keeps one page.

A change goes into the page of its subject. For example, a change about how
osapi queues work goes into the page about the queue. Merge it with the text
that is already there. The README gets one link, or nothing.

If you add each change at the end of one page, the page tells something about
each subject but explains nothing. The documentation of one repository was in
that state after seven changes. It had five subjects in 266 lines. It told a
small amount about each subject, and not sufficient information about any
subject.

The merge is the work. Two statements about the same mechanism become one
statement. The statement that stays has the content of the two. A page that
grows only at the end is a record of how somebody wrote it. It does not describe
what is true.

Write a page in a human voice. Check it for the signs of machine prose:

- em dashes
- bold labels that say the same thing as the line after them
- title case headings
- "serves as" in place of "is"
- lists of three items where the subject does not have three items

Each page in each repository in this organization uses Simplified Technical
English (ASD-STE100). STE uses one word for one thing, short sentences, the
active voice, and commands for steps. This rule applies to each README, each
CONTRIBUTING, the documentation site, and the skills that a binary ships.

A reader whose first language is not English can understand the page in only one
way. An agent that writes the next page has one style to copy. This file states
the rule, and no other file states it. The files of a repository do not write it
again. [ste-100](.claude/skills/ste-100/SKILL.md) has the rules and checks a
page against them.

Text that a generator writes obeys the rule through its source: the definition,
the comment or the template. Command names, flags, code and example output are
technical names, not sentences. Do not change them.

## What the repositories agree on

These rules apply to more than one repository. Thus they are here, and not in
the repository that found them first.

### The repository list is a command, not a document

The repositories in this organization are the result of this command:

```sh
gh repo list osapi-io --no-archived --visibility public
```

**No document keeps a copy of that list.** A written list is correct when you
write it. It is incorrect after somebody adds the next repository, and nothing
shows that change. Thus work on more than one repository gets the set from the
command each time. To use fewer repositories, make the set smaller when you use
it.

`--no-archived` is important. Archived repositories have Dependabot pull
requests that cannot merge, and a search of the organization counts them.

This rule started as a deletion. A list of the repositories, which people
updated by hand, had a dependency graph, which people also updated by hand. The
`go.mod` files and the justfiles already gave that graph. The list was removed,
and the rule that replaced it is `global/repositories` in each constitution.

**People broke the rule after that, and that is the useful part.** The baseline
of `osapi-justfiles` listed six consumers. The command gives seven, because
`specs` also gets justfile modules. The writer made the list from the six
*components*, not from the result of the command. **It was incorrect when the
writer made it. It did not become stale.** Age did not cause the error. The
point of view of the writer caused it.

### A rule a document states is reachable from the repository it binds

If these documents state a rule that people must obey, the repository where
those people work also states it, in one line. The reasons stay here. The
repository needs only the rule, so that a person with one checkout can find it.

A measurement of `osapi` on 2026-09-30 found ten rules that a contributor must
obey. The documentation of `osapi` stated two of them, and did not state eight.
Two of the eight had security advisories. Thus a checkout did not show some of
the rules that cost this organization the most.

```sh
cd ~/git/osapi-io/osapi
grep -ilE 'consistent across all layers' CONTRIBUTING.md   # stated
grep -ilE 'upsert' CONTRIBUTING.md                          # was not
```

### Every README has the shape of its kind

A README has the headings of its kind, in this order. The kinds are the ones
that [ARCHITECTURE.md](ARCHITECTURE.md) uses: the product, the components, and
the repositories of the organization. A repository can add its own headings
after Features, or after Usage where there is no Features, and before
Contributing. Collectors in gohai and Targeting in osapi-orchestrator are
examples. [templates/README.md](templates/README.md) has the shape of a Go
component, the most common kind.

| Kind                 | Repositories                                        | Headings                                                                                                                             |
| -------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| The product          | osapi                                               | Features, What you can ask, Where it goes next, Alternatives, Getting started, Documentation, Sister projects, Contributing, License |
| A Go component       | gohai, nats-client, nats-server, osapi-orchestrator | Install, Features, Usage (optional), Examples, Documentation, Contributing, License                                                  |
| Another component    | osapi-justfiles, osapi-lab                          | Usage, Documentation (optional), Contributing, License                                                                               |
| An organization repo | specs, .github                                      | Usage, its own headings, Contributing (where it has one), License                                                                    |

Each `##` heading starts with one emoji from this index. The same heading always
has the same emoji:

| Heading                 | Emoji |
| ----------------------- | ----- |
| Install                 | 📦    |
| Features                | ✨    |
| Usage, Getting started  | 🚀    |
| Examples                | 🧪    |
| Documentation           | 📚    |
| What you can ask        | 💬    |
| Where it goes next      | 🧭    |
| Alternatives            | ⚖️    |
| Sister projects         | 🧩    |
| Related works           | 🔗    |
| Collectors              | 🧰    |
| Targeting               | 🎯    |
| Operations              | ⚙️    |
| Skills                  | 🤖    |
| Doc-driven development  | 📝    |
| The design docs         | 🗂️    |
| Change the profile page | ✏️    |
| Contributing            | 🤝    |
| License                 | 📄    |

A new heading gets an emoji in this table before a README uses it. A new
repository gets a kind in the first table, and the same kind in ARCHITECTURE.md.

Emojis go only on `##` headings, and in the items of a Features list. Do not put
them in other headings or in body text. Use bold rarely, and never as the label
at the start of each item of a list.

```sh
cd ~/git/osapi-io
for r in */; do
  [ -f "$r/README.md" ] && echo "$r $(grep -E '^## ' "$r/README.md" | tr '\n' '|')"
done
```

### A Go package is one thing

These rules apply to each Go repository:

1. **A package holds one kind of thing.** Its name tells what it holds. Do not
   make a package named `util`, `common`, `helpers` or `shared`. Such a name
   tells nothing, and code that is not related collects in it.
2. **The name of a package is the last part of its path.** An exported name does
   not repeat the name of its package inside a longer name. A caller reads
   `atomicfile.Write`, not `atomicfile.WriteFileAtomic`. The main type of a
   package can have the name of the package, as `time.Time` and
   `context.Context` do.
3. **A caller does not need an alias.** If a file must import two packages that
   have the same name, rename one of the packages. An alias is a different name
   in each file that uses the package. Mock packages are the exception: each is
   named `mocks`, beside the code that it mocks, so a test that uses two of them
   gives one an alias. A clash with a package outside the module, or between two
   names that are both correct, also takes an alias.
4. **A directory can group packages that belong together.** The name of the
   directory tells what the group is, for example `telemetry/` for `metrics` and
   `tracing`.
5. **Do not put many packages under one package.** A package is one thing. If
   packages collect under it, find the group that they make, and give that group
   its own directory.

Rules 1 to 3 come from the Go documentation:
[Effective Go](https://go.dev/doc/effective_go#package-names) and
[Package names](https://go.dev/blog/package-names). A repository puts its own
rules about the layout in its `CONTRIBUTING.md`, after these.

This command counts the imports that use an alias of a package in the same
module. A change to the layout makes the count smaller:

```sh
cd ~/git/osapi-io/osapi
git grep -hP '^\t+[a-zA-Z][a-zA-Z0-9]* "github.com/osapi-io/osapi/' -- '*.go' ':!*.gen.go' | wc -l
```

### Every CONTRIBUTING.md has one shape

[templates/CONTRIBUTING.md](templates/CONTRIBUTING.md) has the sections that the
`CONTRIBUTING.md` of each repository shares, with their headings, their order
and their text. A repository copies them and puts its own sections between them.
It does not rename, move or remove a shared section. A paragraph that the
template marks as optional stays only where its condition is true. specs is the
only exception. It has no code, so its `CONTRIBUTING.md` has its own shape.

Each repository has these sections: Before you start, Prerequisites with Coding
agents, Before you commit, Branches, Commit messages, Submit a pull request, AI
usage and FAQ. The Go repositories also have Setup, Project structure, Code
style with Documentation, Code standards with its five subsections, and Tests
with Test file conventions.

A change to a shared section starts in its template. The same work then changes
each repository and the `swamp-golang-starter` template, which copies this one.
Nobody can trust a convention that is different in each repository.

[templates/AGENTS.md](templates/AGENTS.md) does the same for `AGENTS.md`. Its
shared parts are the summary line, the introduction, Run tools, Where the rules
come from, Commit trailer and Design pages. specs has its own `AGENTS.md`, for
the same reason.

```sh
cd ~/git/osapi-io
for r in */; do
  [ -f "$r/CONTRIBUTING.md" ] && echo "$r $(grep -cE '^##+ ' "$r/CONTRIBUTING.md")"
done
```
