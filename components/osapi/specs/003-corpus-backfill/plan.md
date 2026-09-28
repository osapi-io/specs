# Implementation Plan: Corpus backfill from the published site

**Branch**: `003-corpus-backfill` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md)

**Input**: Feature specification from
`components/osapi/specs/003-corpus-backfill/spec.md`

## Summary

1,898 lines of the published site tell a contributor or an agent how osapi is
built rather than telling an operator how to use it. This moves that content
into the corpus as two subjects — the job system, then building a domain —
leaves every address resolving, and replaces each restatement in the
`add-a-domain` skill with a citation.

The approach is the one the provider contract established: the corpus states the
rule, everything else cites it, and a citation whose target does not exist fails
the build. What that feature proved on one reference — 171 lines down to 127 —
this applies to the six pages that hold the rest.

Nothing in osapi's Go source changes. What changes is where prose lives, which
of two readers each page serves, and whether a rule is stated once or twice.

## Technical Context

**Language/Version**: None. Markdown in two repositories: the corpus under
`components/osapi/`, the site under `docs/docs/sidebar/` in osapi.

**Primary Dependencies**: `@docusaurus/plugin-client-redirects`, which osapi's
site does not yet install and which two of the six pages need. It is the only
dependency this feature adds.

**Storage**: N/A.

**Testing**: The gates that already run. In this repository, `just test` runs
mdformat and `scripts/validate-skills.py`, which resolves every relative link —
so a citation into the corpus that does not resolve fails the build. In osapi,
`just docusaurus-fmt-check` runs Prettier over the site, and the site build
fails on a broken internal link.

**Target Platform**: The published documentation site and the specifications
corpus.

**Project Type**: Documentation. There is no runtime, no interface and no
deployment.

**Performance Goals**: N/A.

**Constraints**: No address that resolves today may 404 afterwards. No surviving
site page may answer an operator with "see the specifications repository". Each
subject's corpus statement and its site change must both land, since the state
between them is duplication.

**Scale/Scope**: Six pages, 1,898 lines by the specification's count and 1,925
as they stand (see research Finding 2). Two subjects, becoming feature
specifications `004` and `005`. One skill updated. Two client-side redirects.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle                                                                                                                                      | How this feature satisfies it                                                                                                                                                                                                                                                                                                |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** — a repository states in full the conventions binding it; a reference held elsewhere does not stand in place of stating them | This is the principle the feature serves. The corpus states each rule; the skill cites it. The one place to be careful is the reverse direction: a site page must not become a reference that stands in place of a statement an operator needs, which FR-012 forbids and the classification in research Decision 1 enforces. |
| **Verification** — a claim is measured, not inspected; where a check can be automated it is automated                                          | The citation gate is `scripts/validate-skills.py`, which already fails on an unresolvable relative link. FR-009 and FR-011 are what verification means here: a rule is checked against the code before it is written, and the corpus statement cites the code so the next reader can check it again rather than trust it.    |
| **Tooling** — versions are pinned; generated artifacts are not hand-edited                                                                     | Adding the redirects plugin pins it in the site's `package.json` like every other dependency. Nothing generated is touched.                                                                                                                                                                                                  |
| **Correction** — a rule invented to fill a template is noise; requirements come from evidence the repository carries                           | Every requirement in this feature's specification cites a page and a line count. Research Finding 1 applies the same test to the content being moved: a principle already stated in the charter becomes a citation rather than a second statement.                                                                           |
| **Workflow** — one workflow governs specification, planning and implementation                                                                 | This plan produces the artifacts Spec Kit expects, and the two subjects it identifies become specifications in their own right rather than being implemented out of this one.                                                                                                                                                |

**Result**: no violations. The Complexity Tracking table below is therefore
empty.

One consequence of the Workflow principle is worth stating plainly: this
feature's own implementation is *not* the writing of the two subject
specifications. It decides the classification, the subjects, the addresses and
the citation pattern, and it carries out the first subject. The second follows
the same path as its own feature.

## Project Structure

### Documentation (this feature)

```text
components/osapi/specs/003-corpus-backfill/
├── plan.md              # This file
├── research.md          # Phase 0: classification, subjects, addresses, findings
├── data-model.md        # Phase 1: what moves where, page by page
├── quickstart.md        # Phase 1: how to verify the move
├── contracts/
│   └── citation.md      # Phase 1: the shape of a citation and the gate that checks it
├── checklists/
│   └── requirements.md  # From /speckit-specify
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Content (two repositories)

```text
specs/                                   # this repository
├── components/osapi/specs/
│   ├── 004-job-system/                  # Subject A, its own feature
│   └── 005-building-a-domain/           # Subject B, its own feature
└── .claude/skills/add-a-domain/
    ├── SKILL.md                         # routing, unchanged in shape
    └── references/                      # restatements become citation tables

osapi/                                   # the site
└── docs/docs/sidebar/
    ├── architecture/
    │   ├── architecture.md              # stays; its Deep Dives links change
    │   ├── job-architecture.md          # splits: operator half stays
    │   ├── system-architecture.md       # splits: operator half stays
    │   ├── api-guidelines.md            # redirect
    │   └── principles.md                # redirect
    └── development/
        └── adding-an-api-domain.md      # short contributor page with citations
```

**Structure Decision**: the corpus half lands here, under
`components/osapi/specs/`, because it describes how one repository behaves. The
page half lands in osapi, because that is where the site is. CONTRIBUTING's
"Closing a change" assumes one implementation repository; this feature has two,
and research Finding 3 records the ordering that makes that safe and the risk it
leaves.

## Complexity Tracking

> No Constitution Check violations, so this table is empty by design.
