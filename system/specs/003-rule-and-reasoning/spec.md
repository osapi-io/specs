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

- **FR-005**: The corpus MUST state the resolution as a separation of two
  statements rather than a precedence between two clauses: **a rule and the
  reason for it are different statements and live in different places.** The
  rule is stated in the repository, imperative and short. The reason is stated
  once in that repository's memory. One statement of each, not two of either.

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

- **FR-007**: The corpus MUST state **the test**, because the test outlives the
  wording and four repositories will apply it.

  **Corrected 2026-09-30, after SC-003 failed.** This required the test to be
  *would somebody who cannot read this make a wrong change?* The reading ran it
  against ten statements, sorted all ten, and then reported that it had sorted
  by grammar: every statement it called reasoning carried a causal connective
  and every statement it called a rule was a bare indicative. It proved the
  point by rewriting one statement without its "so" clause, after which the same
  fact landed as a rule.

  The counterfactual is not wrong so much as **not answerable about one
  statement at a time**, which is how it was written. "A combined endpoint
  destroys the meaning of a 404" is reasoning only because the rule forbidding
  the endpoint is stated too; remove that rule and the same words are the only
  thing standing between a contributor and a broken contract. The question asks
  about a sentence and the answer depends on the set.

  The test MUST therefore sort by **what a statement is about** rather than by
  what its absence would cost: a rule says what somebody does, and reasoning
  says what the system does. That distinction holds for one statement alone,
  which is the property the counterfactual lacked, and it is the pattern
  [data-model.md](data-model.md) found in all ten rows before the reading
  confirmed it.

  The test MUST also answer three things the counterfactual had no answer for,
  each found by the same reading:

  - A sentence that is both is **split**. "A caller can ask for less and cannot
    ask for more, because the wrapper applies its context unconditionally" is
    two statements written as one.
  - A reason recorded while the rule it explains is stated nowhere means **the
    rule is missing**, not implied. This is the most useful thing the reading
    produced and the resolution had no way to say it.
  - Where a tool enforces the rule, the clause about tool configuration wins.
    FR-008 already decided that and the fragment has to say so, because the
    ten-minute ceiling is a rule by one clause and forbidden prose by the other.

  What survives unchanged: the test is about substance rather than form.
  "MANDATORY" in a heading is not what makes something a rule, and a paragraph
  of explanation is not reasoning if omitting it lets somebody ship a
  vulnerability.

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

- **SC-003**: A reader given the fragment alone, and no other document, sorts
  the ten rules of FR-002 into rule and reasoning and states where each goes.
  This is the check that the test is usable by somebody who was not here.

  **Failed on its first run, 2026-09-30, and is the reason FR-007 changed.** A
  pass is not "ten sorted correctly". A sorter can reach ten correct answers by
  pattern-matching causal connectives, which is what happened, so the criterion
  has to ask **how** the reader sorted and not only what they concluded. A pass
  is ten sorted with reasons that refer to what each statement is about. Any
  rerun asks both questions.

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
