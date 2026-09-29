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
The corpus itself is Markdown with no compiled artifact.
[Source: specs/002-agent-key-store/plan.md -> "Language/Version"]
[Source: specs/001-provider-contract/plan.md -> "Language/Version"]

**Primary Dependencies**: NATS JetStream KV (`nats-io/nats.go/jetstream`),
`crypto/ed25519`, and the sibling `osapi-io/nats-client`. The corpus itself
depends on nothing at runtime.
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
under `test/integration` behind the `integration` build tag. In the specs
repository, `just test` runs `mdformat --check`, `just-fmt-check`, and
`scripts/validate-skills.py` over every `SKILL.md` and the relative links in its
references. [Source: specs/002-agent-key-store/plan.md -> "Testing"]
[Source: specs/001-provider-contract/plan.md -> "Testing"]

**Target Platform**: Linux controller and agents; Darwin for development. The
corpus has no target platform — its readers are contributors and agents.
[Source: specs/002-agent-key-store/plan.md -> "Target Platform"]
[Source: specs/001-provider-contract/plan.md -> "Target Platform"]

**Project Type**: Single Go module — controller, agent and shared packages —
alongside a documentation corpus.
[Source: specs/002-agent-key-store/plan.md -> "Project Type"]
[Source: specs/001-provider-contract/plan.md -> "Project Type"]

**Performance Goals**: Verification adds one KV read per verified message on the
controller. Agents heartbeat every 10s and jobs are human-triggered, so the added
load is proportional to fleet size rather than throughput; a per-machine-ID cache
invalidated on acceptance and removal keeps steady-state reads near zero.
[Source: specs/002-agent-key-store/plan.md -> "Performance Goals"]

**Constraints**: No new configuration knob — `ControllerPKI.Enabled`,
`AgentPKI.Enabled` and `ControllerPKI.RotationGracePeriod` already cover
enforcement and rotation. Behaviour with PKI disabled is byte-for-byte unchanged,
and signature verification never fails open. Separately, a rule lives in exactly
one place: two copies drift, and the copy an agent happened to load wins.
[Source: specs/002-agent-key-store/plan.md -> "Constraints"]
[Source: specs/001-provider-contract/plan.md -> "Constraints"]

**Scale/Scope**: Fleets in the hundreds. One stored key per machine ID, plus at
most one superseded key during a rotation grace period. The corpus side is sixteen
requirements covering one layer of one repository.
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

## Configuration

No new configuration. `ControllerPKI.Enabled` governs controller-side enforcement,
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
