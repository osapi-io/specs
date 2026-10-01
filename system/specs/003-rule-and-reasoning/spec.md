# Feature Specification: A rule and the reason for it live in different places

**Feature Branch**: `docs/rule-and-reasoning`

**Created**: 2026-09-30

**Status**: Draft

**Input**: Resolve the conflict between `global/documentation` and
`global/baseline` that blocked gohai's move at specs#219, and state the
resolution as a charter fragment.

## What this specification is, and what it is not

It settles one question: **when a rule binds a contributor and its reasoning is
architecture, where does each live?** Until now the charter has said a
repository states its conventions in full, and separately that a rule is stated
once, without saying which governs a statement that is both.

The answer is not invented here. `osapi` already practises it, twice, and nobody
wrote it down. This feature writes it down and names the compliance work that
follows.

It changes no repository's documentation. It changes one fragment, which
recomposes into six constitutions, and it produces a list of eight rules `osapi`
owes.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A contributor with one checkout can comply (Priority: P1)

Somebody clones `osapi`, writes a provider, and passes a password as a command
argument. The rule forbidding that exists, in the corpus, with a CVE behind it.
Its `CONTRIBUTING.md` does not state it, the site page that used to was reduced,
and they have no way to know.

**Why this priority**: it is the harm `global/documentation` was written to
prevent, and it is currently happening to eight rules in one repository.

**Independent Test**: for each of the eight rules, a reader given only the
`osapi` repository can state the rule.

**Acceptance Scenarios**:

1. **Given** only an `osapi` checkout, **When** a contributor asks how a secret
   reaches a privileged command, **Then** the answer is stdin, from a file in
   that checkout.
2. **Given** only an `osapi` checkout, **When** they ask whether one endpoint
   may both create and update, **Then** the answer is no, from a file in that
   checkout.

### User Story 2 - A reader who wants the reason follows one link (Priority: P2)

Somebody reads the rule, wants to know why it exists, and follows one link to a
document that explains it and does not repeat the rule's wording.

**Why this priority**: it is what distinguishes this resolution from "state
everything twice", which is the outcome the one-statement rule exists to
prevent.

**Independent Test**: no rule's reasoning appears in two places.

### User Story 3 - The next move applies a test rather than a judgement (Priority: P2)

Somebody planning a move for another repository has to decide, heading by
heading, what goes where. Today that is a judgement call; gohai's plan made it
three times and stopped.

**Why this priority**: four repositories have moves or reductions ahead of them,
and a test applied four times beats a judgement made four times.

### Edge Cases

- A rule a tool already enforces. `global/documentation` already says the
  configuration is the statement of record and prose is not. That clause wins,
  and the resolution here must not contradict it.
- A rule with no interesting reason. Not every rule has architecture behind it;
  the resolution must not require inventing reasoning to satisfy a shape.
- A rule that binds several repositories. `global/documentation` already says
  each states it in the same words. This resolution must leave that intact.

## Requirements *(mandatory)*

### Section 1 — what the conflict is

- **FR-001**: The corpus MUST state the conflict as two clauses that cannot both
  be satisfied by a rule that is also architecture. `global/documentation`: a
  repository states in full the conventions binding it, and a reference
  elsewhere does not stand in place of stating them. `global/baseline`: memory
  is the documentation and a fact is stated once. Neither says which governs.

- **FR-002**: The corpus MUST state that the conflict is load-bearing rather
  than theoretical, measured at `osapi` on 2026-09-30. Ten rules the corpus
  states and a contributor must follow; two are stated in `osapi`'s own root
  documents and eight are not.

  | Rule                                                                | In `osapi`'s own docs |
  | ------------------------------------------------------------------- | --------------------- |
  | A domain appears in every layer an existing one does                | **yes**               |
  | Validation is declared via `x-oapi-codegen-extra-tags`              | **yes**               |
  | One endpoint never both creates and updates                         | no                    |
  | Create when it exists is not an error                               | no                    |
  | Update when it is absent **is** an error                            | no                    |
  | A secret reaches a command through stdin, never an argument         | no                    |
  | A caller's value beginning with a dash becomes a flag               | no                    |
  | Ten minutes is a ceiling on any command, not a fallback             | no                    |
  | Anything becoming a path or argument is revalidated in the provider | no                    |
  | A permission absent from the role map reaches nobody                | no                    |

  ```sh
  cd ~/git/osapi-io/osapi
  grep -ilE 'consistent across all layers' CONTRIBUTING.md AGENTS.md   # found
  grep -ilE 'upsert' CONTRIBUTING.md AGENTS.md                          # not found
  ```

