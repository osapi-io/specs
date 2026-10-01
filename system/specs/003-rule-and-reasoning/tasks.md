# Tasks: A rule and the reason for it live in different places

**Feature**: `003-rule-and-reasoning` | **Spec**: [spec.md](spec.md) | **Plan**:
[plan.md](plan.md)

Twelve tasks in five phases. The fragment text is in [plan.md](plan.md) and is
not re-derived here; T002 pastes it.

## Phase 1: correct the specification

- [x] T001 Correct FR-016's constitution count from 6 to 7 in
  [spec.md](spec.md), and say in the same requirement that `system` composes the
  fragment like any other project. Research found this; see
  [research.md](research.md) item 1. It is a miscount rather than a change of
  intent, so it lands here rather than in its own pull request.

  Verify:
  `ls components/*/.specify/memory/constitution.md system/.specify/memory/constitution.md | wc -l`
  returns 7.

  **Done.** FR-016's count corrected to 7 with a command naming both globs, and
  SC-002 corrected the same way: it also said six and greped only
  `components/*/`. Two instances of one miscount in one specification.

## Phase 2: the fragment

- [ ] T002 Add the paragraph from [plan.md](plan.md) to
  `.charter/fragments/global/documentation.md` as the **third** paragraph,
  before the tool-configuration clause. Paste it verbatim; the wording was
  decided in planning and re-deciding it here is how two versions of a rule
  appear.

  **Done.** The fragment is 22 lines.

- [ ] T003 Check the fragment against its own constraints, which is four greps
  rather than a reading:

  ```sh
  wc -l .charter/fragments/global/documentation.md          # under 25
  grep -c '—' .charter/fragments/global/documentation.md    # 0
  grep -ci 'mandatory' .charter/fragments/global/documentation.md   # 0
  grep -ci 'memory\|\.specify' .charter/fragments/global/documentation.md   # 0
  ```

  The last is the one to watch. The paragraph says "wherever that repository's
  design is recorded" precisely so that a fragment binding six repositories does
  not name a Spec Kit directory, and the easiest way to lose that in an edit is
  to make it concrete for clarity.

  **Done.** 22 lines, 0 em dashes, 0 "mandatory", 0 mentions of memory or
  `.specify`.

## Phase 3: compose

- [ ] T004 Recompose **all seven** constitutions by invoking
  `speckit-charter-compose` once per project, with `SPECIFY_INIT_DIR` set to
  that project. Seven invocations, not one: composition resolves one project at
  a time from its own `state.yml`.

  Order does not matter. Each is independent.

  **Done, all seven.** Composition is a deterministic concatenation: each `[F]`
  marker is followed by that fragment's body with one heading level added.
  Verified against the existing output before touching anything, then applied
  identically.

- [ ] T005 [P] Verify every constitution took the change, by a phrase from the
  paragraph rather than by trusting that the tool ran:

  ```sh
  grep -lc 'about to break it is standing' components/*/.specify/memory/constitution.md \
    system/.specify/memory/constitution.md | wc -l    # 7
  ```

  A count below seven names the project that did not compose.
  `global/verification` is why this is a task rather than an assumption: running
  something that would fail if the claim were false.

  **Done.** `grep -l 'about to break it is standing'` over all seven returns 7.

- [ ] T006 [P] Verify nothing else moved in the seven files.
  `speckit-charter-compose` rewrites a whole constitution, so a fragment that
  changed upstream, or a marker that drifted, appears here as an unrelated diff.

  ```sh
  git diff --stat -- components/*/.specify/memory/constitution.md system/.specify/memory/constitution.md
  ```

  Expect seven files, each with the same small insertion. Anything larger is
  investigated before committing, not explained afterwards.

  **Done.** Seven files, one 9-line change each, nothing else moved. Each
  section byte-equals the fragment body with the heading delta applied, checked
  by comparing the two rather than by reading the diff.

## Phase 4: the design

