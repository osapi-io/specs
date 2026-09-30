# Feature Specification: A baseline for osapi-justfiles

**Feature Branch**: `001-justfiles-baseline`

**Created**: 2026-09-29

**Status**: Draft

**Input**: `osapi-justfiles`' `.specify/memory/` holds only a constitution, and
that constitution is composed from `.charter/` — so it states what binds every
repository and nothing about this one. This is unit 6 of the baseline programme
`system`'s [002](../../../../system/specs/002-baseline-shape/spec.md) defines,
taken deliberately out of order.

## Why this one is sixth rather than last

It is the smallest repository in the organization and the largest risk to the
*shape*. 002's FR-011 and FR-013 ask two questions no baseline has yet had to
answer: may a required section be omitted, and can a contract be stated for
something that exposes no code? `osapi-justfiles` has **zero Go files**, no
`docs/` tree and no documentation site. If the seven-section shape cannot be
filled here, the shape is wrong — and 002's own task list says finding that out
after four conforming baselines is the expensive order.

So this specification has two deliverables, not one. The inventory is the
obvious half. The other is the answer, section by section, to whether the shape
fits a repository that is not a Go library — and that answer is recorded here as
evidence about the shape rather than left as a feeling that it went fine.

## What this specification is, and what it is not

**Its subject is a description, not a change.** Nothing lands in the
`osapi-justfiles` repository: no recipe is added, renamed or removed, no fetch
is pinned, no README moves. What this produces is an inventory of how the
repository behaves today, which lives in this feature directory and reaches
memory through archival like any other feature. Step 2 of CONTRIBUTING's
"Closing a change" does not apply.

**Prose was a lead, never a source.** The repository carries a 112-line root
README and five module READMEs totalling 353 lines. None of it was transcribed.
Every count below came from a command, the commands are given so a reader
re-measures rather than trusting this file, and where a count could be taken two
ways it was taken both ways and the results compared.

**This is the first baseline written against `global/baseline`.** That fragment
was composed into all six constitutions by 002 and no baseline had yet been
written under it — gohai's predates it. Whether the fragment was sufficient to
write a baseline from is therefore evidence about the fragment, and FR-020
records it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A consumer knows what it is depending on (Priority: P1)

Somebody maintaining one of the six *other* consuming repositories can state
what `osapi-justfiles` gives them — which recipes exist, what each needs
configured before the import, and what happens to their build when the module
changes — without reading the `.just` files.

**Why this priority**: every repository in the organization runs its tests
through recipes that come from here. It is the one repository whose contract is
consumed by all of the others, and the only one whose contract is nowhere
written down.

**Independent Test**: a reader with no prior knowledge names the five modules,
says which recipes a given module supplies, and states what a consumer must set
before importing it — from this specification alone, without opening the
repository.

**Acceptance Scenarios**:

1. **Given** this specification, **When** a consumer asks what configuring the
   `go` module requires, **Then** the override variables and their defaults are
   stated.
2. **Given** this specification, **When** a consumer asks what version of a
   module their last build used, **Then** the answer is that nothing records it,
   stated as a gap rather than left to be discovered.

______________________________________________________________________

### User Story 2 - The seven-section shape is tested against a repository with no code (Priority: P1)

Somebody about to write the fourth, fifth or sixth baseline knows whether the
shape holds for a repository that is not a Go library, because this one tried it
and said what happened.

**Why this priority**: equal to the first, and the reason this unit is sixth.
The cost of discovering the shape does not fit is paid once here or four times
later.

**Independent Test**: for each of the seven required sections, this
specification states whether it was fillable, what filled it, and — if it was
omitted — why, such that an omission is never indistinguishable from an
oversight.

**Acceptance Scenarios**:

1. **Given** the seven sections, **When** each is checked against this
   specification, **Then** each is either filled or carries a stated reason for
   its absence.
2. **Given** a section that 002 assumed would be about code, **When** it is
   filled for a repository with none, **Then** what filled it is named, so the
   next baseline can tell whether its own case is the same one.

______________________________________________________________________

### User Story 3 - A change here is recognised as the widest change in the organization (Priority: P2)

Somebody editing a module knows, before they do, that it reaches seven
repositories' next continuous integration run with no release, no tag and
nothing recording which version a build used.

