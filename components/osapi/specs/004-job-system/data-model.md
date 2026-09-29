# Data Model: The job system

**Feature**: `004-job-system` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md)

No schema. What this feature has instead is a correspondence: each requirement
in the specification replaces a passage on the site, and each replaced passage
leaves the page. This is that correspondence, and it is what the osapi change
works from.

## The corpus statement, and what each part of it replaces

| Requirement            | Replaces, in `job-architecture.md`                                                            | Lines            |
| ---------------------- | --------------------------------------------------------------------------------------------- | ---------------- |
| FR-001, FR-002         | Overview, Architecture Principles, Job Flow                                                   | 9–27, 52–73      |
| FR-003, FR-004         | NATS Configuration: KV buckets — the key format                                               | 76–96            |
| FR-005                 | KV buckets — the response bucket                                                              | 76–96            |
| FR-006, FR-007         | Subject Hierarchy, Semantic Routing Rules                                                     | 112–152          |
| FR-008                 | Target Types, Label-Based Routing, Label Limits — the rules, not the syntax an operator types | 153–212          |
| FR-009 through FR-013  | Error Handling — items 1, 2 and 3                                                             | 569–621          |
| FR-014, FR-015         | JetStream Configuration; Error Handling item 4                                                | 97–111, 569–621  |
| FR-016, FR-017, FR-018 | Error Handling — items 9 and 10                                                               | 569–621          |
| FR-019, FR-020         | Job States — the transition rules; Error Handling items 7 and 8                               | 237–278, 569–621 |
| FR-021                 | KV buckets — the TTLs                                                                         | 76–96            |
| FR-022, FR-023         | Security Considerations                                                                       | 501–507          |
| —                      | Agent Implementation: Processing Flow, Append-Only Status, Multi-Host, Subscription Patterns  | 314–413          |
| —                      | Facts Collection                                                                              | 414–435          |
| —                      | Package Architecture, Separation of Concerns                                                  | 458–500          |
| —                      | Performance Optimizations                                                                     | 508–568          |

The last four rows are contributor content the specification does not restate
requirement by requirement: it is description rather than rule. It still leaves
the site, and it is stated in the corpus as the specification's context rather
than as numbered requirements — a rule is something a change can violate, and
"the package layout is like this" is not.

## What the page keeps

| Section                                                       | Lines   | Why an operator needs it              |
| ------------------------------------------------------------- | ------- | ------------------------------------- |
| Job Lifecycle: Submission — the CLI examples                  | 221–236 | How to submit one.                    |
| Job States — the list and what each means to somebody polling | 237–278 | What a status means when they see it. |
| Job Polling                                                   | 279–313 | How to watch it.                      |
| Target Types — the `_all` / `_any` / label syntax             | 153–212 | What to type.                         |
| CLI Commands                                                  | 436–457 | The command reference.                |
| Monitoring — the metrics worth watching                       | 622–630 | What to alert on.                     |

## The three corrections

| What the page states                  | What the corpus states                                                | Where the page's version goes                                                          |
| ------------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Job key `{status}.{uuid}`             | `jobs.{job-id}`, with status events keyed separately (FR-003, FR-004) | Removed. Contributor knowledge.                                                        |
| `MaxDeliver: 3`, `AckWait: 30s`       | Defaults of 5 and 2m, overridable (FR-014)                            | Removed. Contributor knowledge, and the configuration file is the statement of record. |
| TTL 24h for completed and failed jobs | One bucket-wide TTL of 1h (FR-021)                                    | Removed, for the same reason.                                                          |

Nothing corrected stays on the page. Correcting a number in two places is how it
drifts again.

## The skill

| Reference                                         | Section                                              | Becomes                                                                                                                  |
| ------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `.claude/skills/add-a-domain/references/agent.md` | Delivery semantics                                   | A citation table naming FR-009 through FR-015.                                                                           |
| `.claude/skills/add-a-domain/references/agent.md` | Processor, registry registration, platform selection | Unchanged. That is how to wire a domain, not how the job system behaves, and it belongs to `005` if it belongs anywhere. |
