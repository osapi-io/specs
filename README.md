[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=for-the-badge)](LICENSE)
[![conventional commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=for-the-badge)](https://conventionalcommits.org)
[![powered by](https://img.shields.io/badge/powered%20by-spec--kit-blue.svg?style=for-the-badge)](https://github.com/github/spec-kit)
![gitHub commit activity](https://img.shields.io/github/commit-activity/m/osapi-io/specs?style=for-the-badge)

# specs

The spec-driven development workspace for [osapi-io]. Every change is designed
here first, then implemented in the repository it belongs to.

## 🎯 Usage

This repository holds no product code. It holds the design record and the
durable knowledge behind [osapi-io]. Each component's entry says why that
component is built the way it is, and what was agreed before it was built.

It is a [Spec Kit] monorepo. Each osapi-io component is a Spec Kit project in
its own directory, and `.charter/` at the root holds the constitution fragments
every component shares:

```
.charter/              # shared constitution fragments, composed into each component
DEPENDENCIES.md        # how the repositories relate
components/
├── osapi/             # a Spec Kit project: .specify/ and specs/
├── gohai/
├── nats-client/
├── nats-server/
├── osapi-orchestrator/
└── osapi-justfiles/
```

A change moves through Spec Kit's workflow, invoked as skills in [Claude Code]:

1. **Specify.** `speckit-specify` writes what the change must do and why, as a
   feature under the component's `specs/`.
2. **Plan.** `speckit-plan` settles the approach against the constitution.
3. **Tasks.** `speckit-tasks` breaks the plan into work.
4. **Implement.** The code lands in the component's own repository. This one
   records what was agreed.
5. **Archive.** `speckit-archive-run` consolidates the merged feature into the
   component's `.specify/memory/`, which is what future work reads first.

What survives a change is `.specify/memory/`, the standing description of how a
component behaves. Every change that passes through keeps it honest.

Two things make this worth the overhead. Reviewers read the design on its own,
separate from the diff that implements it. And one place describes a change
spanning several repositories, instead of scattering it across them.

## 📖 Documentation

[CONTRIBUTING.md](CONTRIBUTING.md) covers prerequisites, setup, how to operate
Spec Kit here, and the PR workflow. The [Spec Kit] repository documents the tool
itself.

## 🤝 Contributing

See the [Contributing](CONTRIBUTING.md) guide for prerequisites, setup,
conventions, and the PR workflow.

## 📄 License

The [MIT] License.

[claude code]: https://claude.ai/code
[mit]: LICENSE
[osapi-io]: https://github.com/osapi-io
[spec kit]: https://github.com/github/spec-kit
