# Quality

Resolve the repository set first, per [SKILL.md](../SKILL.md).

## Is the default branch green

The head commit's check rollup is the direct answer:

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  roll=$(gh api "/repos/osapi-io/$r/commits/HEAD/check-runs?per_page=100" \
    --jq '[.check_runs[] | .conclusion // "pending"] | group_by(.) | map("\(.[0]):\(length)") | join(" ")' 2>/dev/null || true)
  printf "%-22s %s\n" "$r" "${roll:-no checks}"
done
```

A repository with no CI workflow reports no checks. That is a finding in its own
right, not a pass.

## A specific workflow

`gh run list --branch main` includes scheduled jobs and Dependabot's own runs,
so it answers a different question than "did CI pass". Name the workflow:

```bash
gh run list --repo "osapi-io/$r" --workflow go.yml --branch main --limit 1 \
  --json conclusion,createdAt,headSha \
  -q '.[] | "\(.conclusion)  \(.createdAt[:10])  \(.headSha[:8])"'
```

Every Go repository here runs `go.yml`. The specs repository does not, so skip
it or expect an empty result.

## Go version drift

The `go` directive must name the older of the two newest Go minor releases
([why](../../../../.charter/fragments/global/tooling.md)). Nobody is notified
when a new minor ships, so this is the check that catches it.

```bash
floor=$(curl -s --max-time 20 'https://proxy.golang.org/golang.org/toolchain/@v/list' \
  | grep -oE 'go1\.[0-9]+' | sed 's/go1\.//' | sort -un | tail -2 | head -1 | sed 's/^/1./')

gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  d=$(gh api "/repos/osapi-io/$r/contents/go.mod" --jq '.content' 2>/dev/null \
    | base64 -d 2>/dev/null | grep -m1 '^go ' | awk '{print $2}')
  [ -z "$d" ] && continue
  [ "${d%.*}" = "$floor" ] || printf "%s go %s, want %s.0\n" "$r" "$d" "$floor"
done
```

Derive the floor, never hardcode it. A number written into this file is right
the day it is written and wrong after the next release, which is the failure
this check exists to catch.

That command reads the **root** `go.mod` only. Nested modules under `examples/`
declare their own directive and drift separately, which is how six gohai
examples sat at `go 1.25.7` against a root of `1.26.0`. See
[modules.md](modules.md) for finding and fixing those.

Report drift as one block naming every repository behind, not one per
repository: the fix is the same edit in each, and a new Go release puts all of
them behind at once.

```
🔴 go directive behind policy · want 1.26, Go 1.27 is out
   nats-client 1.25.0 · osapi-orchestrator 1.25.7
   → say "bump the go directive" to raise them
```

A repository with no `go.mod` is skipped rather than reported.

## Release state

```bash
gh release list --repo "osapi-io/$r" --limit 1 2>/dev/null
git ls-remote --tags "https://github.com/osapi-io/$r" | tail -3
```

No tags at all means the repository has never been released, which is worth
reporting when a repository has release tooling configured. osapi was in that
state as of 2026-09: a `.goreleaser.yaml` and a release workflow, no tags.

## Coverage

Coverage is enforced in CI rather than reported through the API. `just test`
fails below the target, and the target is declared twice, in
`.github/codecov.yml` and in the shared `go` justfile module. A green CI run is
the coverage answer. Do not try to read a number out of the Codecov badge SVG.

## What this does not cover

Lint findings are not queryable per repository. `golangci-lint` runs inside CI,
so a green `lint` check means zero findings under that repository's
`.golangci.yml`. To see findings, run it locally:

```bash
cd ~/git/osapi-io/<repo> && just go-vet
```

The config is identical across every Go repository in the org by policy, so a
finding in one is usually a finding waiting to happen in the others.
