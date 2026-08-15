## Context

See proposal.md - Why.

`osapi-justfiles` distributes shared `just` recipes to every osapi-io
repository. Consumers fetch raw files over HTTP into a gitignored `.just/`
directory and wire them into a local `justfile`. There is no versioning
handshake: a consumer always fetches from `main`.

Two consumption styles exist today. Five modules (`go`, `bats`, `docs`,
`docker`, `react`) use `mod?` pointing at a `*.mod.just` shim that sets
`working-directory` and imports the real recipe file, producing namespaced
recipes (`just go::fmt`). Two modules (`md`, `just`) use `import?` directly with
flat prefixed recipes (`just md-fmt`).

The files are also published as a scratch Docker image so consumers can copy
them without network access at build time.

## Goals / Non-Goals

**Goals**

- One way to write a module, so new modules do not inherit whichever pattern was
  copied.
- Modules that work in any repository regardless of its directory layout.
- Reproducible formatting output across developer machines and CI.

**Non-Goals**

- Versioned releases of the shared recipes. Consumers fetch `main`; pinning to
  tags or commit SHAs is a separate problem (see Open Questions).
- Documenting how each consuming repository wires modules up. That requires
  those repositories to be specified first.
- Replacing `just` with another task runner.

## Decisions

### Consume with `import?`, not `mod?`

`mod?` requires a shim whose sole job is `set working-directory`. That directory
must exist or the module fails to load entirely — `just` cannot `chdir` into it
and reports a misleading `could not find the shell` error. `docs.mod.just`
points at `../../docs`, so any repository without a `docs/` directory cannot use
that module at all, no matter how its recipes are configured.

`import?` has no shim, no working-directory indirection, and recipes run from
the importing justfile's directory — which is what a repository-wide operation
wants. It also halves the number of files fetched per module.

*Alternative considered:* keep `mod?` and make each shim tolerate a missing
directory. `just` offers no such tolerance; the failure is at config load.

*Alternative considered:* keep `mod?` and give every repository the directories
the shims expect. This forces empty scaffolding into repositories purely to
satisfy the tooling.

### Prefix recipes and variables with the module name

`import` is textual: everything lands in one namespace shared with the consuming
justfile. Without prefixes, two modules defining `fmt` collide, and generic
variable names like `wrap` or `excludes` collide silently — the second
definition wins with no error.

Prefixing also reads better at the call site: `just md-fmt-check` over
`just md::fmt-check`.

*Alternative considered:* keep `mod?` purely for its namespacing. That brings
back the working-directory shim, which is the defect being removed. Namespacing
is not worth reintroducing a failure mode that makes modules unusable in some
repositories.

*Alternative considered:* prefix recipes but leave variables unprefixed, on the
grounds that variables are internal. They are not — `import` is textual, so a
module variable named `wrap` silently overwrites, or is overwritten by, any
other `wrap` in scope. The failure is silent and produces wrong output rather
than an error.

*Trade-off:* namespacing came free with `mod?`; with `import?` it is a naming
discipline that must be maintained by convention.

### One directory per module, documenting itself

The root README carried every module's recipe table inline and grew with each
addition. Co-locating a README with its module keeps documentation next to the
code it describes and makes the root README an index.

Module recipe files keep their distinguishing name (`md/md.just`, not
`md/recipes.just`) because the Docker image flattens all recipe files into a
single directory. A shared generic filename would collide there.

*Alternative considered:* group modules by domain (`lang/go`, `docs/md`). The
modules are organized by toolchain, not domain, and the boundaries do not hold —
`md` and `docs` are both documentation but unrelated, and `just` belongs to no
domain at all. A taxonomy needing a `misc/` bucket on day one is the wrong
taxonomy. Revisit past roughly fifteen modules.

### Pin tool versions, including the language runtime

Pinning the tool alone is not sufficient when its available options depend on
the runtime. `mdformat`'s `--exclude` flag exists only on Python 3.13 and newer;
with the same pinned `mdformat` version, a 3.12 host rejects the flag outright.
This produced a check that passed locally and failed in CI with
`unrecognized arguments`.

Modules therefore pin the runtime as well, and the runner downloads it when
absent. The pin is overridable by environment variable for debugging.

*Alternative considered:* pin the tool but let the runtime float, and require
consuming repositories to provide a new enough one. That pushes an invisible
requirement onto every consumer and onto CI, where the runtime is whatever the
runner image ships. The failure it produces is the one already observed —
passing locally, failing in CI, with an error that names a flag rather than a
runtime.

*Alternative considered:* avoid the runtime-dependent flag entirely and filter
paths before invoking the tool. That works, but re-implements the tool's own
path handling in shell for every module that needs it, and the filtering logic
then has to be maintained per module.

### Formatters must not overlap

`md` uses mdformat and `docs` uses prettier. They produce different output for
the same input, so pointing both at one file makes each undo the other's work on
every run. `md` scans the whole repository by default, so a repository with a
documentation site must exclude that path explicitly.

*Alternative considered:* standardize on one formatter everywhere. Prettier is
already embedded in the Docusaurus toolchain with its own config file, and
mdformat is materially simpler for repositories with no JavaScript at all.
Consolidation is possible later but is not required to remove the ambiguity.

## Risks / Trade-offs

- **Consumers break on merge.** The `.mod.just` URLs stop resolving and `::`
  recipe names disappear at once. → Migrate one module at a time, and update
  consuming repositories in the same session as the module they depend on.

- **Prefix discipline is unenforced.** Nothing rejects a module that defines an
  unprefixed recipe or variable. → Collisions surface as silently wrong
  behavior, not errors. Worth a lint check later.

- **Fetches are not atomic or versioned.** A consumer that fetches while a
  breaking change is merging gets a mixture. → Small, self-contained module
  changes; see Open Questions on pinning.

- **Raw file hosting is cached.** After a merge, the raw endpoint can serve
  stale content for several minutes, so a downstream CI run immediately after a
  merge may fetch the previous version and fail confusingly. → Re-run after the
  cache expires; pinning would remove this entirely.

- **Distribution packaging must track the layout.** The image build must include
  nested module directories; its ignore rules currently cover exactly one level
  of nesting. → Deeper nesting requires updating them.

## Migration Plan

1. `md` and `just` already conform and serve as reference implementations.
1. Convert the remaining five modules one at a time, each moving into a
   directory, gaining a README, converting to flat prefixed recipes, and
   dropping its shim.
1. After each module converts, update every consuming repository's `fetch`
   recipe and call sites before converting the next.
1. Remove the inline module sections from the root README as each is converted,
   leaving only the index table.

Rollback for any step is reverting the module's directory and shim; consumers
pinned to nothing will pick the old layout back up on their next fetch.

## Open Questions

- Should consumers fetch from `main` or from a tag/commit SHA? Pinning removes
  both the stale-cache failure and the mid-merge mixture risk, at the cost of an
  explicit bump to receive fixes. This does not change the requirements above
  and can be decided separately.
- Should an automated check enforce the prefix conventions, or is review
  sufficient?
