# Changelog

## Merged Features Log

### Repository inventory — archived 2026-09-02

**Branch:** `feat/repository-inventory`
**Spec:** [specs/001-repository-inventory/spec.md](../../specs/001-repository-inventory/spec.md)

**What was added:**

- The repository list comes from
  `gh repo list osapi-io --no-archived --visibility public`, stated in the
  constitution so every session reads it, and no document may hold a copy.
- Cross-repository work takes the set from that command rather than from prose.

**New Components:**

- `.charter/fragments/global/repositories.md` — the rule, composed into every
  project's constitution.
- `system/.specify/memory/constitution.md` regenerated to 1.2.0.

**Removed:**

- `system/.specify/memory/dependencies.md`. It held a hardcoded list of five Go
  repositories, cached a dependency graph `go.mod` already states, and occupied
  memory without having been archived there. Not a `RETIRED:` entry — it carried
  no requirement IDs, and the main spec was empty before this run.

**Tasks Completed:** 11/11 tasks
