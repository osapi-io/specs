# Data Model: Corpus backfill from the published site

**Feature**: `003-corpus-backfill` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md)

A documentation feature has no schema. What it has instead is a mapping: for
each section of each page, which of two readers it serves, and therefore where
it ends up. This is that mapping, and it is the artifact the implementation
works from.

The entities the specification names — candidate page, subject, citation, reader
— are defined there. What follows is their population.

## Subject A: the job system → `004`

| Section, as it stands                                                                        | Lines   | Destination                                                                                                                                                                                                           |
| -------------------------------------------------------------------------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Overview, Architecture Principles                                                            | 9–27    | Corpus. What the job system is for and the constraints it holds to.                                                                                                                                                   |
| System Components, Core Components, Job Flow                                                 | 28–73   | Corpus.                                                                                                                                                                                                               |
| NATS Configuration: KV buckets, JetStream                                                    | 74–111  | Corpus. Bucket names, TTLs and consumer settings are what a contributor needs and an operator never sets by hand.                                                                                                     |
| Subject Hierarchy, Semantic Routing Rules                                                    | 112–152 | Corpus.                                                                                                                                                                                                               |
| Target Types, Label-Based Routing, Label Limits                                              | 153–212 | **Split.** The rules are corpus; the `_all` / `_any` / label syntax an operator types stays, and already has a home under the usage documentation to cite.                                                            |
| Supported Operations                                                                         | 213–218 | Corpus.                                                                                                                                                                                                               |
| Job Lifecycle: Submission                                                                    | 221–236 | **Split.** The CLI examples stay; the submission mechanics move.                                                                                                                                                      |
| Job Lifecycle: Job States                                                                    | 237–278 | **Split.** The state list and what each means to somebody polling stays on the site. The transition rules and the priority model move.                                                                                |
| Job Lifecycle: Job Polling                                                                   | 279–313 | Site. This is what an operator does.                                                                                                                                                                                  |
| Agent Implementation: Processing Flow, Append-Only Status, Multi-Host, Subscription Patterns | 314–400 | Corpus.                                                                                                                                                                                                               |
| Facts Collection                                                                             | 401–422 | Corpus, with the operator-facing reference already on the features pages cited rather than restated.                                                                                                                  |
| CLI Commands                                                                                 | 436–465 | Site.                                                                                                                                                                                                                 |
| Package Architecture, Separation of Concerns                                                 | 466–495 | Corpus.                                                                                                                                                                                                               |
| Security Considerations, Performance Optimizations                                           | 488–553 | Corpus.                                                                                                                                                                                                               |
| Error Handling                                                                               | 554–600 | Corpus. The newest content on the page: acknowledgement and redelivery, the idempotency obligation, command deadlines and the backstop, what cancelling a request does not reach, and the four per-host row statuses. |
| Monitoring                                                                                   | 601–630 | **Split.** The metrics an operator watches stay; what emits them moves.                                                                                                                                               |

## Subject B: building a domain → `005`

| Source                                                                      | Lines           | Destination                                                                                                                                                                                                                                                                                                                                                                                              |
| --------------------------------------------------------------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `adding-an-api-domain.md`, all sections                                     | 1–654           | Corpus, wholly. Cross-layer consistency, provider types and file structure, the provider interface, the idempotency obligation, platform variants, naming, `FactsAware`, agent wiring, provider testing, the OpenAPI step and code generation, validation in specifications, handler implementation and broadcast support, registration, startup wiring, the SDK step and its conventions, the CLI step. |
| `api-guidelines.md`                                                         | 1–61            | Corpus, folded in: top-level categories, resource-oriented paths, verb mapping, when to split a category, node as top-level resource.                                                                                                                                                                                                                                                                    |
| `principles.md`                                                             | 1–46            | Corpus, folded in — **after** each of the five is checked against `.charter/fragments/global/` and this project's constitution. One already stated there becomes a citation, not a second statement (research Finding 1).                                                                                                                                                                                |
| `system-architecture.md`: Component Map, Entry Points, Layers, Request Flow | 12–174, 241–266 | Corpus, folded in. This is what a contributor reads immediately before the domain instructions.                                                                                                                                                                                                                                                                                                          |

## What stays on the site

| Page                                                           | What remains, and for whom                                                                                                                                                                  |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `architecture/architecture.md`                                 | Unchanged: the three processes, the deployment models, how a request flows. Somebody deciding what to deploy.                                                                               |
| `architecture/system-architecture.md`                          | Health checks — liveness, readiness, status, their endpoints and CLI access — plus authentication, authorization, CORS and external dependencies. Somebody configuring and calling osapi.   |
| `architecture/job-architecture.md`                             | The job states as observed, polling, the CLI command reference, and the metrics worth watching. Somebody running jobs.                                                                      |
| `development/adding-an-api-domain.md`                          | A short page: what adding a domain involves, a citation table into the corpus, a pointer to the `add-a-domain` skill. Its reader is a contributor, so citing is right here — and only here. |
| `architecture/api-guidelines.md`, `architecture/principles.md` | Nothing. Both addresses become client-side redirects to the contributor page above.                                                                                                         |

## The relationship to what memory already holds

`components/osapi/.specify/memory/` holds two archived features: the provider
contract (001) and the agent key store (002). Both subjects overlap it, and the
overlap is a citation rather than a restatement in every case:

| Moved content                                                                     | What memory already states                    | Treatment                                                                                                               |
| --------------------------------------------------------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| Provider types, file structure, the provider interface, naming, platform variants | The provider contract's FR-001 through FR-015 | The corpus statement cites the existing requirement. Subject B does not restate a provider rule that 001 already holds. |
| The idempotency obligation on a provider                                          | 001                                           | Cited.                                                                                                                  |
| Job signing, response verification, agent identity                                | The agent key store (002)                     | Subject A's security section cites 002 rather than describing signing again.                                            |
| Everything else                                                                   | Nothing yet                                   | Stated for the first time, with the code cited per FR-011.                                                              |

This is the same test FR-008 applies to the site: one statement, any number of
citations. Memory is not exempt from it.
