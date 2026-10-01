# Research: The embedded UI

**Feature**: `007-the-embedded-ui` | **Date**: 2026-09-29

Phase 0. Four things the specification left to planning, each decided with its
reason.

## Decision 1: the union, and why it needed no adjudication

**Decision**: all three unshared sections are carried into the corpus statement
— `Feature flags` from `ui/docs/architecture.md`, `Configuration` and
`Embedding Mechanism` from the site page. No section is dropped and no copy is
declared authoritative.

**Rationale**: the two copies diverged by *addition*, not by contradiction. Each
gained a section describing something that exists; neither states a rule the
other denies. So there is nothing to adjudicate, and the cost of choosing is
asymmetric and avoidable: taking the newer file loses two sections, taking the
site page loses one, taking both loses nothing.

What would have required a decision is a shared section whose substance
differed. None does — FR-013 records that their shared sections differ in
punctuation and capitalisation, which is what a copy looks like shortly before
it stops agreeing at all. Recording that is the point: a reader who finds the
phrasing difference logged as a conflict would go looking for a resolution
nobody made.

**Alternatives considered**: declaring the newer file authoritative, on the
reasoning that recency tracks accuracy. Rejected — recency tracks *editing*, and
the site page was not edited because nobody remembered it existed, which says
nothing about whether `Configuration` is still true. It is:
`controller.ui.enabled` is in the shipped configuration.

## Decision 2: `ui/docs/architecture.md` becomes a pointer, not a deletion

**Decision**: replace its 263 lines with a pointer of under ten lines to the
corpus.

**Rationale**: every other document in this programme either moves or stays.
This one gets a third disposition because **its location is its value**. A
contributor working in `ui/` looks for architecture beside the code they are
editing, and that instinct is correct — it is why the file was created. An
absent file there sends them to search the repository; a two-line pointer does
not.

The risk this accepts, named rather than hidden: a pointer is a file that can be
edited back into a document. Nothing prevents somebody adding a paragraph to it,
and the programme would then have two statements again. What guards against it
is the pointer saying explicitly that it is a pointer and where the statement
lives — the same device the site's contributor index uses.

**Alternatives considered**: deleting it, consistent with the two site pages the
backfill deleted. Rejected for the reason above. Also considered: leaving it and
citing from it, which is what it already effectively does badly — it holds a
full account *and* the corpus would hold one.

## Decision 3: two requirements came from the code, not the pages

**Decision**: FR-007 and FR-010 state things neither prose document says, and
the plan records where they came from so a later reader can tell them from
transcription.

**Rationale**: the UI decodes its JWT client-side **without verifying it**,
because verification is the server's job. The site page says the UI "decodes the
token client-side" with the parenthetical that it is not verification; a
contributor reading only the client code would reasonably take a decode for a
check, and the corpus states the asymmetry as a rule rather than an aside.

And `/ui/` is in `.coverignore`, so osapi's 100% coverage gate says nothing
about the UI. Neither page mentions it. A contributor who assumed the gate
covered the UI would be wrong in a way nothing in the documentation would
correct.

Both are the discipline `global/verification` asks for, applied to a
documentation feature: the prose was a lead, and the code was the source.

**Alternatives considered**: leaving both out as implementation detail. Rejected
— the first is a security-shaped misreading waiting to happen, and the second
changes what a contributor believes their tests prove.

## Decision 4: the corpus statement is `spec.md`, and the skill gains nothing

**Decision**: no new corpus subject file and no new `add-a-domain` reference.
The statement is this feature's `spec.md`, archived into memory like every other
feature's.

**Rationale**: the backfill's two subjects each produced a skill citation
because a contributor adding a domain reaches job delivery and domain
construction on the way. A domain's UI work is not part of adding a domain today
— no domain has UI work, and `grep` for a UI step in the skill's references
returns nothing. FR-017 therefore adds nothing, and `global/correction` is the
reason: a rule invented to fill out a template is noise, and a citation for work
nobody does is that rule.

If UI work becomes part of adding a domain, the citation is added then, by the
change that makes it true.

**Alternatives considered**: a `references/ui.md` in the skill, for symmetry
with the other layers. Rejected as symmetry for its own sake.

## What was verified before writing any requirement

| Claim                                                             | Verified by                                                        | Result                                         |
| ----------------------------------------------------------------- | ------------------------------------------------------------------ | ---------------------------------------------- |
| The SPA is embedded in the binary                                 | `ui/embed.go` exists                                               | Confirmed                                      |
| It shares the API's port                                          | the site page, and `controller.api.port` in configuration          | Confirmed                                      |
| `controller.ui.enabled` disables it, default true                 | the shipped `configs/osapi.yaml` and the page's example            | Confirmed                                      |
| Four component kinds                                              | `ui/src/components/{ui,domain,layout}/` and `ui/src/hooks/`        | Confirmed                                      |
| The client is generated from the same specification as the Go SDK | orval in the UI, `pkg/sdk/client/gen` for Go                       | Confirmed                                      |
| `/ui/` is excluded from coverage                                  | `.coverignore` line 5                                              | Confirmed — **stated in neither page**         |
| The UI does not verify the token                                  | the page's parenthetical, read against the client                  | Confirmed — **stated as an aside, not a rule** |
| 464 UI source files                                               | `find ui/src -type f \( -name '*.tsx' -o -name '*.ts' \) \| wc -l` | Confirmed                                      |
| The two copies diverged                                           | `git log -1 --format=%cs` on each, and their heading sets          | Confirmed — recorded in 006's FR-019           |
