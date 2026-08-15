## 1. Record the capability

- [x] 1.1 Survey what every repository's `docs/` holds, sorted by kind rather
  than by repository
- [x] 1.2 Write the `documentation` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Index each repository's documentation

- [ ] 2.1 `gohai` — `docs/README.md` covering collectors, methodology, and the
  how-to guides
- [ ] 2.2 `nats-client` — `docs/README.md`
- [ ] 2.3 `nats-server` — `docs/README.md`
- [ ] 2.4 `osapi-orchestrator` — `docs/README.md` covering operations and
  features
- [ ] 2.5 `osapi` — exempt; its site navigation is the index. Confirm and record
  the exemption

## 3. Relocate requirements now held in repository documentation

- [ ] 3.1 `osapi` — propose a capability from `docs/sidebar/architecture/`:
  `principles.md` (8 constraints) and `api-guidelines.md` (6 API rules)
- [ ] 3.2 `osapi` — propose a capability from `job-architecture.md`'s
  "Architecture Principles"; leave its remaining 550 descriptive lines in place
- [ ] 3.3 `gohai` — propose a capability from the collector done-definition and
  `docs/methodology.md`'s decision order and field-naming ladder
- [ ] 3.4 Leave each source document in place as a pointer to the capability
- [ ] 3.5 `osapi` — leave `architecture.md`, `system-architecture.md`, and
  `ui.md` in the repository; they describe packages, not requirements

## 4. Remove planning documents from repositories

- [ ] 4.1 Review the 76 planning documents for reasoning worth lifting into a
  change before removal
- [ ] 4.2 `osapi` — remove `docs/plans/` (70 documents)
- [ ] 4.3 `osapi-orchestrator` — remove `docs/plans/` (6 documents)
- [ ] 4.4 Both — note in `CONTRIBUTING.md` that design records are changes in
  the corpus

## 5. Verification

- [ ] 5.1 Confirm every repository's documentation is indexed
- [ ] 5.2 Confirm no repository contains a planning directory
- [ ] 5.3 Confirm no relocated requirement is stated in two places
