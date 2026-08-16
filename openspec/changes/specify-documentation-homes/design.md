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

### One rule was about to be deleted with its only record

Reviewing the 76 planning documents before removal, as section 4 requires, found
seventy that were implementation choreography for shipped work and six that
carried decision rationale. Five of the six describe architecture that the
repository still documents. One does not.

The unified-domain-endpoint plan decided to remove `POST /job` and route all job
creation through domain endpoints. The rule still binds — the only `post:`
remaining on the job API is `/api/job/{id}/retry`, an action on an existing job
rather than a way to create one — but no current document states it. Not
`api-guidelines.md`, not `architecture.md`, not `CLAUDE.md`.

That makes it invisible in a specific way: the rule is expressed as an endpoint
that is *absent*, so nothing a reader opens will mention it, and a contributor
adding a domain has no way to discover the constraint before violating it.

Relocating what the architecture documents say would not have produced this
requirement, because those documents do not say it. It needed its own task, or
deleting the planning directory would have removed the last written record of a
rule still in force.

*Alternative considered:* keep the plan that records it. Rejected — a planning
document is not where a binding rule belongs, and keeping one file to preserve
one sentence reintroduces the directory this change removes.

### An architecture document is not one genre

`osapi` holds three documents named for architecture, and they are three
different things:

| Document                 | Contains                                                    | Reader                            |
| ------------------------ | ----------------------------------------------------------- | --------------------------------- |
| `architecture.md`        | the three processes, deployment models, how a request flows | someone new, or an operator       |
| `system-architecture.md` | component map, entry points, layers, dependencies           | a contributor navigating the code |
| `job-architecture.md`    | routing rules, label limits, job states, package layout     | someone building an operation     |

Only the third governs how new work is built, and it does so from sections
scattered through 561 lines rather than from the block named "Architecture
Principles".

No other repository has a document like these. This is not an organization-wide
category with a naming problem; it is one repository's documents sharing a word.

#### The routing rule proves why extraction matters

`job-architecture.md` states that an operation reaches `jobs.query` or
`jobs.modify` according to its suffix, and lists ten suffixes. The code uses
twenty. `.list` appears ten times and the rule does not classify it. Ten more
verbs — `stop`, `start`, `signal`, `shutdown`, `restart`, `remove`, `reboot`,
`install`, `enable`, `disable` — are unanticipated. Two documented suffixes are
unused.

Nothing enforces the rule: the caller chooses `Query` or `Modify` directly. So
the code outgrew the document, and because a description is not checked against
anything, no one found out. A requirement with scenarios would have failed when
`.list` appeared.

This is the case for decomposing an architecture document into capabilities
stated as the argument would not have made it: not that requirements belong in
the corpus on principle, but that a rule nobody checks stops being true and
keeps being read.

*Alternative considered:* rename the three documents first, so their names match
their genres. Rejected for now — renaming before extraction relabels documents
that still contain requirements, and these are site routes, so the rename costs
external links. It belongs after, when what remains is unambiguously
description.

### The corpus promised something it does not hold

The `specs` README says of `openspec/specs/`:

> What survives is `openspec/specs/` — the current description of how osapi-io
> behaves, kept honest by every change that passes through.

It is not that. Of the six capabilities in the corpus, five govern how work is
done — package layout, coverage targets, continuous integration, labels,
justfile modules, module paths, ignore files, badges. Only `sdk-standards` says
anything about how the software behaves. A reader could learn all forty-five
requirements and know the linting rules without learning that osapi has three
processes or what a provider is.

The gap is an artifact of sequence rather than intent. Every change so far has
been repository standardization, and standardization produces rules about
process. The capabilities queued next — routing, API design, provider semantics,
domain completeness — are about behavior, and the corpus will start to resemble
its own description.

It will never fully match it. Package maps and request flows stay in the
repositories, because writing them as requirements produces a corpus that goes
stale on every refactor — a decision this capability already records.

The README is left as it stands. "The current description of how osapi-io
behaves" is what OpenSpec's own model says `specs/` holds, so the sentence
states the destination correctly and the gap is in the corpus rather than in the
claim. Rewriting it to describe forty-five process rules would have recorded a
temporary state as the permanent intent.

*Alternative considered:* correct the README to say the corpus holds rules. That
was the first draft of this task, and it was wrong. A README that describes what
a directory currently contains, rather than what it is for, stops being true the
moment the next capability lands.

#### An entry point, before there are twenty capabilities

`openspec/` holds six capability directories and eleven archived changes, and
nothing that says where to start. That is survivable at six and is not at
twenty.

The requirement asks for a map rather than a summary: naming each capability and
what it covers, saying what the corpus is, and pointing at the archive for
reasoning. A summary would restate the requirements and drift from them; a map
stays true as long as the names do.

*Alternative considered:* generate the entry point from the capability files.
Rejected — the useful part is the sentence explaining what a capability is for
and when to reach for it, which is not derivable from a list of `SHALL`
statements.

#### Purpose sections carry the orientation

The second requirement follows from the same problem. A capability opening with
its first requirement teaches a reader who already knows the domain and no one
else. Asking the `## Purpose` to state what the capability governs, and why that
ground needs governing, is what makes the corpus readable rather than only
searchable.

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
2. `osapi` and `osapi-orchestrator` remove `docs/plans/`. The documents remain
   in git history.

No document is moved into the corpus.

## Open Questions

- Is anything in the 76 planning documents worth lifting into a change before
  they are removed? They have not been read as part of this audit.
- `gohai`'s `adding-a-collector.md` and `ocsf-validation.md` are how-to guides
  that `CONTRIBUTING.md` points at. Is that the right split, or should short
  guides live in `CONTRIBUTING.md` directly?

### osapi's CLAUDE.md is the largest mixed document

Its 917 lines contain both kinds in alternating blocks. Seven sections are
labelled MANDATORY and read as requirements: every domain must appear in all the
same places as an existing one; provider mutations must be idempotent with a
stated truth table; every node-targeted operation must support broadcast and
return `hostname` and `error` on each result; mutable domains must separate
`POST` from `PUT`; every endpoint taking user input must carry validation tags,
a handler call, a 400 response, and RBAC wiring tests; SDK methods must not
stutter; all function signatures must be multi-line.

Interleaved with them is procedure — an eight-step walkthrough for adding a
domain, with file layouts and code samples — and description of what the
packages currently contain. The procedure and the description stay; the rules do
not, because they decide whether a contribution is accepted and nothing outside
this file records them.

Three of the rules bind repositories that cannot see the file. The SDK
guidelines govern `pkg/sdk`'s public surface, and `osapi-orchestrator` is a
consumer of it — the document even instructs consumers not to import `gen`,
which is an instruction to a different repository.

The same 917 lines also restate branching, commit messages, linting, and test
conventions that `development.md` and `testing.md` already state, in three
places with no pointer between them. That has to be resolved before the root
`CONTRIBUTING.md` is written, or the conversion picks one of three and silently
drops the others.

*Alternative considered:* convert `CLAUDE.md` to a pointer first and sort the
content afterwards. The conversion is what forces the decision about each block,
so deferring it means writing a `CONTRIBUTING.md` that has to be rewritten.