- **FR-003**: The corpus MUST state that **two of the eight carry advisories**,
  GHSA-6gc6-px2x-q95j for the stdin rule and GHSA-7fjw-v3g9-326g for
  revalidating in the provider. The rules this organization learned the hard way
  are among those a contributor's checkout cannot show them, which is the
  sharpest form the problem takes.

- **FR-004**: The corpus MUST state which readers reach what, because the reader
  list is the argument and `global/documentation` already names three of them.

  | Reader                                                  | Has                                      | Reaches the eight |
  | ------------------------------------------------------- | ---------------------------------------- | ----------------- |
  | An agent working in this repository                     | the `add-a-domain` skill and the corpus  | yes               |
  | A contributor with `osapi` checked out                  | `CONTRIBUTING.md` and the published site | **no**            |
  | A reviewer reading an `osapi` pull request in a browser | the diff and `osapi`'s files             | **no**            |

  The skill cites 22 requirement numbers across four feature specifications, so
  the first reader is well served and the fragment's own three examples include
  two who are not.

  ```sh
  grep -rhoE 'FR-[0-9]+' .claude/skills/add-a-domain/ | sort -u | wc -l   # 22
  ```

### Section 2 — the resolution

- **FR-005**: The corpus MUST state the resolution as **an obligation about
  reachability**, not as a taxonomy.

  **Corrected 2026-09-30, after SC-003 failed twice.** This required a
  separation: the rule here, the reasoning there, sorted by a test. Two readings
  showed the sorting cannot be codified, and the second showed why. The test
  said "a rule says what somebody does", and **not one rule in this feature's
  own worked examples says what somebody does**: "one endpoint never both
  creates and updates", "updating something that does not exist is an error",
  "ten minutes is the ceiling". All three describe the system. By the letter of
  the test they were reasons, and the reader classified them as rules anyway and
  said so: "I called it a rule because I know what it is for. The test did no
  work."

  The taxonomy was never the thing that mattered. What matters is what FR-002
  measured: eight rules a contributor must follow that their checkout cannot
  show them. So the obligation is **where the corpus states a rule a contributor
  must follow, that contributor's repository states it too.** Nothing has to be
  sorted, nothing has to be split, and nothing turns on whether a sentence names
  an actor.

  The reasoning is left where it is. `global/baseline`'s one-statement rule
  already governs duplication, and this obligation does not ask for a second
  statement of anything: it asks that the rule be reachable from the repository
  that it binds.

- **FR-006**: The corpus MUST record that this is `osapi`'s existing practice
  rather than a new rule, because `global/correction` requires a requirement
  written from evidence the repository already carries. `osapi`'s
  `CONTRIBUTING.md` does it twice:

  - Under "Adding a new API domain" it states the binding rule in full and in
    bold, "pick an existing domain and `find`/`grep` for it across the codebase.
    Your new domain should appear in all the same places", and links the site
    guide for the nine steps.
  - Under "Input validation" it states the mechanism and the tags, and leaves
    the design reasoning elsewhere.

  Both are the shape this feature ratifies. What was missing is anybody saying
  so, which is why eight other rules did not get the same treatment.

