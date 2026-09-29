# Main Implementation Plan

> **Revision**: 2026-09-29 — Seeded from the gohai baseline
> (`specs/001-gohai-baseline`). Its plan was retrospective and written to the
> archival gate, which that plan says of itself; what is archived here is its
> content, not that admission.

## Technical Context

**Language/Version**: Go. 314 files, 205 of them not tests, measured by
`find . -name '*.go' -not -path './.git/*' | wc -l` and the same with
`-not -name '*_test.go'`.
[Source: specs/001-gohai-baseline/plan.md -> "Language/Version"]

**Primary Dependencies**: None recorded by the baseline. gohai is a library and its
dependency set was not part of the inventory's scope.
[Source: specs/001-gohai-baseline/plan.md -> "Primary Dependencies"]

**Storage**: N/A. gohai collects facts and returns them; it persists nothing.
[Source: specs/001-gohai-baseline/plan.md -> "Storage"]

**Testing**: `just test` in gohai, which gates coverage at 100%. Separately, every
count the corpus states carries the shell command that reproduces it, and re-running
those commands against the repository is what checks the inventory rather than the
formatting.
[Source: specs/001-gohai-baseline/plan.md -> "Testing"]

**Target Platform**: Linux and macOS hosts, selected per collector — a collector
returns nil where a platform does not support it rather than failing.
[Source: specs/001-gohai-baseline/plan.md -> "Constraints"]

**Project Type**: SDK-first Go library with a CLI.
[Source: specs/001-gohai-baseline/plan.md -> "Scale/Scope"]

**Constraints**: A baseline changes nothing in the repository it describes. No count
is stated without the command that produces it. A disagreement between the
repository's prose and its code is recorded as a gap naming both sides, never
silently corrected.
[Source: specs/001-gohai-baseline/plan.md -> "Constraints"]

**Scale/Scope**: 62 collectors, stated by their shared contract rather than
individually.
[Source: specs/001-gohai-baseline/plan.md -> "Scale/Scope"]

## Project Structure

```text
gohai/
├── internal/collector/
│   ├── collector.go      the five-method Collector interface, the ten category
│   │                     constants, PriorResults and the generic GetDep[T]
│   └── registry.go       NewRegistry, Register, Get, Names, NamesInCategory,
│                         Selected, SelectedWith, Run; expandWithDeps and topoLevels
├── pkg/gohai/
│   ├── gohai.go          where all 62 collector packages are registered
│   ├── collectors/       62 packages, one per collector
│   └── ocsf/             FromFacts, the OCSF conversion
├── schemas/
│   ├── gohai.schema.json generated
│   └── gen/              the generator
├── cmd/, main.go         the CLI
└── docs/collectors/      the maintained catalogue the corpus cites
```

**Structure Decision**: one specification for the whole library. gohai has one
contract, so splitting the inventory by category would create ten documents each
restating the same five-method interface.
[Source: specs/001-gohai-baseline/plan.md -> "Structure Decision"]

## Testing Strategy

The inventory itself is checked by re-running the commands each count carries. In
gohai, `just test` gates coverage at 100%.
[Source: specs/001-gohai-baseline/plan.md -> "Testing"]

## How a Baseline Is Produced

The order is the method, and it is what kept prose from becoming a source.

1. **The code first** — the interface and the category constants, the registry
   surface and its dependency handling, then where collectors are registered.
2. **The counts by command**, never by reading a sentence that claimed one.
3. **The prose last**, and only to find disagreements.

This is the reverse of the tempting order, and it is why two gaps were found rather
than inherited: reading the README first would have produced an inventory stating 65
collectors and 9 categories, both wrong, with the code never consulted.
[Source: specs/001-gohai-baseline/plan.md -> "What was read, and how"]
