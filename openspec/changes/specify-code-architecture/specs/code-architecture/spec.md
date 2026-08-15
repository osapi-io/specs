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
declare that target in its coverage configuration.

Generated code SHALL be excluded rather than counted or waived.

#### Scenario: Coverage falls below target

- **WHEN** a change lowers coverage below the declared target
- **THEN** the coverage check reports it, rather than the target being adjusted
  to accommodate the change

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

### Requirement: Repository-specific engineering guidance stays local

Guidance that binds a single repository — how its collectors are written, how
its operations are constructed, which upstream library a component wraps — SHALL
live in that repository, not in the specification corpus.

The corpus SHALL hold only what binds more than one repository.

#### Scenario: One repository documents its own methodology

- **WHEN** a repository has a methodology governing how its components are
  implemented
- **THEN** it lives in that repository's `docs/`, next to the code it governs

#### Scenario: A convention spreads to a second repository

- **WHEN** guidance that was specific to one repository begins binding another
- **THEN** it becomes a capability in the corpus, and the repositories point at
  it rather than each restating it
