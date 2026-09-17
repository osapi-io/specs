# add-a-domain

Answers "what does a new osapi domain have to touch, and in what order?" so
adding one is a prompt rather than an afternoon of grepping a sibling domain.

A domain is a provider plus everything that has to exist for it to be reachable:
agent wiring, an OpenAPI spec, a handler, an SDK service, CLI commands, docs and
permission tables. In September 2026 one domain spanned 81 files.

## Install

Nothing to install. The skill lives in this repository and any skills-aware
agent working from the repository root finds it. The commands it runs need an
[osapi] checkout with [mise] and [just] available.

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

The reference domain comes from the codebase on every run, never from a list
here: one `grep -rl` for an existing domain is the specification for the new
one. A written inventory is right the day it is written and wrong after the next
layer is added.

`SKILL.md` routes, and holds the two things every route needs: the dependency
order that avoids rework, and the cross-layer checklist. One reference file
loads for the layer you asked about, and nothing else enters context.

The layer order is not a style preference. The OpenAPI spec generates the
server, the combined spec and the SDK client together, so writing a handler
before the spec means writing it twice.

## Documentation

| File | Covers |
| --- | --- |
| [SKILL.md](SKILL.md) | Reference domain, routing, layer order, checklist, verify gate |
| [references/provider.md](references/provider.md) | Provider patterns, interface, idempotency, platform stubs, facts, input validation |
| [references/agent.md](references/agent.md) | Processor, registry registration, platform selection, delivery semantics |
| [references/api.md](references/api.md) | OpenAPI spec, verbs, paths, validation, handlers, broadcast, registration, permissions |
| [references/sdk.md](references/sdk.md) | Service files, keeping generated types internal, result types, errors, examples |
| [references/cli.md](references/cli.md) | Commands, flags, output helpers, status codes, exit codes, integration tests |
| [references/docs.md](references/docs.md) | Feature and CLI pages, navbars, permission tables |

Format details are in the [Agent Skills specification].

## Contributing

See the [Contributing](../../../CONTRIBUTING.md) guide. Run `just skill-lint`
after editing, and keep `SKILL.md` a router: how to build one layer belongs in a
reference file, which loads only when that layer is the question.

This skill describes a codebase that moves. When a step no longer matches
[osapi], correct the skill in its own change before continuing the work that
found it, so the next run does not hit the same wall.

Do not run mdformat over this directory. `just md-fmt` already excludes
`.claude/**`, because mdformat reads the opening `---` as a horizontal rule and
collapses YAML frontmatter into a heading, which makes a skill silently
undiscoverable.

## License

The [MIT] License.

[agent skills specification]: https://agentskills.io/specification
[just]: https://just.systems
[mise]: https://mise.jdx.dev
[mit]: ../../../LICENSE
[osapi]: https://github.com/osapi-io/osapi
