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

### Requirement: A consuming justfile declares module configuration

A justfile SHALL NOT use `set allow-duplicate-variables`.

Where a module's behaviour varies per repository, the module SHALL reference the
variable and the consuming justfile SHALL declare it. The module SHALL NOT
define it, because just rejects a variable with two definitions and the consumer
could then not set its own value.

A recipe SHALL work when invoked by name. Someone running
`just <module>-<recipe>` SHALL get the same result as running it through a
recipe that depends on it.

An `export` in the consuming justfile SHALL NOT be used for this. It does not
reach the parse of the file it appears in, so a recipe invoked by name falls
back to the module's default while the same recipe invoked through another
recipe — a child process — gets the exported value. Two answers for one command
is worse than either.

#### Scenario: A developer runs a module recipe by name

- **WHEN** someone runs `just react-fmt-check` rather than `just test`
- **THEN** it uses the repository's configured value, because the consuming
  justfile declares it and that declaration is in scope when just parses

#### Scenario: A module needs a per-repository value

- **WHEN** a module's recipes depend on a path or threshold that differs between
  repositories
- **THEN** the module references the variable and each consuming justfile
  declares it

#### Scenario: A consumer omits a required declaration

- **WHEN** a consuming justfile imports a module without declaring a variable it
  references
- **THEN** it fails at parse time, rather than running against a value nobody
  chose

#### Scenario: A value is the same everywhere

- **WHEN** a variable never varies between repositories, such as a tool version
  or an output directory
- **THEN** the module defines it with an `env()` default and no consumer
  declares anything

### Requirement: Modules taking consumer configuration are exempt from standalone linting

A module that references a variable its consumer declares SHALL be excluded from
the owning repository's per-file justfile check.

Such a module cannot be parsed alone, so the check reports an undefined variable
rather than a formatting fault. The exclusion SHALL be explicit and SHALL name
the modules it covers, so that it is visible rather than inferred.

#### Scenario: The owning repository lints its justfiles

- **WHEN** the repository publishing the modules runs its per-file check
- **THEN** modules taking consumer configuration are skipped by name, and every
  other justfile in the repository is checked

#### Scenario: A skipped module is malformed

- **WHEN** a module that is skipped by the format check contains an error
- **THEN** it surfaces the first time any consuming repository loads it, which
  is on the next run of that repository's checks

### Requirement: Module variables are namespaced

A module's variables SHALL be prefixed with the module's name.

A flat import shares one scope with the consuming justfile and every other
imported module, so an unprefixed name is a collision waiting for the second
module that wants it.

#### Scenario: Two modules want the same name

- **WHEN** more than one module needs a variable for a host, a port, or an image
  name
- **THEN** each prefixes it with its own module name, and both can be imported
  together

#### Scenario: A module is converted

- **WHEN** a shim-based module becomes flat
- **THEN** its variables are renamed with the module prefix in the same change,
  because the shim previously scoped them and the import does not

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
