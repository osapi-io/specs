# AGENTS.md

Test: `just test` | Format: `just md-fmt` | Validate:
`openspec validate --all --strict`

The workflow, the operating model, and every convention live in
@CONTRIBUTING.md. Read it first. This file carries only what an agent needs on
top of that.

## Hard rules

- **Implementation never lands here.** Code goes to the target repository
  (`osapi`, `gohai`, `nats-client`, `nats-server`, `osapi-justfiles`, ...). This
  repository records what was agreed and what is done.
- **Never write to `openspec/specs/` by hand.** It is reached only through
  `/opsx:sync` or `/opsx:archive`.
- **`/opsx:propose` is a planning boundary.** It produces artifacts and stops.
  Do not edit code in the same response, even when the request asks you to build
  something. Wait for an explicit instruction to apply.
- **Read `openspec/config.yaml` before writing artifacts.** Its `context` and
  `rules` are injected into every generation. Apply them; do not restate them
  inside the artifacts.

## Before committing

`just test` must pass. It runs what CI runs — markdown formatting, justfile
lint, and `openspec validate --all --strict`. `just md-fmt` fixes formatting.

A change can validate cleanly and still fail CI on formatting.

## mdformat will change these silently

- GitHub alert syntax (`> [!WARNING]`) is reflowed into a plain blockquote. Use
  bold text for callouts.
- Link definitions are lowercased and sorted.

`.claude/` is excluded from formatting — `openspec update` regenerates it and
would revert any changes.

## Layout

| Path                        | What it is                                           |
| --------------------------- | ---------------------------------------------------- |
| `openspec/specs/`           | The corpus — current requirements. Never hand-edited |
| `openspec/changes/`         | Work in flight: proposal, spec deltas, design, tasks |
| `openspec/changes/archive/` | Completed changes, preserved with their designs      |
| `openspec/config.yaml`      | Constitution — context, rules, operation guidance    |
| `.claude/`                  | openspec-generated commands and skills, committed    |
| `justfile`                  | Imports shared recipes from `osapi-justfiles`        |
