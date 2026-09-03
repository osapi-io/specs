# Implementation Plan: Repository inventory

**Branch**: `feat/repository-inventory` | **Date**: 2026-09-02 | **Spec**:
[spec.md](./spec.md)

**Input**: Feature specification from `specs/001-repository-inventory/spec.md`

## Summary

Merge the seven per-repository `.github/repos.json` manifests into one manifest
in the `osapi-io/.github` repository, delete the originals, and add a charter
fragment stating that the repository list comes from that manifest and may not
be written anywhere else. Fix the two existing violations: the `specs` topic
drift, and the inline repository list in `dependencies.md`.

The merge is mechanical. All seven manifests carry byte-identical `settings`,
`security` and `branch_protection` blocks, so the merged file is one shared
block plus one `repos[]` entry per repository. The `.github` repository itself
already matches that shared block and is added as an eighth entry.

## Technical Context

**Language/Version**: N/A — JSON configuration and Markdown

**Primary Dependencies**: `gh` CLI; `retr0h/gh-reposync` (installed as a `gh`
extension); `jq`

**Storage**: Files in git. `osapi-io/.github` holds the manifest.

**Testing**: `gh reposync --check` is the test. `just test` in the specs repo
covers the Markdown and justfile formatting of anything changed here.

**Target Platform**: Developer and agent workstations. Nothing runs unattended.

**Project Type**: Configuration and documentation change across repositories.

**Performance Goals**: N/A

**Constraints**: `gh reposync` applies `settings`, `security` and
`branch_protection` to every repository in the manifest; the schema has no
per-repository override for them. This is workable only because all eight
repositories want identical values today, which was measured, not assumed.

**Scale/Scope**: Eight repositories. Two repositories are edited in this change
(`osapi-io/.github` and `osapi-io/specs`), plus deletions in six others.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle                                                                                                                     | Assessment                                                                                                                                                                                                                                                                                                  |
| ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** — a repository states in full the conventions binding it; a rule a tool enforces is never restated as prose | **Pass.** The manifest is the configuration, not prose about it. The charter fragment states a rule no tool enforces, which is the case prose is for. The spec names commands instead of quoting their output.                                                                                              |
| **Verification** — a claim is measured, not inspected; where a check can be automated it is automated                         | **Pass with a noted limit.** Every claim in the spec came from `gh repo list`, `gh reposync --check` and `jq` over the manifests. The check is not automated; the spec records why (a stored org-wide token and a failure destination are a larger decision) and defers it explicitly rather than silently. |
| **Tooling** — a tool a repository invokes is declared where it declares its tools                                             | **Pass with a follow-up.** `gh-reposync` is a `gh` extension installed per machine and is not declared in `.mise.toml`. See Complexity Tracking.                                                                                                                                                            |
| **Correction** — a requirement is written from evidence the repository already carries                                        | **Pass.** Every requirement traces to a measured fact: the one-repo-per-manifest shape, the `specs` topic drift, the inline list in `dependencies.md`.                                                                                                                                                      |
| **Workflow** — design output lives under the project's `specs/`, consolidated into `.specify/memory/` on merge                | **Pass.** This feature is under `system/specs/001-repository-inventory/`.                                                                                                                                                                                                                                   |

## Project Structure

### Documentation (this feature)

```text
system/specs/001-repository-inventory/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── checklists/
│   └── requirements.md
└── tasks.md             # Created by /speckit-tasks
```

### Files changed by implementation

```text
osapi-io/.github/
└── repos.json                        # NEW — the single manifest, 8 entries

osapi-io/gohai/.github/repos.json     # DELETED
osapi-io/nats-client/.github/repos.json        # DELETED
osapi-io/nats-server/.github/repos.json        # DELETED
osapi-io/osapi/.github/repos.json              # DELETED
osapi-io/osapi-orchestrator/.github/repos.json # DELETED
osapi-io/osapi-justfiles/.github/repos.json    # DELETED
osapi-io/specs/.github/repos.json              # DELETED

osapi-io/specs/
├── .charter/fragments/global/repositories.md  # NEW — the rule
├── system/.specify/charter/state.yml          # fragment added to composition
├── system/.specify/memory/constitution.md     # regenerated
└── system/.specify/memory/dependencies.md     # stops naming repos inline
```

**Structure Decision**: The manifest lives at the repository root of
`osapi-io/.github` as `repos.json`, not at `.github/repos.json` inside it.
`gh reposync`'s discovery order checks `./repos.json` first, and a `.github`
directory inside the `.github` repository reads as a mistake.

The charter fragment lives in `.charter/fragments/global/` alongside the other
five, because the rule binds every project in the specs repository, not just
`system`.

## Complexity Tracking

| Violation                                                                                                                                     | Why Needed                                                                                                                         | Simpler Alternative Rejected Because                                                                                                                                                                                                                     |
| --------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gh-reposync` is not declared in `.mise.toml`, so the Tooling principle's "declared where the repository declares its tools" is not satisfied | It is a `gh` extension, installed with `gh ext install`, which `mise` does not manage. Nothing in this feature can change that.    | Declaring it is the correct fix but belongs in its own change: it affects how every contributor provisions the repository, and the Correction principle requires a rule change to land on its own. Recorded here so it is not mistaken for an oversight. |
| Two repositories are edited in one logical change (`.github` gains the manifest, six others lose theirs)                                      | The manifests must not both exist; two statements of desired configuration would disagree with nothing to say which wins (FR-003). | Landing them separately leaves a window where either no manifest governs a repository, or two do. The window is the risk, not the multi-repository change.                                                                                               |
