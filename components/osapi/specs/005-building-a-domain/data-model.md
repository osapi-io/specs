# Data Model: Building a domain

**Feature**: `005-building-a-domain` | **Date**: 2026-09-28

Phase 1. A documentation feature's entities are its pages and the statements
inside them. This file fixes every boundary the implementation would otherwise
decide in a diff: which lines leave, what replaces them, and the walkthrough
FR-005 requires.

## Every page, by line range

### `docs/docs/sidebar/development/adding-an-api-domain.md` — 654 lines

Moves **wholly**. Every section is contributor knowledge; the page has no
operator content. What survives at the address is a new short page, specified
below.

| Section                                  | Lines   | Corpus requirement stating it                        |
| ---------------------------------------- | ------- | ---------------------------------------------------- |
| Cross-Layer Consistency                  | 12–24   | FR-001                                               |
| Step 0: Provider Implementation, opening | 25–37   | FR-008                                               |
| Provider Types                           | 38–67   | Cites 001 — FR-002                                   |
| File Structure                           | 68–98   | FR-006, citing 001                                   |
| Provider Interface                       | 99–115  | Cites 001 — FR-002                                   |
| Idempotency                              | 116–152 | Cites 001 — FR-002                                   |
| Platform-Specific Implementations        | 153–174 | Cites 001 — FR-002                                   |
| Provider Naming Conventions              | 175–244 | Cites 001 — FR-002                                   |
| FactsAware                               | 245–261 | FR-010                                               |
| Agent Wiring                             | 262–302 | FR-009                                               |
| Provider Testing                         | 303–308 | FR-002; testing conventions are `CONTRIBUTING.md`'s  |
| Step 1: OpenAPI + Code Generation        | 309–319 | FR-004, FR-011                                       |
| HTTP Verb Conventions                    | 320–333 | FR-013                                               |
| Validation in OpenAPI Specs              | 334–418 | FR-011, FR-012                                       |
| Step 2: Handler Implementation           | 419–438 | FR-006, FR-011                                       |
| Broadcast Support                        | 439–486 | FR-016, FR-017                                       |
| Step 3: Handler Registration             | 487–529 | FR-018                                               |
| Step 4: Startup Wiring                   | 530–538 | FR-018                                               |
| Step 5: Update SDK                       | 539–583 | FR-019, FR-020                                       |
| SDK method naming                        | 584–590 | FR-019 — **the deferral this names does not exist**  |
| SDK example conventions                  | 591–606 | FR-020                                               |
| Step 6: CLI Commands                     | 607–622 | FR-021                                               |
| Step 7: Documentation                    | 623–646 | FR-001 — the consistency obligation in concrete form |
| Step 8: Verify                           | 647–654 | FR-024 — **incomplete as written**                   |

### `docs/docs/sidebar/architecture/api-guidelines.md` — 61 lines

**Deleted.** All six guidelines move to FR-014 and FR-015. The address becomes a
client-side redirect to the contributor page.

Nothing stays, because nothing here is written for an operator: an operator
calls an endpoint, and the endpoint list lives in the published OpenAPI
reference. What this page holds is how to *choose* a path shape, which is a
decision only somebody adding one makes.

### `docs/docs/sidebar/architecture/principles.md` — 46 lines

**Deleted.** All eight principles move to FR-022, each checked against the
charter per FR-023. The address becomes a client-side redirect to the
contributor page.

003 recorded five. The three it never named — Reliability and Stability, CLI
Parity with API, Least Privilege Mode — are the ones most likely to have been
lost by a transcription, and two of them constrain things no other rule covers.

### `docs/docs/sidebar/architecture/system-architecture.md` — 330 lines → 141

| Lines   | Section                                                                           | Disposition                                                                                                     |
| ------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 1–11    | Frontmatter, title, introduction                                                  | **Stays**, with one sentence of editing so it leads into Health Checks rather than into a removed Component Map |
| 12–40   | Component Map                                                                     | Moves — FR-007                                                                                                  |
| 41–53   | Entry Points                                                                      | Moves — FR-007                                                                                                  |
| 54–174  | Layers: CLI, REST API, Job System, Provider Layer, Agent Lifecycle, Configuration | Moves — FR-007. The Job System subsection cites 004 rather than restating it                                    |
| 175–240 | Health Checks: liveness, readiness, status, CLI access                            | **Stays** — an operator's page                                                                                  |
| 241–266 | Request Flow                                                                      | Moves — FR-008                                                                                                  |
| 267–309 | Security: authentication, authorization, CORS; External Dependencies              | **Stays**                                                                                                       |
| 310–end | Further Reading and link definitions                                              | **Stays, edited** — see below                                                                                   |

**The Further Reading list is a build failure waiting to happen.** It links
`api-guidelines.md` and `principles.md`, both of which this feature deletes.
`just docusaurus-build` fails on a link to a missing page, so the list must lose
those two entries in the same change that deletes the pages. It keeps the
`job-architecture.md` and `CONTRIBUTING.md` entries and gains one to the
contributor page.

## The contributor page that survives

`adding-an-api-domain.md`, rewritten. Roughly 60 lines, three parts, no fourth.

