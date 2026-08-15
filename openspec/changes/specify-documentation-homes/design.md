## Context

See proposal.md - Why.

What each repository's `docs/` actually holds:

| Repository           | Contents                                                                                            |
| -------------------- | --------------------------------------------------------------------------------------------------- |
| `gohai`              | `collectors/` (64), `adding-a-collector.md`, `methodology.md`, `ocsf-validation.md`                 |
| `osapi-orchestrator` | `operations/` (125), `features/` (14), `plans/` (6)                                                 |
| `nats-client`        | `client/`                                                                                           |
| `nats-server`        | `server/`                                                                                           |
| `osapi`              | Docusaurus site: `architecture/`, `development/`, `features/`, `sdk/`, `usage/`, plus `plans/` (70) |

Sorting that by kind rather than by repository:

| Kind                                             | Where it is               | Where it belongs |
| ------------------------------------------------ | ------------------------- | ---------------- |
| Reference — what each component does             | repository                | repository       |
| How-to — adding a component, validating output   | repository                | repository       |
| Design rationale binding one repository          | repository                | repository       |
| User-facing documentation                        | repository                | repository       |
| **Design records — what is being built and why** | **repository and corpus** | **corpus**       |

Only one category is in the wrong place, and it is the one this repository was
created to hold.

## Goals / Non-Goals

**Goals**

- A document has one home, and a reader knows which.
- Design history stops accumulating in two places.

**Non-Goals**

- Moving reference documentation into the corpus. 189 collector and operation
  documents describe implementation; they are not requirements and could not be
  written as ones.
- Migrating the 76 existing planning documents. They are a record of what
  happened.
- Imposing a directory structure. `collectors/` and `operations/` are different
  subjects, not inconsistent naming.

## Decisions

### Only design records move

The distinction is whether a document states what SHALL be true or describes
what is. A collector document listing 40 fields and their OCSF mappings
describes implementation; rewriting it as requirements would produce 40
requirements nobody would read and that would need editing with every field
change.

A design record — proposal, alternatives, decision — is the corpus's entire
purpose. That is the only category that moves.

*Alternative considered:* move all documentation into the corpus so everything
is reviewed through the change process. It would put 189 reference documents
behind a proposal workflow and separate them from the code they describe.

*Alternative considered:* leave design records in repositories and let the
corpus hold only cross-repository standards. That is close to the current state,
and it is why 76 planning documents exist alongside a change archive holding the
same kind of thing.

### Leave existing planning documents in place

`osapi` has 70 planning documents spanning February onward, 1.2 MB. They record
what was planned and, in some cases, what was then done differently. Migrating
them into changes would mean inventing proposals, tasks, and completion states
that were never written.

*Alternative considered:* migrate them. The result would be an archive of
fabricated changes, which is worse than a repository containing its own history.

*Alternative considered:* delete them. They are the only record of decisions
made before this repository existed.

### Require an index, not a structure

Every `docs/` directory is organised differently, and each is organised sensibly
for what it holds. What none has is a way to find out what is there without
opening files.

*Alternative considered:* require a common directory structure. `gohai` has no
operations and `osapi-orchestrator` has no collectors; a shared structure would
mean empty directories in both.

## Risks / Trade-offs

- **"No new planning documents" is unenforceable.** Nothing stops one being
  added. → It becomes a review comment with a rule behind it rather than a
  matter of taste.

- **76 documents are removed from the working tree.** Some may contain reasoning
  that was never captured anywhere else. → They remain in git history; nothing
  is destroyed. Anything worth keeping can be lifted into a change before the
  deletion lands.

- **An index goes stale.** A `docs/README.md` listing directories will drift as
  they change. → It lists what each part covers rather than enumerating files.

## Migration Plan

1. Each repository gains a `docs/README.md` index. `osapi` is exempt — its site
   navigation is the index.
1. `osapi` and `osapi-orchestrator` remove `docs/plans/`. The documents remain
   in git history.

No document is moved into the corpus.

## Open Questions

- Is anything in the 76 planning documents worth lifting into a change before
  they are removed? They have not been read as part of this audit.
- `gohai`'s `adding-a-collector.md` and `ocsf-validation.md` are how-to guides
  that `CONTRIBUTING.md` points at. Is that the right split, or should short
  guides live in `CONTRIBUTING.md` directly?
