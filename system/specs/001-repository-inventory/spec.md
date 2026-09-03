# Feature Specification: Repository inventory

**Feature Branch**: `feat/repository-inventory`

**Created**: 2026-09-02

**Status**: Draft

**Input**: One answer to which repositories are part of osapi-io, so work
spanning repositories takes that answer instead of writing its own list.

## Context

Nothing states where the repository list comes from, so work that spans
repositories writes its own. Two copies exist: the reproduction script in
`system/.specify/memory/dependencies.md`, and a draft CI specification since set
aside. Each was correct when written.

`dependencies.md` has a second problem. Memory holds the consolidated output of
merged features, and nothing in this project has ever been archived — no feature
has merged. That file was hand-placed during the OpenSpec retirement in
osapi-io/specs#103 because there was nowhere else to put it. Its dependency
graph is a cached copy of what `go.mod` says, reproducible in seconds, sitting
in a directory reserved for something else.

GitHub already holds the answer:

```bash
gh repo list osapi-io --no-archived --visibility public
```

The gap is a stated rule that this is the answer, placed where work reads it.
`AGENTS.md` already requires the constitution at the start of every session, and
the constitution is generated from fragments in `.charter/`.

## User Scenarios & Testing *(mandatory)*

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

______________________________________________________________________

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

### Edge Cases

- `.github` is returned but holds no code. Work needing only code repositories
  filters at the point of use, rather than maintaining a second list.
- A private repository becomes active. `--visibility public` excludes it.
  Revisit when one exists; none does.
- `gh` unauthenticated fails loudly rather than returning a short list.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The constitution MUST state that the osapi-io repositories are
  what `gh repo list osapi-io --no-archived --visibility public` returns, and
  that no document may hold a copy of that list.
- **FR-002**: The rule MUST be a charter fragment in `.charter/`, with the
  constitution regenerated. `constitution.md` is generated; a direct edit is
  lost at the next compose.
- **FR-003**: `system/.specify/memory/dependencies.md` MUST be deleted. It holds
  a hardcoded repository list, and its dependency graph is a cached copy of what
  `go.mod` already states. It also sits in memory without having been archived
  there, which is the only way anything is meant to arrive.
- **FR-004**: Memory MUST contain only the generated constitution and its
  metadata until a merged feature is archived into it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A session that read the constitution produces the repository list
  without being told how.
- **SC-002**: No document here holds a hand-maintained repository list.
- **SC-004**: `system/.specify/memory/` holds only `constitution.md` and
  `.constitution-template.json`.
- **SC-003**: Adding a repository requires no edit for it to be included.

## Assumptions

- **Nothing of value is lost by deleting `dependencies.md`.** The graph
  reproduces from `go.mod`. The one fact a command cannot produce — that `osapi`
  once declared itself `github.com/retr0h/osapi` and was corrected in
  osapi-io/osapi#446 — is in git history and in that repository.

- **`gh` is available and authenticated.** Already required by the workflow.

- **`.github/repos.json` is out of scope.** Those files configure one repository
  each; they are not a repository list. Consolidating them was considered and
  rejected — the shared block is byte-identical across all seven, so it has
  never drifted, and the one drift that occurred was per-repository data that
  consolidating would not have prevented.

- **The `specs` topic drift is not fixed here.** `gh reposync --check` reports
  the manifest says `spec-kit` while GitHub says `openspec`, from
  osapi-io/specs#103. A one-command fix, unrelated to the repository list.

## Reproducing the measurements

```bash
gh repo list osapi-io --no-archived --visibility public
grep -rn "nats-client" ~/git/osapi-io/specs --include="*.md"
```
