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

### Sort by what a document does, not where it sits

The distinction is whether a document constrains a future decision or reports a
present one. A collector document listing 40 fields and their OCSF mappings
describes implementation; rewriting it as requirements would produce 40
requirements nobody would read and that would need editing with every field
change. A done-definition listing the eleven conditions a collector must meet
before it is accepted decides whether work is merged, and belongs in the corpus.

Applying the test per document rather than per directory matters, because the
directories are already mixed. `osapi`'s `docs/sidebar/architecture/` holds six
documents: `principles.md` and `api-guidelines.md` are entirely normative,
`job-architecture.md` opens with principles and then describes 550 lines of
current implementation, and the other three are package maps. Moving the
directory whole is wrong in either direction.

*Alternative considered:* use "binds more than one repository" as the test. It
sorts `principles.md` correctly, because the SDK and UI are generated as a
consequence of it. But it sends gohai's collector methodology to the repository
purely because gohai is its only consumer — even though it is the rule a
collector is rejected for violating. A rule binding one repository is still a
rule.

*Alternative considered:* move all documentation into the corpus so everything
is reviewed through the change process. It would put 189 reference documents
behind a proposal workflow and separate them from the code they describe.

### Delete the existing planning documents

`osapi` has 70 planning documents and `osapi-orchestrator` has 6, spanning
February onward. They duplicate what the change archive is for, they are never
updated once the work lands, and a reader facing both cannot tell which is
current. Several already describe work that was then done differently.

They remain in git history, so nothing is lost that was ever authoritative.
Before removal, they are read once for reasoning worth lifting into a change.

*Alternative considered:* leave them as historical record. This was the original
decision here, and it was wrong: it preserves two homes for the same kind of
document, which is the problem this change exists to fix.

*Alternative considered:* migrate them into the archive. The result would be an
archive of fabricated changes — proposals, tasks, and completion states that
were never written.

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
