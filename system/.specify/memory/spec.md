# What the repositories agree on

`system` is a project without a repository. Its subject is what the osapi-io
repositories agree on between them, so a rule that binds more than one lives here
rather than in whichever one noticed it first.

Two documents. This one holds the agreements. [architecture.md](architecture.md)
holds how the repositories actually fit together, and is where to start if you
want the product rather than the conventions.

## The repository list is a command, not a document

The repositories in this organization are what this returns:

```sh
gh repo list osapi-io --no-archived --visibility public
```

**No document holds a copy of that list.** A written list is correct when written
and wrong after the next repository is added, and nothing marks the moment it
turns. So work spanning repositories takes the set from the command each time and
narrows it at the point of use.

`--no-archived` matters. Archived repositories hold Dependabot pull requests that
can never merge, and a search across the organization counts them.

This rule started as a deletion. `system/.specify/memory/dependencies.md` held a
hand-maintained dependency graph, and the graph was already derivable from
`go.mod` files and justfiles. It went, and the rule that replaced it is
`global/repositories` in every constitution.

**It has been broken since, which is the useful part.** `osapi-justfiles`' own
baseline listed six consumers. The command returns seven, because `specs` fetches
justfile modules too, and the list was written from the six *components* rather
than from what the command returns. **It was wrong when written, not stale.**
Ageing was never the failure mode; the writer's frame was.

## Every component answers the same seven questions

A reader moving between repositories finds the same answers in the same order.
Seven subjects:

| # | Subject                      | Answers                                                     |
| - | ---------------------------- | ----------------------------------------------------------- |
| 1 | What this repository is       | Its purpose, and who consumes it                            |
| 2 | Where it sits                 | What it depends on, what depends on it, what breaks each way |
| 3 | Architecture                  | The parts, what each is for, what flows between them        |
| 4 | The contract                  | What a consumer may depend on, and what is free to change   |
| 5 | Measurements                  | Counts, each with the command that reproduces it            |
| 6 | Gaps                          | Where the repository's prose and its code disagree, with an owner |
| 7 | What this inventory excludes  | Named omissions, so a gap is never mistaken for an oversight |

**The fixed names belong to the baselines, not to memory.** A baseline is a review
artifact and its headings are the seven above, verbatim: `osapi-justfiles`' baseline
extended three of them, each an improvement in isolation, and the drift would have
propagated to every baseline written by copying it.

Memory answers the same seven questions under headings that name the thing rather
than the section. "What was measured" rather than "Measurements", "Known
limitations" rather than "Gaps", "Not covered here" rather than "What this
inventory excludes", and in between, headings like "The collector contract" or
"Guards ask what happened; predicates ask what a host is" that say what the section
is about. That is deliberate. A document whose headings are a numbered list of
sections reads as a specification, which is what memory stopped being.

So the order is stable and the wording is not, and two of the seven are answered
somewhere other than under a heading of their own. `osapi`'s contract is the SDK
and is answered in [its own document](../../../components/osapi/.specify/memory/architecture/sdk.md)
rather than in its entry point; `gohai` answers its gaps inside the sections that
found them. A reader looking for a question rather than a heading finds it; a
reader expecting seven headings does not, which is worth saying once here rather
than surprising them six times.

**The shape survived a repository with no code.** `osapi-justfiles` has no Go, no
`docs/` tree and no documentation site, and it was baselined sixth deliberately to
find out whether the shape fits before four more were written to it. No section had
to be dropped. Section 4 was the only one needing interpretation, because "the
contract" reads as though it presumes exported symbols: there it is 38 recipe names
and 20 variable names. The bound that keeps the word useful is **something a
consumer's build breaks on**.

## Memory is documentation

Not a specification. No requirement identifiers in the body, no `MUST`, no user
stories, no acceptance scenarios, no success criteria. Those belong to the feature
that produced the knowledge, where a reviewer reads them once. Memory is read
repeatedly by somebody learning the system, and the formalism that serves the first
reader obstructs the second.

Memory is also a **tree**, not a file. `spec.md` says what the repository is and
links to its subjects; a subject with enough in it to explain gets its own document.
Archiving a feature places its content in the subject it belongs to, merged with
what is there, and `spec.md` gains a link at most.

Both rules exist because both were broken. Five archivals copied the feature's form
into memory, so `nats-client`'s opened with `## User Scenarios & Testing` and stated
`SC-006: just test passes in the specs repository`. And osapi's covered five
subjects in 266 lines, which says something about each and explains none of them.

`global/baseline` carries the rule. `scripts/check-memory-docs.py` and
`scripts/check-memory-counts.py` fail the build when it is broken, which is the
only part of this that does not depend on somebody remembering.

## A count carries the command that produces it

A number alone is a claim that was true when somebody typed it, and nothing marks
the moment it stops being true.

`just memory-check` runs every command in every measurement table against the
repository it describes. Getting there fixed seven counts nobody could have
checked: six written as "the same, plus `-not -name '*_test.go'`", which is a
shortcut for whoever wrote the table and cannot be run by anything.

Each command has to stand alone for that reason.

## Classification precedes a move

A repository's documentation is classified before anything is relocated, page by
page, by **who reads it** rather than by where it sits. The move is a separate
change.

osapi is why. Its corpus backfill moved documentation across three features and
none of them wrote the document saying which pages were contributor-facing, so
three pages survived that nobody had examined: two of them 464 lines of contributor
architecture on an operator's site with nowhere to cite. The classification that
found them came a year of features later.

A page a repository's *consumers* read stays with the repository.
`gohai/docs/collectors/` is the example: its readers are library consumers, not
contributors, so it belongs where they will look.

## A rule the corpus states is reachable from the repository it binds

Where the corpus states a rule somebody must follow, the repository they are
working in states it too. The reason lives here and stays here; what this asks is
that the rule be reachable from one checkout.

The measurement that produced it, at `osapi` on 2026-09-30: ten rules the corpus
states and a contributor must follow, two of them stated in `osapi`'s own root
documents and eight not. Two of the eight carry advisories, so the rules this
organization learned the hardest are among those a checkout cannot show you.

```sh
cd ~/git/osapi-io/osapi
grep -ilE 'consistent across all layers' CONTRIBUTING.md   # stated
grep -ilE 'upsert' CONTRIBUTING.md                          # not
```

This is not a charter fragment, and the attempt to make it one is the reason it is
worded as an obligation rather than as a distinction. Two readings tried to apply
a test separating a rule from its reasoning. The first sorted by grammar and said
so. The second found that the test classified every one of its own worked examples
the wrong way, because "a rule says what somebody does" is false of "one endpoint
never both creates and updates" and of every other rule in the set. A test that
needs the reader to already know the answer is not a test.

What replaced it asks nothing to be sorted. A move leaves the rule where a
contributor meets it and takes the reasoning, which is what gohai's move did, and
no repository ends up with a rule it cannot state.

## What is not here

How any one repository works. That is its own memory, and
[architecture.md](architecture.md) links to all six.

Anything about `specs` or `.github` as components. `specs` holds this
documentation; `.github` holds shared configuration and has no justfile. Neither
gets a baseline, and stating that is what stops the difference between "the six
components" and "the repositories" being left implicit, which is exactly what
produced the wrong consumer count above.

______________________________________________________________________

Traced to `specs/001-repository-inventory/` for the list rule and
`specs/002-baseline-shape/` for the shape, the documentation contract and the
classification order.
