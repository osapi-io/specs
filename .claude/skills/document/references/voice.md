# The voice

How every document in this repository is written, and every skill that writes
one. Cited rather than restated: if you are about to paraphrase this into a
skill or a page, link here instead.

A plain engineering voice. Engineers want to read and maintain it. It is not an
academic paper, not marketing and not AI prose.

**The engineering is not simplified. The language is.**

## Writing style

- Simple, direct language over jargon. Use the normal engineering term.
- Do **not** oversimplify the technical detail. Keep the architecture,
  constraints, tradeoffs and reasoning intact.
- Be concrete: what it does, why it exists, how it works, and the tradeoffs.
- The reader is an experienced engineer who does not know this system.
- No buzzwords: leverage, robust, seamless, scalable, paradigm, orchestration as
  a synonym for running things, surface as a synonym for API.
- Do not add general statements or obvious best practice.
- Not everything as a numbered list. Prose, diagrams, tables and short lists,
  whichever makes it clearer.
- Technically precise, but not formal without a reason.
- State the decision. Where there is a tradeoff, say what it is and which side
  you took.
- Use concrete examples. Do not explain terms.
- Tight. Every paragraph explains the system, justifies a decision, or clarifies
  a tradeoff.

The test:

> Would a senior engineer actually write this in an internal design doc?

If it reads like an academic paper, write it again. If it reads like
documentation for beginners, write it again. If it reads like text that tries to
sound technical, write it again.

## Sentences follow STE

Each sentence follows ASD-STE100 Simplified Technical English: one word for
one thing, short sentences, the active voice, commands for steps. The
[ste-100 skill](../../ste-100/SKILL.md) holds the rules. This page decides what
a document says; STE decides how each sentence says it, and wins where they
disagree on a sentence.

## The unslop pass is required

After you write, run `unslop` on the full document. It is a necessary edit pass,
not a suggestion.

It removes these things, and keeps the technical meaning:

- AI phrases and too many words
- corporate and academic language
- explanations that occur two times
- false transitions and filler
- too many headings and bullets
- jargon
- prose that is too polished to be natural

Then read the result again and fix anything it bent out of shape. **Do not let a
shorter document lose technical information.**

## The specific tells

**Significance instead of substance.** Do not write "that indirection is the
whole reason the API cannot do the work, and everything below follows from it".
Write what follows: "at-least-once delivery, the idempotency providers owe, two
independent timeouts, a per-host result instead of one answer." A list of the
results is useful. A claim that results exist is not.

**Commentary about the document.** "This section is short because the subsystem
is thin" tells the reader nothing about the system. Cut it.

**Em dashes.** Use a comma or end the sentence. `just check-docs` fails on them.

**Bold labels that restate the line after them.** "**Performance:** performance
improved by..." A bold lead-in that names a thing, with new detail after it, is
correct.

**Hedged numbers.** "roughly 108 fields" invites nobody to check it, and a count
here stayed wrong for weeks behind a tilde. State the number and the command.

**Aphorisms.** "Prose is a lead; the code is the source" sounds like wisdom and
tells you nothing to do. Write the instruction: read the code, then run
something that fails if you are wrong.

## Worked example

Weak:

```
The job system leverages a robust queuing paradigm to facilitate scalable
execution across the fleet. This architectural decision underscores the system's
commitment to reliability.
```

Better:

```
Work reaches a host by being queued, not by being called. The controller writes a
job, announces it, and waits; an agent picks it up and writes a response back.
Everything awkward about the system comes out of that split: at-least-once
delivery, the idempotency providers owe, two independent timeouts, and a per-host
result instead of one answer.
```

Shorter, names the mechanism, and tells you what to expect.
