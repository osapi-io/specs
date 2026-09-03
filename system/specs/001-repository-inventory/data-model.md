# Data Model: Repository inventory

**Phase 1** | **Date**: 2026-09-02

One artifact: the manifest. Its schema is `gh reposync`'s and is not this
feature's to define; what follows is the shape osapi-io fills in.

## Manifest

**Location**: `osapi-io/.github` repository, `repos.json` at the root.

```jsonc
{
  "org": "osapi-io",              // default owner for every entry

  "settings":          { ... },   // applied to every repo in repos[]
  "security":          { ... },   // applied to every repo in repos[]
  "branch_protection": { ... },   // applied to every repo's configured branch

  "repos": [
    {
      "name":        "gohai",     // required
      "description": "…",         // optional, skipped if omitted
      "topics":      ["…"]        // optional, sorted and deduped, exact match
    }
  ]
}
```

### Shared blocks

`settings`, `security` and `branch_protection` apply to every entry. The schema
has no per-repository override for them.

This is the model's one real constraint. Consolidation works because all eight
repositories want identical values, which was measured rather than assumed. A
repository that later needs different branch protection cannot be expressed
here, and the tool would have to change first.

### Entries

Eight, one per managed repository:

| Repository           | Note                                                       |
| -------------------- | ---------------------------------------------------------- |
| `gohai`              |                                                            |
| `nats-client`        |                                                            |
| `nats-server`        |                                                            |
| `osapi`              |                                                            |
| `osapi-orchestrator` |                                                            |
| `osapi-justfiles`    |                                                            |
| `specs`              | topics corrected to `spec-kit`; see research.md decision 7 |
| `.github`            | holds the manifest; already matches the shared block       |

Each entry carries `name`, `description` and `topics` only. Values are taken
from the existing per-repository manifests unchanged, except `specs`.

### Membership rules

- A repository in `repos[]` is managed: `gh reposync` checks and applies it.
- A repository absent from `repos[]` is unmanaged. There is no archived flag;
  absence is the marker.
- Archived repositories — `osapi-ui`, `osapi-sdk`, `osapi-io-taskfiles` — are
  absent. `osapi-ui`'s existing manifest is deleted rather than merged.

## Derived: the repository list

Anything needing the set of managed repositories reads it from the manifest:

```bash
jq -r '.repos[].name' repos.json
```

This is what replaces the inline list in `dependencies.md` (FR-011) and what the
charter fragment points at (FR-009).

## What is not modelled

`gh reposync` manages repository settings, description, topics, Dependabot,
secret scanning, push protection and branch protection. Webhooks, environments,
Actions settings, collaborators and team access are outside it by design, so
they are outside this manifest and this feature.