**Why this priority**: lower than the two above because it is a consequence of
what they state rather than a separate subject, but it is the fact about this
repository that most changes behaviour once known.

**Independent Test**: this specification states the dependency direction, the
number of incoming edges — seven, taken from the command rather than from a list
— and that the propagation mechanism is a fetch from a branch rather than from a
release.

### Edge Cases

- **A repository with no code still has an interface.** The shape's contract
  section was written expecting exported symbols. Here the contract is 38 recipe
  names and twenty variable names, which is an interface by every test that
  matters: a consumer depends on it, renaming part of it breaks them, and
  nothing in the repository declares it. Stating it was possible; what had to
  change was the assumption that a contract means code.
- **A repository that is its own consumer.** `osapi-justfiles` fetches its own
  `md` module from `main` and imports it, while running its `just` module from
  the working tree. The two halves of its own `test` recipe therefore resolve
  differently, and no other repository in the organization has this shape.
- **A count that is true and misleading.** 002's FR-031 records this repository
  as having **0 documentation pages**. That is exactly right about pages and
  wrong as an answer to "what documentation does it have", because six README
  files are its documentation. The baseline records both rather than
  reinterpreting the figure.
- **A recipe that does not carry its module's name.** Thirty-seven of the 38
  recipes are prefixed with their module, so an import adds a predictable
  namespace. One is not, and it is in the most widely imported module.

## Requirements *(mandatory)*

Every requirement is *the corpus MUST state X*, and each names how it was
checked. The section headings below are the seven 002 fixes, in 002's order.

### 1. What this repository is

- **FR-001**: The corpus MUST state that `osapi-justfiles` is a library of
  shared `just` recipes — not a tool, not a service, and not a Go module. It
  contains **zero Go files**, and its only executable content is `just` recipes
  and the shell they invoke. Verified:
  `find . -name '*.go' -not -path './.git/*' | wc -l` returns 0.
- **FR-002**: The corpus MUST state that it exists so that a convention binding
  several repositories is written once. That is `global/documentation`'s "where
  a convention binds several repositories, each states it in the same words"
  made mechanical: the repositories do not each state the recipe, they each
  fetch it.

### 2. Where it sits

- **FR-003**: The corpus MUST state that `osapi-justfiles` depends on **no**
  other repository in the organization and is depended on by **seven**, itself
  among them — every non-archived public repository in the organization that has
  a justfile at all. It is the only node in the dependency graph with no
  outgoing edge, which is the exact opposite of `osapi`'s position as the hub
  with the most incoming *and* outgoing edges. Verified from every consumer's
  `fetch` recipe, over the set
  `gh repo list osapi-io --no-archived --visibility public` returns rather than
  over a list written here: `grep -A8 '^fetch:' <repo>/justfile`. Only `.github`
  has no justfile.

- **FR-004**: The corpus MUST state which modules each consumer takes, because
  the blast radius of a change differs per module:

  | Consumer             | Modules | Which                                   |
  | -------------------- | ------: | --------------------------------------- |
  | `osapi`              |       5 | all                                     |
  | `gohai`              |       3 | `go`, `just`, `md`                      |
  | `nats-client`        |       3 | `go`, `just`, `md`                      |
  | `nats-server`        |       3 | `go`, `just`, `md`                      |
  | `osapi-orchestrator` |       3 | `go`, `just`, `md`                      |
  | `specs`              |       2 | `just`, `md` — it has no Go and no site |
  | `osapi-justfiles`    |       1 | `md`, from itself — FR-010              |

  So a change to `md.just` reaches **all seven**, `just.just` reaches six,
  `go.just` reaches five, and `react.just` and `docusaurus.just` reach one each.
  `md` has the widest blast radius in the organization.

