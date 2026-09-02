[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=for-the-badge)](LICENSE)
[![conventional commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=for-the-badge)](https://conventionalcommits.org)
[![powered by](https://img.shields.io/badge/powered%20by-spec--kit-blue.svg?style=for-the-badge)](https://github.com/github/spec-kit)
![gitHub commit activity](https://img.shields.io/github/commit-activity/m/osapi-io/specs?style=for-the-badge)

# specs

The spec-driven development workspace for [osapi-io]. Every change is designed
here first, then implemented in the repository it belongs to.

## 🎯 Usage

This repository holds no product code. It holds the design record and the
durable knowledge behind [osapi-io] — why each component is built the way it is,
and what was agreed before it was built.

It is a [Spec Kit] monorepo. Each osapi-io component is a Spec Kit project in
its own directory, and `.charter/` at the root holds the constitution fragments
every project shares:

```
.charter/            # shared constitution fragments, composed into each project
osapi/               # a Spec Kit project: .specify/ and specs/
```

A change moves through Spec Kit's workflow, invoked as skills in [Claude Code]:

1. **Specify** — `speckit-specify` writes what the change must do and why, as a
   feature under the project's `specs/`.
2. **Plan** — `speckit-plan` settles the approach against the constitution.
3. **Tasks** — `speckit-tasks` breaks the plan into work.
4. **Implement** — the code lands in the component's own repository. This one
   records what was agreed.
5. **Archive** — `speckit-archive-run` consolidates the merged feature into the
   project's `.specify/memory/`, which is what future work reads first.

What survives a change is `.specify/memory/` — the standing description of how a
component behaves, kept honest by every change that passes through it.

Why bother: the design is reviewable on its own, separate from the diff that
implements it, and a change spanning several repositories is described in one
place rather than scattered across them.

## 📖 Documentation

[CONTRIBUTING.md](CONTRIBUTING.md) covers prerequisites, setup, how to operate
Spec Kit here, and the PR workflow. Upstream documentation for the tool itself
is the [Spec Kit] repository.

## 🤝 Contributing

See the [Contributing](CONTRIBUTING.md) guide for prerequisites, setup,
conventions, and the PR workflow.

## 📄 License

The [MIT] License.

[claude code]: https://claude.ai/code
[mit]: LICENSE
[osapi-io]: https://github.com/osapi-io
[spec kit]: https://github.com/github/spec-kit
