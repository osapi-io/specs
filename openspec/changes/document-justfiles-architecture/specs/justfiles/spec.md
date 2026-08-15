## Purpose

Defines how shared `just` recipes are structured, consumed, named, versioned,
and documented, so that every osapi-io repository wires up the same tooling in
the same way and a new module can be written without guessing.

## ADDED Requirements

### Requirement: Module directory layout

Each shared module SHALL live in its own directory containing its recipe file
and a README documenting it. The recipe file SHALL be named after the module so
that filenames remain unique when modules are flattened into a single directory
by downstream packaging.

#### Scenario: Adding a new module

- **WHEN** a new shared module named `foo` is added
- **THEN** it is created as `foo/foo.just` with a companion `foo/README.md`

#### Scenario: Two modules packaged together

- **WHEN** modules are collected into one flat directory for distribution
- **THEN** no two module recipe files collide by name

### Requirement: Import-based consumption

Modules SHALL be consumed with `import?` rather than `mod?`, and SHALL NOT
require a shim file that sets a working directory. Recipes SHALL execute from
the directory of the justfile that imports them.

A module SHALL be usable by a repository regardless of which subdirectories that
repository happens to contain.

#### Scenario: Repository without a docs directory

- **WHEN** a repository with no `docs/` directory imports a module
- **THEN** the module loads and its recipes run successfully

#### Scenario: Fetching a module

- **WHEN** a consuming repository fetches a module
- **THEN** exactly one file is retrieved for that module, with no companion shim
  file required

### Requirement: Prefixed recipe names

Recipes exported by a module SHALL be prefixed with the module name and
separated by hyphens. Because imported recipes share a single namespace with the
consuming justfile, module-level variables SHALL also be prefixed.

#### Scenario: Invoking a module recipe

- **WHEN** a consumer runs the format check from module `md`
- **THEN** the recipe is invoked as `just md-fmt-check`

#### Scenario: Two modules defining the same concept

- **WHEN** modules `md` and `just` both provide formatting recipes
- **THEN** they expose `md-fmt` and `just-fmt` respectively, and neither shadows
  the other

### Requirement: Environment variable naming

Every environment variable a module reads SHALL be prefixed with `JUST_`.

#### Scenario: Module exposes a configurable value

- **WHEN** module `md` allows the line wrap width to be overridden
- **THEN** the variable is named `JUST_MDFORMAT_WRAP`

### Requirement: Pinned tool versions

A module that invokes an external tool SHALL pin that tool's version. Where the
tool's available options depend on its language runtime, the module SHALL pin
the runtime version as well.

#### Scenario: Runtime affects available flags

- **WHEN** a tool's command-line flag exists only on a newer language runtime
- **THEN** the module pins the runtime so the flag is present on every machine
  and in CI

#### Scenario: Upstream releases a new tool version

- **WHEN** the tool publishes a new release
- **THEN** consuming repositories are unaffected until the pin is changed

### Requirement: Self-documenting modules

Each module's README SHALL document its recipes, its requirements, what it
excludes, and every environment variable it reads. The repository root README
SHALL index the modules and link to them rather than documenting them inline.

#### Scenario: Reading a module's documentation

- **WHEN** a developer wants to know what a module does
- **THEN** the module's own README lists its recipes and environment variables

#### Scenario: Adding a module to the index

- **WHEN** a new module is added
- **THEN** the root README gains a row linking to it, and does not restate its
  recipe table

### Requirement: Non-overlapping formatters

Two modules that format the same file type SHALL NOT be configured to operate on
the same paths, and each SHALL provide a means of excluding paths owned by
another.

#### Scenario: Repository uses two formatters

- **WHEN** a repository formats root markdown with one module and a
  documentation site with another
- **THEN** the paths handled by each are disjoint, and neither reformats the
  other's files
