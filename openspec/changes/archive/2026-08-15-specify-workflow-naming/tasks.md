## 1. Record the requirement

- [x] 1.1 Survey workflow names against what each runs
- [x] 1.2 Write the requirement
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Rename the workflows

- [x] 2.1 `gohai` — `docs-lint.yml` → `markdown-lint.yml`, `name: Markdown Lint`
- [x] 2.2 `nats-client` — same
- [x] 2.3 `nats-server` — same
- [x] 2.4 `osapi-orchestrator` — same
- [x] 2.5 `specs` — same
- [x] 2.6 `osapi` — split into `docusaurus-lint.yml` and `markdown-lint.yml`
- [x] 2.7 `osapi` — `docs-build.yml` → `docusaurus-build.yml`, and
  `docs-deploy.yml` → `docusaurus-deploy.yml`, so the site's three workflows
  name their subject the same way

## 3. Normalize the remaining names

- [x] 3.a `stale.yml` — `Mark stale issues and pull requests` → `Stale`, in all
  seven repositories
- [x] 3.b `labeler.yml` — confirm `Pull Request Labeler` names its subject, or
  shorten to `Labeler`
- [x] 3.c `commit-lint.yml` — `Conventional Commits` names a standard rather
  than the subject; rename to `Commit Lint`

## 4. Verification

- [x] 4.0 Confirm every workflow file is kebab case and every name is title case
  naming the same subject

- [x] 4.1 Confirm no workflow names a tool or subject it does not check

- [x] 4.2 Confirm the same check carries the same workflow name everywhere

- [x] 4.3 Confirm no workflow bundles unrelated subjects

- [x] 4.4 Confirm workflows covering one subject name it consistently
