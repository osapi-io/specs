## Purpose

Defines how Go code is arranged within an osapi-io repository, what test
coverage is expected, and which toolchain versions are supported, so that
consistency which currently exists by copying is held by a rule.

## ADDED Requirements

### Requirement: Package layout

A repository SHALL place code according to who may import it:

| Directory   | Contains                                                  |
| ----------- | --------------------------------------------------------- |
| `pkg/`      | The public API other repositories import                  |
| `internal/` | Code this repository alone uses, enforced by the compiler |
| `cmd/`      | Command-line entry points                                 |

A repository SHALL only carry the directories it needs. A library with no
command-line interface has no `cmd/`; a library with nothing private has no
`internal/`.

#### Scenario: Library gains a CLI

- **WHEN** a library adds a command-line wrapper over its public API
- **THEN** the commands go in `cmd/`, and the library remains the product in
  `pkg/`

#### Scenario: Helper is not part of the API

- **WHEN** code exists to support the public API but should not be imported by
  other repositories
- **THEN** it goes in `internal/`, where the compiler enforces the boundary

### Requirement: Coverage target

A repository containing Go code SHALL target 100% test coverage, and SHALL
declare that target both in its coverage service configuration and in the recipe
that checks coverage locally. The two declarations SHALL state the same number,
and each SHALL carry a comment naming the other.

What is excluded from coverage SHALL be defined in exactly one place. The
excluded files SHALL be removed from the coverage profile before it is uploaded,
so the local check and the coverage service measure the same set rather than
each applying their own exclusions.

Generated code SHALL be excluded rather than counted or waived.

A coverage check SHALL fail when coverage is below the target. Reporting the
number without failing does not satisfy this requirement.

#### Scenario: Coverage falls below target

- **WHEN** a change lowers coverage below the declared target
- **THEN** the check fails, rather than the target being adjusted to accommodate
  the change

#### Scenario: The two declarations disagree

- **WHEN** one declaration is raised or lowered and the other is not
- **THEN** that is a defect, and the comment in each names the other so whoever
  edits one knows to edit both

#### Scenario: An exclusion is added

- **WHEN** a file is added to the exclusion list
- **THEN** it disappears from both the local number and the service's number,
  because both read a profile the exclusions were already applied to

#### Scenario: The uploaded profile is chosen automatically

- **WHEN** a coverage service discovers coverage files itself rather than being
  given one
- **THEN** the workflow names the filtered profile explicitly, because
  discovering an unfiltered profile reports a different number for the same
  commit

### Requirement: Supported Go versions

A repository SHALL support the two most recent major Go versions, and SHALL
declare a minimum in `go.mod` consistent with that.

#### Scenario: A new major Go version is released

- **WHEN** Go publishes a new major version
- **THEN** support for the oldest of the three may be dropped, and `go.mod`
  updated accordingly

### Requirement: Release tooling

A repository that publishes a binary SHALL use goreleaser, configured in
`.goreleaser.yaml`, so that releases are produced the same way everywhere.

#### Scenario: Repository publishes no binary

- **WHEN** a repository produces no distributable artifact
- **THEN** it carries no release configuration

### Requirement: The pre-commit recipe fixes everything CI checks

A repository's `ready` recipe SHALL address every check its continuous
integration runs. A contributor who runs it and commits SHALL NOT then fail on
something the recipe could have fixed.

#### Scenario: CI checks a format the recipe does not fix

- **WHEN** continuous integration verifies the formatting of a file type
- **THEN** `ready` formats that file type, so running it before committing is
  sufficient

#### Scenario: A new check is added to CI

- **WHEN** a check is added to continuous integration
- **THEN** `ready` is extended in the same change, or the check is one nothing
  local can fix

### Requirement: Continuous integration is consistent by type

Repositories of the same type SHALL run the same set of workflows, and those
workflows SHALL differ only where the repository's build genuinely requires it.

Action and dependency versions are maintained by Dependabot. This capability
SHALL NOT name a version, because the current one changes without anyone
deciding it. What a repository SHALL do is keep its update queue moving — a
backlog of unmerged bumps is how repositories that should match stop matching.

#### Scenario: Repositories differ only by dependency version

- **WHEN** one repository's workflows pin older versions than another's
- **THEN** the difference is an unmerged update queue rather than a deliberate
  choice, and the queue is worked rather than the difference documented

#### Scenario: A version is proposed as a requirement

- **WHEN** someone proposes recording a specific action or module version here
- **THEN** it is declined, because Dependabot moves it and the corpus would be
  wrong by the next bump

#### Scenario: A build genuinely requires different infrastructure

- **WHEN** a repository must build on a different runner, or needs different
  credentials, than its siblings
- **THEN** its workflow differs in those respects and matches in all others
