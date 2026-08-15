## Why

Five repositories run a workflow called **Docs Lint** that no longer lints docs.
The justfile conversion moved markdown formatting from prettier to mdformat, and
the workflow kept its name:

| Repository                                                           | Workflow  | Runs                                          |
| -------------------------------------------------------------------- | --------- | --------------------------------------------- |
| `gohai`, `nats-client`, `nats-server`, `osapi-orchestrator`, `specs` | Docs Lint | `md-fmt-check`                                |
| `osapi`                                                              | Docs Lint | `docusaurus-fmt-check` **and** `md-fmt-check` |

The first five check markdown, not documentation. The sixth checks two unrelated
subjects under one name, so a failure does not say which.

## What Changes

- A workflow's file name and `name` state what it checks
- The same check has the same workflow name in every repository
- A workflow does not bundle unrelated subjects; two subjects means two
  workflows

## Impact

- `code-architecture` — one added requirement
- Six repositories rename `docs-lint.yml`, and `osapi` splits its into two
