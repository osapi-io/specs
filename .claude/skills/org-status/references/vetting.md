# Vetting a pull request

Resolve the repository set first, per [SKILL.md](../SKILL.md).

A green check says the code builds. It does not say the code is what it claims
to be. A pull request that brings in a typosquatted module, a hijacked release,
or a workflow change dressed as a version bump passes CI the same way an honest
one does. Vetting is the check that tells them apart.

Vet every pull request before calling it ready, before approving it, and before
[merging.md](merging.md) touches it. That includes checking the branch out:
`just test`, `just go-mod` and `go generate` run whatever the branch contains, so
a checkout followed by the gate executes the pull request on this machine.

Every pull request ends with one of three verdicts:

| Verdict | Means | What happens |
| --- | --- | --- |
| CLEAN | every check below passed | may be reported as ready |
| LOOK | something a person has to read | report it with the reason; never merge it from a sweep |
| STOP | a signal of tampering | report it first, do not approve, merge, rebase or check out |

## Step 1: who made it

```bash
gh pr view "$n" --repo "osapi-io/$r" --json author,isCrossRepository,headRefName \
  -q '"author=\(.author.login) fork=\(.isCrossRepository) branch=\(.headRefName)"'

gh api "/repos/osapi-io/$r/pulls/$n/commits" --paginate \
  --jq '.[] | "\(.sha[:8])\t\(.author.login // "none")\t\(.committer.login // "none")\t\(.commit.verification.verified)"'
```

A commit Dependabot made reads `dependabot[bot]  web-flow  true`, meaning
GitHub committed and signed it.

- **STOP** when the title reads like a bump and the author is not
  `app/dependabot`, or when a `dependabot/` branch comes from a fork. Both are
  impersonation, and the second is how one gets past a reviewer who trusts the
  branch name.
- **LOOK** when any commit on a Dependabot branch is not the signed
  `dependabot[bot]` one. A tidy commit pushed by a maintainer, per
  [merging.md](merging.md), is the usual reason and is fine, but it is now a
  human change and gets read like one. Name the commit and its author.

## Step 2: what it touches

A bump changes a small, fixed set of files. Anything outside it is not a bump.

```bash
gh pr view "$n" --repo "osapi-io/$r" --json files -q '.files[].path'
```

| Branch | Allowed |
| --- | --- |
| `dependabot/go_modules/...` | `go.mod` and `go.sum`, at the root or under `examples/` |
| `dependabot/github_actions/...` | `.github/workflows/*.yml`, `uses:` lines only |
| `dependabot/bun/...`, `dependabot/npm_and_yarn/...` | `package.json` and its lockfile, in the directory the entry names |

**STOP** for any other path on a Dependabot branch. For a workflow bump, read the
diff and confirm every changed line is a `uses:` line:

```bash
gh pr diff "$n" --repo "osapi-io/$r" | grep -E '^[-+][^-+]' | grep -vE '^[-+]\s+(- )?uses: '
```

Any output is a STOP.

## Step 3: what changed in go.mod

```bash
gh pr diff "$n" --repo "osapi-io/$r" |
  awk '/^diff --git/ { mod = ($0 ~ /go\.mod$/) } mod && /^[-+][^-+]/ { print }'
```

Every `+` line should be a `-` line with the same module path and a newer
version. Anything else needs a reader:

- **STOP** for an added or changed `replace` directive. It swaps a module for
  different code while `go.mod` still names the original.
- **LOOK** for a module path that appears only on the `+` side. Run it through
  step 4.
- **LOOK** for a changed `toolchain` or `tool` line, or a `go` directive that
  moves, on a branch whose title names one dependency.
- **LOOK** for a pseudo-version (`v0.0.0-20261030150403-7af8fac5354e`) where a
  tag used to be. Dependabot proposes tagged releases, so an untagged commit is
  somebody's choice.

## Step 4: new modules

The bumped module is not the only one that can arrive. Its new release may
require modules nobody here depended on before, and a typosquat arrives that
way, one level down, where nobody reads.

List the module paths the branch adds to `go.sum` that the base does not have:

```bash
base=$(gh pr view "$n" --repo "osapi-io/$r" --json baseRefOid -q .baseRefOid)
known=$(mktemp)
gh api "/repos/osapi-io/$r/contents/go.sum?ref=$base" --jq .content |
  base64 -d | awk '{print $1}' | sort -u > "$known"

gh pr diff "$n" --repo "osapi-io/$r" |
  awk '/^diff --git/ { s = ($0 ~ /go\.sum$/) } s && /^\+[^+]/ { print substr($1, 2) }' |
  sort -u | comm -13 "$known" - > "$known.new"
cat "$known.new"
```

Repeat with the `examples/` paths for a branch that touches them. For each new
path:

**Does it resemble something already depended on?**

```bash
python3 -I .claude/skills/org-status/scripts/resembles.py "$known" < "$known.new"
```

It flags a path within two edits of a known one (`labstack/ech0` against
`labstack/echo`), and a known name under a different owner (`evil/gopsutil`
against `shirou/gopsutil`). Any line of output is a **STOP** until a person has
confirmed the module is the real one.

**How old is it?**