- **FR-004a**: The corpus MUST record that **`specs` is a consumer, and that
  this baseline originally said six consumers rather than seven.** The design
  record fetches `md` and `just` — it has no Go and no documentation site, so it
  takes the two modules that apply to any repository holding markdown and a
  justfile.

  **How it was missed, and what found it.** This specification was written from
  the six repositories the baseline programme enumerates, which are the six
  *components*. `specs` is not a component — it is where the components are
  described — so it was never in the frame, despite being the repository the
  specification was being written in and the one whose `just test` had been run
  dozens of times while writing it. What found it was the task that says to take
  the repository set from
  `gh repo list osapi-io --no-archived --visibility public` rather than from a
  list written here, which is `global/repositories` applied to this feature's
  own verification. **A written list is right when written and wrong afterwards,
  and the failure mode is not that the list ages — it is that the writer's frame
  was never the whole set.**

  The consequence is not only arithmetic. `specs`' `just test` is the gate for
  every corpus change in the organization, and it depends on an unpinned fetch
  of `md.just` — so the design record's own formatting gate can be changed by a
  commit to the repository the design record describes. That circularity is
  recorded with FR-017's gap rather than as a separate finding, because the fix
  is the same one.

- **FR-005**: The corpus MUST state that a change here is the **widest change
  available in the organization**, and why: it reaches every consumer's next
  continuous integration run with no release, no tag and no review in the
  consuming repository. This is a statement about reach, not a criticism of the
  mechanism; FR-016 records the gap.

### 3. Architecture

Stated at the level 002's FR-004 to FR-006 require: what each part is for and
what passes between parts, nothing a rename would falsify.

- **FR-006**: The corpus MUST state that the repository is **five independent
  modules**, one per directory, each holding exactly one `.just` file named
  after its directory and one `README.md`. There is no shared code between
  modules and no module imports another. A consumer takes the modules it wants
  and ignores the rest, which is why `nats-server` never sees a React recipe.

- **FR-006a**: The corpus MUST state **what each module is for**, not only that
  there are five of them. 002's FR-004 requires architecture at the level of
  what a part is for, and naming the parts is not the same as saying what they
  do:

  | Module       | What it is for                                                          |
  | ------------ | ----------------------------------------------------------------------- |
  | `docusaurus` | Builds, serves, deploys and formats a Docusaurus documentation site     |
  | `go`         | Builds, tests, formats, lints and measures coverage for a Go project    |
  | `just`       | Formats and checks a repository's justfiles, using just's own formatter |
  | `md`         | Formats every markdown file in a repository with mdformat               |
  | `react`      | Builds, lints, formats and serves a React application                   |

  **This was missing, and the SC-001 reading is what found it.** The
  specification listed the five names in three places — FR-006, FR-011's recipe
  table, FR-013's variable table — and said nowhere what any of them does. A
  reader could infer it from the recipe prefixes, and the reading did,
  correctly. That is the failure: an inventory whose reader has to infer the
  purpose of a part from the names of its recipes has described the repository's
  *shape* and not its *architecture*, which is the distinction 002's FR-004
  draws. The purposes above were taken from each module's README and checked
  against its recipe list.

- **FR-007**: The corpus MUST state what passes between a module and its
  consumer, in both directions: **recipes** out, **variables** in. A consumer
  assigns the variables it needs to override, then imports the module; the
  module's recipes read those variables. Nothing else crosses the boundary — no
  configuration file, no environment contract, no generated artifact.

- **FR-008**: The corpus MUST state the consumption mechanism, because it is
  architecture rather than detail: a consumer's `fetch` recipe `curl`s each
  module from `raw.githubusercontent.com` at `refs/heads/main` into
  `.just/remote/`, and `.just/` is gitignored in every consumer. So the modules
  are **fetched, not vendored**: nothing about which version a consumer has is
  recorded in that consumer.

- **FR-009**: The corpus MUST state that the import is **optional** —
  `import? '.just/remote/<module>.just'` — so a consumer's justfile parses
  before `just fetch` has ever run, and a missing module surfaces as an unknown
  recipe rather than a parse error.

- **FR-010**: The corpus MUST state that `osapi-justfiles` is **its own
  consumer, asymmetrically**: its root justfile fetches `md.just` from `main`
  and imports it, while invoking its `just` module directly from the working
  tree with `just --justfile just/just.just`. So one half of its own `test`
  recipe checks the code in front of you and the other half checks whatever
  `main` holds. Verified: the repository's root `justfile`.

### 4. The contract

What a consumer may depend on. Stated in two halves because a consumer depends
on both.

