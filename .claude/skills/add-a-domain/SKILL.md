---
name: add-a-domain
description: Add or extend an osapi API domain, a provider plus every layer it must appear in. Covers the provider implementation and its platform variants, agent processor and registry wiring, the OpenAPI spec and validation tags, the Echo handler with broadcast targeting, handler registration and startup wiring, the SDK service, CLI commands, and the docs and permission tables a new domain must be added to. Use when asked to add a domain, add a provider, add an operation or endpoint to an existing domain, wire a provider into the agent, add an SDK service, add CLI commands for a domain, or when asked what a new domain has to touch, why a domain feels half-finished, or which layer is missing. Also use when reviewing a domain for cross-layer consistency against an existing one.
---

# Add a domain

The osapi binary has this skill. This file only points to it, so that the skill
has one source. The work happens in a checkout of osapi, beside this repository.

In that checkout, run this command, and obey its output:

```bash
go run . skill get --name add-a-domain
```

The skill names reference files, for example `references/api.md`. To read
one, run:

```bash
go run . skill get --name add-a-domain --reference references/api.md
```
