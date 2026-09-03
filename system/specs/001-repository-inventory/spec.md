# Feature Specification: Repository inventory

**Feature Branch**: `feat/repository-inventory`

**Created**: 2026-09-02

**Status**: Draft

**Input**: osapi-io should have one place that says what repositories it has, so
work spanning repositories reads that instead of each piece of work writing its
own list.

## Context

Work that spans repositories has to start by knowing which repositories exist.
Right now nothing answers that, so each piece of work writes its own list, and
each list is correct when written and wrong after the next repository is added.

Two copies exist already. `system/.specify/memory/dependencies.md` names its
repositories inline in its reproduction script. A draft specification for shared
CI, since set aside, named another set inline and was set aside partly for that
reason.

The pieces to fix this already exist:

- Each repository carries `.github/repos.json`, declaring its description,
  topics, settings, security options and branch protection.
- `retr0h/gh-reposync` reads those manifests. `--apply` brings a repository in
  line with its manifest; `--check` reports drift.

What is missing is that every manifest declares exactly one repository — its
own. So to learn what osapi-io contains, you must already know where to look.
`gh reposync`'s documented model is the opposite: one manifest in the
organization's `.github` repository listing every managed repository. osapi-io's
`.github` repository holds only `profile/README.md`.

Consolidating the manifests gives one file to read. That alone does not make
anyone read it, so the rule to read it belongs in the constitution, which
`AGENTS.md` already requires every session to load.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One file says what repositories exist (Priority: P1)

Someone starting work that touches more than one repository opens the manifest,
sees every repository and what each one is, and works from that.

**Why this priority**: This is the whole feature. Everything else supports it.

**Independent Test**: Read the manifest. Compare its list to the organization.
They agree, and no second list had to be consulted.

**Acceptance Scenarios**:

1. **Given** the manifest, **When** someone asks what repositories osapi-io
   manages, **Then** one file answers, with no prior knowledge of where to look.
2. **Given** a repository is added to the organization, **When** it is added to
   the manifest, **Then** nothing else needs editing for it to be known.
3. **Given** the manifest, **When** `gh reposync --check` is run against it,
   **Then** it checks every listed repository in one run.

______________________________________________________________________

### User Story 2 - Work that spans repositories is told to read it (Priority: P2)

An agent or a person begins cross-repository work. The constitution tells them
to take the repository list from the manifest and forbids writing another list
somewhere else.

**Why this priority**: A file nobody is told to read gets ignored, which is how
the two existing hardcoded lists came about. `AGENTS.md` already requires the
constitution to be read before work starts, so a rule placed there is seen every
session without anyone remembering.

**Independent Test**: Start cross-repository work in a fresh session. The
constitution names the manifest as the source, and no list is written anywhere
else.

**Acceptance Scenarios**:

1. **Given** the constitution, **When** a session begins, **Then** it states
   that the repository list comes from the manifest.
2. **Given** work needing the repository list, **When** it takes that list,
   **Then** it reads the manifest rather than writing its own copy.
3. **Given** a document containing a hardcoded repository list, **When** it is
   reviewed against the constitution, **Then** it is a violation to be fixed.

### Edge Cases

- A repository exists in the organization but is not in the manifest.
- A repository is archived. The organization contains archived, private
  repositories, at least one on a plan where branch protection cannot be read.
- The organization's own `.github` repository, which holds no code.
- A manifest names a repository that no longer exists.

## Requirements *(mandatory)*

### Functional Requirements

**The manifest**

- **FR-001**: The repositories osapi-io manages MUST be listed in a single
  manifest in the organization's `.github` repository.
- **FR-002**: That manifest MUST be the file `gh reposync` already consumes, so
  the list and the thing that is enforced are one artifact. No second document
  describing repositories is created.
- **FR-003**: The per-repository `.github/repos.json` files MUST be removed from
  every repository that can still be written to. Two statements of a
  repository's desired configuration would disagree, and nothing would say which
  wins.
- **FR-004**: Archived repositories are exempt from FR-003. GitHub makes an
  archived repository read-only, so its stale manifest cannot be deleted without
  unarchiving it. `osapi-ui` carries one and keeps it. The manifest is inert:
  nothing reads it, because FR-006 keeps archived repositories out of the
  inventory.
- **FR-005**: The organization's own `.github` repository MUST be listed. It is
  a real, public, non-archived repository, and it already matches the shared
  configuration block, so listing it introduces no drift. The one file naming
  the organization's repositories should not omit the repository it lives in.
- **FR-006**: Archived repositories MUST NOT be listed. `gh reposync` has no
  concept of an archived repository, and at least one cannot be read at all.
  Absence from the manifest is what marks a repository as unmanaged.
- **FR-007**: A manifest entry naming a repository that no longer exists MUST be
  reported rather than passed over. `gh reposync --check` fails on it, which is
  the required behaviour; the entry is then removed.
- **FR-008**: Changing one repository's configuration therefore becomes a pull
  request in `.github` rather than in that repository. This is the accepted cost
  of FR-001 and is recorded so it is not later mistaken for an oversight.

**The rule that makes it read**

- **FR-009**: The constitution MUST state that the repository list comes from
  the manifest, and that no other document may contain one.
- **FR-010**: That rule MUST be added as a charter fragment and the constitution
  recomposed, since `constitution.md` is generated from fragments and a direct
  edit would be overwritten.

**Existing violations**

- **FR-011**: `system/.specify/memory/dependencies.md` MUST stop naming
  repositories inline and take them from the manifest instead.
- **FR-012**: The `specs` topic drift MUST be resolved, so the manifest matches
  reality on the day it lands. `gh reposync --check` reports it today: the
  manifest says `spec-kit`, GitHub still says `openspec`. The manifest is
  correct; osapi-io/specs#103 retired OpenSpec and the change was never applied.

### Key Entities

- **Managed repository**: A repository whose configuration osapi-io declares.
- **Manifest**: The single list of managed repositories and how each is
  configured. Read by `gh reposync`, and by anything needing the repository
  list.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: "What repositories does osapi-io manage?" is answered by reading
  one file, with no prior knowledge of which repositories to look in.
- **SC-002**: `gh reposync --check` passes against the manifest, starting from a
  state where it does not pass today.
- **SC-003**: No document in the specs repository contains a hand-maintained
  list of osapi-io repositories.
- **SC-004**: Adding a repository requires exactly one edit for it to be known.
- **SC-005**: A session reading the constitution learns where the repository
  list lives without being told separately.

## Assumptions

- **`gh reposync` is the mechanism and is not replaced.** It already models the
  declaration, the application and the drift check.
- **Nothing runs automatically.** `gh reposync --check` is run by a person or an
  agent when it matters. Running it on a schedule would need a stored
  organization-wide token and somewhere for failures to go; that is a separate
  decision, worth making only if forgetting turns out to bite again.
- **Applying stays manual.** `--apply` mutates settings and branch protection
  with administrator rights.
- **The organization's `.github` repository is in scope as a location**, whether
  or not it is itself managed. It currently holds only `profile/README.md`.

## Reproducing the measurements

```bash
# What the organization actually contains
gh repo list osapi-io --limit 100 --json name,visibility,isArchived

# How many repositories each manifest declares
for f in ~/git/osapi-io/*/.github/repos.json; do
  printf "%-40s declares=%s\n" "$f" "$(jq '.repos|length' "$f")"
done

# Declared versus actual
cd ~/git/osapi-io/specs && gh reposync --check
```
