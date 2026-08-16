## 1. Record the capability

- [x] 1.1 Survey what every repository's `docs/` holds, sorted by kind rather
  than by repository
- [x] 1.2 Write the `documentation` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Index each repository's documentation

- [x] 2.1 `gohai` — `docs/README.md` covering collectors, methodology, and the
  how-to guides
- [x] 2.2 `nats-client` — `docs/README.md`
- [x] 2.3 `nats-server` — `docs/README.md`
- [x] 2.4 `osapi-orchestrator` — `docs/README.md` covering operations and
  features
- [x] 2.5 `osapi` — exempt; its site navigation is the index. Confirm and record
  the exemption. Confirmed: the Docusaurus content root is `docs/docs/`, and
  `sidebars.ts` is the navigation the requirement accepts in place of a second
  index

## 3. Relocate requirements now held in repository documentation

- [ ] 3.1 `osapi` — propose a capability from `docs/sidebar/architecture/`:
  `principles.md` (8 constraints) and `api-guidelines.md` (6 API rules)
- [ ] 3.2 `osapi` — propose a capability from `job-architecture.md`'s
  "Architecture Principles"; leave its remaining 550 descriptive lines in place
- [ ] 3.3 `gohai` — propose a capability from the collector done-definition and
  `docs/methodology.md`'s decision order and field-naming ladder
- [ ] 3.4 `osapi` — propose capabilities from `CLAUDE.md`'s seven MANDATORY rule
  blocks: cross-layer consistency, provider idempotency, broadcast response
  shape, HTTP verb separation, OpenAPI validation, SDK method naming, and the Go
  code standards (signatures, `types.go`, test-file naming, mocking)
- [ ] 3.5 `osapi` — propose a capability from `docs/sidebar/sdk/guidelines.md`;
  "never expose generated types" and "JSON tags required" bind every consumer of
  `pkg/sdk`, including `osapi-orchestrator`
- [ ] 3.6 `osapi` — resolve the three-way duplication of branching, commit
  messages, linting, and test conventions across `CLAUDE.md`, `development.md`,
  and `testing.md` before the root `CONTRIBUTING.md` is written, so the
  conversion has one source to draw from
- [ ] 3.9 `osapi` — capture "job creation goes through domain endpoints" as a
  requirement. Removing `docs/plans/` deletes its only written record: the rule
  still binds (the sole `post:` on the job API is `/api/job/{id}/retry`, an
  action on an existing job) but is stated in no current document, so relocating
  what `api-guidelines.md` and `job-architecture.md` say will not produce it
- [ ] 3.7 Leave each source document in place as a pointer to the capability
- [ ] 3.8 `osapi` — leave `architecture.md`, `system-architecture.md`, `ui.md`,
  and the eight-step "Adding a New API Domain" walkthrough in the repository;
  they describe packages and procedure, not requirements

## 4. Remove planning documents from repositories

- [x] 4.1 Review the 76 planning documents for reasoning worth lifting into a
  change before removal
- [x] 4.2 `osapi` — remove `docs/plans/` (70 documents)
- [x] 4.3 `osapi-orchestrator` — remove `docs/plans/` (6 documents)
- [ ] 4.4 Both — note in `CONTRIBUTING.md` that design records are changes in
  the corpus. Done for `osapi-orchestrator`; `osapi` has no root
  `CONTRIBUTING.md` until `standardize-repository-layout` task 4.5 writes one

## 5. Verification

- [x] 5.1 Confirm every repository's documentation is indexed
- [x] 5.2 Confirm no repository contains a planning directory
- [ ] 5.3 Confirm no relocated requirement is stated in two places
