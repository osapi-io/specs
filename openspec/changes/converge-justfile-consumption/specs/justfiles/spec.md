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
