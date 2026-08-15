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

### A module must lint on its own

The first attempt at per-repository configuration had the module reference a
variable and the consuming justfile declare it. It worked at runtime and was
wrong: `go/go.just` and `react/react.just` no longer parsed on their own, so
`osapi-justfiles` could not lint the files it owns. `just --fmt --check`
reported `Variable go_coverage_target not defined` — a design fault surfacing as
a formatting error.

That was missed because the repository's own lint passed in CI and failed
locally. CI installs just through an unpinned setup action; the version it
resolved does not reject undefined variables during a format check, and just
1.45 does. The same commit was green in one place and red in the other.

The mechanism that keeps modules self-contained is `set dotenv-load`. A dotenv
file is read before variables are evaluated, so `env()` sees it — which `export`
in a justfile never achieves, because `export` populates the environment of
recipes rather than of the parse.

```just
set dotenv-load := true
set dotenv-filename := '.justenv'

import? '.just/remote/go.just'
```

```
.justenv:  JUST_COVERAGE_TARGET=99.9
```

The module keeps `go_coverage_target := env("JUST_COVERAGE_TARGET", "100")`, so
it parses alone, lints alone, and needs no consumer cooperation to be checked.

*Alternative considered:* `set allow-duplicate-variables := true` and let the
consumer reassign. It suspends the duplicate check for every variable in the
file to serve one.

*Alternative considered:* exclude modules that need consumer variables from the
owning repository's lint. It exempts exactly the files most likely to be wrong.
