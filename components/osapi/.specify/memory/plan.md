# Main Implementation Plan

> **Revision**: 2026-09-26 — Seeded from the provider contract
> (`specs/001-provider-contract`). A documentation feature: no dependencies, no
> modules, no configuration, no routing. That feature's plan was written
> retrospectively to satisfy the archival gate, so what is recorded here is the
> shape the work had rather than a plan that directed it.

> **Revision**: 2026-09-26 — Composed the per-agent public key store
> (`specs/002-agent-key-store`) into the shared fields. This is the first feature
> with code, so Language/Version, Primary Dependencies, Storage, Testing, Target
> Platform, Project Type, Performance Goals, Constraints and Scale/Scope each now
> carry a real value beside the corpus one. No scalar conflicts: the corpus fields
> said "not applicable" where this feature states a value.

> **Revision**: 2026-09-28 — Composed building a domain
> (`specs/005-building-a-domain`): the build walkthrough, the documentation surface
> after both backfill subjects, and the two-repository sequence. No new dependency
> at runtime; `@docusaurus/plugin-client-redirects` added to the site.

> **Revision**: 2026-09-30 — Composed osapi's own baseline
> (`specs/006-osapi-baseline`), which is the frame this plan described a corpus
> backfill for and never described the repository of. Adds the Purpose and Place
> section below, the request path, and what breaks in each direction of the
> dependency graph. No scalar conflicts: every field composed.

> **Revision**: 2026-09-30 — Composed the embedded UI
> (`specs/007-the-embedded-ui`). The UI is the part of osapi this plan had never
> described: Language/Version, Primary Dependencies, Project Type, Testing,
> Constraints and Scale/Scope each now account for it, the structure gains `ui/`, and
> Configuration gains the one knob an operator has over it. No scalar conflicts —
> every field composed, because a plan describing a Go module and a corpus said
> nothing the UI contradicts.

> **Revision**: 2026-09-29 — Recorded two things the move taught rather than planned:
> this repository has **two markdown formatters divided by path**, so the Docusaurus
> gates passing says nothing about `md-fmt-check`, and a document may be a **pointer**
> — a third disposition beside moving and staying, for a file whose location is its
> value.

> **Revision**: 2026-09-28 — Composed the corpus backfill: the citation contract that
> the skill linter enforces, and the two redirected addresses. Its two-repository
> sequence was already here through its second subject, so nothing was restated.

## What osapi Is, and Where It Sits

**First, for the reason `global/baseline` gives**: memory states what the
repository is before it states what was decided about it.

osapi is a controller exposing a REST API and an agent running on each managed
host, shipping together. **Work reaches a host by being queued rather than
called**, which is the one fact that explains why the API cannot simply do the
work: the provider runs on the agent. The path a mutating request takes is
`CLI → SDK → REST API → job client → NATS → agent → provider`.

Six layers, each stated by what it is for: the CLI parses and prints; the REST
API validates and delegates; the job system carries work to a host; a provider
does the work there; the agent lifecycle registers providers and dispatches to
them; configuration is resolved once at startup.

Three kinds of consumer — an operator through the CLI, a program through the Go
SDK at `pkg/sdk/client`, and `osapi-orchestrator` through that same SDK. The
exported surface of `pkg/sdk/client` is the contract; everything under
`internal/` is not.

**Where it sits**: it imports `nats-client` and `nats-server`, and
`osapi-orchestrator` imports it. A change to either NATS repository can break
osapi's transport. A change to osapi's SDK surface breaks the orchestrator —
which pins a pseudo-version commit rather than a tag, so nothing breaks there
until somebody bumps it, **which is why a rename and its bump want to land
together**. It also depends on `osapi-justfiles` for its build, through a
justfile fetch that appears in no `go.mod` and is unpinned.
[Source: specs/006-osapi-baseline/spec.md -> FR-001]
[Source: specs/006-osapi-baseline/spec.md -> FR-006]
[Source: specs/006-osapi-baseline/spec.md -> FR-007]

## Summary

The provider contract is stated in the corpus rather than inferred from whichever
sibling provider a reader opens first. Sixteen requirements, all of the form "the
corpus MUST state X", documenting practice the fourteen node providers and their
categorized siblings already follow.
[Source: specs/001-provider-contract/plan.md -> "Summary"]