- **FR-011**: The corpus MUST state the **38 recipes** by name, grouped by
  module, and MUST record that the count was verified two ways that agree — by
  grep for recipe headers and by
  `just --justfile <d>/<d>.just --working-directory . --summary`:

  | Module       | Recipes | Names                                                                                                                                                                                                                            |
  | ------------ | ------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `docusaurus` |      10 | `docusaurus-build`, `-bump`, `-clean`, `-deploy`, `-deps`, `-fmt`, `-fmt-check`, `-generate`, `-serve`, `-start`                                                                                                                 |
  | `go`         |      16 | `go-deps`, `go-fmt`, `go-fmt-check`, `go-generate`, `go-mod`, `go-mod-bump`, `go-mod-check`, `go-test`, `go-unit`, `go-unit-cov`, `go-unit-cov-check`, `go-unit-cov-gaps`, `go-unit-cov-map`, `go-unit-int`, `go-vet`, **`run`** |
  | `just`       |       2 | `just-fmt`, `just-fmt-check`                                                                                                                                                                                                     |
  | `md`         |       2 | `md-fmt`, `md-fmt-check`                                                                                                                                                                                                         |
  | `react`      |       8 | `react-build`, `react-deps`, `react-dev`, `react-fmt`, `react-fmt-check`, `react-generate`, `react-lint`, `react-test`                                                                                                           |

- **FR-011a**: The corpus MUST state that **two of the 38 recipes take
  arguments**, because a recipe's signature is part of what a consumer invokes
  and a bare name does not carry it: `docusaurus-bump version` requires one, and
  `run *args` is variadic and forwards what it is given to `go run`. The other
  36 take none. Verified by reading each module's recipe headers; the two appear
  as `{{ version }}` and `{{ args }}` in their bodies, which is how they were
  found — see FR-013a.

- **FR-012**: The corpus MUST state that **37 of the 38 recipes are prefixed
  with their module's name and one is not**: `run`, in the `go` module. A
  consumer importing `go.just` therefore gains an unprefixed recipe name in the
  most widely imported module, where a name collision with the consumer's own
  `run` is possible. Recorded as an inconsistency in the contract, not as a
  defect to fix here.

- **FR-013**: The corpus MUST state the **twenty override variables and their
  defaults**, because they are the half of the contract a consumer must act on
  before the import rather than after:

  | Module       | Variable             | Default                                                   |
  | ------------ | -------------------- | --------------------------------------------------------- |
  | `docusaurus` | `docusaurus_dir`     | `docs`                                                    |
  | `docusaurus` | `docusaurus_host`    | `localhost`                                               |
  | `docusaurus` | `docusaurus_port`    | `3001`                                                    |
  | `go`         | `go_git_root`        | **computed** — `git rev-parse --show-toplevel`            |
  | `go`         | `go_main_package`    | `main.go`                                                 |
  | `go`         | `go_coverage_dir`    | `.coverage`                                               |
  | `go`         | `go_coverage_target` | `100`                                                     |
  | `go`         | `go_fmt_excludes`    | **empty** — a consumer adds `! -path` clauses             |
  | `go`         | `go_os_tags`         | **computed** — `-tags=ubuntu` on Ubuntu, empty elsewhere  |
  | `go`         | `go_packages`        | **computed** — `go list ./...` less `node_modules`        |
  | `md`         | `md_version`         | `1.0.0`                                                   |
  | `md`         | `md_gfm_version`     | `1.0.0`                                                   |
  | `md`         | `md_wrap`            | `80`                                                      |
  | `md`         | `md_python`          | `3.13`                                                    |
  | `md`         | `md_site_dir`        | `docs`                                                    |
  | `md`         | `md_excludes`        | excludes `.claude`, `node_modules`, `.worktrees`, `.just` |
  | `md`         | `md_site_exclude`    | **derived** from `md_site_dir`; empty when that is empty  |
  | `md`         | `md_extra_excludes`  | **empty**                                                 |
  | `react`      | `react_dir`          | `.`                                                       |
  | `react`      | `react_fmt_pattern`  | `src/**/*.{ts,tsx,css}`                                   |
  | `just`       | none                 | it takes no configuration                                 |

  **Every default is stated, and four of them are not literals.** The table
  originally printed defaults for only three of `go`'s seven variables while
  FR-013a asserted that all twenty have one. Both were true — the four unprinted
  ones are computed or empty rather than absent — but a reader comparing the
  table against FR-013a's claim had no way to tell which. The SC-001 reading hit
  exactly that and said so. **An empty default and a missing default look
  identical in a table that prints neither, and they are opposite facts**: one
  means a consumer need not act, the other means they must.

  Nineteen of the twenty are declared in their module's header block;
  `go_packages` is declared at `go/go.just:147`, beside the recipe that uses it.

