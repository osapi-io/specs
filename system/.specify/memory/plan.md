# Main Implementation Plan

> **Revision**: 2026-09-02 — First archival. Seeded from `specs/001-repository-inventory`; every section was previously empty.

## Summary

The repository list comes from a command rather than a document. A charter
fragment states it, the constitution carries it into every session, and the one
file that kept its own copy is gone.

[Source: specs/001-repository-inventory/plan.md -> "Summary"]

## Technical Context

**Language/Version**: N/A — Markdown and shell commands
[Source: specs/001-repository-inventory/plan.md -> "Language/Version"]

**Primary Dependencies**: `gh` CLI, authenticated. Installed by hand via
`brew`, not by `mise`, which resolves it through `aqua` whose attestation check
fails for that package.
[Source: specs/001-repository-inventory/plan.md -> "Primary Dependencies"]

**Testing**: `just test` covers Markdown and justfile formatting. Rules stated
in the constitution are verified by reading the generated file and running the
command they name.
[Source: specs/001-repository-inventory/plan.md -> "Testing"]

**Project Type**: Documentation and configuration, in this repository.
[Source: specs/001-repository-inventory/plan.md -> "Project Type"]

**Constraints**: `constitution.md` is generated from fragments in `.charter/`.
It must be regenerated with `/speckit-charter-compose` then
`/speckit-constitution`, never edited — a direct edit is lost at the next
compose.
[Source: specs/001-repository-inventory/plan.md -> "Constraints"]

**Scale/Scope**: One repository.
[Source: specs/001-repository-inventory/plan.md -> "Scale/Scope"]

## Project Structure

```text
specs/
├── .charter/
│   ├── manifest.yml                      # fragments the registry offers
│   └── fragments/global/                 # shared by system and every component
│       ├── documentation.md
│       ├── verification.md
│       ├── tooling.md
│       ├── correction.md
│       ├── workflow.md
│       └── repositories.md
└── system/.specify/
    ├── charter/
    │   ├── state.yml                     # fragments this project composes
    │   └── snapshots/fragment/global/    # one per composed fragment
    └── memory/
        ├── constitution.md               # generated; never hand-edited
        ├── spec.md                       # this document's sibling
        └── plan.md
```

**Structure Decision**: Charter fragments live at the repository root, in
`.charter/`, because they are shared by `system` and every project under
`components/`. Each project's `state.yml` selects the subset it composes.

[Source: specs/001-repository-inventory/plan.md -> "Structure Decision"]

## Configuration

`.mise.toml` provisions `just` and `uv`. `gh` is installed by hand alongside
`mise`; it cannot be provisioned by `mise`, whose `aqua` backend fails release
attestation for that package, and adding it makes `mise exec -- gh` fail where
it otherwise resolves from `PATH`.

[Source: specs/001-repository-inventory/plan.md -> "Primary Dependencies"]

## Testing Strategy

`just test` runs `md-fmt-check` and `just-fmt-check`, the same checks CI runs.
A rule that lives in the constitution is verified by reading the generated
`constitution.md` for its section and running the command the rule names —
there is nothing to unit test.

[Source: specs/001-repository-inventory/plan.md -> "Testing"]

## Complexity Tracking

No constitution violations to justify.

[Source: specs/001-repository-inventory/plan.md -> "Complexity Tracking"]
