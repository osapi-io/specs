## 1. Record the requirement

- [x] 1.1 Audit files, directories, workflow bodies, recipe bodies, and
  documented claims across every non-deprecated repository
- [x] 1.2 Broaden the documented-relationships requirement to cover tooling and
  directories
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Fix the tooling

- [x] 2.1 `nats-client` — `deps` installs `go.uber.org/mock/mockgen`, not the
  deprecated `golang/mock/mockgen`
- [x] 2.2 `nats-server` — same
- [x] 2.3 `nats-client`, `nats-server` — documentation names the library
  `go.mod` declares

## 3. Fix the documentation

- [x] 3.1 `gohai` — remove the claim about which library `osapi` uses
- [x] 3.2 `gohai` — point plans at a directory that exists, or drop the
  reference
- [x] 3.3 `nats-client`, `nats-server` — same
- [x] 3.4 `osapi-orchestrator` — no change needed. `go.mod` declares no mocking
  library and no documentation claims one; the single "mock server" reference is
  `httptest.Server`, which is accurate

## 4. Repoint references orphaned by the CONTRIBUTING conversion

- [x] 4.1 `gohai` — `docs/adding-a-collector.md` links twice to
  `../CLAUDE.md#done-definition-every-collector-every-time`; that content is now
  in `CONTRIBUTING.md` and `CLAUDE.md` is a seven-line pointer
- [x] 4.2 `gohai` — `docs/collectors/kernel.md` and `docs/collectors/memory.md`
  justify decisions "per CLAUDE.md"; name the file that states the rule
- [x] 4.3 `osapi` — `CLAUDE.md` says `printKV` and `printStyledTable` are in
  `cmd/ui.go`; they are in `internal/cli/ui.go` and `cmd/ui.go` does not exist

## 5. Repair broken links

Sixty relative links across the reference documentation do not resolve — the
sixteen counted here were the subset found by hand. Sixteen more sit in
`osapi-orchestrator/docs/plans/`, left for `specify-documentation-homes` to
remove with that directory.

- [x] 5.1 `gohai` — `docs/methodology.md` links to `docs/adding-a-collector.md`
  from inside `docs/`, and to `schemas/field-mapping.md` and
  `schemas/ocsf-gaps.md` in a `docs/schemas/` directory that does not exist
- [x] 5.2 `gohai` — `docs/collectors/README.md` links to the same two absent
  schema documents, plus `rackspace.md`, `softlayer.md`, and `eucalyptus.md`,
  which do not exist
- [x] 5.3 `gohai` — `docs/collectors/load.md` links to
  `../features/dependencies.md`, which does not exist
- [x] 5.4 `osapi` — `docs/docs/sidebar/intro.md` prefixes four links with
  `sidebar/`, resolving to `sidebar/sidebar/`
- [x] 5.5 `osapi-orchestrator` — three operation pages link to
  `../file/upload.md`; the file is at `operations/files/file/upload.md`

## 6. Correct claims contradicted by the code

- [x] 6.1 `osapi` — `CLAUDE.md` states `nats-client` and `nats-server` are
  "linked via `replace` in `go.mod`". `go.mod` declares no `replace` directive
- [x] 6.2 `osapi` — `docs/docs/sidebar/usage/configuration.md` states two config
  fields carry a `required` tag; `internal/config/types.go` has seven
- [x] 6.3 `osapi` — the same page's "Required Fields" table lists four rows, two
  of which are environment variables pasted from the table above it

## 7. Remove the orphaned artifact

- [x] 7.1 `gohai` — remove `schemas/all-fields.txt`, which nothing references.
  1,304 rows, not the 803 recorded here; 803 was `field-mapping.md`'s row count,
  itself now 950

## 8. Verification

- [x] 8.1 Confirm no documentation names a library the repository does not
  declare
- [x] 8.2 Confirm no documentation points at a directory that does not exist
- [x] 8.3 Confirm no repository describes another repository's tooling
- [x] 8.4 Confirm every heading anchor referenced across files resolves
- [x] 8.5 Confirm no reference cites `CLAUDE.md` for content that moved to
  `CONTRIBUTING.md`
- [x] 8.6 Confirm every relative link across the documentation resolves
- [x] 8.7 Confirm no documented count contradicts the code it describes

## 9. Found while applying

Fixed under requirements this change already carries, but not enumerated above.

- [x] 9.1 `gohai` — `docs/collectors/README.md` links three deprecated
  collectors (`rackspace`, `softlayer`, `eucalyptus`) to pages that will never
  exist; unlinked
- [x] 9.2 `gohai` — `CONTRIBUTING.md` places the executor mock at
  `internal/executor/mocks/`; `go:generate` writes it to
  `internal/executor/gen/` and every test imports it from there
- [x] 9.3 `gohai` — `field-mapping.md` documented as 803 rows (950),
  `ocsf-gaps.md` as 73 entries (82), and the tier split as ~108/~74/~768
  (107/91/752)
- [x] 9.4 `osapi-orchestrator` — twenty-six operation pages link into
  `examples/` one `../` short, resolving under `docs/`
- [x] 9.5 `osapi-orchestrator` — the group page cites `user.go`, which covers no
  group operations; `group.go` does
- [x] 9.6 `osapi` — `system-architecture.md` locates the notifier at
  `internal/notify/`; it is `internal/controller/notify/`
- [x] 9.7 `osapi` — `intro.md` links `category/api` without the leading slash
  the other five references use
- [x] 9.8 `osapi-justfiles` — `md/README.md` links to `../README.md#docsjust`;
  the module was renamed to `docusaurus` and the parent README no longer carries
  per-module sections
- [x] 9.9 `osapi-justfiles` — `AGENTS.md` points at a `docs/plans/` directory
  that does not exist
