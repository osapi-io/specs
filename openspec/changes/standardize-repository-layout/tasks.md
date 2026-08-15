## 1. Record the standard

- [x] 1.1 Survey all nine active repositories for common files, README
  structure, and section vocabulary
- [x] 1.2 Write the `repo-standards` capability covering repository types,
  required files, contributing location, agent guidance, and README structure
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Convert osapi-justfiles

The first repository converted, and the reference for the rest.

- [ ] 2.1 Consolidate `docs/contributing.md` and `docs/development.md` into a
  root `CONTRIBUTING.md`
- [ ] 2.2 Add `AGENTS.md` carrying only agent-specific guidance, pointing to
  `CONTRIBUTING.md`
- [ ] 2.3 Reduce `CLAUDE.md` to a pointer to `AGENTS.md`
- [ ] 2.4 Update every inbound reference to the old `docs/` paths
- [ ] 2.5 Confirm `just test` and CI pass

## 3. Convert the remaining repositories

One repository per change, applying both the file layout and the README
structure for its type.

- [ ] 3.1 `gohai` (Go library)
- [ ] 3.2 `nats-client` (Go library)
- [ ] 3.3 `nats-server` (Go library)
- [ ] 3.4 `osapi-orchestrator` (Go library, pending the open question on its
  type)
- [ ] 3.5 `osapi` (main product; file layout only, README exempt)
- [ ] 3.6 `osapi-ui` (needs README content written, not only restructured)

## 4. Verification

- [ ] 4.1 Confirm every in-scope repository carries the required files
- [ ] 4.2 Confirm no repository still contains `docs/contributing.md` or
  `docs/development.md`
- [ ] 4.3 Confirm no cross-repository link still points at the old paths
- [ ] 4.4 Confirm each README uses only vocabulary sections, in order
