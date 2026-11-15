# Quality

Resolve the repository set first, per [SKILL.md](../SKILL.md).

## Is the default branch green

The check rollup of the head commit is the direct answer:

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  roll=$(gh api "/repos/osapi-io/$r/commits/HEAD/check-runs?per_page=100" \
    --jq '[.check_runs[] | .conclusion // "pending"] | group_by(.) | map("\(.[0]):\(length)") | join(" ")' 2>/dev/null || true)
  printf "%-22s %s\n" "$r" "${roll:-no checks}"
done
```

A repository with no CI workflow reports no checks. That is a finding, not a
pass.

## A specific workflow

`gh run list --branch main` includes scheduled jobs and the runs of Dependabot.
Thus it answers a different question from "did CI pass". Name the workflow:

```bash
gh run list --repo "osapi-io/$r" --workflow go.yml --branch main --limit 1 \
  --json conclusion,createdAt,headSha \
  -q '.[] | "\(.conclusion)  \(.createdAt[:10])  \(.headSha[:8])"'
```

Each Go repository here runs `go.yml`. The specs repository does not. Skip it,
or expect an empty result.

## Go version drift

The `go` directive must name the older of the two newest Go minor releases
([why](../../../../CONSTITUTION.md)). Nobody gets a notification when a new
minor release ships. Thus this check finds it.

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

Calculate the minimum. Never hardcode it. A number in this file is correct on
the day that somebody writes it, and incorrect after the next release. This
check exists to find that failure.

That command reads only the **root** `go.mod`. Nested modules under `examples/`
declare their own directive, and they become old separately. Thus six gohai
examples stayed at `go 1.25.7` while the root was `1.26.0`.
[modules.md](modules.md) tells how to find and fix those.

Report drift as one block that names each repository that is behind. Do not use
one block for each repository. The fix is the same edit in each, and a new Go
release puts all of them behind at the same time.

```
🔴 go directive behind policy · want 1.26, Go 1.27 is out
   nats-client 1.25.0 · osapi-orchestrator 1.25.7
   → say "bump the go directive" to raise them
```

Skip a repository with no `go.mod`. Do not report it.

## Tool version drift

The constitution requires that the two provisioning paths use the same version.
It also says what occurs if they do not: if one path pins a version and the
other does not, the two become different ([why](../../../../CONSTITUTION.md)).
Thus no repository selects its own linter version. Four repositories that lint
with four different versions is a finding.

Ask the module what will really run. **Do not grep `go.mod`.** An indirect
requirement with no version line of its own can supply a tool. A grep reads that
as "not pinned", but the module resolves a specific version.

```bash
latest=$(curl -s --max-time 20 'https://proxy.golang.org/github.com/golangci/golangci-lint/v2/@latest' \
  | sed -n 's/.*"Version":"\([^"]*\)".*/\1/p')

gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  d=~/git/osapi-io/$r
  [ -f "$d/go.mod" ] || continue
  v=$(cd "$d" && go list -m github.com/golangci/golangci-lint/v2 2>/dev/null | awk '{print $2}')
  [ -n "$v" ] && [ "$v" != "$latest" ] && printf "%s %s, want %s\n" "$r" "$v" "$latest"
done
```

Report drift as one block that names each repository that is behind, as for the
go directive. The fix is the same command in each, and a new linter release puts
all of them behind at the same time.

An old pin is not only cosmetic. A linter that is older than the toolchain can
crash and report no findings. v2.12.2 crashed in `buildir` under Go 1.27. The
crash shows as a red build on an unrelated pull request.

Before, nobody could see this drift. The shared `deps` recipes resolved each
tool again on each run, and linted with the newest version. The pins did
nothing, so nothing compared them. That is fixed. Thus this check is now useful.

## Release state

```bash
gh release list --repo "osapi-io/$r" --limit 1 2>/dev/null
git ls-remote --tags "https://github.com/osapi-io/$r" | tail -3
```

No tags means that the repository never had a release. Report that when a
repository has release tooling. osapi was in that state in 2026-09: it had a
`.goreleaser.yaml` and a release workflow, and no tags.

## Coverage

CI enforces coverage. The API does not report it. `just test` fails below the
target. Two files declare the target: `.github/codecov.yml` and the shared `go`
justfile module. A green CI run is the coverage answer. Do not try to read a
number from the SVG of the Codecov badge.

## What this does not cover

You cannot query lint findings for each repository. `golangci-lint` runs in CI.
Thus a green `lint` check means zero findings under the `.golangci.yml` of that
repository. To see findings, run it locally:

```bash
cd ~/git/osapi-io/<repo> && just go-vet
```

By policy, the config is the same in each Go repository in the org. Thus a
finding in one usually becomes a finding in the others later.