The job system is stated there too, on the same terms: how work reaches an agent,
what is guaranteed about delivery and what that obliges an agent to do, and the two
clocks that bound an operation. Roughly 430 lines left the published site's
architecture page, whose remaining 203 are for somebody running jobs rather than
building one, and the `add-a-domain` skill cites the requirements instead of
restating the mechanics.
[Source: specs/004-job-system/plan.md -> "Summary"]

## Technical Context

**Language/Version**: Go, `go 1.26.0` directive, CI builds the floor and stable.
TypeScript for the embedded UI under `ui/src/`, built by Vite. The corpus itself is
Markdown with no compiled artifact.
[Source: specs/002-agent-key-store/plan.md -> "Language/Version"]
[Source: specs/001-provider-contract/plan.md -> "Language/Version"]
[Source: specs/007-the-embedded-ui/spec.md -> FR-003]

**Primary Dependencies**: NATS JetStream KV (`nats-io/nats.go/jetstream`),
`crypto/ed25519`, and the sibling `osapi-io/nats-client`. On the UI side, stated as
what each part is for rather than as versions, because versions date and roles do
not: React with TypeScript for the application, Vite to build it, Tailwind for
styling, React Router for navigation, and orval to generate the API client from the
same combined OpenAPI specification the Go SDK generates from. The corpus itself
depends on nothing at runtime.
[Source: specs/007-the-embedded-ui/spec.md -> FR-003]
[Source: specs/002-agent-key-store/plan.md -> "Primary Dependencies"]
[Source: specs/001-provider-contract/plan.md -> "Primary Dependencies"]

**Storage**: NATS JetStream KV. The enrollment bucket holds pending records under
an `enrollment.` prefix and accepted agents' keys under `accepted.`, so no new
bucket, config field or provisioning step appears. The job system uses three of its
own: `job-queue` for definitions under `jobs.{job-id}` and their append-only status
events, `job-responses` for results, and `agent-facts` for the facts an agent
gathers independently — with one TTL per bucket rather than per status.
[Source: specs/004-job-system/plan.md -> "Storage"]
 Corpus content lives in
`components/osapi/specs/`, `.specify/memory/`, and the skill references that cite
them. [Source: specs/002-agent-key-store/plan.md -> "Storage"]
[Source: specs/001-provider-contract/plan.md -> "Storage"]

**Testing**: In osapi, `testify/suite` table tests with `validateFunc`, generated
mocks only, and `just test` as the gate at 99.9% coverage; integration tests live
under `test/integration` behind the `integration` build tag. **`ui/` is excluded from
that gate** by `/ui/` in `.coverignore`, so the coverage figure says nothing about the
UI and its correctness rests on its own checks.
[Source: specs/007-the-embedded-ui/spec.md -> FR-010] In the specs
repository, `just test` runs `mdformat --check`, `just-fmt-check`, and
`scripts/validate-skills.py` over every `SKILL.md` and the relative links in its
references. [Source: specs/002-agent-key-store/plan.md -> "Testing"]
[Source: specs/001-provider-contract/plan.md -> "Testing"]

**Target Platform**: Linux controller and agents; Darwin for development. The
corpus has no target platform — its readers are contributors and agents.
[Source: specs/002-agent-key-store/plan.md -> "Target Platform"]
[Source: specs/001-provider-contract/plan.md -> "Target Platform"]

**Project Type**: Single Go module — controller, agent and shared packages — with a
React single-page application compiled into the binary, alongside a documentation
corpus. [Source: specs/007-the-embedded-ui/spec.md -> FR-001]
[Source: specs/002-agent-key-store/plan.md -> "Project Type"]
[Source: specs/001-provider-contract/plan.md -> "Project Type"]

**Performance Goals**: Verification adds one KV read per verified message on the
controller. Agents heartbeat every 10s and jobs are human-triggered, so the added
load is proportional to fleet size rather than throughput; a per-machine-ID cache
invalidated on acceptance and removal keeps steady-state reads near zero.
[Source: specs/002-agent-key-store/plan.md -> "Performance Goals"]

**Constraints**: A document keeping its address must read as a whole page afterwards
rather than as a remainder, and no requirement restates what the provider contract,
the job system or building a domain already states — the UI's permission model cites
osapi's rather than repeating it.
[Source: specs/007-the-embedded-ui/plan.md -> "Constraints"]
Separately: no new configuration knob — `ControllerPKI.Enabled`,
`AgentPKI.Enabled` and `ControllerPKI.RotationGracePeriod` already cover
enforcement and rotation. Behaviour with PKI disabled is byte-for-byte unchanged,
and signature verification never fails open. Separately, a rule lives in exactly
one place: two copies drift, and the copy an agent happened to load wins.
[Source: specs/002-agent-key-store/plan.md -> "Constraints"]
[Source: specs/001-provider-contract/plan.md -> "Constraints"]

