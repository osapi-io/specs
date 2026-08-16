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

### Workflows for one subject read as a set

`osapi` has three workflows for its documentation site: lint, build, and deploy.
Renaming only the lint left `Docusaurus Lint` beside `Docs Build` and
`Deploy to GitHub Pages` — three names for one subject, none wrong on its own.

Nothing in the requirement forced the other two to change, because each states
what it does. But a reader scanning the check list sees three unrelated-looking
jobs where there is one subject, and someone adding a fourth has no name to
follow.

*Alternative considered:* leave them, since neither is misleading. That is true
and is why this needed a rule rather than a defect report — the requirement now
says workflows covering one subject name it the same way.

### Naming form is part of the same consistency work

An earlier reading of this change treated the remaining odd names as style
rather than substance, and left them: `Mark stale issues and pull requests` in
sentence case, `Deploy to GitHub Pages` naming a hosting service,
`Conventional Commits` naming a standard rather than the subject.

That reading was inconsistent with everything else agreed here. `LICENSE` is
byte-identical across repositories, `AI_POLICY.md` word-identical,
`CONTRIBUTING.md` sections fixed by name and order, module variables prefixed to
a pattern. Workflow names are the same kind of thing: a reader moving between
repositories should not have to work out whether two differently-worded checks
are the same check.

So the form is specified — kebab-case files, title-case names, both naming the
same subject. It rules out three things seen in practice: a sentence, a
destination in place of a subject, and a standard in place of a subject.

*Alternative considered:* require the `name` to be the title-case rendering of
the file name. It reads badly where a file abbreviates —`dep-review.yml` would
become `Dep Review` rather than `Dependency Review`. The `name` may spell out
what the file shortens, as long as both name the same subject.