- **FR-013a**: The corpus MUST state that FR-013's table is **complete** — every
  variable any module's recipes read has an assignment with a default in that
  module — and MUST state how that was established rather than asserting it.
  Each module's `{{ variable }}` references were compared against its assignment
  lines; the only two references not matched by an assignment are
  `{{ version }}` and `{{ args }}`, and both are recipe parameters rather than
  module variables, which is FR-011a. So there is no variable a consumer must
  set without a default, and no variable the table omits.

  **This requirement exists because the check nearly did not happen.** The plan
  had named "a variable a module reads without assigning a default" as a limit
  of the inventory — a caveat, stated and left. Running the comparison took one
  command and turned the caveat into a verified fact. A limit that can be tested
  is not a limit; it is a check nobody ran.

- **FR-013b**: The corpus MUST state the variable count as **20** rather than as
  "about twenty", and MUST carry the command that produces it. The figure is
  exact, enumerable from FR-013's own table, and FR-013a has already established
  that the table omits nothing — so there was never anything to approximate.

  **Recorded rather than silently corrected, because the hedge is the
  interesting part.** This specification stated "about twenty" in five places
  while listing all twenty in a table two paragraphs away, and FR-016's
  measurement table had no row for them at all. A count is the one thing this
  repository's constitution says must never be a claim somebody typed, and the
  approximation survived a specification, an amendment and a plan. It was found
  by the consistency pass, not by re-reading. A hedge reads as caution and
  functions as an unmeasured number.

- **FR-014**: The corpus MUST state that **each module pins the tools it invokes
  while nothing pins the module**. `md` pins mdformat 1.0.0, mdformat-gfm 1.0.0
  and Python 3.13; `go` pins a coverage target of 100. So the inner versions are
  fixed and the outer one floats, which is the reverse of what a reader would
  assume from either half alone.

- **FR-015**: The corpus MUST state what stability a consumer may actually
  expect, and MUST state it as what is true rather than as what would be
  reasonable: **the contract is whatever `main` holds.** There is no release, no
  tag, no version number and no deprecation path, so a recipe renamed on `main`
  is renamed for every consumer at their next `just fetch`. A consumer may
  depend on the names above being what `main` holds today and on nothing about
  tomorrow. Inventing a compatibility policy the repository does not have would
  be the standard `global/correction` forbids.

### 5. Measurements

- **FR-016**: The corpus MUST state each measurement with the command that
  produces it, per `global/baseline`. Measured 2026-09-29 at `e765614`:

  | Measurement                | Value | Command                                                                                 |
  | -------------------------- | ----: | --------------------------------------------------------------------------------------- |
  | Go files                   |     0 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                    |
  | Modules                    |     5 | `ls -d */ \| while read d; do [ -f "$d$(basename $d).just" ] && echo $d; done \| wc -l` |
  | Recipes, all modules       |    38 | `just --justfile <d>/<d>.just --working-directory . --summary` per module               |
  | Override variables         |    20 | `grep -hcE '^[a-z_][a-z0-9_]* *:?= ' */*.just \| paste -sd+ - \| bc`                    |
  | `.just` lines, all modules |   487 | `wc -l */*.just`                                                                        |
  | Markdown files             |    11 | `find . -name '*.md' -not -path './.git/*' \| wc -l`                                    |
  | Module READMEs             |     5 | `wc -l */README.md`                                                                     |
  | Module README lines        |   353 | `wc -l */README.md`                                                                     |
  | Root README lines          |   112 | `wc -l README.md`                                                                       |
  | Documentation site pages   |     0 | no `docs/` tree exists                                                                  |

  Per module, recipes / `.just` lines / README lines / variables: `docusaurus`
  10 / 83 / 64 / 3; `go` 16 / 215 / 93 / 7; `just` 2 / 41 / 39 / 0; `md` 2 / 60
  / 100 / 8; `react` 8 / 88 / 57 / 2. The variables are the column this table
  originally had no row for, which is FR-013b.

