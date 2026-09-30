# Feature Specification: The embedded UI

**Feature Branch**: `007-the-embedded-ui`

**Created**: 2026-09-29

**Status**: Draft

**Input**: The twelfth unit of the baseline programme, and the move
[osapi's baseline](../006-osapi-baseline/spec.md) classified. osapi ships an
embedded single-page application, and how it is built is stated in **two places
that have already diverged** — `docs/docs/sidebar/architecture/ui.md` on the
operator's site and `ui/docs/architecture.md` beside the code. Neither is in the
corpus. A third statement replaces both.

## Why this is one feature and not part of the baseline

The baseline classified; this relocates. `system`'s
[002](../../../../system/specs/002-baseline-shape/spec.md) FR-026 and FR-027 put
them in that order and keep them separate, because osapi got it the other way
round the first time: the corpus backfill moved documentation across three
features and none of them wrote the document that says which pages are
contributor-facing. These two UI pages are what that omission cost — they were
never candidates, so nothing examined them.

## What makes this move different from the backfill's

The backfill reconciled a site page against the code. This reconciles **three
statements**, and the third is the one that makes the order matter.

| Statement                              | Lines | Last touched | Holds, that the others do not          |
| -------------------------------------- | ----- | ------------ | -------------------------------------- |
| `docs/docs/sidebar/architecture/ui.md` | 264   | 2026-08-15   | `Configuration`, `Embedding Mechanism` |
| `ui/docs/architecture.md`              | 263   | 2026-09-02   | `Feature flags`                        |
| `development/ui-development.md`        | 200   | —            | the whole of how to develop the UI     |

Relocating only the site page would leave the copy beside the code as the sole
statement by default — and that copy is the one missing `Configuration` and
`Embedding Mechanism`. Doing half of this reaches a worse state than doing none
of it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The UI's architecture is stated once (Priority: P1)

Somebody changing the UI reads how it is built in one place, and what they read
is not contradicted by a second document they did not know existed.

**Why this priority**: two statements exist today and they have diverged. Every
day that holds, the chance grows that somebody reads the stale one.

**Independent Test**: after the change, one statement of the UI's architecture
exists across the corpus, the site and the repository; every other mention is a
citation.

**Acceptance Scenarios**:

1. **Given** the corpus, **When** a contributor asks how the SPA reaches the
   binary, **Then** the embedding mechanism is stated with the file that
   implements it.
2. **Given** the repository, **When** somebody looks for UI architecture beside
   the code, **Then** they find a pointer to the corpus rather than a second
   account.

______________________________________________________________________

### User Story 2 - An operator keeps what they use (Priority: P1)

Somebody running osapi can still turn the UI off, and still find out what each
screen shows and which role sees it.

**Why this priority**: three sections of the site page are an operator's, and a
move that took them would cost a reader their reference to save a contributor a
click.

**Independent Test**: the surviving page answers how to disable the UI, what
each page shows, and what the three built-in roles permit — and reads as a whole
page rather than a remainder.

**Acceptance Scenarios**:

1. **Given** the site after the change, **When** an operator asks how to disable
   the UI, **Then** `controller.ui.enabled` and its default are still there.

______________________________________________________________________

### User Story 3 - The divergence is recorded, not silently resolved (Priority: P2)

Somebody reading the corpus later can tell that two documents disagreed, which
sections each was missing, and which way the disagreement was settled.

**Why this priority**: the Correction principle. A merge that quietly picked a
winner would leave no trace that a rule had been in two places, and the next
reader would have no reason to check.

### Edge Cases

- **A section only one copy has.** Three exist: `Feature flags` in the file
  beside the code, `Configuration` and `Embedding Mechanism` on the site. Each
  is carried forward on its own merits, and the corpus records which copy it
  came from — a union, not a choice of winner.
- **A section both have, worded differently.** Their shared sections agree in
  substance and differ in punctuation and capitalisation. The corpus states the
  substance once; the wording difference is evidence of copying rather than a
  disagreement to resolve.
- **An operator section inside a contributor page.** `ui.md` is a split, not a
  move. This is the shape `system-architecture.md` took: what an operator
  configures and sees stays, how it is built goes.
- **A page that is wholly contributor.** `ui-development.md` is. It moves
  entire, the shape `adding-an-api-domain.md` took, and its address keeps a
  short index.

## Requirements *(mandatory)*

Every requirement is *the corpus MUST state X*. No Go code changes; `ui/` is not
touched except for the documentation file it carries.

### What the UI is, and how it reaches the user

- **FR-001**: The corpus MUST state that osapi ships a single-page application
  embedded in the controller binary, served from the same host and port as the
  REST API, so enabling it adds no network configuration. Evidence:
  `ui/embed.go`, and the `controller.api.port` it shares.
- **FR-002**: The corpus MUST state that the UI is disabled by
  `controller.ui.enabled: false`, that the default is true, and that when
  disabled the controller skips registering the SPA handler and serves only the
  REST API. This is the one rule in the set an **operator** acts on, and it
  stays on the site as well — cited there, stated here.

### How it is built

- **FR-003**: The corpus MUST state the stack at the level of what each part is
  for rather than as a version list: React with TypeScript for the application,
  Vite to build it, Tailwind for styling, React Router for navigation, and orval
  to generate the API client from the same OpenAPI specification the Go SDK
  uses. Versions are evidence and date; the roles do not.
- **FR-004**: The corpus MUST state the four kinds of component and what
  separates them — primitives, domain components, layout, and hooks — because
  that boundary is the one a contributor has to place a new file against.
  Evidence: `ui/src/components/{ui,domain,layout}/` and `ui/src/hooks/`.
- **FR-005**: The corpus MUST state that the UI's API client is **generated from
  the same specification as the Go SDK**, so an endpoint added to a domain
  reaches both, and that a fetch mutator adapts it to the browser. This is the
  fact that makes the UI part of osapi rather than a separate application.
- **FR-006**: The corpus MUST state the embedding mechanism: the built assets
  are compiled into the Go binary, which is why there is no separate deployment.
  Evidence: `ui/embed.go`, `ui/dist/`.
- **FR-007**: The corpus MUST state how the UI authenticates — the same JWT the
  rest of osapi uses — and MUST state the asymmetry plainly: the UI decodes the
  token client-side **without verifying it**, because verification is the
  server's job. A contributor who reads only the client would otherwise take the
  decode for a check.
- **FR-008**: The corpus MUST state that the UI's permission model is osapi's,
  not a second one: three built-in roles and `resource:verb` permissions
  matching the Go model. Where it reaches what those permissions mean, it MUST
  cite rather than restate.

### Developing it

- **FR-009**: The corpus MUST state the UI's development obligations — where the
  dev server runs, how a production build is produced, the component and
  file-naming conventions, and what regenerating the SDK requires — as the
  contract a contributor obeys rather than as a transcript of commands. Commands
  belong in the justfile, and `global/documentation` says a rule a tool enforces
  is not restated as prose.
- **FR-010**: The corpus MUST state that `ui/` is excluded from the coverage
  gate by `.coverignore`, so the UI's correctness rests on its own checks rather
  than on Go coverage. Evidence: `/ui/` in `.coverignore`. A contributor who
  assumed the gate covered it would be wrong in a way nothing would tell them.

### The divergence, recorded

- **FR-011**: The corpus MUST record that the UI's architecture was stated twice
  and that the two copies had diverged before this feature, naming what each
  held that the other did not and when each was last touched. Evidence:
  [006's FR-019](../006-osapi-baseline/spec.md).
- **FR-012**: The corpus MUST state that the three unshared sections were
  carried forward as a **union rather than by choosing a winner**:
  `Feature flags` from the copy beside the code, `Configuration` and
  `Embedding Mechanism` from the site page. Picking the newer file would have
  lost two sections; picking the site page would have lost one.
- **FR-013**: The corpus MUST state that the shared sections agreed in substance
  and differed in punctuation, and that this is evidence of copying rather than
  a disagreement requiring judgement. A reader who finds the phrasing difference
  recorded as a conflict would look for a decision that was never needed.

### What happens to the three documents

- **FR-014**: `docs/docs/sidebar/architecture/ui.md` MUST be **split**:
  `Configuration`, `Pages` and the RBAC model stay and must read as a whole page
  for an operator; the embedding mechanism, application structure, stack,
  component architecture, auth flow and SDK generation go to the corpus. Roughly
  60 lines stay of 264.
- **FR-015**: `development/ui-development.md` MUST move **entire**, its address
  keeping a short contributor index with a citation table — the shape
  `adding-an-api-domain.md` took.
- **FR-016**: `ui/docs/architecture.md` MUST be **replaced by a pointer** to the
  corpus rather than deleted. It sits where a contributor working in `ui/` will
  look first, and an absent file there sends them to search; a two-line pointer
  does not. This is the one place in the programme where a file beside the code
  survives as a pointer, and the reason is that its location is its value.
- **FR-017**: The `add-a-domain` skill MUST NOT gain a UI reference. A domain's
  UI work is not part of adding a domain today, and inventing a citation for
  work nobody does would be the rule invented to fill a template that
  `global/correction` warns about.

### Key Entities

- **Embedded UI**: A single-page application compiled into the controller binary
  and served from the REST API's port.
- **Component kind**: One of four — primitive, domain, layout, hook — the
  boundary a new file is placed against.
- **Generated client**: The UI's API access, produced from the same OpenAPI
  specification as the Go SDK.
- **Divergent copy**: One of two statements of the same architecture, each
  holding a section the other lacked.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who has seen neither UI page answers three questions from
  the corpus alone: how does the UI reach a user's browser, where does a new
  component go, and what does the UI verify about a token? Each would mislead a
  contributor if unanswered — a separate deployment assumed, a file placed
  wrongly, a client-side decode taken for a check.
- **SC-002**: One statement of the UI's architecture exists. `grep` for the
  stack, the component kinds and the embedding across the site, `ui/docs/` and
  the corpus returns the corpus statement and citations, not a second account.
- **SC-003**: The surviving site page answers how to disable the UI, what each
  screen shows, and what the three roles permit, and reads as a whole page.
- **SC-004**: `ui/docs/architecture.md` is a pointer of under ten lines.
- **SC-005**: Both disagreements between the two former copies are recorded with
  what each held, and all three unshared sections survive in the corpus.
- **SC-006**: `just test` in the specs repository, and
  `just docusaurus-fmt-check` with `just docusaurus-build` in osapi.
- **SC-007**: No Go code changes. `git -C osapi diff --stat` touches only
  markdown.

## Assumptions

- The corpus statement merges before the osapi change, the sequence
  [003's research](../003-corpus-backfill/research.md) fixed: corpus first
  leaves a window where both state the rules, and site first leaves one where
  neither does.
- The union of the unshared sections is correct without adjudication. All three
  describe things that exist — feature flags, the enable switch, the embedding —
  so none is a claim the other copy contradicted.
- `ui/`'s own `AI_POLICY.md` is policy rather than architecture and is out of
  scope.
- Counts were measured on `b003df6` in specs and `0cca62060` in osapi. The line
  counts will date; what the sections are will not.
