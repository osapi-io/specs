## Why

`osapi-justfiles` is consumed by every repository in the organization, but its
design has never been written down. The result is drift: two different module
consumption styles, env vars that follow the stated convention in seven cases
and ignore it in two, and modules whose documentation lives in a root README
that grows without bound. New modules are written by copying whichever existing
module the author looked at first.

Nothing records which of those patterns is intentional, so every change is a
judgment call and inconsistency compounds.

## What Changes

- Establish the `justfiles` capability describing how shared recipes are
  structured, consumed, named, and documented.
- Adopt directory-per-module as the required layout: each module owns a
  directory containing its recipe file and a README that documents it. The root
  README indexes them rather than documenting them inline.
- Adopt `import?` with flat, prefixed recipe names as the required consumption
  style, replacing `mod?` with `::` namespacing. This removes the `.mod.just`
  shim and its `set working-directory`, which made modules fail outright in
  repositories lacking the directory the shim pointed at.
- Require the `JUST_` prefix on every environment variable, matching the
  convention already stated in `CLAUDE.md`.
- Require that a module pin the versions of any tool it invokes, including the
  language runtime where tool behavior depends on it.
- **BREAKING** Migrate the five modules still using `mod?` (`go`, `bats`,
  `docs`, `docker`, `react`). Consuming repositories must update their `fetch`
  recipes and call sites.

Documenting how each consuming repository wires these modules up is out of
scope; that belongs to a later capability once those repositories are themselves
documented.

## Capabilities

### New Capabilities

- `justfiles`: how shared just recipes are structured, consumed, named,
  versioned, and documented across osapi-io.

### Modified Capabilities

None. This is the first capability in the corpus.

## Impact

- `osapi-justfiles`: five modules move into directories and convert to flat
  recipes; each gains a README; the root README becomes an index.
- Consuming repositories (`osapi`, `gohai`, `nats-client`, `nats-server`,
  `specs`): `fetch` recipes and call sites change. Their `just-lint` job fails
  until updated, since the old `.mod.just` URLs stop resolving.
- `md` and `just` already follow the target design and serve as the reference
  implementations.
