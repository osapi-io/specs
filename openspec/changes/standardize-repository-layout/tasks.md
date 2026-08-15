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

- [ ] 4.1 `gohai` (Go library)
- [ ] 4.2 `nats-client` (Go library)
- [ ] 4.3 `nats-server` (Go library)
- [ ] 4.4 `osapi-orchestrator` (Go library, pending the open question on its
  type)
- [ ] 4.5 `osapi` (main product; file layout only, README exempt) — the only
  repository with neither a root `CONTRIBUTING.md` nor `AGENTS.md`, a 917-line
  `CLAUDE.md`, and three competing contributing documents:
  `docs/CONTRIBUTING.md` (60 lines),
  `docs/docs/sidebar/development/contributing.md` (109), and
  `ui/docs/contributing.md`
- [x] 4.6 `osapi-ui` — not converted; recorded as deprecated instead

## 5. Pin the tools whose output is checked

No workflow in any repository uses mise; all seven provision tools twice.

- [ ] 5.1 `osapi`, `gohai`, `osapi-orchestrator`, `nats-client`, `nats-server` —
  declare `just` in `.mise.toml`. None does, so it comes from the developer's
  system: Homebrew's 1.45.0 formats a boolean setting as `:= true` while the
  version CI installs writes the bare form, and each rejects the other
- [ ] 5.1a Record which version `extractions/setup-just` installs, and declare
  that version, so `mise install` and CI agree
- [ ] 5.2 Confirm `.mise.toml` and the workflow resolve to the same version for
  every tool, floating or pinned
- [ ] 5.3 Confirm no tool is pinned in one path and floating in the other
- [x] 5.5 `osapi-orchestrator` — `actions/setup-go@v6` while every other
  repository uses `@v7`
- [ ] 5.6 Confirm Dependabot raises each new pin, in both locations

## 6. Resolve the deprecated repositories

- [ ] 6.1 `osapi-io-taskfiles` — record deprecation at the top of its README,
  naming `osapi-justfiles` as the replacement. Blocked: the repository is now
  archived and cannot be pushed to. Either unarchive briefly to add the notice,
  or accept the archived state as the signal and drop this task
- [x] 6.2 Archive `osapi-sdk` on GitHub
- [x] 6.3 Archive `osapi-ui` on GitHub
- [x] 6.4 Archive `osapi-io-taskfiles` on GitHub

## 6a. Correct the react module override

- [ ] 6a.1 `osapi-justfiles` — make the `react` module take its directory as
  configuration instead of a shim setting a working directory
- [ ] 6a.2 `osapi` — drop the tracked `.just/remote/react.mod.just` and its
  `.gitignore` exception once the module is configurable

## 7. Verification

- [ ] 7.1 Confirm every in-scope repository carries the required files
- [ ] 7.2 Confirm no repository still contains `docs/contributing.md` or
  `docs/development.md`
- [ ] 7.3 Confirm no cross-repository link still points at the old paths
- [ ] 7.4 Confirm each README uses only vocabulary sections, in order
- [ ] 7.5 Confirm `LICENSE`, `AI_POLICY.md`, and `CODE_OF_CONDUCT.md` are
  byte-identical everywhere
- [ ] 7.6 Confirm no `.mise.toml` and no workflow floats a tool whose output a
  check compares
- [ ] 7.7 Confirm `just test` locally and CI agree on every repository
- [ ] 7.8 Confirm every deprecated repository is archived on GitHub
- [ ] 7.9 Confirm no tracked file was removed on the basis of its path without
  its content being read
