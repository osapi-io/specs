---
name: ste-100
description: Write or rewrite technical documentation in ASD-STE100 Simplified Technical English, the controlled language that makes procedures and descriptions clear to readers whose first language is not English. Covers word choice (one word, one meaning, approved verbs), noun clusters, verb forms and voice, sentence length, procedures, descriptive text and safety instructions, adapted for software docs where commands, flags and identifiers are technical names. Use when asked to write in STE or Simplified Technical English, to make a page clearer for non-native readers, to check a page against STE, or when writing osapi or specs docs once they adopt this voice. Also use to review a sentence, a procedure or a warning for STE.
compatibility: Applies to Markdown in any osapi-io repository. Run the repository's own format and test recipes afterwards through `mise exec -- just`.
license: MIT
metadata:
  author: osapi-io
  source: https://github.com/osapi-io/specs
---

# ASD-STE100 Simplified Technical English

A controlled language: few words, one meaning each, and fixed rules for
sentences. Text in STE reads one way only, for a non-native reader and for
machine translation.

## 1. Classify the text

A **procedure** tells the reader what to do. A **description** says what a
thing is or how it works. A **safety instruction** warns. Each has its own
rules. Thus classify each paragraph before you write it. Never put two kinds in
one paragraph.

## 2. Route

Load only the reference the text needs.

| The text has | Read |
| --- | --- |
| Any words at all: terms, verbs, names, noun clusters | [words.md](references/words.md) |
| Sentences: length, voice, tense, -ing forms, lists | [sentences.md](references/sentences.md) |
| Steps the reader follows | [procedures.md](references/procedures.md) |
| Explanation of how something is or works | [descriptions.md](references/descriptions.md) |
| A warning or a caution | [safety.md](references/safety.md) |
| A request to check, review or score existing text | [checking.md](references/checking.md) |

Writing a whole page means words, sentences, and the one for each kind of text
it holds.

## 3. Report

When you rewrite, give the page, then the terms that you selected: the one name
of each thing and the one verb of each action. When you check, give each
sentence that breaks a rule, the rule and its rewrite, in page order.

## Rules

1. **STE decides sentences; the house voice decides content.** The
   [voice](../document/references/voice.md) still says what a page states, and
   `unslop` still runs. Where they disagree on a sentence, STE wins.
2. **Do not lose engineering to shorten a sentence.** Split it instead.
3. **The dictionary is ASD's.** Its list of approved words is not reproduced
   here. Without it, use the most common word with its first meaning, the same
   way every time.
