## Purpose

Records how osapi-io repositories depend on one another and how those
dependencies are declared, so that a description of the system can be checked
against what the code actually does.

## ADDED Requirements

### Requirement: Module path matches repository location

A Go module SHALL declare a path matching the repository that holds it.

#### Scenario: Consumer resolves a dependency

- **WHEN** a developer runs `go get` using the repository's location
- **THEN** the module resolves, because its declared path is that location

#### Scenario: Repository moves between owners

- **WHEN** a repository moves to a different organization
- **THEN** its module path is updated to match, and consumers are updated in the
  same change

### Requirement: Dependencies are declared by version

A repository SHALL depend on another by a released or pinned version in
`go.mod`.

A repository SHALL NOT contain a `replace` directive. No repository contains one
today, and the documentation that described `replace` as the linking mechanism
was wrong.

#### Scenario: Consumer builds without the sibling checked out

- **WHEN** a repository is built by someone who has not cloned its sibling
  repositories
- **THEN** the build resolves every dependency from the module proxy

#### Scenario: Local development against an unreleased change

- **WHEN** a developer needs to build against an unreleased change in a sibling
  repository
- **THEN** they use a local workspace or a temporary pin rather than committing
  a `replace` directive

### Requirement: Documented relationships match declared ones

Documentation describing a dependency between repositories SHALL match what
`go.mod` declares. A repository SHALL NOT describe itself as consumed by, or
consuming, a repository it has no declared dependency on.

#### Scenario: A relationship is planned but not built

- **WHEN** a repository is intended to be used by another but is not yet
- **THEN** its documentation says so, rather than describing the intended state
  as current

#### Scenario: A dependency is removed

- **WHEN** a repository stops depending on another
- **THEN** the documentation describing that relationship is removed in the same
  change
