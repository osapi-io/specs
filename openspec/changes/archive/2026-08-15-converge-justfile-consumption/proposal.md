## Why

The `justfiles` capability records two consumption styles because both exist:
six modules ship a `.mod.just` shim with namespaced recipes, and one module
(`md`) ships a single file consumed by import with flat prefixed recipes.

Recording both was correct — specifying either would have made most of the
repository non-compliant the day it landed. But two styles is not a design, it
is a transition that was never finished. The shim style has a defect the flat
style does not: a shim sets a working directory, and if that directory does not
exist the module fails to load entirely, reporting an error that names neither
the directory nor the module. `docs.mod.just` points at `../../docs`, so any
repository without a `docs/` directory cannot use it at all.

A conversion of the `just` module to the flat style is already written and
passing, with nowhere to belong.

## What Changes

- **BREAKING** Converge on the flat, import-based consumption style. Modules
  ship one file, recipes and variables are prefixed with the module name, and no
  `.mod.just` shim exists.
- Convert the six modules still using the shim style: `just`, `go`, `bats`,
  `docs`, `docker`, `react`.
- Update every consuming repository's `fetch` recipe and call sites.

## Capabilities

### Modified Capabilities

- `justfiles`: the requirement recording two consumption styles becomes a
  requirement for one.

## Impact

- `osapi-justfiles`: six modules move into directories, convert to flat prefixed
  recipes, and lose their shims. The root README loses its remaining inline
  module sections.
- `gohai`, `nats-client`, `nats-server`, `osapi`: `fetch` recipes and call sites
  change. Their `just-lint` job fails from the moment a module they consume is
  converted until they are updated.
- `specs`: already consumes `md` in the flat style; its `just` module usage
  changes.
