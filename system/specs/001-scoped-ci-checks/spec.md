# Feature Specification: Scoped continuous integration checks

**Feature Branch**: `feat/scoped-ci-checks`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "CI should only run the go gates when go files
change, and generally only run a job when a file of that type changes."

## User Scenarios & Testing *(mandatory)*

Every repository in osapi-io runs its full check suite on every pull request.
None of the 60 workflow files across the six repositories filters on paths, so a
change to a single line of prose runs compilation, unit tests, integration
tests, and a documentation site build.

### User Story 1 - A documentation change is not gated on the compiler (Priority: P1)

A contributor corrects a sentence in `CONTRIBUTING.md` and opens a pull request.
Only the checks that can judge that change run.

**Why this priority**: This is the case that produced the feature.
osapi-io/osapi#467 changed one line of prose and failed, because a Go job
fetched shared justfiles over the network and the connection reset. The change
could not have broken anything the failing job tested.

**Independent Test**: Open a pull request touching only `**.md` and confirm the
Go and site-build workflows report as skipped rather than run.

**Acceptance Scenarios**:

1. **Given** a pull request whose diff is entirely Markdown, **When** checks are
   evaluated, **Then** no workflow that compiles or tests code runs.
2. **Given** that same pull request, **When** checks are evaluated, **Then** the
   Markdown formatting check does run.
3. **Given** a pull request touching both a Markdown file and a Go file,
   **When** checks are evaluated, **Then** the Go workflows run.

### User Story 2 - A change that can affect a check still runs it (Priority: P1)

A contributor changes something that is not source code but does decide how the
code builds or is judged: the lint configuration, the justfile, the tool
versions, or a workflow file itself. Every check that the change could alter
still runs.

**Why this priority**: A filter that is too narrow is worse than none. It
reports success for a suite that never ran, and nothing in the pull request says
so. This is the failure mode the feature must not introduce.

**Independent Test**: Open a pull request changing only `.golangci.yml` and
confirm the Go lint workflow runs.

**Acceptance Scenarios**:

1. **Given** a pull request changing only the lint configuration, **When**
   checks are evaluated, **Then** the lint workflow runs.
2. **Given** a pull request changing only the justfile or a fetched justfile
   module, **When** checks are evaluated, **Then** every workflow invoking a
   recipe runs.
3. **Given** a pull request changing only a workflow file, **When** checks are
   evaluated, **Then** that workflow runs.
4. **Given** a pull request changing only files under `ui/` in osapi, **When**
   checks are evaluated, **Then** the Go workflows run, because the Go build
   embeds `ui/dist/` and fails without it.

### User Story 3 - The convention survives the next repository (Priority: P2)

A repository is added to osapi-io, or a workflow is added to an existing one. It
carries the same scoping without anyone remembering to apply it.

**Why this priority**: Four of the six repositories already hold a
byte-identical `go.yml`, which stayed identical only because nobody edited it.
Sixty files kept in agreement by hand will not stay in agreement.

**Independent Test**: Add a workflow to one repository and confirm the mechanism
that keeps repositories in agreement either supplies the scoping or reports the
omission.

**Acceptance Scenarios**:

1. **Given** a new repository in the organization, **When** its continuous
   integration is set up, **Then** it takes the scoping from the same place
   every other repository takes it.
2. **Given** a workflow added without scoping, **When** it is reviewed, **Then**
   the omission is visible rather than silent.

### Edge Cases

- A pull request that only deletes files, or only renames them, is still a
  change to those paths and is scoped by the same rules.
- A merge queue or a re-run must reach the same decision as the original run,
  since the diff is unchanged.
- No repository declares any named required status check, so a skipped workflow
  cannot leave a pull request waiting on a check that never reports. This is the
  usual hazard of path filtering and it does not apply here. Should named
  required checks be introduced later, that assumption must be re-examined.
- A change to the file that defines the scoping rules must run everything, since
  the change alters what would otherwise be skipped.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A workflow MUST run when the pull request changes any file whose
  content that workflow inspects, builds, or tests.
- **FR-002**: A workflow MUST run when the pull request changes any file that
  determines how that workflow behaves, including its own definition, the task
  runner recipes it invokes, the tool versions it resolves, and the
  configuration of the tools it runs.
- **FR-003**: A workflow MUST NOT run when every file in the pull request is
  provably outside both FR-001 and FR-002.
- **FR-004**: Where a workflow cannot be shown to be unaffected by a path, it
  MUST run. Scoping fails toward running rather than skipping.
- **FR-005**: The scoping for a given workflow MUST be identical across every
  repository that runs that workflow, and a difference MUST be traceable to a
  difference in what that repository contains.
- **FR-006**: Adding a repository or a workflow MUST NOT require restating the
  scoping by hand for it to apply.

### Key Entities

- **Workflow**: a continuous integration job definition, currently a file under
  `.github/workflows/` in each repository. Sixty exist across six repositories.
- **Scope**: the set of paths a workflow depends on, comprising what it examines
  and what changes its behavior.
- **Repository**: one of the six osapi-io repositories that runs checks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A pull request changing only Markdown runs zero workflows that
  compile, test, or build a site. Today it runs ten in osapi and seven in gohai.
- **SC-002**: A pull request changing a Go file, a build configuration file, or
  a workflow definition runs exactly the workflows it runs today. Scoping
  removes no coverage from a change that could affect it.
- **SC-003**: Every workflow that runs in more than one repository has the same
  scope in each, verifiable by comparing the files.
- **SC-004**: A repository added after this feature has scoped checks without a
  separate change to give it them.

## Assumptions

- Branch protection continues to name no required status checks. Verified across
  osapi, gohai and osapi-justfiles at the time of writing.
- The four repositories currently sharing a byte-identical `go.yml` should
  continue to share it. osapi differs because it embeds a user interface, which
  is a real difference rather than drift.
- `paths-ignore` is the safer form of the two GitHub offers, because it
  enumerates what is inert and runs everything on anything unrecognized, which
  is FR-004. This is an assumption about form and the plan may overturn it.

## Affected repositories

osapi, gohai, nats-client, nats-server, osapi-orchestrator, osapi-justfiles.

The feature is specified here rather than in any one of them because its subject
is an agreement all six honor, not the behavior of one. Bringing each repository
into line is compliance work in that repository's own pull request.
