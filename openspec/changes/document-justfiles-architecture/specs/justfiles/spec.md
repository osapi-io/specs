## Purpose

Records how shared `just` recipes are distributed, consumed, named, and
documented across osapi-io today, including the two consumption styles currently
in use, so that the architecture is written down before it is changed.

## ADDED Requirements

### Requirement: Recipes are distributed as fetched files

Shared recipes SHALL be distributed as individual files fetched over HTTP into a
gitignored directory in the consuming repository. A consuming repository SHALL
declare what it fetches, so the set of shared recipes it depends on is visible
in its own justfile.

Fetches SHALL resolve against the default branch; there is no version handshake
between a module and its consumers.

#### Scenario: Consumer obtains shared recipes

- **WHEN** a repository runs its `fetch` recipe
- **THEN** the shared files it names are downloaded into `.just/remote/`, which
  is excluded from version control

#### Scenario: A module changes upstream

- **WHEN** a module is modified upstream
- **THEN** consuming repositories receive the change on their next fetch,
  without declaring a version

### Requirement: Two consumption styles are in use

A module SHALL be consumed in one of two styles, and SHALL be internally
consistent in the style it uses.

A **shim-based** module ships two files: a recipe file and a `.mod.just` shim
that sets a working directory and imports it. Its recipes are namespaced by
module, and they execute from the directory the shim names.

A **flat** module ships one file, consumed by import. Its recipes and variables
are prefixed with the module name, and they execute from the directory of the
justfile that imports them.

#### Scenario: Fetching a shim-based module

- **WHEN** a repository consumes the `go` module
- **THEN** it fetches both `go.mod.just` and `go.just`, and invokes recipes as
  `just go::fmt`

#### Scenario: Fetching a flat module

- **WHEN** a repository consumes the `md` module
- **THEN** it fetches a single file, and invokes recipes as `just md-fmt`

#### Scenario: Shim target is missing

- **WHEN** a repository consumes a shim-based module whose shim names a
  directory that repository does not contain
- **THEN** the module fails to load and its recipes cannot be run

### Requirement: Environment variable naming

Every environment variable a module reads SHALL be prefixed with `JUST_`.

#### Scenario: Module exposes a configurable value

- **WHEN** the `md` module allows its line wrap width to be overridden
- **THEN** the variable is named `JUST_MDFORMAT_WRAP`

### Requirement: Recipe filenames are globally unique

Recipe filenames SHALL be unique across all modules, because distribution
flattens every module's recipe file into a single directory.

#### Scenario: Modules collected for distribution

- **WHEN** every module's recipe file is packaged into one flat directory
- **THEN** no two files collide by name

### Requirement: Every module is documented

Each module SHALL document its recipes and every environment variable it reads.
Documentation SHALL live either in the repository root README or in a README
beside the module, and the root README SHALL make every module discoverable.

#### Scenario: Reading a module's documentation

- **WHEN** a developer wants to know which recipes a module provides
- **THEN** the root README either documents them or links to the module's own
  README

### Requirement: Formatters do not operate on the same paths

Where two modules format the same file type with different tools, they SHALL NOT
be configured to operate on the same paths, and a module that scans an entire
repository SHALL provide a way to exclude paths another module owns.

#### Scenario: Repository uses two markdown formatters

- **WHEN** a repository formats root markdown with one module and a
  documentation site with another
- **THEN** the paths each handles are disjoint, and neither reformats the
  other's files