- [ ] T007 Add the agreement to `system/.specify/memory/spec.md`: the rule, the
  test, and the two failures that produced it. Keep it to what a reader needs,
  which is the separation and the question. The ten worked examples stay in
  [data-model.md](data-model.md); memory names the pattern rather than listing
  ten rows.

  **Done.** One agreement added to `system`'s memory: the separation, the
  question, the two failures that made the test about consequence rather than
  form, and that this was `osapi`'s practice before it was anybody's rule.

- [ ] T008 Add the counts to `system`'s memory with their commands, if the
  agreement states any. Anything stated as a number in memory is run by
  `just memory-check` on every test, and a number without a command fails it.

  **Done, nothing owed.** The agreement states no counts, so there is nothing
  for `memory-check` to run. The ten worked examples stayed in
  [data-model.md](data-model.md), the feature's artifact rather than memory.

- [ ] T009 Run `unslop` over what T007 wrote, per AGENTS.md. The tells to expect
  in this particular text are a bold label restating the line after it, and
  commentary about the document, because the subject is documentation and it is
  easy to slip into writing about writing.

  **Done.** One change: the opening was passive where the fragment's siblings
  name the actor, so "the rule is stated in the repository" became "a repository
  states the rule".

## Phase 5: verify

- [ ] T010 SC-003, the reading, from [plan.md](plan.md)'s procedure. A fresh
  reader given the amended fragment and the ten rules as unlabelled one-liners
  sorts them and states a reason each. A pass is ten sorted with reasons about
  consequence. A failure is sorting by wording, or asking for the reasoning
  before sorting.

  This is the only task that checks the test works rather than checking a
  paragraph landed. If it fails, T002's wording is wrong and Phase 2 runs again.

  **RUN AND FAILED, 2026-09-30.** The reader sorted all ten and then said how:
  "I sorted substantially on the presence of a causal connective. Every
  statement I called REASONING carries one ... Every statement I called RULE is
  a bare indicative with none. That is grammar detection, not the counterfactual
  test."

  They proved it rather than asserting it. Rewrite statement 10 from "a
  permission absent from the role map can be held by no token, **so** the
  endpoint is unreachable" to "every permission an endpoint checks appears in
  the role map", and it lands as a rule with nothing about the world having
  changed.

  This is the failure this task exists to catch, and it caught it before the
  wording bound seven constitutions. Phase 2 and Phase 3 are reset to unstarted
  and re-run after the amendment below.

  Four defects in the paragraph, in order of how much they matter:

  1. **The test is not a property of one statement.** It asks a counterfactual
     about a sentence while the answer depends on what else the reader can see.
     "A combined endpoint destroys the meaning of a 404" is reasoning *only
     because* the rule forbidding the endpoint is also stated. Remove that rule
     and the same words become the only thing standing between a contributor and
     a broken contract. Every reasoning verdict is a claim about the set, and
     the paragraph presents it as a claim about the sentence.
  2. **It does not rank itself against the clause below it.** The ten-minute
     ceiling is a rule by this paragraph and forbidden prose by the next one,
     which says a rule a tool enforces is never restated. The spec's FR-008
     already decided that the tool clause wins; the fragment does not say so.
  3. **No handling for a sentence that is both.** "A caller can ask for less and
     cannot ask for more, because the wrapper applies its context
     unconditionally" splits mid-sentence, and the paragraph says a rule and its
     reason are two statements without saying to split one that is not.
  4. **"Short enough to check against a diff" fails on the most rule-like of the
     ten.** Checking that a domain appears in every layer needs the list of
     layers, which is not in the sentence.

  A fifth thing, which is a finding rather than a defect: a reason recorded
  while the rule it explains is stated nowhere means **the rule is missing**,
  not implied. The paragraph has no way to say that, and it is the most useful
  thing the reading produced.

  **RUN AND FAILED A SECOND TIME, against the corrected test.** The paragraph
  was rewritten to sort by what a statement is about rather than by what its
  absence would cost, and the rerun asked the reader for their method as well as
  their verdicts. Both were worse than the first time, and usefully so.

  The reader's actual procedure, in its words: cluster the ten into topic pairs,
  label the directive member of each pair, and use the paragraph "as a
  label-chooser rather than as a decision procedure". Grammar was load-bearing
  in five of ten, and the absence of a connective drove the other five.

  **The defect that ends the approach**: the corrected test said "a rule says
  what somebody does", and not one rule in this feature's own `data-model.md`
  says what somebody does. "One endpoint never both creates and updates."
  "Updating something that does not exist is an error." "Ten minutes is the
  ceiling." All describe the system, so by the letter of the test all three are
  reasons. The reader classified them as rules and said why: "I called it a rule
  because I know what it is for. The test did no work."

  ```sh
  grep -c 'what somebody does' .charter/fragments/global/documentation.md   # the test
  grep -E '^\| (One endpoint|Update when|Ten minutes)' \
    system/specs/003-rule-and-reasoning/data-model.md                        # all marked rule
  ```

  Three more, each real:

  - **Six of ten verdicts were relational.** A test written to apply to one
    sentence only works against a corpus. "A combined endpoint destroys the
    meaning of a 404" is acceptable reasoning only because the rule forbidding
    the endpoint exists somewhere the reader can see.
  - **The asymmetry was never argued.** A rule without its reason was fine and a
    reason without its rule was a defect. For a convention binding several
    repositories the first paragraph puts the rule in all of them and the
    separation puts the reason in one, so the offline contributor gets rules
    with no reasons, which is the mirror of the failure the separation called
    fatal.
  - **"The rule is stated nowhere" is unfalsifiable at scale.** Reaching it for
    one statement took an exhaustive search of nine others. Against a repository
    it needs a complete search of everything the repository states.

  The one thing the reader would defend without hedging is the clause already in
  the fragment: a rule a tool enforces is named rather than restated, because
  the configuration is checkable and the failure mode is clear.

  **So the taxonomy is abandoned rather than reworded a third time**, and FR-005
  now states an obligation about reachability instead. Phase 2 and Phase 3 stay
  unstarted. T010 is rewritten with the criterion it is checking.