**Part 1 — what adding a domain involves.** Prose, under ten lines. Names the
layers a domain touches and says that a domain is complete when it appears
everywhere an existing domain appears. States that the rules live in the corpus
and the sequence is in the skill. Does **not** restate a rule, list the eight
steps, or explain a mechanism.

**Part 2 — the citation table.** One row per requirement a contributor needs,
each naming the rule and linking to it. The rule's *name*, never its content —
[contracts/citation.md](../003-corpus-backfill/contracts/citation.md) fixes the
form. The link is to this repository on GitHub rather than a relative path,
because the corpus is not part of the published site; that is the one place the
citation contract's "relative, not absolute" property cannot apply, and the page
says so in a sentence so a reader does not read it as an oversight.

**Part 3 — the pointer to the skill.** Two or three lines: `add-a-domain`
carries the sequence and the working examples, it is invoked by name, and it
cites these same requirements. Nothing about how to install it.

What the page must **not** contain: any of the eight steps' contents, any code
block, any table of provider types or naming conventions, or a summary of a
rule. A summary is a second statement, and a second statement is what this
feature exists to end.

## The walkthrough

This is what FR-005 requires stated as a walkthrough rather than as eight
requirements, and [research.md](research.md) Decision 2 says why it lives here:
archival folds this file into `.specify/memory/plan.md`, where the approach
belongs, while FR-004's forced orderings stay in the requirements.

**Forced by tooling** — these three are requirements, not walkthrough, because a
build breaks if they are violated:

1. The domain's `gen/api.yaml` exists before `just generate` runs, because
   generation reads it.
2. Generation runs before the handler is written, because the handler implements
   the generated `StrictServerInterface`.
3. The combined specification is regenerated — `redocly join`, inside
   `just generate` — before `go generate ./pkg/sdk/client/gen/...`, because the
   SDK client generates from the combined file and not from the domain's own.

**Conventional** — the order below is how it is done, and a reader who departs
from it produces working code:

| Step | What it produces                                                | Why here                                                                                                               |
| ---- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| 0    | The provider, under `internal/provider/…`                       | The operation has to exist before anything can call it. Testable alone, which makes it the cheapest place to be wrong. |
| 1    | `gen/api.yaml`, `cfg.yaml`, `generate.go`, then `just generate` | Forced before step 2.                                                                                                  |
| 2    | The handler, one file per endpoint, with its tests              | Implements what step 1 generated.                                                                                      |
| 3    | `handler.go` exporting `Handler()`                              | Separate from step 2 so the middleware wiring is reviewable on its own.                                                |
| 4    | One appended line in `registerControllerHandlers`               | Smallest step; the domain becomes reachable here.                                                                      |
| 5    | The SDK service, four files, plus the example and doc page      | Forced after the combined specification regenerates.                                                                   |
| 6    | The CLI commands                                                | Consumes the SDK, so after it.                                                                                         |
| 7    | The documentation, eight files                                  | Conventionally last because it describes what the previous steps produced.                                             |
| 8    | Verification                                                    | Last by definition.                                                                                                    |

**The trap in step 7 and 8.** Step 7 edits documentation and step 8's commands
do not check it: `docusaurus-fmt-check` and `docusaurus-build` run only in
`just test`. A contributor who follows the sequence exactly can hand in work
that fails continuous integration on the files the previous step told them to
write. FR-024 records this, and the corpus states the gate as `just ready` and
`just test` rather than reproducing step 8's list.

## What the skill holds afterwards

The `add-a-domain` skill is 849 lines across `SKILL.md` and six references.
Afterwards each reference states rule *names* with citations, and the mechanics
live here.

| Reference                | Lines today | What changes                                                                                                                          |
| ------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `references/provider.md` | 127         | Unchanged. It already cites 001 — this is the pattern the backfill copies.                                                            |
| `references/agent.md`    | 124         | Already cites 004 from Subject A. Gains citations for FR-009 and FR-010.                                                              |
| `references/api.md`      | 193         | The largest change: validation, verbs, broadcast and registration become rows citing FR-011 through FR-018.                           |
| `references/sdk.md`      | 122         | The `sdk-standards` deferral at line 6 is **named as unwritten** rather than repeated. Verifiable conventions cite FR-019 and FR-020. |
| `references/cli.md`      | 83          | Becomes rows citing FR-021.                                                                                                           |
| `references/docs.md`     | 60          | Becomes rows citing FR-001's concrete form — step 7's eight files.                                                                    |

## The relationship to what memory already holds

Memory holds three archived features. Every overlap is a citation.

| Content reached here                                                                  | Held by                   | Treatment                                                                   |
| ------------------------------------------------------------------------------------- | ------------------------- | --------------------------------------------------------------------------- |
| Provider types, file structure, the interface, naming, platform variants, idempotency | 001, FR-001–FR-015        | Cited — FR-002                                                              |
| Delivery semantics, the two clocks, the dead letter queue                             | 004, memory FR-040–FR-054 | Cited — FR-003                                                              |
| Job signing, response verification, agent identity                                    | 002                       | Cited — FR-003                                                              |
| Testing conventions                                                                   | osapi's `CONTRIBUTING.md` | Cited, not copied. A rule a repository already states is not restated here. |
| Everything else                                                                       | Nothing yet               | Stated for the first time, with the file cited per 003's FR-011             |
