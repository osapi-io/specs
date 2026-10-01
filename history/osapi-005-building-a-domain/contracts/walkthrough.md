# Contract: what a walkthrough is, and how it differs from a requirement

**Feature**: `005-building-a-domain` | **Date**: 2026-09-28

003's [citation contract](../../003-corpus-backfill/contracts/citation.md)
records the shape a citation must have, because FR-007 and FR-008 are only
enforceable if a checker can resolve one. This contract records the same kind of
thing for a distinction FR-004 and FR-005 rest on: a sequence stated as a
requirement binds, and a sequence stated as a walkthrough advises. Without a
test for which is which, the two collapse and every step becomes a rule.

## The test

Ask what a reader would call the corpus if a step moved tomorrow.

| If the step moved, the corpus is…                                               | Then it is a… | Where it goes                                          |
| ------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------ |
| **Wrong** — following it produces a build that fails                            | Requirement   | `spec.md`, folded into `.specify/memory/spec.md`       |
| **Dated** — following it produces working code by a route nobody takes any more | Walkthrough   | `data-model.md`, folded into `.specify/memory/plan.md` |

The question is deliberately about the *reader's* verdict rather than the
author's intent. An author knows why they put the steps in that order and will
defend all eight; a reader only discovers the difference by disobeying one.

## Applied

Three orderings are requirements, because each has a tool that fails:

| Ordering                                                     | What fails if it is violated                                              |
| ------------------------------------------------------------ | ------------------------------------------------------------------------- |
| `gen/api.yaml` before `just generate`                        | Generation has nothing to read                                            |
| Generation before the handler                                | The handler implements an interface that does not exist                   |
| `redocly join` before `go generate ./pkg/sdk/client/gen/...` | The SDK generates from a combined specification that lacks the new domain |

Everything else in the eight steps is a walkthrough. Writing the CLI before the
SDK service is unusual and works. Writing the documentation first is unusual and
works. Neither is wrong, so neither is a requirement.

## Why this matters more than it looks

A sequence is the part of a contributor document a reader most needs and the
part most likely to rot, and the two facts pull against each other. Stating all
eight steps as requirements would feel more rigorous and would be worse: every
tooling change would demand a specification amendment in its own pull request,
and the amendments would be about step numbering rather than about rules. That
is the cost FR-005 avoids, and it is a cost this project has already paid once —
`job-architecture.md` carried three numbers that the code had outgrown, and they
were stated with the same confidence as the rules around them.

## What checks it

Nothing automatic, and this contract says so rather than implying a gate exists.
What checks it is review: a requirement in this specification that states a step
ordering must name the tool that enforces it, and a reviewer can ask for that
name. A requirement that cannot name one belongs in the walkthrough.

The SC-001 reading is the indirect check. A reader asked *which of those
orderings is forced?* — the second of the four questions — can only answer it if
the corpus has kept the two kinds apart.
