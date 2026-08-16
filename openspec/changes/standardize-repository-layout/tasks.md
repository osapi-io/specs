## 1. Record the standard

- [x] 1.1 Survey all nine active repositories for common files, README
  structure, and section vocabulary
- [x] 1.2 Write the `repo-standards` capability covering repository types,
  required files, contributing location, agent guidance, and README structure
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Convert osapi-justfiles

The first repository converted, and the reference for the rest.

- [x] 2.1 Consolidate `docs/contributing.md` and `docs/development.md` into a
  root `CONTRIBUTING.md`
- [x] 2.2 Add `AGENTS.md` carrying only agent-specific guidance, pointing to
  `CONTRIBUTING.md`
- [x] 2.3 Reduce `CLAUDE.md` to a pointer to `AGENTS.md`
- [x] 2.4 Update every inbound reference to the old `docs/` paths
- [x] 2.5 Confirm `just test` and CI pass

## 3. Boilerplate sweep

`LICENSE`, `AI_POLICY.md`, and `CODE_OF_CONDUCT.md` must be byte-identical
across every repository. Done as one pass rather than inside each conversion, so
a conversion pull request is only that repository's own work.

- [x] 3.1 Establish the canonical copies in `osapi-justfiles` — `osapi-io`
  wording, 2026 John Dewey, enforcement contact filled in
- [x] 3.2 `specs`
- [x] 3.3 `gohai`
- [x] 3.4 `nats-client`
- [x] 3.5 `nats-server`
- [x] 3.6 `osapi`
- [x] 3.7 `osapi-orchestrator`
- [x] 3.8 `osapi-ui`

## 4. Convert the remaining repositories

One repository per change, applying both the file layout and the README
structure for its type.

- [x] 4.1 `gohai` (Go library)
- [x] 4.2 `nats-client` (Go library)
- [x] 4.3 `nats-server` (Go library)
- [x] 4.4 `osapi-orchestrator` (Go library, pending the open question on its
  type)
- [x] 4.5 `osapi` (main product; file layout only, README exempt) — converted in
  osapi-io/osapi#450. The 917-line `CLAUDE.md` split by audience: contributor
  conventions to a root `CONTRIBUTING.md`, agent-specific guidance to
  `AGENTS.md`, and the nine-step domain walkthrough to its own site page.
  `CLAUDE.md` is now a pointer. Of the three competing contributing documents,
  `docs/CONTRIBUTING.md` and `ui/docs/contributing.md` were removed and
  `docs/docs/sidebar/development/contributing.md` reduced to a pointer.
  `ui/docs/architecture.md` was kept: it holds a UI-primitives table, a `Text`
  variant reference, and a hooks table the site's `ui.md` does not, so removing
  it would lose content. Folding it in belongs to `specify-documentation-homes`
- [x] 4.6 `osapi-ui` — not converted; recorded as deprecated instead
- [x] 4.7 `specs` (documentation) — its `CODE_OF_CONDUCT.md` named no
  enforcement contact, leaving no way to report a violation, and its `LICENSE`
  named `OSAPI` as copyright holder rather than `John Dewey`

## 5. Pin the tools whose output is checked

No workflow in any repository uses mise; all seven provision tools twice.

