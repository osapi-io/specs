# Quickstart: Repository inventory

**Phase 1** | **Date**: 2026-09-02

How to verify the feature works, end to end.

## Prerequisites

```bash
gh auth status                    # authenticated, repo scope
gh ext list | grep reposync       # retr0h/gh-reposync installed
jq --version
```

If the extension is missing: `gh ext install retr0h/gh-reposync`.

## Before: record the starting state

Run these first so the after-state can be compared against something.

```bash
cd ~/git/osapi-io

# Every manifest declares exactly one repository — the problem
for f in */.github/repos.json; do
  printf "%-40s declares=%s\n" "$f" "$(jq '.repos|length' "$f")"
done

# One drift exists
cd specs && gh reposync --check     # => [specs] topics: DRIFT, exit 1
```

## Scenario 1: One file answers what repositories exist (FR-001, SC-001)

```bash
cd ~/git/osapi-io/.github
jq -r '.repos[].name' repos.json
```

**Expected**: eight names — `gohai`, `nats-client`, `nats-server`, `osapi`,
`osapi-orchestrator`, `osapi-justfiles`, `specs`, `.github`. No other file
consulted.

## Scenario 2: No second manifest survives (FR-003)

```bash
ls ~/git/osapi-io/*/.github/repos.json 2>&1
```

**Expected**: no such file. The only `repos.json` is in the `.github`
repository.

## Scenario 3: The manifest matches reality (FR-012, SC-002)

```bash
cd ~/git/osapi-io/.github
gh reposync --check
```

**Expected**: every repository reports `OK` across settings, description,
topics, security and branch protection. Exit 0. This is the check that fails
today on `specs` topics; it must pass after the drift is applied.

## Scenario 4: One run covers every repository (FR-001)

Confirm the output of scenario 3 names all eight repositories, not one. Before
this feature, `gh reposync --check` from any repository reported on that
repository alone.

## Scenario 5: The constitution points at the manifest (FR-009, FR-010, SC-005)

```bash
grep -A5 -i "repositor" ~/git/osapi-io/specs/system/.specify/memory/constitution.md
```

**Expected**: a section stating the repository list comes from the manifest and
that no other document may contain one. It must appear in the generated
`constitution.md`, not only in the fragment — proving the recompose ran.

```bash
grep -c "global/repositories" ~/git/osapi-io/specs/system/.specify/charter/state.yml
```

**Expected**: `1`.

## Scenario 6: No hardcoded list remains (FR-011, SC-003)

```bash
cd ~/git/osapi-io/specs
grep -rn "nats-client" --include="*.md" . | grep -v "specs/001-repository-inventory"
```

**Expected**: no hit that is a hand-maintained list of repositories.
`dependencies.md` reads its repositories from the manifest instead of naming
them inline.

## Scenario 7: Adding a repository is one edit (SC-004)

Add an entry to `repos[]` in the manifest. Then:

```bash
jq -r '.repos[].name' repos.json | grep <new-name>   # known
gh reposync --check --repo <new-name>                # checked
```

**Expected**: both succeed with no other file edited.

## Repo formatting checks

Anything changed inside the specs repository must still pass its own checks:

```bash
cd ~/git/osapi-io/specs && mise exec -- just test
```

**Expected**: `md-fmt-check` and `just-fmt-check` both clean.
