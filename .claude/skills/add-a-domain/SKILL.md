---
name: add-a-domain
description: Add or extend an osapi API domain — a provider plus every layer it must appear in. Covers the provider implementation and its platform variants, agent processor and registry wiring, the OpenAPI spec and validation tags, the Echo handler with broadcast targeting, handler registration and startup wiring, the SDK service, CLI commands, and the docs and permission tables a new domain must be added to. Use when asked to add a domain, add a provider, add an operation or endpoint to an existing domain, wire a provider into the agent, add an SDK service, add CLI commands for a domain, or when asked what a new domain has to touch, why a domain feels half-finished, or which layer is missing. Also use when reviewing a domain for cross-layer consistency against an existing one.
compatibility: Requires an osapi checkout with mise and just available. Commands run through `mise exec -- just`.
license: MIT
metadata:
  author: osapi-io
  source: https://github.com/osapi-io/specs
---

# Add a domain

## 1. Establish the reference domain

Every run, before writing anything. Pick a recently completed domain of the same
shape as the one being added and read it. `sysctl` for a direct-write domain,
`cron` for a meta provider that deploys files, `docker` for one that talks to an
external API, `ntp` for the simplest CRUD shape.

```bash
grep -rl 'sysctl\|Sysctl' --include='*.go' --include='*.yaml' --include='*.md' . \
  | grep -vE '/gen/|/node_modules/|docs/docs/gen|\.worktrees' | sort
```

That list is the specification for the new domain. It ran to 81 files in
September 2026. The codebase is the reference, not this skill: where they
disagree, read the code and fix the skill
([why](../../../.charter/fragments/global/correction.md)).

Never copy a domain's files wholesale. Read one, then write the new one.

## 2. Route

| The task | Read |
| --- | --- |
| The operations themselves, platform variants, idempotency | [provider.md](references/provider.md) |
| Getting the provider called by a job | [agent.md](references/agent.md) |
| Endpoints, validation, handler, broadcast, registration | [api.md](references/api.md) |
| The Go SDK service consumers call | [sdk.md](references/sdk.md) |
| `osapi client ...` commands | [cli.md](references/cli.md) |
| Feature page, CLI pages, permission tables, navbars | [docs.md](references/docs.md) |
| A whole new domain, end to end | All six, in that order |

## 3. The order that avoids rework

The layers depend on each other in one direction. Going out of order means
regenerating or rewriting.

1. **Provider** — the operations, with its own tests passing.
2. **Agent** — processor and registry, so a job reaches the provider.
3. **OpenAPI spec** — then `just generate`, which produces the server, the
   combined spec, and the SDK's generated client together.
4. **Handler** — with validation and broadcast, then registration and startup.
5. **SDK service** — wrapping the generated client.
6. **CLI** — wrapping the SDK.
7. **Docs and tables** — feature page, CLI pages, permissions, navbars.

A new permission is decided at step 3 and lands in step 7. Write it down when
you choose it; it is the thing most often missed.

## 4. Cross-layer checklist

Run this before calling a domain done. Every line is a place a domain appears,
and a domain that is missing from one of them is half-finished.

```
provider    internal/provider/{category}/{domain}/    types.go, platform files, mocks/
agent       internal/agent/processor_{domain}.go      dispatch to the provider
            cmd/agent_setup.go                        construct and Register
api         internal/controller/api/node/{domain}/gen/  api.yaml, cfg.yaml, generate.go
            internal/controller/api/node/{domain}/    types.go, {domain}.go, handler.go,
                                                      one file per endpoint, tests
            cmd/controller_setup.go                   one Handler(...) line
sdk         pkg/sdk/client/{domain}.go                service methods
            pkg/sdk/client/{domain}_types.go          result types, gen -> SDK conversion
            pkg/sdk/client/osapi.go                   Client field, wired in New()
            examples/sdk/client/{domain}.go           one runnable example
cli         cmd/client_node_{domain}.go               parent command
            cmd/client_node_{domain}_{op}.go          one per endpoint
docs        docs/docs/sidebar/features/{domain}-management.md
            docs/docs/sidebar/usage/cli/client/node/{domain}/*.md
            docs/docusaurus.config.ts                 features and SDK dropdowns
            features/features.md, features/authentication.md,
            usage/configuration.md                   permission tables
```

Prove it rather than reading it back: the `grep -rl` from step 1, run against
the new domain, should return the same shape of list as the reference domain.

## 5. Verify

```bash
mise exec -- just generate     # specs, server, SDK client, docs
mise exec -- just ready        # generate, format, lint, build both binaries
mise exec -- just test         # lint, unit, coverage gate
```

Coverage is gated at 99.9%, so an untested branch fails the build rather than
merging. `just test` also runs `go-mod-check`, which fails when a nested module
under `examples/` is untidy: a new SDK example adds one.

Never run `go build ./...` or `go test ./...` directly. The UI is embedded with
`//go:embed dist/*`, so both fail unless `ui/dist/` is populated, which the
`just` recipes do first.

## Rules

1. **The reference domain settles style questions.** Naming, file splits, table
   output, error wording: read the sibling domain rather than inventing. A
   difference in wording reads as a difference in rule.
2. **Idempotency is not optional.** Create on an existing resource is
   `Changed: false`, delete on a missing one is `Changed: false`, update on a
   missing one is an error. The table in
   [provider.md](references/provider.md) is the contract, and it is what makes
   these operations safe to run repeatedly.
3. **Every node-targeted operation supports broadcast.** `_all`, `_any`,
   hostname, and label selectors, returning the same collection shape whether
   one host answered or forty.
4. **Validation is declared in the OpenAPI spec**, enforced by
   `validation.Struct()` in the handler, and checked again in the provider where
   a value becomes a path or a command argument.
5. **Generated code is never hand-edited.** Change the spec and regenerate. A
   hand-edit survives until the next `just generate` and then disappears.
6. **Stop at the first disagreement with the code.** This skill is written from
   the codebase of September 2026. When a step no longer matches, correct the
   skill in its own change before continuing, so the next run does not hit the
   same wall.
