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
- [ ] 3.3 `gohai`
- [ ] 3.4 `nats-client`
- [ ] 3.5 `nats-server`
- [ ] 3.6 `osapi`
- [ ] 3.7 `osapi-orchestrator`
- [ ] 3.8 `osapi-ui`

## 4. Convert the remaining repositories

One repository per change, applying both the file layout and the README
structure for its type.

- [ ] 4.1 `gohai` (Go library)
- [ ] 4.2 `nats-client` (Go library)
- [ ] 4.3 `nats-server` (Go library)
- [ ] 4.4 `osapi-orchestrator` (Go library, pending the open question on its
  type)
- [ ] 4.5 `osapi` (main product; file layout only, README exempt)
- [ ] 4.6 `osapi-ui` (needs README content written, not only restructured)

## 5. Verification

- [ ] 5.1 Confirm every in-scope repository carries the required files
- [ ] 5.2 Confirm no repository still contains `docs/contributing.md` or
  `docs/development.md`
- [ ] 5.3 Confirm no cross-repository link still points at the old paths
- [ ] 5.4 Confirm each README uses only vocabulary sections, in order
- [ ] 5.5 Confirm `LICENSE`, `AI_POLICY.md`, and `CODE_OF_CONDUCT.md` are
  byte-identical everywhere
