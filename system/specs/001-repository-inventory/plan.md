# Implementation Plan: Repository inventory

**Branch**: `feat/repository-inventory` | **Date**: 2026-09-02 | **Spec**:
[spec.md](./spec.md)

**Input**: Feature specification from `specs/001-repository-inventory/spec.md`

## Summary

Add a charter fragment stating that the osapi-io repository list comes from
`gh repo list osapi-io --no-archived --visibility public`, regenerate the
constitution, and rewrite `dependencies.md` to use the command instead of naming
repositories inline.

Two files change. No code, no configuration, no other repository.

## Technical Context

**Language/Version**: N/A — Markdown and a shell command

**Primary Dependencies**: `gh` CLI, authenticated

**Testing**: `just test` in the specs repo covers Markdown formatting. The rule
itself is verified by reading the generated constitution and running the
command.

**Project Type**: Documentation change in one repository.

**Constraints**: `constitution.md` is generated from fragments. It must be
regenerated, not edited.

**Scale/Scope**: One repository, two files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle                                                                              | Assessment                                                                                                                                                                                                                                         |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Documentation** — a rule a tool already enforces is never restated as prose          | **Pass.** No tool enforces where the repository list comes from, so a rule in prose is the right form. The rule names a command rather than restating its output.                                                                                  |
| **Verification** — a claim is measured, not inspected                                  | **Pass.** The command is the measurement, run each time, rather than a list someone once checked.                                                                                                                                                  |
| **Tooling** — a tool a repository invokes is declared where it declares its tools      | **Pass.** `gh` is already required by the workflow.                                                                                                                                                                                                |
| **Correction** — a requirement is written from evidence the repository already carries | **Pass.** Two hardcoded lists exist. An earlier draft of this feature proposed consolidating `.github/repos.json`; that was dropped because the duplication it targeted has never drifted, which is the same principle applied against the author. |
| **Workflow** — design output lives under the project's `specs/`                        | **Pass.** Under `system/specs/001-repository-inventory/`.                                                                                                                                                                                          |

## Project Structure

### Documentation (this feature)

```text
system/specs/001-repository-inventory/
├── plan.md
├── spec.md
├── checklists/requirements.md
└── tasks.md
```

No `research.md`, `data-model.md`, `contracts/` or `quickstart.md`. There is one
entity, no interfaces, and the verification fits in the tasks.

### Files changed by implementation

```text
specs/
├── .charter/fragments/global/repositories.md   # NEW — the rule
├── .charter/manifest.yml                       # fragment registered
├── system/.specify/charter/state.yml           # fragment composed in
├── system/.specify/memory/constitution.md      # regenerated
└── system/.specify/memory/dependencies.md      # uses the command
```

**Structure Decision**: The fragment goes in `.charter/fragments/global/`
alongside the existing five, because the rule binds every project here, not just
`system`.

## Complexity Tracking

No constitution violations to justify.
