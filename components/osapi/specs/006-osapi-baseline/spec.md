# Feature Specification: A baseline for osapi

**Feature Branch**: `006-osapi-baseline`

**Created**: 2026-09-29

**Status**: Completed — amended 2026-09-29 before planning: FR-019 through
FR-021 record a 263-line second statement of the UI architecture at
`ui/docs/architecture.md`, which the page classification did not reach because
it counted published pages. The two copies have already diverged.

**Input**: osapi's memory holds 1,840 lines from five archived features and
nowhere says what the repository is. Its `spec.md` sections are *The job
system*, *Building a domain* and *Where knowledge lives*; its `plan.md` sections
are about the corpus backfill. A reader arriving there learns how job delivery
works before learning what osapi is for, and never learns that it sits between
the NATS repositories and the orchestrator. This is the first baseline written
to the shape [system's 002](../../../../system/specs/002-baseline-shape/spec.md)
fixes, and FR-029 puts osapi first because it is the dependency hub.

## What this is, and what it is not

**Its subject is a description.** No Go code changes. What this produces is the
frame osapi's memory lacks — what the repository is, where it sits, and how it
is built — plus a classification of all 219 site pages.

**It cites rather than restates.** osapi's contract is already four archived
features: the provider contract, the agent key store, the job system, building a
domain. A baseline that restated any of it would be the second statement the
whole programme exists to end, so section 4 below is mostly citation and says
so.

**Prose, not Given/When/Then.** 002's FR-017 requires it: a baseline is read
repeatedly by somebody learning a system, and the formalism that helps a
reviewer check a change obstructs that reader. The user stories below carry the
template's acceptance form because the template requires it of a feature
specification; the inventory those stories describe does not.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Somebody learns what osapi is (Priority: P1)

Somebody arriving at osapi's memory learns what the repository is for, what it
sits between, and how its parts fit — before learning how any one mechanism
works.

**Why this priority**: it is the gap. The memory is detailed and frameless.

**Independent Test**: a reader given the corpus alone states what osapi is for,
names both its upstream dependencies and its downstream consumer, and describes
the path a request takes without opening the code.

**Acceptance Scenarios**:

1. **Given** the corpus, **When** a reader asks what osapi is, **Then** the
   answer is in section 1 rather than inferred from a requirement about job
   delivery.
2. **Given** the corpus, **When** a reader asks what would break if
   `nats-client` changed, **Then** section 2 names the direction and the
   consequence.

______________________________________________________________________

### User Story 2 - The architecture survives a rename (Priority: P1)

Somebody reads the architecture six months from now and finds it still true,
because it states what each part is for rather than transcribing how it
currently calls.

**Why this priority**: osapi is 2,739 Go files. An architecture written at the
level of function names would be wrong within a month, and a wrong statement
carries the authority of a specification.

**Independent Test**: no section names a function as the claim rather than as
evidence for one, and nothing in the baseline lists the code.

**Acceptance Scenarios**:

1. **Given** the architecture section, **When** a function is renamed, **Then**
   the section cites a stale path and remains true.

______________________________________________________________________

### User Story 3 - The pages that stayed are the pages an operator reads (Priority: P2)

Somebody auditing the site after the backfill can tell, for every page, whether
it was left there deliberately and for whom.

**Why this priority**: three contributor pages survived the backfill because 003
named six candidates and these were not among them. Without a classification
nobody would find them.

**Independent Test**: all 219 pages are classified, and the three contributor
pages are named with what to do about them.

### Edge Cases

- **A page the backfill was never scoped to.** Three exist. 003 classified six
  candidate pages and moved what they held; the UI and SDK-development pages
  were never candidates, so they were never examined. An inventory that only
  re-checked 003's six would have missed them exactly as 003 did.
- **A demonstration that looks like a restatement.** `sdk/guidelines.md` shows
  the SDK rules working with worked examples and cites 005's FR-019 and FR-020
  for the rules themselves. Showing a rule working is not stating it twice, and
  the distinction has to be drawn explicitly or the page reads as a violation.
- **A page that is only a pointer.** Three development pages are 17 to 24 lines
  and defer to osapi's own `CONTRIBUTING.md`. Deferring is what
  `global/documentation` asks for; they stay.
- **Memory that already holds the answer.** Most of what a contributor needs
  about providers, jobs and domains is already archived. The baseline's job is
  to say so and where, not to say it again.

## Requirements *(mandatory)*

Every requirement is *the corpus MUST state X*. The seven sections 002's FR-001
fixes are the organising structure, and each requirement below names which it
serves.

### Section 1 — what this repository is

- **FR-001**: The corpus MUST state that osapi is two things that ship together:
  a controller exposing a REST API, and an agent that runs on each managed host.
  Work reaches a host by being queued rather than by being called. Verified:
  `cmd/` holds both entry points; `main.go` dispatches.
- **FR-002**: The corpus MUST state who consumes it — an operator through the
  CLI, a program through the Go SDK at `pkg/sdk/client`, and
  `osapi-orchestrator` through that same SDK. Three readers, and most of the
  site serves the first.

### Section 2 — where it sits

- **FR-003**: The corpus MUST state both directions of osapi's place in the
  graph. **Upstream**: `nats-client` and `nats-server`, which it imports.
  **Downstream**: `osapi-orchestrator`, which imports it. Verified:
  `grep -oE "osapi-io/[a-z-]+" go.mod`.
- **FR-004**: The corpus MUST state what breaks in each direction, because a
  dependency named without a consequence is trivia. A change to either NATS
  repository can break osapi's transport; a change to osapi's SDK surface breaks
  the orchestrator, which pins a pseudo-version commit rather than a tag, so
  nothing breaks there until somebody bumps it — which is why a rename and its
  bump want to land together.
- **FR-005**: The corpus MUST state that osapi also depends on `osapi-justfiles`
  for its build, that this appears in no `go.mod` because it is fetched by a
  justfile recipe, and that the fetch is unpinned. Owner of the pinning: those
  repositories.

### Section 3 — architecture

- **FR-006**: The corpus MUST state the six layers and **what each is for**, not
  how it currently calls: the CLI parses and prints; the REST API validates and
  delegates; the job system carries work to a host; a provider does the work
  there; the agent lifecycle registers providers and dispatches to them;
  configuration is resolved once at startup. Verified: the directory structure
  under `cmd/`, `internal/controller/`, `internal/job/`, `internal/provider/`,
  `internal/agent/`, `internal/config/`.
- **FR-007**: The corpus MUST state the path a mutating request takes —
  `CLI → SDK → REST API → job client → NATS → agent → provider` — and that the
  provider runs on the agent rather than the controller, because that single
  fact explains why the API cannot simply do the work.
- **FR-008**: The corpus MUST NOT transcribe the call chain, list the exported
  surface, or walk the files. 002's FR-005 forbids all three. Where a symbol
  appears it is evidence for a claim, never the claim.
- **FR-009**: Where the architecture reaches job delivery, provider behaviour,
  agent identity or domain construction, the corpus MUST **cite** the archived
  features that already state them rather than summarising. Memory's own
  `#### The job system`, `#### Building a domain` and
  `#### Where knowledge lives` are the destinations.

### Section 4 — the contract

- **FR-010**: The corpus MUST state that osapi's contract is **already stated**,
  and cite it: the provider contract ([001](../001-provider-contract/spec.md)),
  the agent key store ([002](../002-agent-key-store/spec.md)), the job system
  ([004](../004-job-system/spec.md)), and building a domain
  ([005](../005-building-a-domain/spec.md)). This section is mostly citation and
  the corpus MUST say why, so a reader does not read its brevity as an omission.
- **FR-011**: The corpus MUST state what a consumer of the SDK may depend on and
  what is free to change: the exported surface of `pkg/sdk/client` is the
  contract, and everything under `internal/` is not. Verified: the package
  layout.

### Section 5 — measurements

- **FR-012**: The corpus MUST state each count with the command that reproduces
  it, and MUST state what each counts, because two of them differ by a
  definition rather than by a measurement:

  | Count                    | Value | Command                                                                                                                   |
  | ------------------------ | ----- | ------------------------------------------------------------------------------------------------------------------------- |
  | Go files                 | 2,739 | `find . -name '*.go' -not -path './.git/*' \| wc -l`                                                                      |
  | Go files excluding tests | 1,814 | the same, plus `-not -name '*_test.go'`                                                                                   |
  | Site pages               | 219   | `find docs/docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                                      |
  | Files under `docs/`      | 221   | `find docs -name '*.md' -not -path '*/node_modules/*' \| wc -l`                                                           |
  | Provider categories      | 6     | `ls -d internal/provider/*/ \| wc -l`                                                                                     |
  | API domains              | 24    | `ls -d internal/controller/api/node/*/ internal/controller/api/*/ \| grep -vE '/(gen\|mocks\|common\|apierr)/$' \| wc -l` |
  | SDK methods              | 117   | `grep -cE '^func \(s \*[A-Za-z]+Service\)' pkg/sdk/client/*.go` summed                                                    |

- **FR-013**: The corpus MUST state that **219 and 221 are different
  quantities**: 219 are site pages under `docs/docs/`, and 221 adds
  `docs/README.md` and `docs/SUPPORT.md`, which are the Docusaurus project's own
  files rather than published pages. 002's FR-023 records osapi at 221; the
  classification below covers 219.

### Section 6 — gaps

- **FR-014**: The corpus MUST record that **three contributor pages survived the
  corpus backfill**, and why they did: 003 named six candidate pages and
  classified those; these three were never candidates, so nothing examined them.

  | Page                            | Lines | What it holds                                                      |
  | ------------------------------- | ----- | ------------------------------------------------------------------ |
  | `architecture/ui.md`            | 264   | The embedded UI's structure, tech stack and component architecture |
  | `development/ui-development.md` | 200   | How to set up and develop the UI                                   |
  | `sdk/guidelines.md`             | 227   | How to develop the SDK, with worked examples                       |

  464 of those lines — the two UI pages — have **no corpus counterpart at all**,
  so they are contributor knowledge on an operator's site with nowhere to cite.
  That is the state the backfill existed to end, surviving in a corner it never
  looked at.

- **FR-015**: The corpus MUST state that `sdk/guidelines.md` is a **different
  case from the other two**. Its rules are already stated as 005's FR-019 and
  FR-020, and the page cites them and then demonstrates them with worked
  examples. Showing a rule working is not stating it twice. What it holds beyond
  demonstration — package structure and the response pattern — is the part with
  no counterpart.

- **FR-016**: The corpus MUST record that this finding changes the programme's
  arithmetic. `system`'s 002 states osapi's move is "already done, across three
  features"; that is true of the six pages 003 scoped and false of these three.
  osapi needs a move after all, so the programme is **twelve units, not
  eleven**, and 002 needs amending — in its own change, not this one.

### The drift this inventory did not look for, and found anyway

- **FR-019**: The corpus MUST record that `ui/docs/architecture.md` exists,
  holds **263 lines** of contributor documentation, and is **a second statement
  of the site's `architecture/ui.md`** — and that the two have already diverged.

  This was outside FR-018's classification, which counted the 219 pages under
  `docs/docs/` and therefore never reached a documentation file living beside
  the code it describes. The count was right about published pages and
  incomplete about the repository's documentation, which are different
  questions.

  The two files cover the same ground — tech stack, application structure,
  authentication, SDK generation, component architecture, pages — and each now
  holds a section the other does not:

  |                                        | Last touched | Holds, that the other does not         |
  | -------------------------------------- | ------------ | -------------------------------------- |
  | `ui/docs/architecture.md`              | 2026-09-02   | `Feature flags`                        |
  | `docs/docs/sidebar/architecture/ui.md` | 2026-08-15   | `Configuration`, `Embedding Mechanism` |

  Verified: `git log -1 --format=%cs` on each, and a comparison of their `##`
  headings. Their shared sections still agree in substance and differ in
  punctuation, which is what a copy looks like shortly before it stops agreeing
  at all.

- **FR-020**: The corpus MUST state that this is **the drift the one-statement
  rule exists to prevent, observed rather than hypothesised**. Two documents
  were once the same, were edited eighteen days apart, and each gained content
  the other never got. Nothing marked the moment they stopped agreeing, which is
  the failure `global/documentation` describes and the reason the corpus holds
  one statement and citations.

- **FR-021**: The corpus MUST state that osapi's move therefore reconciles
  **three** statements, not two: the site page, the file beside the code, and
  the corpus statement that will replace both. A move that relocated only the
  site page would leave the divergent copy in place and make it the sole
  statement by default — the worse outcome, because the surviving copy is the
  one missing `Configuration` and `Embedding Mechanism`.

### Section 7 — what this inventory excludes

- **FR-017**: The corpus MUST state what it leaves out and why, so an omission
  is never mistaken for an oversight:

  - **Everything the five archived features already state.** Cited, not
    repeated.
  - **How any individual provider or domain works.** 24 domains and 6 provider
    categories; the contract they share is stated and the instances are not.
  - **The CLI's full command surface.** 143 pages of reference under
    `usage/cli`, which is where an operator should read it.
  - **The UI's internals.** They are FR-014's gap, and stating them here would
    be doing the move this feature is not.
  - **osapi's testing conventions.** Its own `CONTRIBUTING.md`'s, cited.
  - **Documentation outside `docs/`, beyond the one file FR-019 records.** The
    classification counted published pages; `ui/docs/architecture.md` was found
    by looking wider and is recorded as a gap. `ui/AI_POLICY.md` and the
    repository-root files are policy and process rather than architecture, and
    are not inventoried.

### The classification of all 219 pages

- **FR-018**: The corpus MUST classify every site page as user-facing or
  contributor-facing, by who reads it rather than where it sits — 002's FR-025.

  | Pages                                                                           | #       | Reader             | Disposition                                                                                          |
  | ------------------------------------------------------------------------------- | ------- | ------------------ | ---------------------------------------------------------------------------------------------------- |
  | `usage/cli`                                                                     | 143     | operator           | stays                                                                                                |
  | `sdk/client`, `sdk/platform`, `sdk/sdk.md`                                      | 34      | a program's author | stays — a consumer's reference, the same case as gohai's collector catalogue                         |
  | `features`                                                                      | 30      | operator           | stays                                                                                                |
  | `architecture/architecture.md`, `job-architecture.md`, `system-architecture.md` | 3       | operator           | stays — already reduced to their operator halves by 003 and 005                                      |
  | `development/contributing.md`, `development.md`, `testing.md`                   | 3       | contributor        | stays — 17 to 24 lines each, pointers to `CONTRIBUTING.md`, which is deferring rather than restating |
  | `usage/configuration.md`                                                        | 1       | operator           | stays                                                                                                |
  | `intro.md`                                                                      | 1       | operator           | stays                                                                                                |
  | `development/adding-an-api-domain.md`                                           | 1       | contributor        | stays — already reduced to a citation index by 005                                                   |
  | `architecture/ui.md`                                                            | 1       | **contributor**    | **moves** — FR-014                                                                                   |
  | `development/ui-development.md`                                                 | 1       | **contributor**    | **moves** — FR-014                                                                                   |
  | `sdk/guidelines.md`                                                             | 1       | **contributor**    | **partly moves** — FR-015                                                                            |
  | **Total**                                                                       | **219** |                    | **216 stay, 3 move or partly move**                                                                  |

  The arithmetic reconciles against the directory counts: `architecture` 4,
  `development` 5, `features` 30, `sdk` 35, `usage` 144, and `intro.md` 1.

### Key Entities

- **Controller**: The process exposing the REST API and owning the job queue.
- **Agent**: The process on a managed host that executes queued work through
  providers.
- **Provider**: The unit that does the work on a host. Its contract is 001's.
- **Domain**: An area of behaviour exposed as endpoints. Its construction is
  005's.
- **Site page**: One of 219 published pages, each classified by who reads it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader given the corpus alone states what osapi is for, names
  both upstream dependencies and the downstream consumer, and describes the
  request path.
- **SC-002**: Every count in the baseline is paired with its command, and
  running the seven commands reproduces the seven values.
- **SC-003**: No section transcribes a call chain or lists the exported surface.
- **SC-004**: Section 7 is non-empty — five exclusions, each with a reason.
- **SC-005**: All 219 site pages are classified, and the three contributor pages
  are named with their line counts and what holds them.
- **SC-006**: Nothing in the osapi repository changes. `git -C osapi status` is
  clean.
- **SC-007**: `just test` passes in the specs repository.

## Assumptions

- The audience is a contributor or an agent working on osapi, or somebody
  consuming its SDK. An operator is served by the site, which is why 216 of 219
  pages stay.
- Counts were measured on `0cca62060`, `main` at the time of writing. They will
  date; the commands are what survives.
- The three contributor pages are recorded here and **moved by a separate
  feature**. 002's FR-026 puts the baseline before the move, and its FR-027
  makes the move its own feature. This baseline classifies; it relocates
  nothing.
- osapi's five archived features stay exactly as they are. A baseline and
  archived features answer different questions, and neither replaces the other.
