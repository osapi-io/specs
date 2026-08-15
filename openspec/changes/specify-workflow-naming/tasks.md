## 1. Record the requirement

- [x] 1.1 Survey workflow names against what each runs
- [x] 1.2 Write the requirement
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Rename the workflows

- [ ] 2.1 `gohai` — `docs-lint.yml` → `markdown-lint.yml`, `name: Markdown Lint`
- [ ] 2.2 `nats-client` — same
- [ ] 2.3 `nats-server` — same
- [ ] 2.4 `osapi-orchestrator` — same
- [ ] 2.5 `specs` — same
- [ ] 2.6 `osapi` — split into `docusaurus-lint.yml` and `markdown-lint.yml`
- [ ] 2.7 `osapi` — `docs-build.yml` → `docusaurus-build.yml`, and
  `docs-deploy.yml` → `docusaurus-deploy.yml`, so the site's three workflows
  name their subject the same way

## 3. Verification

- [ ] 3.1 Confirm no workflow names a tool or subject it does not check
- [ ] 3.2 Confirm the same check carries the same workflow name everywhere
- [ ] 3.3 Confirm no workflow bundles unrelated subjects
- [ ] 3.4 Confirm workflows covering one subject name it consistently