```bash
curl -s --max-time 20 "https://api.deps.dev/v3/systems/go/packages/$(printf %s "$m" | sed 's|/|%2F|g')" |
  jq -r '[.versions[].publishedAt] | min'
```

A module whose first release is under 90 days old is **LOOK**. Say how old it is
and which module requires it.

### npm

A pull request that touches `bun.lock` or `package-lock.json` gets the same two
questions. `deps.sh` reads both, so compare the base against the head:

```bash
s=.claude/skills/org-status/scripts
git fetch -q origin "pull/$n/head:vet-$n"
comm -13 <("$s/deps.sh" . "$base" | awk '$1=="npm"{print $2}' | sort -u) \
         <("$s/deps.sh" . "vet-$n" | awk '$1=="npm"{print $2}' | sort -u)
```

Fetching a ref runs nothing, so this is safe before a verdict. Check each new
name the way step 4 checks a module, with deps.dev's npm endpoint
(`/v3/systems/npm/packages/<name>`).

## Step 5: the release itself

A real package can ship a malicious release when its maintainer's account is
taken over. Those releases are usually found and pulled within days, so how
recently a version was published is a risk in itself.

```bash
curl -s --max-time 20 "https://proxy.golang.org/$m/@v/$v.info" | jq -r .Time
```

**LOOK** when the target version was published under 72 hours ago. Waiting for
it to age costs nothing, and Dependabot proposes the next release anyway.

Ask OSV whether the version is a known bad release. Its feed includes the
OpenSSF malicious-packages list, whose identifiers start `MAL-`:

```bash
curl -s --max-time 20 -X POST https://api.osv.dev/v1/query \
  -d "{\"package\":{\"name\":\"$m\",\"ecosystem\":\"Go\"},\"version\":\"${v#v}\"}" |
  jq -r '[.vulns[]?.id] | join(" ")'
```

- **STOP** for any `MAL-` identifier.
- **LOOK** for a `GHSA-` or `GO-` identifier. The bump lands on a version with a
  known vulnerability, and [triage.md](triage.md) decides whether it matters.

Run both against every module whose version the bump moves, indirect ones
included, not only the one in the title. `scripts/osv-malicious.sh` does the OSV
half for a whole list at once, and also catches a hijacked release published
under a `GHSA-` id rather than `MAL-`:

```bash
"$s/deps.sh" . "vet-$n" | comm -13 <("$s/deps.sh" . "$base") - | "$s/osv-malicious.sh"
```

Any `MALICIOUS` line is a **STOP**.

## Step 6: an Actions bump

For each changed `uses:` line, the owner and repository on the `+` side must
match the `-` side exactly, and the new ref must exist upstream:

```bash
gh api "/repos/$owner/$repo/git/ref/tags/$tag" --jq .object.sha
```

- **STOP** when the owner or repository changed, or the tag does not exist.
- **STOP** when GitHub has an advisory against the action and the new version
  is in its range:

```bash
gh api "/advisories?ecosystem=actions&affects=$owner/$repo" --jq '.[] | "\(.ghsa_id)\t\(.vulnerabilities[0].vulnerable_version_range)\t\(.summary[:70])"'
```

- **LOOK** when the release was published under 72 hours ago, as in step 5:

```bash
gh api "/repos/$owner/$repo/releases/tags/$tag" --jq .published_at
```

## A pull request a person wrote

The steps above assume a bump, where anything unexpected is a signal. A human
pull request is expected to change code, so there is nothing to compare it
against, and the verdict is never better than LOOK until somebody has read it.
Vetting says where to read first. These paths run code in CI or on a
maintainer's machine, and a change to any of them is named in the report:

| Path | Why |
| --- | --- |
| `.github/workflows/`, `.github/actions/` | runs in CI with the repository's token |
| `justfile`, `.just/`, `.mise.toml` | runs on every `just test`, locally and in CI |
| `go.mod` `replace` and `tool` lines | swaps code, or adds a binary the gate runs |
| `//go:generate` lines | runs on `go generate` |
| `Dockerfile`, `scripts/`, any `*.sh` | runs during a build |
| any binary file | cannot be read |

In a workflow, these are a **STOP** until a maintainer has read them:
`pull_request_target`, a new `permissions:` grant of `write`, a new reference to
`secrets.`, and `curl ... | sh` or anything else that runs a download.

A first-time contributor's workflows wait for approval before they run. Approve
that run only after reading the workflow files in the diff.

## Reporting

Lead the pull request's block with the verdict and the reason, worst first. A
CLEAN bump earns no block of its own.

```
🔴 osapi #631 · dependabot · 1d · STOP
   bump golang.org/x/net adds github.com/googel/uuid to go.sum
   resembles github.com/google/uuid, first published 9 days ago
   https://github.com/osapi-io/osapi/pull/631
   → do not merge. Say "close 631" to close it, then report the module
```

## Never

- **Approve, merge, rebase, or check out a STOP.** A rebase asks Dependabot to
  rebuild the branch, and a checkout followed by any recipe runs it.
- **Clear a verdict because CI is green.** CI ran the code; it did not judge it.
- **Skip vetting because the author is Dependabot.** The author line is the
  first thing an impersonation copies.
