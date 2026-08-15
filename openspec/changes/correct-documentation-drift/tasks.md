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

## 4. Remove the orphaned artifact

- [ ] 4.1 `gohai` — remove `schemas/all-fields.txt`, which nothing references

## 5. Verification

- [ ] 5.1 Confirm no documentation names a library the repository does not
  declare
- [ ] 5.2 Confirm no documentation points at a directory that does not exist
- [ ] 5.3 Confirm no repository describes another repository's tooling
