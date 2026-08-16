## Context

`.github/labeler.yml` is copied between repositories and then left. It shows: a
label for a test framework the organization never adopted, Go labels in two
repositories holding no Go, and no label at all for justfiles — the files this
organization has spent the most time changing.

## Decisions

### Labels follow the repository, not the template

The same rule already applies to toolchain files: a repository carries the
configuration its toolchain requires and nothing more. A label is the same kind
of claim — it says this repository contains this kind of thing — and it decays
the same way, because nothing fails when it stops being true.

`kind/bats` is the clearest case. It was added when the `bats` module existed,
and survived the module's deletion by an evening. Nothing noticed, because a
label matching nothing produces no error; it simply never appears.

*Alternative considered:* keep a superset of labels everywhere so the files stay
identical. It makes every repository claim kinds it does not have, and the label
list stops describing anything.

### Do not let one label subsume another

`github/action` matches `.github/**/*.yml`. `kind/yaml` matches `**/*.yml`.
Every workflow change carries both, and the pair conveys less than either alone
would: a reader cannot tell a workflow change from any other YAML change by
looking at which labels appeared, because both always appear together.

*Alternative considered:* delete `kind/yaml` and keep `github/action`. YAML
outside `.github/` exists — codecov, dependabot, goreleaser — and would become
unlabelled.

### Prefixes are part of the name

`github/action` is the only label not prefixed `kind/`, and it classifies the
same way the others do. Consistency here is worth more than the slightly better
reading of the current name, because a reader guessing a label name should be
able to guess it.

### What applying it found

Two things the audit nearly missed, recorded because neither is visible from
reading a labeler file.

`kind/docs` matched `docs/**` and nothing else. Every `README.md`,
`CONTRIBUTING.md`, `AGENTS.md` and `AI_POLICY.md` change was therefore
unlabelled, in every repository — the documentation most often edited was the
documentation least often labelled. It now matches `**/*.md` as well.

`osapi-justfiles` holds a `Dockerfile`. The first pass of the audit assumed a
repository of shared recipes would hold no container files and would have
dropped `kind/docker` from it. Counting rather than assuming is what caught it,
and is why the verification is written as a count of matching files rather than
a review of the config.

### Format is not purpose

The first pass labelled by format: Go, TypeScript, YAML, justfiles, markdown.
That is the easy half, and it leaves markdown doing far too much work — 638
files across seven repositories, covering a README, a contributing guide, agent
guidance, two policies, and reference documentation. A pull request editing
`AGENTS.md` and one editing a collector reference carried identical labels.

Splitting by purpose gives `kind/agents`, `kind/contributing`, and
`kind/policy`, and narrows `kind/docs` to what it should have meant: the README
and the documentation tree.

The same reasoning applies to configuration. `.golangci.yml`,
`.goreleaser.yaml`, `codecov.yml` and `dependabot.yml` were all `kind/yaml`,
which says they are YAML and nothing else. A change to how a repository is
linted, released, or measured is a different kind of change from any other YAML
edit.

And three kinds were invisible because of their names: `LICENSE`, `.mise.toml`,
and `.coverignore` have no extension a format label could match.

*Alternative considered:* one label per file, named after the file. It scales
with the number of files rather than the number of reasons to care, and a reader
scanning labels wants to know what kind of change this is, not which file it
touched.
