---
name: build-a-behavior
description: Build or change an osapi behavior, the typed definition under internal/behaviors/<name>/ that osapi's API routes, agent dispatch, CLI commands, OpenAPI spec, docs pages, settings, permissions and tests are generated from. Use when asked to add a behavior or a domain, manage something new on a host, add a method or a setting to a behavior, give a behavior a provider for another platform, or when a behavior fails osapi dsl behavior validate, behavior-gen-check or its tests. Also use to decide whether something should be a behavior at all, whether it should be internal or served, which platforms it runs on, whether it should require another behavior or be split into an internal one, and whether it belongs in osapi-orchestrator instead. Not for operations that run on the controller itself, such as the agents, the jobs and the audit log, which the build-an-endpoint skill in osapi covers.
---

# Build a behavior

The osapi binary has this skill. This file only points to it, so that the skill
has one source. The work happens in a checkout of osapi, beside this repository.

In that checkout, run this command, and obey its output:

```bash
go run . skill get --name build-a-behavior
```

The skill names reference files, for example `references/services.md`. To read
one, run:

```bash
go run . skill get --name build-a-behavior --reference references/services.md
```
