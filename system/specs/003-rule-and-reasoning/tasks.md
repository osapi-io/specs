# Tasks: A rule and the reason for it live in different places

**Feature**: `003-rule-and-reasoning` | **Spec**: [spec.md](spec.md) | **Plan**:
[plan.md](plan.md)

Twelve tasks in five phases. The fragment text is in [plan.md](plan.md) and is
not re-derived here; T002 pastes it.

## Phase 1: correct the specification

- [ ] T001 Correct FR-016's constitution count from 6 to 7 in
  [spec.md](spec.md), and say in the same requirement that `system` composes the
  fragment like any other project. Research found this; see
  [research.md](research.md) item 1. It is a miscount rather than a change of
  intent, so it lands here rather than in its own pull request.

  Verify:
  `ls components/*/.specify/memory/constitution.md system/.specify/memory/constitution.md | wc -l`
  returns 7.

## Phase 2: the fragment

- [ ] T002 Add the paragraph from [plan.md](plan.md) to
  `.charter/fragments/global/documentation.md` as the **third** paragraph,
  before the tool-configuration clause. Paste it verbatim; the wording was
  decided in planning and re-deciding it here is how two versions of a rule
  appear.

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

## Phase 3: compose

- [ ] T004 Recompose **all seven** constitutions by invoking
  `speckit-charter-compose` once per project, with `SPECIFY_INIT_DIR` set to
  that project. Seven invocations, not one: composition resolves one project at
  a time from its own `state.yml`.

  Order does not matter. Each is independent.

- [ ] T005 [P] Verify every constitution took the change, by a phrase from the
  paragraph rather than by trusting that the tool ran:

  ```sh
  grep -lc 'about to break it is standing' components/*/.specify/memory/constitution.md \
    system/.specify/memory/constitution.md | wc -l    # 7
  ```

  A count below seven names the project that did not compose.
  `global/verification` is why this is a task rather than an assumption: running
  something that would fail if the claim were false.

- [ ] T006 [P] Verify nothing else moved in the seven files.
  `speckit-charter-compose` rewrites a whole constitution, so a fragment that
  changed upstream, or a marker that drifted, appears here as an unrelated diff.

  ```sh
  git diff --stat -- components/*/.specify/memory/constitution.md system/.specify/memory/constitution.md
  ```

  Expect seven files, each with the same small insertion. Anything larger is
  investigated before committing, not explained afterwards.

## Phase 4: the design

- [ ] T007 Add the agreement to `system/.specify/memory/spec.md`: the rule, the
  test, and the two failures that produced it. Keep it to what a reader needs,
  which is the separation and the question. The ten worked examples stay in
  [data-model.md](data-model.md); memory names the pattern rather than listing
  ten rows.

- [ ] T008 Add the counts to `system`'s memory with their commands, if the
  agreement states any. Anything stated as a number in memory is run by
  `just memory-check` on every test, and a number without a command fails it.

- [ ] T009 Run `unslop` over what T007 wrote, per AGENTS.md. The tells to expect
  in this particular text are a bold label restating the line after it, and
  commentary about the document, because the subject is documentation and it is
  easy to slip into writing about writing.

## Phase 5: verify

- [ ] T010 SC-003, the reading, from [plan.md](plan.md)'s procedure. A fresh
  reader given the amended fragment and the ten rules as unlabelled one-liners
  sorts them and states a reason each. A pass is ten sorted with reasons about
  consequence. A failure is sorting by wording, or asking for the reasoning
  before sorting.

  This is the only task that checks the test works rather than checking a
  paragraph landed. If it fails, T002's wording is wrong and Phase 2 runs again.

- [ ] T011 [P] `just test` in the specs repository. mdformat, just-fmt,
  skill-lint, 69 counts and 26 documents.

- [ ] T012 Record what is owed, with owners, in this task list rather than in an
  issue, because both items are live work with a named next step:

  | Owed                                                 | Owner   | Blocked until |
  | ---------------------------------------------------- | ------- | ------------- |
  | State the eight rules in `osapi`'s own documentation | `osapi` | this merges   |
  | Amend `gohai`'s 002 for the fourth axis              | `gohai` | this merges   |

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
