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

### Requirement: A module defines its defaults, a consumer overrides them

A module SHALL define every variable it references, with a default, so that it
parses and lints on its own.

A consuming justfile that needs a different value SHALL set
`set allow-duplicate-variables := true` and assign the variable again. The later
assignment wins.

The assignment SHALL be a plain variable, not an environment variable. A
variable assigned in the consuming justfile is in scope when just parses it, so
a recipe behaves the same whether it is run by name, reached through another
recipe, or overridden on the command line.

#### Scenario: A developer runs a module recipe by name

- **WHEN** someone runs `just react-fmt-check` rather than `just test`
- **THEN** it uses the repository's value, because the assignment is in scope
  when just parses the justfile

#### Scenario: A repository is content with the defaults

- **WHEN** a repository's values match every module default
- **THEN** it assigns nothing and does not set `allow-duplicate-variables`

#### Scenario: A value is needed for one invocation

- **WHEN** someone wants a different value for a single run
- **THEN** they override it on the command line, as
  `just <name>=<value> <recipe>`

#### Scenario: The module is checked on its own

- **WHEN** the repository publishing the modules lints each file individually
- **THEN** every module parses, because each defines what it references, and
  none is excluded from the check

### Requirement: Overriding uses assignment, not the environment

A consuming justfile SHALL NOT configure a module by exporting an environment
variable that the module reads with `env()`.

`export` does not reach the parse of the file it appears in, but does reach
child processes. A module recipe invoked by name would use the default while the
same recipe reached through another recipe used the exported value — one command
with two answers, depending on how it was called.

A module MAY read `env()` for a value that genuinely varies by environment
rather than by repository, since nothing in the repository can state it.

#### Scenario: An export is proposed for a per-repository value

- **WHEN** someone proposes `export JUST_X := "y"` in a consuming justfile to
  configure a module
- **THEN** it is declined, because the value would apply only when the recipe is
  reached as a child process

#### Scenario: A value belongs to the environment

- **WHEN** a value differs between a developer machine and continuous
  integration rather than between repositories
- **THEN** the module reads it with `env()` and ships a default

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