- **FR-007**: The corpus MUST record that **the sorting test is abandoned**, and
  why, because the attempt is the evidence for the obligation replacing it.

  Two readings, two failures, and the failures were different. The first sorted
  by grammar and admitted it: every statement it called reasoning carried a
  causal connective. The second described its real procedure, which was to
  cluster the ten into topic pairs and label the directive member of each pair,
  with the paragraph used "as a label-chooser rather than as a decision
  procedure". It then found four things wrong with the test itself, of which two
  are fatal: the stated definition classifies every one of this feature's own
  rules as a reason, and six of ten verdicts were relational, so a test written
  to apply to one sentence only works on a corpus.

  It also found the asymmetry nobody had argued for: a rule without its reason
  was treated as fine and a reason without its rule as a defect. For a
  convention binding several repositories the first paragraph puts the rule in
  all of them and the separation puts the reason in one, so the offline
  contributor the fragment is written for gets rules with no reasons. That is
  the mirror of the failure the separation called fatal.

  What survives is the one thing the second reading would defend without
  hedging: the existing clause that a rule a tool enforces is named rather than
  restated, because the configuration is checkable and has a clear failure mode.
  The obligation in FR-005 is written to the same standard.

- **FR-008**: The corpus MUST state what the resolution does **not** license. It
  does not license restating the reasoning in the repository, which is the
  duplication `global/baseline` forbids. It does not license a rule stated only
  in memory, which is the absence `global/documentation` forbids. And it leaves
  the existing clause about tool configuration untouched: a rule a tool enforces
  is still never restated as prose, and that clause wins where it applies.

### Section 3 — the fragment

- **FR-009**: `.charter/fragments/global/documentation.md` MUST gain the rule,
  in the voice and at the length of the existing eight fragments, which run 11
  to 58 lines and average 23. The addition is a paragraph, not a section.

- **FR-010**: The fragment MUST NOT carry the evidence. The ten rules, the
  advisories, the reader table and `osapi`'s two worked examples belong in
  `system`'s memory, which is where a reader goes for why. A fragment that
  carried its own evidence would be the longest of the nine and would say in six
  constitutions what belongs in one place.

- **FR-011**: All six constitutions MUST be recomposed, because a fragment
  changed and not composed binds nothing. This is `speckit-charter-compose` per
  project and is implementation rather than specification.

### Section 4 — what this makes other people owe

- **FR-012**: `osapi` MUST state the eight rules in its own documentation. This
  is **compliance work in `osapi`'s own pull request**, not a feature, per the
  rule that once something binds every component bringing a repository into line
  is ordinary work. It cites the fragment and this feature.

  Owner: `osapi`. This feature produces the list and does not do the work.

- **FR-013**: The corpus MUST record what this means for `osapi`'s three merged
  features, specifically rather than in general. They are **not wrong about
  where the reasoning goes**, and 005's FR-026 is wrong about the rule: it
  required "the contributor half of the site" removed, and removing it removed
  the only place a contributor could read rules the corpus then held alone. The
  specifications stay as they are, because they record what was decided; the
  repository gains the eight statements under FR-012.

  This is the Correction principle working as intended rather than a failure of
  it. Applying a rule a fourth time found what three applications did not.

- **FR-014**: `gohai`'s 002 MUST be amended before its plan resumes, and this
  feature MUST say so rather than leaving a blocked plan with no named next
  step. Its FR-001 splits content three ways and needs a fourth axis: a rule's
  one-line statement stays in `gohai` even when its reasoning moves. Under the
  resolution, three of its nine contested headings each split rather than moving
  whole.

  Owner: `gohai`, after this merges.

- **FR-015**: The corpus MUST state that a **skill does not discharge the
  obligation**. The `add-a-domain` skill lives in this repository, cites 22
  requirement numbers, and is unreachable from an `osapi` checkout. It serves
  the first reader well and is not a substitute for the repository stating its
  rules, because two of the three readers `global/documentation` names cannot
  run it. No change to the skill; it is simply not the answer to this question.

### Section 5 — measurements

