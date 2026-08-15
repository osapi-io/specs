## 1. Record the requirement

- [x] 1.1 Audit files, directories, workflow bodies, recipe bodies, and
  documented claims across every non-deprecated repository
- [x] 1.2 Broaden the documented-relationships requirement to cover tooling and
  directories
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Fix the tooling

- [ ] 2.1 `nats-client` — `deps` installs `go.uber.org/mock/mockgen`, not the
  deprecated `golang/mock/mockgen`
- [ ] 2.2 `nats-server` — same
- [ ] 2.3 `nats-client`, `nats-server` — documentation names the library
  `go.mod` declares

## 3. Fix the documentation

- [ ] 3.1 `gohai` — remove the claim about which library `osapi` uses
- [ ] 3.2 `gohai` — point plans at a directory that exists, or drop the
  reference
- [ ] 3.3 `nats-client`, `nats-server` — same
- [ ] 3.4 `osapi-orchestrator` — state that it uses no mocking library

## 4. Repoint references orphaned by the CONTRIBUTING conversion

- [ ] 4.1 `gohai` — `docs/adding-a-collector.md` links twice to
  `../CLAUDE.md#done-definition-every-collector-every-time`; that content is now
  in `CONTRIBUTING.md` and `CLAUDE.md` is a seven-line pointer
- [ ] 4.2 `gohai` — `docs/collectors/kernel.md` and `docs/collectors/memory.md`
  justify decisions "per CLAUDE.md"; name the file that states the rule
- [ ] 4.3 `osapi` — `CLAUDE.md` says `printKV` and `printStyledTable` are in
  `cmd/ui.go`; they are in `internal/cli/ui.go` and `cmd/ui.go` does not exist

## 5. Repair broken links

Sixteen of 526 relative links across the reference documentation do not resolve.

- [ ] 5.1 `gohai` — `docs/methodology.md` links to `docs/adding-a-collector.md`
  from inside `docs/`, and to `schemas/field-mapping.md` and
  `schemas/ocsf-gaps.md` in a `docs/schemas/` directory that does not exist
- [ ] 5.2 `gohai` — `docs/collectors/README.md` links to the same two absent
  schema documents, plus `rackspace.md`, `softlayer.md`, and `eucalyptus.md`,
  which do not exist
- [ ] 5.3 `gohai` — `docs/collectors/load.md` links to
  `../features/dependencies.md`, which does not exist
- [ ] 5.4 `osapi` — `docs/docs/sidebar/intro.md` prefixes four links with
  `sidebar/`, resolving to `sidebar/sidebar/`
- [ ] 5.5 `osapi-orchestrator` — three operation pages link to
  `../file/upload.md`; the file is at `operations/files/file/upload.md`

## 6. Correct claims contradicted by the code

- [ ] 6.1 `osapi` — `CLAUDE.md` states `nats-client` and `nats-server` are
  "linked via `replace` in `go.mod`". `go.mod` declares no `replace` directive
- [ ] 6.2 `osapi` — `docs/docs/sidebar/usage/configuration.md` states two config
  fields carry a `required` tag; `internal/config/types.go` has seven
- [ ] 6.3 `osapi` — the same page's "Required Fields" table lists four rows, two
  of which are environment variables pasted from the table above it

## 7. Remove the orphaned artifact

- [ ] 7.1 `gohai` — remove `schemas/all-fields.txt`, which nothing references

## 8. Verification

- [ ] 8.1 Confirm no documentation names a library the repository does not
  declare
- [ ] 8.2 Confirm no documentation points at a directory that does not exist
- [ ] 8.3 Confirm no repository describes another repository's tooling
- [ ] 8.4 Confirm every heading anchor referenced across files resolves
- [ ] 8.5 Confirm no reference cites `CLAUDE.md` for content that moved to
  `CONTRIBUTING.md`
- [ ] 8.6 Confirm every relative link across the documentation resolves
- [ ] 8.7 Confirm no documented count contradicts the code it describes
