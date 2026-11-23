# document

Answers "where does this design go, and what does the page look like?". Thus a
new page needs one prompt, not a guess about which of twenty files to edit.

This repository is doc-driven. You design something when you write its page.
Then you build it. Then you correct the page where the build showed an error. It
is the same page all three times. The skill covers the page.

## Install

You install nothing. The skill is in this repository. Each agent that reads
skills finds it when it works from the repository root. The checks it runs need
[mise] and [just].

## Usage

Ask in plain language, or invoke it directly with `/document`.

| Ask                                                   | You get                                                             |
| ----------------------------------------------------- | ------------------------------------------------------------------- |
| "document how job retries work"                       | The right component, the existing page if there is one, and a draft |
| "where does the subject naming convention go?"        | A component page or `ARCHITECTURE.md`, with the reason              |
| "the ten-minute timeout is a ceiling, not a fallback" | The page corrected, with what it said and how you found out         |
| "review permissions.md against the house voice"       | The tells, quoted, with rewrites                                    |

## What it does

There are six steps, in order:

1. Find if the page exists.
2. Put the subject in its location.
3. Find what is true from the code, not from the existing prose.
4. Write it.
5. Link it from the index of the component.
6. Run the checks and `unslop`.

Know the placement test without the skill. Ask if the subject is how one
repository operates, or an agreement that two repositories must keep. The first
is a page under `components/<name>/`. The second goes in `ARCHITECTURE.md`. A
rule for each repository goes in `CONSTITUTION.md`.

[references/voice.md](references/voice.md) carries the writing standard: plain
engineering prose, concrete over abstract, say the tradeoff, and the tells to
avoid.

[just]: https://just.systems
[mise]: https://mise.jdx.dev
