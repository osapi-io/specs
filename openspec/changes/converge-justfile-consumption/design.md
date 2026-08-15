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

### Modules ship defaults; consumers override them

`set allow-duplicate-variables := true` is just's mechanism for overriding a
variable an import defined, and it is what this design uses. Every property
wanted holds at once:

|                                             |                             |
| ------------------------------------------- | --------------------------- |
| `just go-cov-check` run by name             | uses the repository's value |
| `just test`, reaching it as a child process | same value                  |
| `just go_coverage_target=95 go-cov-check`   | 95                          |
| module lints on its own                     | passes                      |
| consuming justfile lints                    | passes                      |

Earlier revisions of this design forbade the setting, on the grounds that it
suspends the duplicate-definition check for the whole file. That reasoning cost
more than it saved. Every alternative tried in its place failed on something
real:

- **The consumer declares the variable and the module does not.** The module
  then references something it does not define, so the repository publishing it
  cannot parse or lint the file at all.
- **The module reads `env()` and the consumer exports it.** `export` reaches
  child processes but not the parse of its own file, so `just react-fmt-check`
  used the default while `just test` used the repository's value.
- **A committed dotenv file.** Works, and puts a value in a second file when the
  justfile could state it.
- **Excluding the affected modules from the format check.** Exempts the files
  most worth checking.
- **Format-checking them through a generated harness that supplies the
  variables.** Works, and is machinery to avoid a one-line setting.

What the setting actually gives up is narrow: inside a justfile that sets it, an
accidental duplicate assignment no longer errors. In a file whose purpose is to
import modules and override their defaults, that is close to free — and it is
the only thing that makes a recipe behave the same however it is invoked.

### Two modules had no consumers

Scoping the remaining conversions turned up that half of them are dead.

`bats` is fetched by no repository, and no `.bats` file exists anywhere in the
organization. It appears only in the root README, as an example of consuming a
module.

`docker` is loaded by `osapi` and nothing invokes its recipes; images are
published by goreleaser. Its `dockerfile` variable defaults to
`Dockerfile.local`, and `osapi` has `Dockerfile` and `Dockerfile.dev` — so the
one repository that loads it could not have run it successfully.

Converting them would apply the same care as a live module to code nothing runs,
and would leave two more files that every consumer fetches. Removing them leaves
`converge` with two real conversions, `docs` and `just`.

*Alternative considered:* convert them for consistency, so every module has the
same shape. Consistency across modules nobody runs is not worth the fetch, the
README, or the next person's time reading them.

*Alternative considered:* fix `docker` and keep it, since image publishing is
plausible future work. Its recipes are two lines wrapping `docker build` and
`docker push`; if that need returns it is cheaper to write than to have carried.

### Split docs and md by path, not by activity

`docs.just` does two unrelated things: it runs a Docusaurus site — build, start,
serve, deploy, generate — and it formats markdown with prettier. Four
repositories fetch it only for `docs::fmt`, and `md` exists to format markdown.

The obvious split was by activity: `docs` builds the site, `md` formats
everything. That breaks on content. `osapi`'s site contains `.mdx` files and
component syntax — `<DocCardList />`, `import` statements — which mdformat
cannot parse and would mangle. Prettier can, because Docusaurus is a prettier
ecosystem.

So the boundary is the path. `docusaurus` owns its site directory completely,
including formatting it, because the tooling that builds that content is also
the tooling that can format it. `md` owns everything else and excludes that
directory. Each file has exactly one formatter, and neither module needs to know
what the other does beyond where it stops.

The rename follows from that: `docs` names a location, and a repository can hold
documentation without a site. `docusaurus` names the thing the module manages,
so a reader can tell whether their repository needs it.

Both take the path as configuration. A repository states where its site lives,
and the exclusion in `md` uses the same value.

*Alternative considered:* have `md` format the site too, with prettier dropped
entirely. It would reformat every `.md` in the site and cannot handle the `.mdx`
files at all.

*Alternative considered:* keep formatting in `docs` and have `md` used only by
repositories without a site. Every repository here has a site, so `md` would
have no consumers but `specs`.

### Converting a consumer is more than its recipes

`gohai` was the first library moved from prettier to `md`, and the module swap
was the easy part. What review caught afterwards was everything the swap
implied: `CONTRIBUTING.md` still told contributors that markdown is formatted
with Prettier via Bun and showed `just docs::fmt`, both of which the same change
had removed.

That is not a new rule — `correct-documentation-drift` already requires
documentation to name the tools a repository installs. It was missed because the
task list said "update consumers" and left what that means to whoever was doing
it.

So the task list now enumerates it: justfile, workflows, deleted configuration,
`.mise.toml`, the contributing guide, and the reference links in whatever was
touched. Six steps, of which two are documentation and were the two skipped.

The same pass turned up that `gohai`'s guide had four references with no
definition, left over from the earlier `development.md` to `CONTRIBUTING.md`
conversion. Those rendered as literal text and had done for some time. Checking
them is now part of converting a consumer, because a change that rewrites a
guide is the moment its links are read.
