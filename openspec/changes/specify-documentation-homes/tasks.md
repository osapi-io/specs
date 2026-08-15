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

## 3. Remove planning documents from repositories

- [ ] 3.1 Review the 76 planning documents for reasoning worth lifting into a
  change before removal
- [ ] 3.2 `osapi` — remove `docs/plans/` (70 documents)
- [ ] 3.3 `osapi-orchestrator` — remove `docs/plans/` (6 documents)
- [ ] 3.4 Both — note in `CONTRIBUTING.md` that design records are changes in
  the corpus

## 4. Verification

- [ ] 4.1 Confirm every repository's documentation is indexed
- [ ] 4.2 Confirm no repository contains a planning directory