- [x] 5.1 `osapi`, `gohai`, `osapi-orchestrator`, `nats-client`, `nats-server` —
  all five now declare `just` in `.mise.toml`, so it no longer comes from the
  developer's system. `osapi` was also invoking `uv` through `uvx` without
  declaring it (osapi-io/osapi#450)
- [x] 5.1a Record which version `extractions/setup-just` installs. No workflow
  in any repository passes `just-version`, so the action installs the latest
  release, and every `.mise.toml` declares `just = "latest"`. Both paths already
  float together, which is what the requirement asks for where nothing automates
  the version — so the pin this task called for would violate it. Recorded
  rather than applied
- [x] 5.2 Confirm `.mise.toml` and the workflow resolve to the same version for
  every tool, floating or pinned. `just`, `bun`, and `uv` float on both sides;
  `node` is `22` in both. `go` did not agree, and had already diverged: mise
  supplied 1.25.7 while continuous integration built with 1.26.6, so every
  contributor formatted and linted on a different toolchain than the one
  checking the result. All five Go repositories now declare `go = "latest"`,
  matching the workflows' `go-version: stable`
- [x] 5.3 Confirm no tool is pinned in one path and floating in the other.
  Nothing bumps `.mise.toml`, so the requirement's own answer is that both paths
  float. `go` now floats on both sides in all five Go repositories, and every
  suite passes on 1.26.6
- [x] 5.5 `osapi-orchestrator` — `actions/setup-go@v6` while every other
  repository uses `@v7`
- [x] 5.6 Confirm Dependabot raises each new pin, in both locations. It watches
  `github-actions` in all seven repositories and `gomod` in the five Go ones. It
  does not watch `.mise.toml`, and no ecosystem exists that would — which is why
  the tools declared there float rather than pin

## 6. Resolve the deprecated repositories

- [x] 6.1 `osapi-io-taskfiles` — dropped. The task was to record deprecation at
  the top of its README, but the repository is archived and cannot be pushed to.
  Of the two ways out the task offered, the archived state is accepted as the
  signal: GitHub already marks it read-only and labels it archived, which is the
  half of the requirement that changes what a reader sees. Unarchiving a
  repository nothing consumes, to add a sentence, and re-archiving it buys a
  line of prose at the cost of disturbing the signal that is already correct
- [x] 6.2 Archive `osapi-sdk` on GitHub
- [x] 6.3 Archive `osapi-ui` on GitHub
- [x] 6.4 Archive `osapi-io-taskfiles` on GitHub

## 6a. Correct the react module override

- [x] 6a.1 `osapi-justfiles` — the `react` module takes `react_dir` as
  configuration and fails at parse time when a consumer omits it, rather than
  relying on a shim to set a working directory
- [x] 6a.2 `osapi` — `.just/remote/react.mod.just` is gone and nothing under
  `.just/` is tracked; `.gitignore` ignores `.just/remote/*` with no exception.
  The root justfile sets `react_dir := "ui"` directly

## 7. Verification

- [x] 7.1 Confirm every in-scope repository carries the required files. All
  seven carry `README.md`, `LICENSE`, `AI_POLICY.md`, `CODE_OF_CONDUCT.md`,
  `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, and `.mise.toml`
- [x] 7.2 Confirm no repository still contains `docs/contributing.md` or
  `docs/development.md`. None does. `osapi` was the last, and its two remaining
  copies under `ui/docs/` went with the conversion (osapi-io/osapi#450)
- [x] 7.3 Confirm no cross-repository link still points at the old paths. The
  inbound links in `osapi`'s two architecture pages now point at the root
  `CONTRIBUTING.md`, and the site builds with no broken link. One stale pointer
  was found and fixed in the other direction: `osapi-orchestrator`'s `AGENTS.md`
  still named the removed `docs/plans/` (osapi-io/osapi-orchestrator#74)
- [x] 7.4 Confirm each README uses only vocabulary sections, in order. Five of
  six audit clean. `osapi-justfiles` did not: `Usage` carried the `Install`
  emoji, `Available Recipes` was an invented name for a table of links that the
  `Documentation` section covers, and `Documentation` — required for a utility
  repository — was missing (osapi-io/osapi-justfiles#60). `gohai` and
  `osapi-orchestrator` carry subject-specific sections, all placed before
  `Contributing` as the requirement permits
- [x] 7.5 Confirm `LICENSE`, `AI_POLICY.md`, and `CODE_OF_CONDUCT.md` are
  byte-identical everywhere. `AI_POLICY.md` and `CODE_OF_CONDUCT.md` are, in all
  seven. `LICENSE` was not: `specs` carried a differently titled and differently
  wrapped variant, which this change replaces with the canonical copy. The rest
  differ only on the copyright year, as the requirement allows — 2024 for
  `osapi`, 2025 for the two NATS libraries, 2026 for the rest
- [x] 7.6 Confirm no `.mise.toml` and no workflow floats a tool whose output a
  check compares. Every tool now floats on both paths together, which is what
  the requirement asks where nothing automates the version. The case that
  mattered was `go`, whose toolchain `go-fmt-check` compares against: it was
  pinned locally and floating in continuous integration, and the two had already
  parted
- [x] 7.7 Confirm `just test` locally and CI agree on every repository. Run in
  all seven on `main` after the Go float landed: `gohai`, `nats-client`,
  `nats-server`, `osapi-orchestrator`, `osapi`, `osapi-justfiles`, and `specs`
  all pass locally, on the same toolchain continuous integration uses
- [x] 7.8 Confirm every deprecated repository is archived on GitHub.
  `osapi-sdk`, `osapi-ui`, and `osapi-io-taskfiles` all report archived
- [x] 7.9 Confirm no tracked file was removed on the basis of its path without
  its content being read. Every file removed in osapi-io/osapi#450 was read
  first, and that is what kept `ui/docs/architecture.md`: its path matched the
  stale osapi-ui leftovers beside it, but its contents hold a component
  reference the site does not carry
