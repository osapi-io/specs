# document

Answers "where does this design go, and what does the page look like?" so writing
one is a prompt rather than a guess about which of twenty files to edit.

This repository is doc-driven: you design something by writing its page, build it,
then correct the page where building proved it wrong. Same page all three times.
The skill covers the writing.

## Install

Nothing to install. The skill lives in this repository and any skills-aware agent
working from the repository root finds it. The checks it runs need [mise] and
[just].

## Usage

Ask in plain language, or invoke it directly with `/document`.

| Ask                                              | You get                                                                 |
| ------------------------------------------------ | ----------------------------------------------------------------------- |
| "document how job retries work"                   | The right component, the existing page if there is one, and a draft      |
| "where does the subject naming convention go?"   | A component page or `ARCHITECTURE.md`, with the reason                   |
| "the ten-minute timeout is a ceiling, not a fallback" | The page corrected, with what it said and how you found out         |
| "review permissions.md against the house voice"   | The tells, quoted, with rewrites                                        |

## What it does

Six steps, in order: find whether the page exists, place the subject, work out
what is true from the code rather than from existing prose, write it, link it from
the component's index, then run the checks and `unslop`.

The placement test is the one worth knowing without the skill: ask whether the
subject is how one repository behaves, or an agreement two of them must both keep.
The first is a page under `components/<name>/`, the second belongs in
`ARCHITECTURE.md`, and a rule every repository follows belongs in
`CONSTITUTION.md`.

[VOICE.md](../../../VOICE.md) carries the writing standard: plain
engineering prose, concrete over abstract, say the tradeoff, and the tells to
avoid.

[just]: https://just.systems
[mise]: https://mise.jdx.dev