**Scale/Scope**: Fleets in the hundreds. One stored key per machine ID, plus at
most one superseded key during a rotation grace period. 464 UI source files under
`ui/src/`, by `find ui/src -type f \( -name '*.tsx' -o -name '*.ts' \) | wc -l`. The
corpus side is sixteen requirements covering one layer of one repository.
[Source: specs/007-the-embedded-ui/research.md -> "464 UI source files"]
[Source: specs/002-agent-key-store/plan.md -> "Scale/Scope"]
[Source: specs/001-provider-contract/plan.md -> "Scale/Scope"]

## Project Structure

```text
internal/controller/enrollment/
├── types.go             AcceptedAgent record, AgentKeyStore interface
├── keystore.go          record, look up, remove, rotation grace, cache
├── keystore_adapter.go  adapts the watcher to the job client's lookup
└── accept.go            writes the key on accept, removes it on reject

internal/job/
├── registration.go      canonical bytes an agent signs when registering
└── client/
    ├── types.go         AgentKey, AgentKeyStore, the rejection causes
    ├── signing.go       verifies a response against the stored key
    └── agent.go         ListAgents reports verified and key-stored state

internal/agent/heartbeat.go    signs the registration
internal/validation/target.go  only verified registrations resolve

ui/
├── embed.go             //go:embed dist/* — what puts the SPA in the binary
├── dist/                Vite production build output (generated)
├── docs/architecture.md a pointer to the corpus, per FR-111
└── src/
    ├── components/ui/     primitives — no osapi resource
    ├── components/domain/ one resource each
    ├── components/layout/ the page's chrome
    ├── hooks/             state and data, .ts so they cannot hold markup
    └── sdk/               the generated client and its fetch mutator

components/osapi/specs/001-provider-contract/spec.md    the provider contract
components/osapi/.specify/memory/spec.md                where archival puts it
.claude/skills/add-a-domain/references/provider.md      cites it, per FR-016
```

**Structure Decision**: The key store belongs to the enrollment package, because
acceptance is the only event allowed to write it and enrollment already owns that
moment and the KV handle. Verification callers depend on a narrow lookup interface
declared in the job client, so neither the client nor target resolution imports the
enrollment package wholesale.
[Source: specs/002-agent-key-store/plan.md -> "Structure Decision"]

For the corpus: the rule lives in it and the skill points at it.
FR-016 makes that direction binding rather than conventional, so the skill
reference holds only what the specification does not: where a provider's files
go, what they are called, and the scaffolding to start from.
[Source: specs/001-provider-contract/plan.md -> "Structure Decision"]

## Testing Strategy

`just test` in the specs repository is the gate for corpus work: mdformat over
the markdown, justfile formatting, and the skill validator, which checks each
`SKILL.md` against the Agent Skills specification and resolves every relative
link in its references. A citation into the corpus that does not resolve fails
the build, which is what keeps FR-016's direction enforceable rather than
aspirational.
[Source: specs/001-provider-contract/plan.md -> "Testing"]

Corpus work that moves content off the published site is also gated in osapi:
`just docusaurus-fmt-check` for formatting and `just docusaurus-build`, which fails
on an internal link left pointing at a heading that moved. Those two run in the
repository the pages live in, so a subject's two halves are each checked where they
land.
[Source: specs/004-job-system/plan.md -> "Testing"]

**osapi has two markdown formatters, divided by path.** Prettier formats `docs/**`
through the Docusaurus recipes; mdformat formats everything else, `ui/docs/` included,
through `just md-fmt-check`. A change touching both needs both run, and the Docusaurus
gates passing says nothing about the other — which is how a nine-line pointer passed
review and failed CI.
[Source: specs/007-the-embedded-ui/tasks.md -> T013]

Neither gate catches what matters most about a split: the build fails on a link into
removed content, and says nothing about whether the surviving page reads as a page.
That is review. Nor does either catch a link that still **resolves** while describing
content that has moved — three such sentences survived the UI move's build and were
corrected by reading, not by a gate.
[Source: specs/007-the-embedded-ui/plan.md -> "Testing"]

## Configuration

