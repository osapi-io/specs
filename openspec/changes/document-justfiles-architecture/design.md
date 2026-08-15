## Context

See proposal.md - Why.

`osapi-justfiles` distributes shared `just` recipes to every osapi-io
repository. Consumers fetch raw files over HTTP into a gitignored `.just/`
directory and wire them into a local `justfile`. There is no versioning
handshake: a consumer always fetches the default branch. The files are also
published as a scratch Docker image, which flattens every recipe file into one
directory.

As of this change, seven modules exist:

| Module                                          | Style     | Files                    | Documented  |
| ----------------------------------------------- | --------- | ------------------------ | ----------- |
| `md`                                            | `import?` | one file, in `md/`       | own README  |
| `just`, `go`, `bats`, `docs`, `docker`, `react` | `mod?`    | recipe file + shim, root | root README |

`md` is the newer of the two and the only one built that way. It was written
after the shim-based style caused a concrete failure, described below.

## Goals / Non-Goals

**Goals**

- Record the architecture as it exists, including its inconsistencies, before
  any of it is changed.
- Capture the failure modes already observed, so a later change is argued from
  evidence rather than preference.

**Non-Goals**

- Choosing between the two consumption styles. That is the next change.
- Migrating any module, or altering any consuming repository.
- Versioned releases of the shared recipes.
- Documenting how each consuming repository wires modules up.

## Decisions

### Record both consumption styles rather than mandate one

Six of seven modules use the shim-based style and one uses the flat style.
Writing either as a requirement would make most of the repository non-compliant
the moment the spec landed, and the corpus would describe an intention rather
than a system.

The spec therefore states that both styles exist, describes each contract
precisely, and records the shim style's failure mode as a scenario. Converging
on one style becomes a change that modifies this requirement, with the evidence
for the choice already recorded here.

*Alternative considered:* specify the flat style and treat the six shim-based
modules as non-compliant. That reads as the plan rather than the architecture,
and leaves the corpus false until a multi-repository migration finishes.

*Alternative considered:* specify the shim style, since it is what most modules
do, and treat `md` as the exception. That enshrines the style with the known
defect and requires rewriting the requirement almost immediately.

### Do not require version pinning

Only two of seven modules pin the versions of the tools they invoke — `md` pins
its formatter and language runtime, `go` pins its tool dependencies. The rest
install whatever is current.

Pinning is a good practice and one of the reasons `md` is reproducible, but it
is not currently true of the architecture, so the spec does not claim it.

*Alternative considered:* require it anyway, since it is obviously desirable.
That is the same error as mandating a consumption style — a requirement four
modules fail on the day it is written.

### Record the shim failure mode as a scenario, not a complaint

The shim sets `working-directory`; if that directory does not exist, `just`
cannot change into it and the module fails to load entirely, reporting
`could not find the shell` — an error that names neither the directory nor the
module. `docs.mod.just` points at `../../docs`, so any repository without a
`docs/` directory cannot use it at all.

This is recorded as a scenario under the consumption requirement, making it a
property of the architecture rather than an argument inside a design document
that the corpus will not retain.

*Alternative considered:* leave it out of the spec and describe it only here.
Design documents stay with their change; scenarios survive into the corpus. This
behavior is something a consumer will encounter, so it belongs where it
survives.

### Keep formatter non-overlap as a requirement

Two modules format markdown with different tools — `md` with mdformat, `docs`
with prettier — and they produce different output for the same input. A
repository pointing both at one path would have each undo the other's work on
every run. `md` scans the whole repository by default, so the exclusion
mechanism is load-bearing today, not aspirational.

*Alternative considered:* standardize on one formatter and remove the problem.
That is a real change to two modules and every repository that uses them, so it
cannot be recorded as though it were already true.

## Risks / Trade-offs

- **A spec describing two styles invites new modules to pick either.** →
  Recording the shim failure mode gives an author a reason to prefer the flat
  style without the spec mandating it.

- **Fetches are not atomic or versioned.** A consumer fetching while a change
  merges gets a mixture. → Small, self-contained module changes; see Open
  Questions on pinning.

- **Raw file hosting is cached.** After a merge, the raw endpoint can serve
  stale content for several minutes, so a downstream CI run immediately after a
  merge may fetch the previous version and fail confusingly. → Re-run after the
  cache expires; version pinning would remove this entirely.

- **Distribution packaging must track the layout.** The image build includes
  nested module directories, and its ignore rules cover exactly one level of
  nesting. → Deeper nesting requires updating them. This has not been verified
  by an image build.

## Migration Plan

None. This change alters no module and no consuming repository.

## Open Questions

- Should consumers fetch the default branch or a tag/commit SHA? Pinning would
  remove both the stale-cache failure and the mid-merge mixture risk, at the
  cost of an explicit bump to receive fixes.
- Should the conventions the spec does state — the `JUST_` prefix, unique
  filenames — be enforced by a check rather than review? The prefix convention
  was documented and still drifted, which suggests review alone is not enough.
