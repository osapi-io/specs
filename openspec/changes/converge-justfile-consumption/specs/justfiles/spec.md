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

### Requirement: A module is self-contained

A justfile SHALL NOT use `set allow-duplicate-variables`.

A module SHALL define every variable it references, so that it parses and lints
on its own. A module SHALL NOT reference a variable it expects its consumer to
declare.

A variable whose value may differ between repositories SHALL read `env()` with a
default. A consuming repository SHALL override it by exporting the corresponding
environment variable in its justfile.

An `export` does not reach the parse of the file it appears in, so a consumer
cannot use it to change a variable in a module it imports directly. It does
reach child processes, and a consuming justfile invokes module recipes as child
processes — which is where the override takes effect.

#### Scenario: A module is checked on its own

- **WHEN** a repository lints each of its justfiles individually
- **THEN** every module parses, because none depends on a variable defined
  elsewhere

#### Scenario: A repository needs a different value

- **WHEN** a repository's application is not at the root, or its coverage target
  differs
- **THEN** its justfile exports the environment variable, and the module keeps
  its default for every other repository

#### Scenario: Overriding by reassignment is proposed

- **WHEN** someone proposes assigning the variable again in the consuming
  justfile
- **THEN** it is declined: just rejects a variable with two definitions, and
  `set allow-duplicate-variables` suspends that check for the whole file to
  serve one variable

#### Scenario: A value is computed rather than configured

- **WHEN** a variable is derived at run time, such as the repository root or the
  package list
- **THEN** it needs no environment variable, because no repository sets it

#### Scenario: The repository owning the modules lints them

- **WHEN** the repository that publishes the modules runs its own checks
- **THEN** it exports the same variables in its root justfile, so each module is
  checked with a real value rather than excluded

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
