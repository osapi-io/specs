## Why

`osapi-justfiles` is consumed by every repository in the organization, but its
architecture has never been written down. Nothing records how a module is
distributed, how a consumer wires it up, or which conventions are deliberate, so
every change to it is a judgment call and new modules are written by copying
whichever existing module the author looked at first.

The absence has already produced drift. Two consumption styles are in use.
Environment variables followed the stated `JUST_` convention in seven cases and
ignored it in two until recently. One module documents itself; the rest are
documented in a root README that grows with each addition.

Writing the architecture down is a prerequisite for changing it deliberately.

## What Changes

- Establish the `justfiles` capability, recording how shared recipes are
  distributed, consumed, named, and documented as of today.
- Record that two consumption styles are in use: six modules ship a `.mod.just`
  shim with namespaced recipes, and one module (`md`) ships a single file
  consumed by import with flat prefixed recipes.
- Record the constraints that hold across every module: the `JUST_` prefix on
  environment variables, globally unique recipe filenames, discoverable
  documentation, and non-overlapping formatters.
- Record the known failure mode of the shim-based style, where a module cannot
  load at all in a repository lacking the directory its shim names.

Nothing is migrated by this change, and no module changes. Converging on a
single consumption style is a separate change, so that the architecture is
recorded before it is altered rather than after.

Documenting how each consuming repository wires these modules up is also out of
scope; that belongs to a later capability once those repositories are themselves
documented.

## Capabilities

### New Capabilities

- `justfiles`: how shared just recipes are distributed, consumed, named, and
  documented across osapi-io.

### Modified Capabilities

None. This is the first capability in the corpus.

## Impact

- `osapi-justfiles`: no code change. This change records what is already there.
- Consuming repositories (`osapi`, `gohai`, `nats-client`, `nats-server`,
  `specs`): no change. They are affected only by the migration change that
  follows.