`controller.ui.enabled` turns the embedded UI off, defaulting to true; when it is
false the controller skips registering the SPA handler and serves only the REST API.
The UI shares `controller.api.port`, so enabling it adds no network configuration.
This is the only setting an operator has over the UI, and the published site states
it as well as the corpus — cited there, stated here.
[Source: specs/007-the-embedded-ui/spec.md -> FR-002]

Otherwise no new configuration. `ControllerPKI.Enabled` governs controller-side enforcement,
`AgentPKI.Enabled` the agent side, and `ControllerPKI.RotationGracePeriod` how long
a replaced agent key keeps verifying. All three already existed and were already
documented as covering PKI enrollment and signing.
[Source: specs/002-agent-key-store/plan.md -> "Constraints"]

## Documentation Surface

Two audiences, split by who is served rather than by where a page sits. The corpus
under `components/osapi/specs/` states how osapi is built, for a contributor or an
agent; the published site under `docs/docs/sidebar/` states how to use it, for an
operator. A rule lives in one of them and is cited from the other, never stated
twice — a citation being a relative link naming a requirement, which
`scripts/validate-skills.py` resolves.

The site does not send an operator to the corpus. A contributor page may cite it,
and the `add-a-domain` skill does; an operator page that answers with "see the
specifications repository" has lost its reader.
[Source: specs/004-job-system/plan.md -> "Constraints"]

Both backfill subjects have landed, so the split is now the site's actual shape.
950 lines of contributor knowledge left `docs/`: the job system page kept its
operator half, the domain page became a 76-line index, the API guidelines and
principles pages were deleted with their addresses redirected, and the system
architecture page kept health checks, authentication, authorization, CORS and
external dependencies while its component map, entry points, layers and request
flow moved.

Two site pages cite the corpus, and both have contributor readers: the domain index
and the SDK development guidelines. Their links are **absolute GitHub addresses**,
because the corpus is a separate repository and is not published as part of the
site — the one place the relative-link rule cannot apply, and the domain index says
so in a note rather than leaving it to look like an oversight.
[Source: specs/005-building-a-domain/plan.md -> "Documentation Surface"]

The UI move adds a third citing page — the UI development index — and a **third
disposition**. Until it, a document either moved or stayed. `ui/docs/architecture.md`
does neither: it is a **pointer**, kept for its location rather than its content,
because a contributor working in `ui/` looks for architecture beside the code and an
absent file there sends them searching. It is the only one in the programme, and the
reason is specific to it rather than a precedent for keeping files.

The risk that disposition accepts, named rather than hidden: a pointer is a file
somebody can edit back into a document. Nothing prevents it except the file saying it
is a pointer and where the statement lives — which is why that sentence is a
requirement rather than a courtesy.
[Source: specs/007-the-embedded-ui/research.md -> "Decision 2"]

After the UI move, **585 more lines** of contributor knowledge have left osapi: the
architecture page went 264 to 82, the development page 200 to 52, and the file beside
the code 263 to 9. Four documents stated the UI's architecture when this started and
one does now. Reproduce from `osapi/` with
`wc -l docs/docs/sidebar/architecture/ui.md docs/docs/sidebar/development/ui-development.md ui/docs/architecture.md`.
[Source: specs/007-the-embedded-ui/plan.md -> "Scale/Scope"]

## Routing & Navigation

`GET /agent` reports `key_stored` and `verified` per agent, so a rollout can be
staged before enforcement is enabled. No new endpoint.
[Source: specs/002-agent-key-store/spec.md -> FR-012]

## Building a Domain: the Walkthrough

Which orderings are obligations and which are convention is stated in the
specification (FR-058) and the reason for the split is that a reader would call the
corpus *wrong* if a forced ordering moved and merely *dated* if a conventional one
did. Three are forced, because a build breaks:

1. The domain's `gen/api.yaml` exists before `just generate` runs, because
   generation reads it.
2. Generation runs before the handler is written, because the handler implements the
   generated `StrictServerInterface`.
3. The combined specification is regenerated — `redocly join`, inside
   `just generate` — before `go generate ./pkg/sdk/client/gen/...`, because the SDK
   client generates from the combined file and not from the domain's own.

The rest is how it is done, and a reader who departs from it produces working code:

