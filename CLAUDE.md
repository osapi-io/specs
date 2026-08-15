# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
this repository.

## Project Overview

This repository is the spec-driven development workspace for
[osapi-io](https://github.com/osapi-io). Changes to any osapi-io repository are
designed here first, then implemented in the repository they belong to.

**Implementation does not happen in this repository.** Code lands in the target
repo (`osapi`, `gohai`, `nats-client`, `nats-server`, `osapi-justfiles`, ...).
What lives here is the agreement: what was proposed, what was decided, and what
is done.

## Operating Model

See @CONTRIBUTING.md for the full model. In short:

- `openspec/specs/` is the corpus — the current description of how osapi-io
  behaves. **Never write to it by hand.** Deltas reach it only through
  `/opsx:sync` or `/opsx:archive`.
- `openspec/changes/` holds work in flight. Each change carries a proposal, spec
  deltas, a design, and tasks.
- `openspec/config.yaml` is the constitution. Its `context` and `rules` are
  injected into every artifact generated. Read it before writing artifacts; do
  not restate it inside them.

The `/opsx:*` commands come from OpenSpec and are generated into `.claude/` by
`openspec init`. They are committed, so they work on a fresh clone.

## Planning Boundary

`/opsx:propose` creates planning artifacts **only**. Do not edit project code in
the same response, even when the request asks you to build something. Stop after
the artifacts exist and wait for an explicit instruction to apply.

## Before Committing

Always run:

```bash
just test
```

This runs everything CI runs — markdown formatting, justfile lint, and
`openspec validate --all --strict`. If formatting fails, `just md-fmt` fixes it.
Do not open a pull request without a passing `just test`.

Markdown is formatted by [mdformat](https://pypi.org/project/mdformat/) and
wrapped at 80 columns. Two things it will silently change, so write them
correctly the first time:

- GitHub alert syntax (`> [!WARNING]`) is reflowed into a plain blockquote. Use
  bold text for callouts.
- Link definitions are lowercased and sorted.

`.claude/` is excluded from formatting because `openspec update` regenerates
those files and would revert any changes.

## Conventions

- **Commits** follow [Conventional Commits](https://www.conventionalcommits.org)
  with the 50/72 rule.
- **Branches** are named `type/short-description`. `main` is protected — every
  change goes through a pull request.
- **Requirements** use SHALL with at least one `WHEN`/`THEN` scenario, and
  describe observable behavior rather than files or libraries.

## Repository Structure

```
openspec/
├── config.yaml         # constitution: context, rules, operation guidance
├── specs/              # the corpus — current requirements
└── changes/            # in-flight changes
    └── archive/        # completed changes, preserved with their designs
.claude/                # openspec-generated commands and skills (committed)
justfile                # imports shared recipes from osapi-justfiles
```
