## Purpose

Defines the configuration files a Go library carries, which of them must match
across libraries and which may vary, so that a difference between two libraries
is a recorded decision rather than an artifact of who edited what last.

## ADDED Requirements

### Requirement: Ignore baseline

A Go library's `.gitignore` SHALL include `.coverage/`, `.just/`, `dist/`, and
`.worktrees/`. It MAY add entries for artifacts specific to that repository,
such as a compiled binary at the repository root.

A `.gitignore` SHALL NOT ignore a dependency lockfile. Lockfiles are committed
so that builds resolve the same dependency versions.

#### Scenario: Repository produces a binary at the root

- **WHEN** a library builds a binary whose name collides with a package
  directory
- **THEN** it adds that path to `.gitignore`, keeping the baseline entries

#### Scenario: Repository has a documentation site

- **WHEN** a library's documentation site produces a lockfile
- **THEN** the lockfile is committed, and `node_modules/` is ignored instead

### Requirement: Badge row

A Go library README SHALL open with these badges, in this order:

`release`, `codecov`, `go report card`, `license`, `build`, `powered by`,
`conventional commits`, `built with just`, `go reference`.

A library MAY insert one badge naming the technology it wraps, placed
immediately before `built with just`.

#### Scenario: Reader compares two libraries

- **WHEN** a reader opens two Go library READMEs
- **THEN** the badges appear in the same order, differing only by a technology
  badge

#### Scenario: Library wraps a named technology

- **WHEN** a library wraps NATS
- **THEN** it may carry a `nats` badge before `built with just`

### Requirement: Generated code is excluded from coverage

Coverage configuration SHALL exclude generated mocks in every Go library,
whether or not that library currently generates any.

#### Scenario: Library gains generated mocks

- **WHEN** a library starts generating mocks
- **THEN** they are already excluded from coverage, without a configuration
  change

### Requirement: Recipe surface

A Go library's justfile SHALL provide `deps`, `test`, `generate`, and `ready`,
so that the same command does the same thing in every library.

`generate` SHALL exist even where a library currently generates nothing.

#### Scenario: Contributor moves between libraries

- **WHEN** a contributor runs `just ready` in any Go library
- **THEN** it formats, lints, and regenerates, without their needing to check
  which recipes that library defines

### Requirement: Lint configuration baseline

`.golangci.yml` SHALL be identical across Go libraries except for directory
exclusions, which are specific to a library's package layout.

#### Scenario: Library excludes one of its own packages

- **WHEN** a library needs to exclude a package it owns from linting
- **THEN** it adds that directory exclusion, leaving the rest of the
  configuration unchanged

### Requirement: Files permitted to vary

These files SHALL be allowed to differ between libraries, because their content
is determined by the repository:

| File                     | Determined by                               |
| ------------------------ | ------------------------------------------- |
| `.coverignore`           | which packages that library excludes        |
| `.goreleaser.yaml`       | the binary that library produces            |
| `.github/dependabot.yml` | which example modules that library contains |

Every other shared configuration file SHALL match, subject to the exceptions
stated above.

#### Scenario: A difference is proposed

- **WHEN** a library needs a shared configuration file to differ
- **THEN** either the file is one permitted to vary, or the difference is a
  change to this capability
