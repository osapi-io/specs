## REMOVED Requirements

### Requirement: Two consumption styles are in use

**Reason**: This change converges every module on one style, so a requirement
permitting two is withdrawn rather than revised. Its premise — that shim-based
and flat modules are both legitimate — is what the change removes.

**Migration**: Every shim-based module is converted to a single imported recipe
file, and its consumers switch from `mod?` to `import?`. Recipes previously
invoked as `just <module>::<recipe>` are invoked as `just <module>-<recipe>`.
Modules needing a specific subdirectory take it as configuration instead of
inheriting it from a shim's working directory.

## ADDED Requirements

### Requirement: Import-based consumption

Modules SHALL be consumed with `import?`, and SHALL NOT ship a shim file that
sets a working directory. A module SHALL consist of a single recipe file.

Recipes SHALL execute from the directory of the justfile that imports them, so a
module is usable by a repository regardless of which subdirectories that
repository contains.

#### Scenario: Repository without a docs directory

- **WHEN** a repository with no `docs/` directory imports a module
- **THEN** the module loads and its recipes run successfully

#### Scenario: Fetching a module

- **WHEN** a consuming repository fetches a module
- **THEN** exactly one file is retrieved for that module

#### Scenario: A shim is proposed

- **WHEN** a module needs to operate on a specific subdirectory
- **THEN** it takes that path as configuration rather than as a working
  directory set by a shim

### Requirement: A consumer declares what it configures

A justfile SHALL NOT use `set allow-duplicate-variables`.

Where a module's behaviour varies per consuming repository, the module SHALL
reference the variable without defining it, and the consuming justfile SHALL
declare it. A module SHALL NOT ship a default for such a variable.

A flat import shares one scope, so a module default cannot be overridden — just
rejects a variable with two definitions. `set allow-duplicate-variables` would
permit it, at the cost of disabling that check for every variable in the file.
Requiring the declaration instead keeps the check and makes the value visible in
the repository it applies to.

A module MAY read `env()` for values that vary by environment rather than by
repository, since those are set where there is no justfile to edit.

#### Scenario: A module needs a per-repository value

- **WHEN** a module's recipes depend on a path or threshold that differs between
  repositories
- **THEN** the module references the variable and each consuming justfile
  declares it

#### Scenario: A consumer omits a required declaration

- **WHEN** a consuming justfile imports a module without declaring a variable
  that module references
- **THEN** it fails at parse time, rather than running against a default nobody
  chose

#### Scenario: Overriding a module default is proposed

- **WHEN** someone proposes shipping a default in a module and letting consumers
  override it
- **THEN** it is declined, because the override requires
  `set allow-duplicate-variables`, which suspends the duplicate check for the
  whole justfile to serve one variable

#### Scenario: A value varies by environment, not by repository

- **WHEN** a value differs between a developer machine and continuous
  integration rather than between repositories
- **THEN** the module reads it with `env()` and ships a default, because there
  is no justfile to edit in that environment

### Requirement: Fetched files are not linted

A repository's justfile checks SHALL exclude the directory holding fetched
modules, at every depth.

A module that references a variable its consumer declares cannot be parsed on
its own, so a per-file check reports an undefined variable rather than a
formatting fault. The files are also not the consuming repository's to correct.

#### Scenario: A repository fetches modules into a subdirectory

- **WHEN** a repository fetches modules below its root, such as into a nested
  application directory
- **THEN** those files are excluded from linting as well as the ones at the root

#### Scenario: A fetched module fails a standalone parse

- **WHEN** a lint pass parses a fetched module by itself and reports an
  undefined variable
- **THEN** the exclusion is the fix, not a change to the module
