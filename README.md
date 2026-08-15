[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=for-the-badge)](LICENSE)
[![conventional commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=for-the-badge)](https://conventionalcommits.org)
[![powered by](https://img.shields.io/badge/powered%20by-openspec-blue.svg?style=for-the-badge)](https://github.com/Fission-AI/OpenSpec)
[![bun](https://img.shields.io/badge/Bun-000000?style=for-the-badge&logo=bun&logoColor=white)](https://bun.sh)
![gitHub commit activity](https://img.shields.io/github/commit-activity/m/osapi-io/specs?style=for-the-badge)

# specs

The spec-driven development workspace for [osapi-io]. Every change is designed
here first, then implemented in the repo it belongs to.

## 🎯 Usage

This repo is where osapi-io development starts. Before code is written in
[osapi], [gohai], or any other repo, the change is proposed and agreed here — in
Markdown, where it is cheap to argue about.

A change moves through four stages, each a slash command in Claude Code:

1. **Propose** — `/opsx:propose "add a health endpoint"` opens a change under
   `openspec/changes/`, containing the proposal, the requirements it adds or
   alters, a design, and a task breakdown.
2. **Review** — the proposal is reviewed as a pull request here. Scope,
   requirements, and design are settled before anything is built.
3. **Implement** — `/opsx:apply` works the task list. The code lands in the
   target repo; this repo records what was agreed and what is done.
4. **Archive** — `/opsx:archive` files the completed change under
   `openspec/changes/archive/`.

What survives is `openspec/specs/` — the current description of how osapi-io
behaves, kept honest by every change that passes through.

Why bother: the design is reviewable on its own, separate from the diff that
implements it. Decisions get a written record instead of living in a PR comment
thread, and a change that spans several repos is described in one place rather
than scattered across them.

## 📖 Documentation

See the [OpenSpec] documentation for the workflow and CLI reference.

## 🤝 Contributing

See the [Contributing](CONTRIBUTING.md) guide for prerequisites, setup,
conventions, and the PR workflow.

## 📄 License

The [MIT] License.

[gohai]: https://github.com/osapi-io/gohai
[mit]: LICENSE
[openspec]: https://github.com/Fission-AI/OpenSpec
[osapi]: https://github.com/osapi-io/osapi
[osapi-io]: https://github.com/osapi-io
