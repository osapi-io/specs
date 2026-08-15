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

A module SHALL define every variable it references, with a default, so that it
parses and lints on its own. A module SHALL NOT reference a variable it expects
its consumer to declare.

A consuming repository SHALL override a default by setting the corresponding
environment variable in a committed dotenv file, loaded with `set dotenv-load`.
`env()` resolves against the process environment when just parses the file, and
a dotenv file is loaded before that — so the override reaches the module, while
an `export` in the consuming justfile does not.

#### Scenario: A module is checked on its own

- **WHEN** a repository lints each of its justfiles individually
- **THEN** every module parses, because none depends on a variable defined
  somewhere else

#### Scenario: A repository needs a different value

- **WHEN** a repository's application lives somewhere other than the default, or
  its coverage target differs
- **THEN** it sets the variable in its dotenv file, and the module keeps its
  default for every other repository

#### Scenario: Overriding a module default is proposed

- **WHEN** someone proposes assigning the variable again in the consuming
  justfile
- **THEN** it is declined: just rejects a variable with two definitions, and
  `set allow-duplicate-variables` suspends that check for the whole file to
  serve one variable

#### Scenario: No dotenv file is present

- **WHEN** a repository needs no overrides
- **THEN** it carries no dotenv file and every module uses its default

### Requirement: Fetched files are not linted

A repository's justfile checks SHALL exclude the directory holding fetched
modules, at every depth.

Fetched files are not the consuming repository's to correct, and a fault in one
is fixed upstream rather than locally.

#### Scenario: A repository fetches modules into a subdirectory

- **WHEN** a repository fetches modules below its root, such as into a nested
  application directory
- **THEN** those files are excluded from linting as well as the ones at the root

#### Scenario: A fetched module is malformed

- **WHEN** a lint pass would fail on a fetched module
- **THEN** the exclusion keeps the consuming repository green and the module is
  corrected upstream, where the repository that owns it lints it