### 6. Gaps

Each is recorded with both sides named and an owner. None is this feature's to
fix, and 002's FR-024 established that a recorded gap belongs to whoever owns
the repository it is in.

- **FR-017**: The corpus MUST record that **every consumer fetches from
  `refs/heads/main`**, so nothing pins the modules and nothing records which
  version a build used. The rule this strains is `global/tooling`'s "both
  provisioning paths resolve to the same version" — which here has no mechanism
  at all rather than a divergent one. Stated as the rule it strains rather than
  asserted as a violation: the principle's committed-output clause does **not**
  bite, because `.just/` is gitignored rather than committed. Owner:
  `osapi-justfiles`, with a change in each consumer. First recorded by
  `system`'s 002.
- **FR-018**: The corpus MUST record the **self-consumption asymmetry** FR-010
  states as a gap as well as architecture: the repository supplying the modules
  checks its own markdown against whatever `main` holds rather than against the
  file in its working tree, so a change to `md.just` cannot be tested by the
  repository that owns it before it is on `main`. Owner: `osapi-justfiles`.
- **FR-019**: The corpus MUST record that **002's own inventory has a gap this
  baseline found**. 002's FR-031 records `osapi-justfiles` as having 0
  documentation pages, which is true of pages and misleading as a statement
  about documentation: six README files are this repository's documentation,
  five of them documenting one module each. The correct statement is that it has
  **no documentation pages and six documentation files**. Owner: `system`'s 002,
  amended in its own change — not here, and not by reinterpreting the figure.
- **FR-020**: The corpus MUST record whether `global/baseline` was sufficient to
  write this baseline from, since this is the first written under it. **It was,
  with one thing it does not say.** The fragment names the seven subjects and
  the count-with-command rule, and both were directly usable. What it does not
  say is what a "contract" means for a repository that exposes no code — the
  word reads as though it presumes exported symbols, and this baseline had to
  decide that 38 recipe names and 20 variable names are one. That decision is
  recorded here rather than folded in silently, because the next non-Go
  repository will need the same one. Whether the fragment should say so is
  `system`'s to decide.

### 7. What this inventory excludes

- **FR-021**: The corpus MUST state what it deliberately leaves out, so a later
  reader can tell an omission from an oversight:

  - **What each recipe does internally.** The recipes are named and their
    configuration stated; the shell inside them is not transcribed. It is the
    statement of record and prose about it would drift — `global/documentation`.
  - **The contents of the five module READMEs.** They document the interface of
    the file beside them; this states that they exist and what they cover.
  - **The repository's own contributor conventions.** `AGENTS.md`,
    `CONTRIBUTING.md`, `CLAUDE.md`, `CODE_OF_CONDUCT.md` and `AI_POLICY.md` are
    that repository's and are cited rather than copied.
  - **The `Dockerfile` and the five GitHub workflows.** Its continuous
    integration runs `just-lint` and commit linting; what those configurations
    contain is not inventoried here.
  - **Whether any recipe is correct.** This states what the contract is, not
    whether a recipe does what its name suggests.

- **FR-021a**: The corpus MUST use `system`'s 002 FR-001 section names
  **verbatim** — "What this repository is", "Where it sits", "Architecture",
  "The contract", "Measurements", "Gaps", "What this inventory excludes" —
  rather than names that merely mean the same thing.

  **This baseline did not, and the correction is the point.** Three of its
  headings were extended: "What *the* repository is", "Where it sits *among the
  others*", and "Measurements\*, and the commands that reproduce them\*". Every
  one was an improvement in isolation — clearer, more specific, better prose.
  The order was right and so was the meaning, so nothing read as wrong.

  It matters because this is the **first** baseline written to the shape, and
  four more will be written by copying it rather than by re-reading 002. A
  section name that drifts by one word per baseline is how six documents stop
  being one set, and the whole argument for a fixed order is that a reader
  moving between baselines finds the same answer in the same place. A heading is
  where they look first.