- **FR-016**: The corpus MUST carry these counts with their commands, measured
  2026-09-30:

  | Measurement                         | Value | Command                                                                                           |
  | ----------------------------------- | ----: | ------------------------------------------------------------------------------------------------- |
  | Charter fragments                   |     8 | `ls .charter/fragments/global/*.md \| wc -l`                                                      |
  | Lines in `global/documentation`     |    14 | `wc -l .charter/fragments/global/documentation.md`                                                |
  | Constitutions to recompose          |     7 | `ls components/*/.specify/memory/constitution.md system/.specify/memory/constitution.md \| wc -l` |
  | Requirement numbers the skill cites |    22 | `grep -rhoE 'FR-[0-9]+' .claude/skills/add-a-domain/ \| sort -u \| wc -l`                         |

### Section 6 — gaps

- **FR-017**: **Gap**: nothing checks that a rule in memory is stated in its
  repository. This feature states the rule and creates no mechanism, so the
  eight can become nine the next time a move happens. A checker would have to
  know which statements in memory are rules, which is the judgement FR-007's
  test exists to make and not something a script can make. Owner: `system`,
  recorded rather than solved, and the honest position is that this one may not
  be automatable.

- **FR-018**: **Gap**: the five components other than `osapi` have not been
  measured against FR-012. The ten-rule audit was done for `osapi` because that
  is where the three moves happened. Owner: each component, when its own move
  runs.

### Section 7 — what this feature excludes

- **FR-019**: The corpus MUST state what it leaves out: writing the eight
  statements in `osapi`, amending `gohai`'s 002, `gohai`'s `collectors.md`, any
  change to the `add-a-domain` skill, deciding 002's FR-040 about what a
  citation points at, and any mechanism that would check FR-012 automatically.

### Key Entities

- **Rule**: a statement somebody must follow to avoid making a wrong change.
  Lives in the repository, imperative.
- **Reasoning**: why the rule exists, what it buys, what breaks without it.
  Lives in that repository's memory, once.
- **The test**: would somebody who cannot read this make a wrong change?

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The fragment states the rule and the test in a paragraph, and
  `global/documentation` stays under 25 lines.

- **SC-002**: All **seven** constitutions carry the new text, verified by grep
  for a phrase from it. **Corrected 2026-09-30, during planning**: this said six
  and counted only `components/*/`. `system` composes `global/documentation`
  like any other project and its constitution carries the marker, so recomposing
  six would leave `system`'s own constitution stating a rule `system` wrote and
  does not carry. That is the confusion between "the six" and "the repositories"
  that `osapi-justfiles`' baseline recorded, in a different place.

  ```sh
  grep -l 'about to break it is standing' \
    components/*/.specify/memory/constitution.md system/.specify/memory/constitution.md | wc -l
  ```

- **SC-003**: A reader given the fragment alone **says, for each of the ten
  rules of FR-002, whether a contributor with only that repository could follow
  it**. No sorting, no taxonomy. The criterion is whether the obligation is
  applicable by somebody who was not here, and the answer is a yes or a no per
  rule rather than a classification.

  **Failed twice as written and was rewritten, 2026-09-30.** It used to ask a
  reader to sort the ten into rule and reasoning. The first reading sorted by
  grammar, the second sorted by topic pairing, and the second proved the test
  contradicted this feature's own examples. A criterion a reader cannot satisfy
  without importing knowledge the fragment does not give them is not measuring
  the fragment.

- **SC-004**: The eight rules `osapi` owes are listed by name, each with where
  its reasoning already lives, so the compliance PR has no discovery to do.

- **SC-005**: No rule's reasoning is stated twice after this feature, which is
  unchanged from before it, because this feature moves nothing.

- **SC-006**: `just test` passes in the specs repository.

## Assumptions

- Recomposing six constitutions is mechanical and produces no conflict. Each
  project's `.specify/charter/state.yml` lists the fragments it composed, and
  `global/documentation` is mandatory in `manifest.yml`, so all six take the
  change.
- The ten rules of FR-002 are a sample rather than an audit. They were chosen
  because the corpus states them and a contributor must follow them; a full
  audit of `osapi`'s memory against `osapi`'s documentation is the compliance
  PR's job under FR-012.
- "Imperative and short" is judged by a reader rather than measured. A rule that
  takes a paragraph to state is a candidate for being two rules.