- [x] T011 [P] `just test` in the specs repository. mdformat, just-fmt,
  skill-lint, 69 counts and 26 documents.

  **Done.** `just test` passes: mdformat, just-fmt, skill-lint, 69 counts, 26
  documents.

- [x] T012 Record what is owed, with owners, in this task list rather than in an
  issue, because both items are live work with a named next step:

  | Owed                                                 | Owner   | Blocked until |
  | ---------------------------------------------------- | ------- | ------------- |
  | State the eight rules in `osapi`'s own documentation | `osapi` | this merges   |
  | Amend `gohai`'s 002 for the fourth axis              | `gohai` | this merges   |

  **Done.** Both rows stand, and neither is in this feature.

## Dependencies & Execution Order

- **Phase 1** is independent and can run first or last. It corrects a count.
- **Phase 2** blocks Phase 3. Composition reads the fragment.
- **Phase 3** blocks nothing inside this feature and is what makes the rule
  bind.
- **Phase 4** is independent of Phases 2 and 3: the design can be written before
  the fragment composes, and is better written after T002 fixes the wording.
- **Phase 5** depends on everything. T010 specifically depends on T002 and on
  nothing else, so it can run before composition and catch a wording failure
  early.

**The one ordering that matters**: T002 before T004. A fragment composed before
its text is final puts the wrong words in seven files, and the second compose
looks like a correction to a rule rather than a typo fix.

## Notes

- Nothing here changes a repository's documentation. The two things that will
  are T012's rows, in their own repositories' pull requests.
- T005 and T006 are the tasks that exist because composition is a generator.
  Everything generated needs a check that it generated what was intended, which
  is the lesson `global/tooling` records about committed output.