- **FR-022**: The corpus MUST state that **no section of the seven was
  omitted**, and MUST say what filled each, because that is this unit's second
  deliverable. Sections 1, 2, 5, 6 and 7 filled as they would for any
  repository. Section 3 filled with the five-module structure and the
  fetch-and-override mechanism, at the level a rename survives. Section 4 filled
  with recipe names and variable names, which required deciding that a contract
  need not be code — the one place the shape had to be interpreted rather than
  followed. **The shape fits a repository with no Go code, and 002's FR-011 need
  not be exercised: no section had to be dropped.**

- **FR-022a**: The corpus MUST record what the SC-001 reading said about this
  document as a document, because it is a finding about the shape and not only
  about this baseline.

  The reading answered all three questions but reported that the file reads as
  **a list of requirements with a layer of self-referential narrative**, not as
  one coherent reader-facing document — and that the consumer-facing facts a
  maintainer actually wants are interleaved with, and outnumbered by, commentary
  about the specification-writing exercise. It named the passages: why this unit
  is sixth, FR-004a's account of missing `specs`, FR-013b on the hedge, FR-021a
  on the renamed headings, FR-020's verdict on the fragment.

  **That is accurate, and it is not fixed by deleting them.** This document
  carries two deliverables — the inventory for a consumer, and the shape finding
  for the programme — and User Story 2 is the second one. The meta-narrative
  *is* what FR-020 and FR-022 were asked to produce. What the reading exposes is
  that one document serving both readers serves the first one worse, which is
  the same structural problem the corpus backfill solved by splitting a page
  rather than by editing it.

  Recorded here rather than acted on, because the fix is not this baseline's: it
  is whether `system`'s 002 should require the shape finding to live somewhere
  other than the baseline a consumer reads. Owner: `system`'s 002, alongside
  FR-020's question about the same fragment.

  It also reported that the file assumes a reader knows what `just`, a recipe, a
  justfile and `import?` are, and knows spec-kit's vocabulary — FR-, SC-, "the
  seven sections", "unit 6". The first set is reasonable for a reader of a
  justfile library. The second is not obviously reasonable for a maintainer of a
  consuming repository, and no requirement here addresses it.

### Key Entities

- **Module**: One directory holding one `.just` file and one `README.md`,
  independent of the other four. Five exist.
- **Recipe**: One named entry point a consumer may invoke. 38 exist, 37 carrying
  their module's prefix.
- **Override variable**: A value a consumer assigns before the import, which the
  module's recipes read. Twenty, each with a default.
- **Consumer**: A repository whose justfile fetches and imports at least one
  module. Seven, `osapi-justfiles` and `specs` among them — every non-archived
  public repository in the organization that has a justfile.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who has not opened the repository names the five modules,
  says which recipes a named module supplies, and states what must be configured
  before importing the `go` module — from this specification alone.
- **SC-002**: Every count in this specification is paired with a command, and
  running that command reproduces the figure.
- **SC-003**: A reader can state what happens to their build when a module
  changes, and that nothing records which version their last build used.
- **SC-004**: For each of the seven required sections, this specification says
  whether it was filled and what filled it; no section is absent without a
  stated reason.
- **SC-005**: The three gaps are stated with both sides named and an owner, and
  none is corrected here.
- **SC-006**: `just test` passes in the specifications repository.
- **SC-007**: Nothing in the `osapi-justfiles` repository changes.

## Assumptions

- The measurements are of `e765614`. Line and recipe counts will date; the
  commands are given so a reader re-measures rather than trusting them, and what
  the modules are for will outlast both.
- A README is documentation and a `.just` file is not, for the purpose of
  FR-019's classification. The README describes an interface for a reader; the
  `.just` file is the interface.
- The five module READMEs stay where they are. A module's README documents the
  file beside it and its reader is a contributor in a consuming repository;
  moving it to the corpus would separate an interface from its description,
  which is the opposite of what the programme is for. This is the same reasoning
  002's FR-028 applied to `gohai/docs/collectors/`.
- Nothing about the fetch mechanism is being proposed, defended or condemned
  here. FR-017 records that nothing pins it; what to do about that belongs to a
  change in the repository that owns it.
- The dependency graph is the one `system`'s memory states, and this baseline
  states only its own edges, per 002's FR-019.
