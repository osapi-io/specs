# The voice

How every document in this repository is written, and every skill that writes
one. Cited rather than restated: if you are about to paraphrase this into a
skill or a page, link here instead.

An engineer explaining a system to another engineer who has to work on it.

The test: **would a senior engineer write this in an internal design doc?** If
it reads like a paper, rewrite it. If it reads like documentation written for
beginners, rewrite it. If it reads like something trying to sound technical,
rewrite it.

The guidelines, short form:

- Simple direct language. Normal engineering terms, not fancier synonyms.
- Do not oversimplify. The reader should still get the real tradeoffs,
  constraints and architecture.
- Concrete: what it does, why it exists, how it works, what the tradeoffs are.
- The reader is an experienced engineer who does not know this system.
- No buzzwords unless they earn their place.
- No padding with obvious statements or generic best practice.
- Not every idea as a numbered list. Prose, diagrams, tables, short lists, where
  each is clearest.
- Precise without being formal for its own sake.
- State opinions and decisions. Name the tradeoff and the side you took.
- Concrete examples over explanations of terminology.
- Tight. Every paragraph explains the system, justifies a decision, or clarifies
  a tradeoff.

## What to do

**Plain words.** Use the normal engineering term. "Use" not "leverage", "help"
not "facilitate", "is" not "serves as". If a fancier synonym is clearer, use it;
it rarely is.

**Concrete over abstract.** Name the file, the function, the number. "The
controller waits 30 seconds, set by `controller.api.job_timeout`" beats "the
controller has a configurable timeout".

**Say the tradeoff.** Where there was a real choice, say what it cost. "Two
buckets rather than one means a reader of a result does not walk the status
history; it also means the result's TTL is a separate setting nobody remembers
to set." A decision with no cost stated reads as if there was nothing to decide.

**Keep the real detail.** Simplifying until the tradeoffs disappear is worse
than being dense. The reader is experienced; they are not familiar with this
system.

**Lead with what will bite them.** A rule with a silent failure mode is worth
more than three paragraphs about structure.

## What to avoid

**Significance instead of substance.** Do not write "that indirection is the
whole reason the API cannot do the work, and everything below follows from it".
Write what follows: "at-least-once delivery, the idempotency providers owe, two
independent timeouts, a per-host result instead of one answer." Naming the
consequences is useful; asserting that there are consequences is not.

**Commentary about the document.** "This section is short because the subsystem
is thin" tells the reader nothing about the system. Cut it.

**Buzzwords.** leverage, robust, seamless, scalable, paradigm, holistic,
orchestration as a synonym for "running things", surface as a synonym for "API".

**Em dashes.** Use a comma or end the sentence. `just check-docs` fails on them.

**Bold labels that restate the line after them.** "**Performance:** performance
improved by..." A bold lead-in that names a thing and is followed by new detail
is fine.

**Everything as a numbered list.** Use prose where the ideas connect, a table
where the data is tabular, a list where the items are genuinely parallel. Three
nested lists in a row means the structure is doing the thinking.

**Padding.** Every paragraph explains the system, justifies a decision, or
clarifies a tradeoff. If it does none of those, delete it.

**Hedged numbers.** "roughly 108 fields" invites nobody to check it, and a count
in this repository stayed wrong for weeks behind a tilde. State the number and
the command.

## Worked example

Weak:

> The job system leverages a robust queuing paradigm to facilitate scalable
> execution across the fleet. This architectural decision underscores the
> system's commitment to reliability.

Better:

> Work reaches a host by being queued, not by being called. The controller
> writes a job, announces it, and waits; an agent picks it up and writes a
> response back. Everything awkward about the system comes out of that split:
> at-least-once delivery, the idempotency providers owe, two independent
> timeouts, and a per-host result instead of one answer.

The second one is shorter, names the mechanism, and tells you what to expect.
