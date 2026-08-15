## Context

Workflow names were accurate when written. `docs-lint.yml` ran
`docs::fmt-check`, which formatted a `docs/` directory with prettier. Moving
markdown formatting to mdformat changed what the check does without changing
what it is called.

## Decisions

### Name the workflow for the check, not the directory

`Docs Lint` describes a location. Four of the five repositories running it have
no documentation site at all — they hold plain markdown, and the check formats
every file in the repository including the README. Calling that "Docs Lint" is
wrong twice: it is not limited to docs, and it is not what a reader looks for
when markdown formatting fails.

*Alternative considered:* leave the names and rely on the step names inside each
workflow. The failed-check list shows workflow names, not step names, so the
reader sees `Docs Lint` and has to open it.

### Two subjects means two workflows

`osapi` checks a Docusaurus site and markdown outside it. Those use different
formatters and fail for different reasons. Under one workflow name, a red check
does not say which formatter objected, and the two cannot be re-run separately.

*Alternative considered:* one workflow with two clearly named steps. It reads
well in the log and badly in the check list, which is where a failure is first
seen.
