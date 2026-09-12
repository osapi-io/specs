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
