# Main Project Specification

> **Revision**: 2026-09-02 — First archival. Seeded from `specs/001-repository-inventory`; every section was previously empty.

## User Scenarios & Testing

### User Story 1 - Cross-repository work knows where to get the list (Priority: P1)

Work touching more than one repository runs the command and uses its output,
rather than a list written somewhere.

**Why this priority**: This is the feature.

**Independent Test**: In a fresh session, the constitution names the command.

**Acceptance Scenarios**:

1. **Given** a session that read the constitution, **When** work needs the
   repository list, **Then** the constitution names the command producing it.
2. **Given** a repository is added to the organization, **When** the command
   runs, **Then** it appears with nothing edited.
3. **Given** a repository is archived or made private, **When** the command
   runs, **Then** it is absent.

[Source: specs/001-repository-inventory/spec.md -> User Story 1]

### User Story 2 - The written list is removed (Priority: P2)

`system/.specify/memory/dependencies.md` is deleted.

**Why this priority**: A rule the repository already breaks is not a rule yet.
Deleting the file resolves both problems at once — the hardcoded repository
list, and a file occupying memory without having been archived there.

**Independent Test**: Memory holds only the generated constitution and its
metadata. Searching the specs repository finds no hardcoded repository list.

**Acceptance Scenarios**:

1. **Given** `system/.specify/memory/`, **When** its contents are listed,
   **Then** only `constitution.md` and `.constitution-template.json` remain.
2. **Given** any document here, **When** searched for a hand-maintained
   repository list, **Then** none is found.
3. **Given** the deleted dependency graph is wanted again, **When** it is
   needed, **Then** it is reproduced from `go.mod` rather than read from a
   record.

[Source: specs/001-repository-inventory/spec.md -> User Story 2]

### Edge Cases

- `.github` is returned but holds no code. Work needing only code repositories
  filters at the point of use, rather than maintaining a second list.
  [Source: specs/001-repository-inventory/spec.md -> ".github is returned but holds no code"]
- A private repository becomes active. `--visibility public` excludes it.
  Revisit when one exists; none does.
  [Source: specs/001-repository-inventory/spec.md -> "A private repository becomes active"]
- `gh` unauthenticated fails loudly rather than returning a short list.
  [Source: specs/001-repository-inventory/spec.md -> "gh unauthenticated fails loudly"]

## Requirements

### Functional Requirements

- **FR-001**: The constitution MUST state that the osapi-io repositories are
  what `gh repo list osapi-io --no-archived --visibility public` returns, and
  that no document may hold a copy of that list.
  [Source: specs/001-repository-inventory/spec.md -> FR-001]
- **FR-002**: The rule MUST be a charter fragment in `.charter/`, with the
  constitution regenerated. `constitution.md` is generated; a direct edit is
  lost at the next compose.
  [Source: specs/001-repository-inventory/spec.md -> FR-002]
- **FR-003**: `system/.specify/memory/dependencies.md` MUST be deleted. It holds
  a hardcoded repository list, and its dependency graph is a cached copy of what
  `go.mod` already states. It also sits in memory without having been archived
  there, which is the only way anything is meant to arrive.
  [Source: specs/001-repository-inventory/spec.md -> FR-003]
- **FR-004**: Memory MUST contain only the generated constitution and its
  metadata until a merged feature is archived into it.
  [Source: specs/001-repository-inventory/spec.md -> FR-004]

### Key Entities

- **Repository list**: The set of public, unarchived repositories in the
  osapi-io organization. Produced by a command, never stored.
  [Source: specs/001-repository-inventory/spec.md -> "Repository list"]

## Success Criteria

### Measurable Outcomes

- **SC-001**: A session that read the constitution produces the repository list
  without being told how.
  [Source: specs/001-repository-inventory/spec.md -> SC-001]
- **SC-002**: No document here holds a hand-maintained repository list.
  [Source: specs/001-repository-inventory/spec.md -> SC-002]
- **SC-003**: Adding a repository requires no edit for it to be included.
  [Source: specs/001-repository-inventory/spec.md -> SC-003]
- **SC-004**: `system/.specify/memory/` holds only `constitution.md` and
  `.constitution-template.json`.
  [Source: specs/001-repository-inventory/spec.md -> SC-004]

## Assumptions

- **AS-001**: Nothing of value is lost by deleting `dependencies.md`. The graph
  reproduces from `go.mod`. The one fact a command cannot produce — that `osapi`
  once declared itself `github.com/retr0h/osapi` and was corrected in
  osapi-io/osapi#446 — is in git history and in that repository.
  [Source: specs/001-repository-inventory/spec.md -> "Nothing of value is lost by deleting dependencies.md"]
- **AS-002**: `gh` is available and authenticated. Already required by the
  workflow.
  [Source: specs/001-repository-inventory/spec.md -> "gh is available and authenticated"]
- **AS-003**: `.github/repos.json` is out of scope. Those files configure one
  repository each; they are not a repository list. Consolidating them was
  considered and rejected — the shared block is byte-identical across all seven,
  so it has never drifted, and the one drift that occurred was per-repository
  data that consolidating would not have prevented.
  [Source: specs/001-repository-inventory/spec.md -> ".github/repos.json is out of scope"]
- **AS-004**: The `specs` topic drift is not fixed here. `gh reposync --check`
  reports the manifest says `spec-kit` while GitHub says `openspec`, from
  osapi-io/specs#103. A one-command fix, unrelated to the repository list.
  [Source: specs/001-repository-inventory/spec.md -> "The specs topic drift is not fixed here"]
