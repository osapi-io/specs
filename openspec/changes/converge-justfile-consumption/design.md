## Context

See proposal.md - Why.

The `justfiles` capability records two consumption styles because both exist.
That was the right call when the architecture was documented — specifying either
would have made most of the repository non-compliant immediately. It leaves the
corpus describing a transition rather than a design.

A conversion of the `just` module to the flat style is already written and
passing as osapi-justfiles#39. It has been held because merging it would break
four consuming repositories with no specification covering the migration.

## Goals / Non-Goals

**Goals**

- One consumption style, so a module author has nothing to choose between.
- Remove the failure mode where a module cannot load in a repository that lacks
  a directory its shim names.

**Non-Goals**

- Changing what any recipe does. This is a change to how modules are consumed,
  not to their behavior.
- Converting consuming repositories to anything else while they are open.

## Decisions

### Converge on flat rather than on shims

The shim style has a defect the flat style does not: `set working-directory`
fails the entire module load when the directory is absent, with an error that
names neither the directory nor the module. The flat style has no equivalent
failure.

The cost is that `import` shares one namespace, so recipes and variables must be
prefixed by convention rather than namespaced by the tool.

*Alternative considered:* converge on shims, since six of seven modules use
them. That standardizes on the style with the known defect and requires every
repository to contain the directories every shim names.

*Alternative considered:* keep both indefinitely. Two styles means a module
author picks, and the record shows they pick whichever module they read first.

### Convert one module at a time

Every consuming repository fetches from the default branch, so a module
conversion breaks its consumers the moment it merges. Converting one module and
immediately updating its consumers keeps the broken window to one module rather
than six.

*Alternative considered:* convert all six at once and fix consumers after. That
leaves every repository's lint job failing simultaneously, and makes it
impossible to tell which conversion caused which failure.

## Risks / Trade-offs

- **Consumers break between a module converting and their update.** → One module
  at a time, consumers updated before the next module starts.

- **The raw file endpoint caches for several minutes.** A consumer updated
  immediately after a merge can still fetch the previous version. → Re-run after
  the cache expires; this is already recorded in the `justfiles` design.

- **Prefix discipline is unenforced.** Nothing rejects a module defining an
  unprefixed recipe or variable, and a collision is silent. → Already an open
  question on the `justfiles` capability.

## Migration Plan

For each module: move into a directory, add a README, convert to flat prefixed
recipes, delete the shim, remove its inline section from the root README. Then
update every consuming repository before starting the next module.

`just` is first, because its conversion is already written.

## Open Questions

- Should the fetch pin a tag or commit rather than the default branch? It would
  remove both the stale-cache failure and the broken window during conversion.
  Recorded on the `justfiles` capability and unanswered.

### A module must lint on its own, and export is how a consumer configures it

The first attempt had the module reference a variable and the consuming justfile
declare it. It ran correctly and was wrong: `go/go.just` and `react/react.just`
no longer parsed alone, so `osapi-justfiles` could not lint the files it owns.
`just --fmt --check` reported `Variable go_coverage_target not defined` — a
design fault surfacing as a formatting error. Consumers were unaffected
throughout, because they exclude fetched modules from linting.

The mechanism that resolves it is `export`, which behaves differently than it
first appears. It does not reach the parse of the file it appears in — which is
why `export JUST_COVERAGE_TARGET := "99.9"` in osapi's justfile seemed to do
nothing. It does reach child processes, and a consuming justfile invokes module
recipes as child processes rather than as dependencies, so the export lands
exactly where the module is parsed.

The module therefore keeps `env("JUST_COVERAGE_TARGET", "100")` and parses
alone; the consumer exports the variable and gets its own value.

The same applies to the repository that owns the modules. `osapi-justfiles`
exports the variables in its root justfile, so its own lint checks each module
with a real value rather than skipping it.

*Alternative considered:* `set allow-duplicate-variables` and reassignment in
the consumer. It suspends the duplicate check for every variable in the file.

*Alternative considered:* a committed dotenv file per repository. It works and
adds a second file to look in for a value the justfile could state.

*Alternative considered:* exempt the two modules from the owning repository's
lint. It exempts the files most worth checking.
