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

### Running a recipe by name has to work

Three properties were wanted at once: a developer can run `just react-fmt-check`
directly, no repository carries an extra configuration file, and the repository
owning the modules can lint each module on its own. just makes at most two of
them available, because it resolves a variable when it parses the file.

- The consuming justfile declares the variable. Running the recipe by name
  works. The module cannot be parsed alone.
- The module defines the variable and the consumer exports an override. The
  module parses alone. Running the recipe by name silently uses the default,
  because `export` populates the environment of recipes rather than of the parse
  — so `just test` and `just react-fmt-check` disagree.
- The consumer commits a dotenv file. Everything works, at the cost of a second
  file holding a value the justfile could state.

Running a recipe by name is what a developer does, and a command that means two
different things depending on how it was reached is worse than a module that
needs its consumer present to parse. So the consumer declares, and the two
modules that take consumer configuration are excluded by name from the owning
repository's per-file check.

That exclusion is a real cost and worth stating plainly: `go/go.just` and
`react/react.just` are not format-checked. What protects them is that six
repositories load them on every run, so an error surfaces immediately and
everywhere rather than quietly.

*Alternative considered:* the consuming justfile wraps each module recipe it
uses, so the name resolves locally. It is a wrapper per recipe per repository,
maintained by hand, to restore behaviour the recipe already had.

*Alternative considered:* `set allow-duplicate-variables`, letting the module
ship a default the consumer reassigns. It suspends the duplicate check for every
variable in the file to serve one.
