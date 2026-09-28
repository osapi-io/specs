# Research: Corpus backfill from the published site

**Feature**: `003-corpus-backfill` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md)

The specification defers two decisions to planning: which subjects the moved
content becomes (FR-004), and what happens to each page's address (FR-006). Both
need the pages read in full. This records the answers, and three findings the
reading produced that the specification did not anticipate.

## Decision 1: the classification of each candidate page

FR-001 requires each page classified as moving wholly, splitting, or staying,
justified by who reads it. The six pages, read in full:

| Page                                  | Lines | Classification       | Reader, and why                                                                                                                                                                                                           |
| ------------------------------------- | ----- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `development/adding-an-api-domain.md` | 654   | moves wholly         | Every section instructs somebody changing the code: provider types, file layout, the idempotency obligation, agent wiring, OpenAPI generation, handler and registration, SDK and CLI. Nothing tells an operator anything. |
| `architecture/job-architecture.md`    | 630   | splits               | The mechanics — subjects, streams, consumers, KV buckets, delivery, error handling — are for a contributor. The job states an operator polls and the CLI command reference are for an operator.                           |
| `architecture/system-architecture.md` | 330   | splits               | The component map, the layer descriptions and the request flow are for a contributor. Health checks, their endpoints and CLI access, authentication, authorization and CORS are what an operator configures and calls.    |
| `architecture/architecture.md`        | 204   | stays                | The three processes, the single-host and multi-host deployment models, and how a request flows are what somebody deciding what to deploy needs. Its "Deep Dives" links change; its content does not.                      |
| `architecture/api-guidelines.md`      | 61    | moves wholly, folded | Path shape, verb mapping and where a new domain sits are rules for whoever adds one. Too small for a specification of its own, per FR-004.                                                                                |
| `architecture/principles.md`          | 46    | moves wholly, folded | Design principles constrain how osapi is built. Also too small to stand alone, and partly already stated elsewhere — see Finding 1.                                                                                       |

**Rationale**: the test is who is served, not where the page sits. Two of the
six pages under `architecture/` are operator-facing in part or in whole, which
is why the specification's own Assumptions expected at least one "stays" or
"splits".

**Alternatives considered**: moving all six wholly, which is what the line
counts suggest and what a reader of the directory names would guess. Rejected
because it would take the health check endpoints, the CORS configuration and the
deployment models with it — the content an operator opens the site for.

## Decision 2: the subjects

FR-004 requires grouping by subject rather than by page, each large enough to
warrant a specification. Two subjects, which become the next two feature
specifications in this project:

### Subject A — the job system (becomes `004`)

From `job-architecture.md`: the architecture principles, the component map, the
NATS configuration (KV buckets, JetStream), the subject hierarchy and semantic
routing, target types and label routing, the job lifecycle as the system runs
it, the agent's processing flow and append-only status model, multi-host
processing, and the error handling rules — acknowledgement, redelivery and the
idempotency obligation, command deadlines, what cancellation does and does not
reach, and the four per-host row statuses.

First, per FR-005: it is the largest body of contributor knowledge on the site,
and the `add-a-domain` skill leans on it most.

### Subject B — building a domain (becomes `005`)

From `adding-an-api-domain.md` wholly; from `api-guidelines.md` the path, verb
and placement rules; from `principles.md` what survives Finding 1; and from
`system-architecture.md` the component map, the layer descriptions and the
request flow, which are what a contributor needs before touching any of it.

**Alternatives considered**: one specification per page, which the specification
already rejects; and four subjects, splitting the API surface conventions and
the layer map into their own. Rejected because a 61-line and a 46-line
specification are the "specifications nobody reads" the spec's Edge Cases name,
and because the layer map exists to be read immediately before the domain
instructions.

## Decision 3: what happens to each address

FR-006 requires a per-page answer, and FR-012 forbids sending an operator to the
corpus.

| Address                               | What it keeps                                                                                                                                   | Why this and not the other                                                                                                                                                                       |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `development/adding-an-api-domain.md` | A short contributor page: what adding a domain involves, a citation table to the corpus requirements, and a pointer to the `add-a-domain` skill | Its reader is a contributor, so citing the corpus is right for this page. A redirect would strand the reader arriving from an issue or a bookmark with no explanation of where the content went. |
| `architecture/job-architecture.md`    | An operator page: the job states, polling, and the CLI command reference, keeping the title                                                     | Something real remains, so the address keeps a page rather than a redirect.                                                                                                                      |
| `architecture/system-architecture.md` | An operator page: health checks and their endpoints, authentication, authorization, CORS, external dependencies                                 | Same reason. The layer map leaves; what an operator configures stays.                                                                                                                            |
| `architecture/architecture.md`        | Unchanged                                                                                                                                       | Nothing moves out of it.                                                                                                                                                                         |
| `architecture/api-guidelines.md`      | A client-side redirect to the surviving contributor page                                                                                        | Nothing operator-facing remains, and a 61-line stub beside a 46-line stub is clutter that answers nobody.                                                                                        |
| `architecture/principles.md`          | A client-side redirect to the same page                                                                                                         | Same.                                                                                                                                                                                            |

Two redirects require `@docusaurus/plugin-client-redirects`, which the site does
not currently install: `docusaurus.config.ts` declares only the OpenAPI plugin.
Adding it is in scope for the page change, and is the only dependency this
feature introduces.

**Alternatives considered**: deleting both files outright. Rejected by FR-006 —
their addresses resolve today, they are linked from the architecture sidebar,
and a 404 is invisible to whoever caused it.

## Finding 1: some principles are already stated as org-wide rules

`principles.md` states five design principles. Two of them are already rules in
the charter that every osapi-io repository composes: "Automation through
OpenAPI" overlaps `global/tooling`'s statement about generated artifacts, and
"Simplicity and Minimalism" overlaps what `global/documentation` says about
restating.

FR-008 requires one statement of each rule, which makes this a classification
problem rather than a moving problem: a principle already stated in the charter
becomes a citation, not a second statement in the corpus. Each of the five is
checked against `.charter/fragments/global/` and against this project's own
constitution before it is written anywhere.

## Finding 2: the job system page has grown since the specification was written

`job-architecture.md` is 630 lines, not the 603 the specification records. The
difference is an Error Handling section added while closing the September
review: command deadlines and the backstop, why cancelling an API request does
not stop a running agent operation, and the four per-host row statuses including
`timeout`.

This is the newest and most precise contributor knowledge on the page, it cites
the code it describes, and it is exactly what Subject A is for. The line count
in the specification's Assumptions is stale by 27 lines; the classification it
supports is not.

## Finding 3: moving a subject cannot be one change

FR-010 requires each subject to move in a single change, so no reader finds two
disagreeing statements. The corpus lives in the specifications repository and
the pages live in osapi, and `main` is protected in both: one change cannot span
them.

What is achievable, and what this plan commits to:

1. The corpus specification merges first, in the specifications repository. It
   is the statement of record, and at this moment the site still holds the same
   text — two copies, saying the same thing, because one was written from the
   other.
2. The osapi change follows, in one pull request per subject: it removes or
   rewrites the pages, adds the redirects, and updates the skills to cite.

The window between them holds two identical statements and no citation pointing
at either, so no reader is sent somewhere that disagrees with where they are.
The risk is not divergence but abandonment: a corpus specification merged
without its site change leaves the duplication permanent. The task list
therefore carries the site change as a blocking task of the same subject, not as
follow-up work.

**Alternatives considered**: moving the page in the same pull request that adds
the corpus specification, which is impossible across repositories; and writing
the corpus specification only after the page is deleted, which loses the content
if the second change stalls.
