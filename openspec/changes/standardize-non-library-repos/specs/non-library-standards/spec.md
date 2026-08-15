## Purpose

Defines the configuration carried by repositories that are not Go libraries —
main product, UI, utility, and documentation — so that types with only one or
two repositories are held to a standard rather than compared against nothing.

## ADDED Requirements

### Requirement: Repository management files

Every repository SHALL contain `.github/repos.json`, `.github/dependabot.yml`,
`.github/labeler.yml`, and `.github/delete-merged-branch-config.yml`.

`dependabot.yml` SHALL track the `github-actions` ecosystem, and any package
ecosystem the repository actually uses. `labeler.yml` content varies with the
labels a repository defines.

#### Scenario: Repository has no package manifest

- **WHEN** a repository contains no language manifest, such as a documentation
  repository
- **THEN** its `dependabot.yml` tracks `github-actions` only, rather than being
  omitted

#### Scenario: Auditing repository management

- **WHEN** a repository is checked against the standard
- **THEN** the absence of any of those four files is a defect

### Requirement: Every repository has continuous integration

Every repository SHALL run checks on pull requests. At minimum, commit message
conventions and the formatting of whatever the repository primarily contains
SHALL be verified.

A repository SHALL NOT rely on review alone to catch what a check could catch.

#### Scenario: Repository contains no compiled code

- **WHEN** a repository holds markdown and configuration rather than a compiled
  artifact
- **THEN** it still runs checks — commit conventions, markdown formatting, and
  any validation specific to its content

#### Scenario: Repository holds a user interface

- **WHEN** a repository holds a front-end application
- **THEN** it runs the checks appropriate to that toolchain, such as formatting,
  linting, and a build

### Requirement: Toolchain files match the toolchain

A repository SHALL carry the configuration files its toolchain requires, and
SHALL NOT carry files for a toolchain it does not use.

| File                                                | Present when                           |
| --------------------------------------------------- | -------------------------------------- |
| `.golangci.yml`, `.coverignore`, `.goreleaser.yaml` | the repository builds Go               |
| `.prettierignore`, `package.json`                   | the repository builds front-end assets |
| `.dockerignore`                                     | the repository publishes an image      |

#### Scenario: Documentation repository

- **WHEN** a repository holds only specifications
- **THEN** it carries no Go, front-end, or container configuration

#### Scenario: Utility repository publishes an image

- **WHEN** a utility repository distributes its assets as a container image
- **THEN** it carries `.dockerignore`, and that file is not evidence it builds
  an application

### Requirement: Development-only files are the main product's alone

Files supporting local development of a running service — live-reload
configuration, local orchestration compose files, environment shims — SHALL be
carried only by the repository that runs as a service.

#### Scenario: Library adds a compose file

- **WHEN** a library needs a service running to test against
- **THEN** that belongs in its test setup, not as a development compose file at
  the repository root
