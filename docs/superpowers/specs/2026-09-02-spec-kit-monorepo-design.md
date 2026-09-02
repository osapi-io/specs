# Restructure `specs` as a Spec Kit monorepo

> This design document is a bootstrap artifact. It records the one change that
> installs the workflow; every change after it goes through Spec Kit.

## Context

This repository holds an OpenSpec corpus of 8 capabilities and 67 requirements.
None describe what any component does. Roughly 55 are mechanically checkable
(badge rows, ignore baselines, file presence, workflow naming); ~10 are judgment
calls that now live in the five Go repositories' `CONTRIBUTING.md` files. One is
a live contradiction: `code-architecture` requires 100% coverage while `osapi`
declares 99.9%.

Fourteen archived changes were read in full before this design. Every one is
repository hygiene. A grep across all of them for job routing, JetStream,
subject hierarchy, and label selectors returns nothing. Two facts were salvaged:
the cross-repo dependency graph, and why `osapi`'s gate is 99.9% (nine
unreachable guard statements, not missing tests). Salvaging caught the archive
recording `osapi`'s module path as `github.com/retr0h/osapi`, renamed in #446 —
stale the moment it was written.

What is wanted instead: evergreen documentation stating why each component is
built the way it is, so a feature starts from that knowledge and folds its
discoveries back afterwards.

## Goals / Non-Goals

**Goals:**

- One checkout carries the whole system's context.
- Knowledge accumulates rather than being archived per change.
- Structure is Spec Kit's own. Nothing invented.

**Non-Goals:**

- Merging the seven code repositories. Code stays where it is.
- Moving `osapi`'s 30 feature documents (~4,163 lines). Those are user-facing
  reference and keep publishing from the Docusaurus site.
- Preserving the OpenSpec corpus or its change archive.

## Decisions

### Spec Kit's structure, with nothing added

`specify init` creates exactly `.specify/` and `specs/`. It prescribes no
documentation directory, and its monorepo example uses `apps/` and `packages/`,
which are JavaScript conventions rather than Spec Kit's.

Evergreen knowledge lives in `.specify/memory/`, which is what the `archive`
extension consolidates into. A separate documentation tree would be a second
home for the same thing.

*Alternative: a hand-written `docs/domains/` tree beside the projects.*
Rejected. It invents structure the tooling has no knowledge of, and splits
evergreen content between a directory nothing maintains and a memory directory
an extension does.

### One project per repository, plus `system`

Spec Kit is directory-scoped: a monorepo holds several independent projects,
each with its own `.specify/`, `specs/`, constitution, and feature numbering.
Root resolution prefers the nearest `.specify/`.

```
specs/
├── .charter/                     Charter registry, shared fragments
├── osapi/                        .specify/ + specs/
├── gohai/                        .specify/ + specs/
├── nats-client/                  .specify/ + specs/
├── nats-server/                  .specify/ + specs/
├── osapi-orchestrator/           .specify/ + specs/
├── osapi-justfiles/              .specify/ + specs/
└── system/                       .specify/ + specs/
```

`system` is a project like any other. Its subject is how the repositories
relate rather than one codebase, so the dependency graph and any domain
spanning repositories consolidate into its memory.

*Alternative: one project for the whole organization.* Rejected. Every
feature's knowledge would consolidate into a single memory document, so
`osapi` job routing would sit beside `gohai` collectors.

*Alternative: a project per domain rather than per repository.* Rejected.
Domains are a documentation axis and features are a repository axis. A feature
almost always lands in one repository, so repository granularity is what the
workflow needs; domain knowledge is carried by memory within each project.

### Constitutions composed from one registry

Seven projects need the same rules with explicit per-project variance. Charter
composes each constitution from a shared registry:

```
.charter/
├── manifest.yml                  version, name, mandatory and recommended
├── fragments/
│   ├── global/                   rules every project holds
│   └── languages/                Go-specific rules
└── sub-constitutions/            per-package scoping, `_` is a path separator
```

Composition marks each section with a typed comment (`[F]` fragment, `[SC]`
registry sub-constitution, `[PS]` project-specific), so a shared rule can be
updated in the registry and recomposed without losing local content.

*Alternative: seven independent constitutions.* Rejected — it is the
duplication this repository exists to prevent, and the failure Charter names
in its own problem statement.

### Constitution articles come from recorded failures

The existing-projects guide is explicit: use principles already true for the
repository, evidenced by its README, contribution guide, and CI configuration.
"Do not invent standards merely to fill the constitution template — unrealistic
rules create noise instead of useful constraints."

The corpus violated this. Its 100% coverage rule was invented to fill a
template and `osapi` never satisfied it.

Five candidate articles, each earned by a failure this repository has already
had:

1. A repository states in full the conventions binding it. A pointer to another
   repository is not a statement. *(A repository shipped citing a capability
   that did not yet exist.)*
2. A rule a tool enforces is never restated as prose. *(Five repositories
   listed the linter set wrongly, beside the configuration that was right.)*
3. A claim about the codebase is measured, not inspected. *(Four wrong verdicts
   on test doubles; a coverage-diff settled it.)*
4. Both provisioning paths resolve to the same version. *(Every contributor
   built on Go 1.25.7 while continuous integration used 1.26.6.)*
5. When applying a rule disproves it, work stops and the rule is corrected
   first. *(One requirement was wrong four times.)*

### Extensions selected on evidence

| Extension | Role | Signal |
| --- | --- | --- |
| `archive` | Consolidates merged features into `.specify/memory/` | 28 stars, updated within the week; fold/separate/contradiction verdicts, `[Source: …]` traceability, bounded inputs |
| `charter` | Composes constitutions from the shared registry | 7 stars, active |
| `docguard` | Validates documentation against code | 27 stars, most recently updated in the catalog |

Rejected: **Blueprint Index** — the closest description, zero stars.
**Brownfield Bootstrap** — 62 stars but five months stale. **Repository
Index**, **dotdog**, **arch-governance** — low signal.

The catalog states that maintainers verify formatting only and do not review,
audit, endorse, or support extension code. Each selected extension is read
before it is depended on.

### Baselining goes through the workflow

`osapi`'s six architecture documents (1,466 lines) do not arrive as a
hand-written tree. They arrive as a feature whose deliverable is the inventory,
which the existing-projects guide permits, and `archive` folds the result into
`osapi/.specify/memory/`.

*Alternative: copy the files in directly.* Rejected. It would seed memory with
content no workflow produced and no `[Source: …]` reference points at.

## Risks / Trade-offs

- **`/speckit.implement` has no code to write here.** → The workflow's
  implementation phase runs in the code repository; this monorepo holds the
  specification and memory. The first real feature will show whether that seam
  is workable, which is why one project is initialized and exercised before the
  other six.

- **Seven `specify init` runs each write agent command files.** → Spec Kit's
  monorepo guide treats this as normal; root resolution finds the nearest
  `.specify/`. The repetition is visible but not harmful.

- **Three selected extensions are community code, unaudited by Spec Kit
  maintainers.** → Each is read before use, and `archive` is the only one the
  workflow depends on. The other two are additive.

- **Deleting the corpus dangles references in six repositories.** → Eight files
  cite `osapi-io/specs`, and `osapi-justfiles` cites `openspec/specs/justfiles/`
  by path. Those are updated in the same change as the deletion, not after.

- **The salvaged facts are claims, not truths.** → One was already stale when
  read. They enter `system`'s memory through the workflow, where a
  `[Source: …]` reference records what they came from.
