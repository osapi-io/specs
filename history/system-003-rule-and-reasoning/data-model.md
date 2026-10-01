# Rule, reasoning, and the test between them

**Feature**: `003-rule-and-reasoning` | **Date**: 2026-09-30

## The two entities

| Entity        | Is                                                        | Lives in                        | Form                         |
| ------------- | --------------------------------------------------------- | ------------------------------- | ---------------------------- |
| **Rule**      | A statement somebody must follow to avoid a wrong change  | the repository                  | imperative, one or two lines |
| **Reasoning** | Why the rule exists, what it buys, what breaks without it | that repository's design record | prose, once                  |

They are not two halves of one statement. Each is complete on its own: a rule
that needs its reasoning to be followed is not yet a rule, and reasoning that
restates the rule has made the second statement this forbids.

## The test

> Would somebody who cannot read this make a wrong change?

Applied to one statement at a time, before deciding where it goes.

| Answer                                            | It is     | It goes           |
| ------------------------------------------------- | --------- | ----------------- |
| Yes, they would do the wrong thing                | a rule    | the repository    |
| No, they would do the right thing not knowing why | reasoning | the design record |

**What the test deliberately ignores**: whether the statement is written as an
imperative, whether it carries the word "must", whether its heading says
MANDATORY, and how long it is. All four are form, and the two failures this
feature exists to fix were both invisible to form. gohai has three MANDATORY
headings that are rules and one that is reasoning wearing an imperative;
`osapi`'s stdin rule is a paragraph of explanation whose omission costs a
vulnerability.

## Worked examples, from FR-002's ten

These are the evidence FR-010 keeps out of the fragment. They live here, and
`system`'s memory will carry the shorter version.

| Statement                                                     | Test says | Where  |
| ------------------------------------------------------------- | --------- | ------ |
| One endpoint never both creates and updates                   | rule      | repo   |
| Why a combined endpoint destroys 404's meaning                | reasoning | design |
| A secret reaches a command through stdin, never an argument   | rule      | repo   |
| That arguments are logged and appear in the process table     | reasoning | design |
| Update when absent is an error, create when present is not    | rule      | repo   |
| Why the asymmetry: the caller asserted a thing exists         | reasoning | design |
| A permission absent from the role map reaches nobody          | rule      | repo   |
| That `ResolvePermissions` returns early on direct permissions | reasoning | design |
| Ten minutes is a ceiling on any command                       | rule      | repo   |
| That a caller can ask for less and cannot ask for more        | reasoning | design |

The pattern in every row: the rule is what to do, the reasoning is what the
system does. A contributor needs the first to be correct and the second to be
confident.

## What changes in each file

| File                                          | Change                                           |
| --------------------------------------------- | ------------------------------------------------ |
| `.charter/fragments/global/documentation.md`  | one paragraph, third position, 14 lines to 22    |
| seven `constitution.md`                       | recomposed, the paragraph appears in each        |
| `system/.specify/memory/spec.md`              | one agreement added: the rule, the test, and why |
| `system/specs/003-rule-and-reasoning/spec.md` | FR-016's constitution count, 6 to 7              |

## State transitions

None. A fragment has no lifecycle; it is composed or it is not. The one thing
worth naming is that composition is the transition: a fragment edited and not
composed binds nothing, and a constitution edited by hand is discarded on the
next compose.
