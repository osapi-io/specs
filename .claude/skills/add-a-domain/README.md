# add-a-domain

Answers "what must a new osapi domain touch, and in what order?". Thus a new
domain needs one prompt, not an afternoon of searches in a sibling domain.

A domain is a provider, and each part that must exist so that callers can get to
it: the agent wiring, an OpenAPI spec, a handler, an SDK service, CLI commands,
docs and permission tables. In September 2026, one domain had 81 files.

## Install

You install nothing. The skill is in this repository. Each agent that reads
skills finds it when it works from the repository root. The commands that it
runs need an [osapi] checkout, with [mise] and [just].

## Usage

Ask in plain language, or invoke it directly with `/add-a-domain`.

| Ask | You get |
| --- | --- |
| `add a domain for managing X` | The whole path, provider through docs, in dependency order |
| `add a provider for X` | Provider pattern, platform variants, idempotency contract |
| `wire this provider into the agent` | Processor and registry registration |
| `add an endpoint to the sysctl domain` | Spec, validation, handler, broadcast, tests |
| `add an SDK service for X` | Service files, result types, error branches, example |
| `add CLI commands for X` | Commands, flags, output helpers, exit codes |
| `what am I missing for X?` | The cross-layer checklist, run against the code |
| `is this domain consistent with sysctl?` | A comparison against the reference domain |

## How it works

The reference domain comes from the codebase on each run, never from a list
here. One `grep -rl` for an existing domain is the specification for the new
one. A written inventory is correct on the day that somebody writes it. It is
incorrect after somebody adds the next layer.

`SKILL.md` routes, and holds the two things every route needs: the dependency
order that avoids rework, and the cross-layer checklist. One reference file
loads for the layer you asked about, and nothing else enters context.

The layer order is not a preference. The OpenAPI spec generates the server, the
combined spec and the SDK client together. Thus if you write a handler before
the spec, you write it two times.

## Documentation

| File | Covers |
| --- | --- |
| [SKILL.md](SKILL.md) | Reference domain, routing, layer order, checklist, verify gate |
| [references/provider.md](references/provider.md) | Where a provider's files go, what they are called, and the scaffolding; the contract itself is cited from the corpus |
| [references/agent.md](references/agent.md) | Processor, registry registration, platform selection, delivery semantics |
| [references/api.md](references/api.md) | OpenAPI spec, verbs, paths, validation, handlers, broadcast, registration, permissions |
| [references/sdk.md](references/sdk.md) | Service files, keeping generated types internal, result types, errors, examples |
| [references/cli.md](references/cli.md) | Commands, flags, output helpers, status codes, exit codes, integration tests |
| [references/docs.md](references/docs.md) | Feature and CLI pages, navbars, permission tables |

Format details are in the [Agent Skills specification].

## Citing the corpus instead of restating it

This skill cites a rule that the corpus states. It never repeats it. The
citation is a table row that names the requirement, not a sentence that points
to a document:

| Rule | Stated in |
| --- | --- |
| A provider returns a typed result, never a formatted string | [what an operation returns](../../../components/osapi/providers.md#what-an-operation-returns) |

Three things make that a citation rather than a link:

- **It is relative.** A relative link breaks clearly when the target moves. An
  absolute URL to the same file continues to open a page that does not say what
  the row claims now.
- **It names the section.** "See the provider contract" is only a pointer. A
  link to the heading tells a reader if the information is there.
- **It does not state the rule again.** The row names the rule and its location.
  Citations exist to prevent two statements of one rule. With two statements,
  the copy that an agent loads first is the one that applies.

`references/provider.md` is the example. A citation of the contract, not a copy,
made it shorter: 127 lines, not 171.

## Contributing

Refer to the [Contributing](../../../CONTRIBUTING.md) guide. Keep `SKILL.md` a
router. How to build one layer goes in a reference file, which loads only when
the question is about that layer.

This skill describes a codebase that changes. When a step does not match [osapi]
now, correct the skill in its own change. Do that before you continue the work
that found the difference. Then the next run does not hit the same problem.

Do not run mdformat on this directory. `just md-fmt` already excludes
`.claude/**`. mdformat reads the first `---` as a horizontal rule, and changes
the YAML frontmatter into a heading. Then agents cannot find the skill, and
nothing reports it.

## License

The [MIT] License.

[agent skills specification]: https://agentskills.io/specification
[just]: https://just.systems
[mise]: https://mise.jdx.dev
[mit]: ../../../LICENSE
[osapi]: https://github.com/osapi-io/osapi
