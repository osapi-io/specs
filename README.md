[![license](https://img.shields.io/badge/license-MIT-brightgreen.svg?style=for-the-badge)](LICENSE)
[![conventional commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=for-the-badge)](https://conventionalcommits.org)
[![powered by](https://img.shields.io/badge/powered%20by-spec--kit-blue.svg?style=for-the-badge)](https://github.com/github/spec-kit)
![gitHub commit activity](https://img.shields.io/github/commit-activity/m/osapi-io/specs?style=for-the-badge)

# specs

The spec-driven development workspace for [osapi-io]. Every change is designed
here first, then implemented in the repository it belongs to.

## Usage

This repository holds no product code. It holds the design record and the
durable knowledge behind [osapi-io]: what was agreed before something was built,
and why it is built that way.

It is a [Spec Kit] monorepo, and knowledge sits at one of three levels:

```
.charter/       rules binding every repository
components/     one project per repository, for how that repository behaves
system/         agreements between repositories: protocols, conventions, the graph
```

A change is designed here first, reviewed as a pull request, then implemented in
the repository it belongs to. What survives is each project's
`.specify/memory/`, the standing description of how things behave, which every
later change reads first and keeps honest.

Two things make that worth the overhead. Reviewers read the design on its own,
separate from the diff that implements it. And one place describes a change
spanning several repositories, instead of scattering it across them.

[CONTRIBUTING.md](CONTRIBUTING.md) has the workflow, the skills that run it, and
the test for which level a change belongs to.

## Documentation

[CONTRIBUTING.md](CONTRIBUTING.md) covers prerequisites, setup, how to operate
Spec Kit here, and the PR workflow. The [Spec Kit] repository documents the tool
itself.

## Contributing

See the [Contributing](CONTRIBUTING.md) guide for prerequisites, setup,
conventions, and the PR workflow.

## License

The [MIT] License.

[mit]: LICENSE
[osapi-io]: https://github.com/osapi-io
[spec kit]: https://github.com/github/spec-kit