| Step | What it produces | Why here |
| --- | --- | --- |
| 0 | The provider, under `internal/provider/…` | The operation must exist before anything can call it, and it is testable alone, which makes it the cheapest place to be wrong. |
| 1 | `gen/api.yaml`, `cfg.yaml`, `generate.go`, then `just generate` | Forced before step 2. |
| 2 | The handler, one file per endpoint, with its tests | Implements what step 1 generated. |
| 3 | `handler.go` exporting `Handler()` | Separate from step 2 so the middleware wiring is reviewable on its own. |
| 4 | One appended line in `registerControllerHandlers` | Smallest step; the domain becomes reachable here. |
| 5 | The SDK service, four files, plus the example and doc page | Forced after the combined specification regenerates. |
| 6 | The CLI commands | Consumes the SDK, so after it. |
| 7 | The documentation, eight files | Describes what the previous steps produced. |
| 8 | Verification | Last by definition. |

**The trap in the last two steps.** Step 7 edits documentation and step 8's
commands do not check it: `docusaurus-fmt-check` and `docusaurus-build` run only in
`just test`. A contributor following the sequence exactly can hand in work that
fails continuous integration on the files the previous step told them to write — so
the gate is `just ready` **and** `just test`, which is FR-078.
[Source: specs/005-building-a-domain/data-model.md -> "The walkthrough"]

## Landing a Corpus Change Across Two Repositories

A backfill subject lands in two pull requests and **the corpus one merges first**.
The two orders fail differently, and only one failure is recoverable by waiting.

Corpus first leaves a window where both the corpus and the site state the same
rules: visible, bounded by the second pull request, and a reader consulting either
gets a correct answer. Site first leaves a window where **neither** does — the page
is gone, the skill's citations point at a corpus that has not merged so `skill-lint`
fails, and a reader at the old address gets a redirect to a page whose citation
table resolves to nothing. Nothing recovers that except merging what should have
gone first.

Archival is third, after both. Running it earlier records intentions as outcomes.
[Source: specs/005-building-a-domain/research.md -> "Decision 1"]

Where the content being moved is stated in **two** places that have diverged, the
order binds harder still, and a further rule applies: **the repository change is one
commit.** Landing half of it leaves the divergent copy as the sole statement, and the
copy left standing is the one missing sections — a worse state than doing none of it,
and one no gate reports.
[Source: specs/007-the-embedded-ui/tasks.md -> "Two repositories, and the order"]

One thing this sequence does not cover, learned by getting it wrong: for a corpus
feature there is **no second corpus pull request**. The statement is `spec.md`, which
merged at stage 1, so the corpus half of the sequence is already done before
implementation starts and its tasks are verification rather than writing. A plan that
schedules a corpus pull request during implementation is describing a step that
cannot happen.
[Source: specs/007-the-embedded-ui/tasks.md -> "A correction to Phase 3"]

## What a Citation Is, and What Checks It

A documentation change exposes no interface. What it has is a convention other work
depends on, and a gate that fails when the convention is broken.

A citation is a **relative markdown link from the citing file to the corpus
requirement**, in a table mapping each rule to the requirement that states it. Three
properties matter:

1. **Relative, not absolute.** `scripts/validate-skills.py` resolves relative links
   from the file's own directory; an absolute URL is checked by nothing, which makes
   it a restatement with extra steps. **From a skill's reference file the depth is
   four `../` levels** — `references/` → the skill → `skills/` → `.claude/` → the
   repository root. Three lands in `.claude/` and resolves to nothing; the gate says
   so by name, which is how this note came to be written.
2. **Named to a requirement, not to a document.** "See the job system specification"
   is a pointer; "FR-007" is a citation. Only the second tells a reader whether what
   they are looking for is there.
3. **One statement per rule.** The citing file states the rule's *name* and where it
   lives. It does not restate the rule.

**The one sanctioned exception to property 1**: a page on the published site cannot
link relatively into the corpus, because the corpus is a separate repository and is
not published as part of the site. Those two pages use absolute GitHub addresses and
say so in a note, rather than leaving the departure to look like an oversight.

`just skill-lint` is what fails when a citation stops resolving. That is what makes
the one-statement rule enforceable rather than aspirational.
[Source: specs/003-corpus-backfill/contracts/citation.md]

## Redirected Addresses

Two site addresses now resolve by client-side redirect rather than by a page, through
`@docusaurus/plugin-client-redirects`:

| Address | Redirects to |
| --- | --- |
| `/sidebar/architecture/api-guidelines` | `/sidebar/development/adding-an-api-domain` |
| `/sidebar/architecture/principles` | the same contributor index |

Both pages were wholly contributor knowledge sitting in an operator's navigation, so
neither kept a half. The redirect is what satisfies the rule that no address which
resolved before a move fails after it.
[Source: specs/003-corpus-backfill/plan.md -> "Redirects"]
