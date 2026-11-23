# Audit

Resolve the repository set first, per [SKILL.md](../SKILL.md).

Use this page when the user asks if somebody hacked, exploited or compromised
anything, and in each sweep. [vetting.md](vetting.md) examines a pull request
before it merges. This page asks the same question about what already merged. It
also checks that the defences that make vetting easy are still there.

It answers in two parts. **Compromise** looks for evidence that something
occurred. **Defences** looks for a missing guard. A missing guard is not
evidence, but it makes the next attack easier. Report them separately. A missing
cooldown is not a breach. If you put the two in one list, each looks like the
other.

## Compromise

### Who can push

```bash
gh api /orgs/osapi-io/members --jq '.[].login'
gh api /orgs/osapi-io/outside_collaborators --jq '.[].login'
gh api /orgs/osapi-io/installations \
  --jq '.installations[] | "\(.app_slug)\t\(.repository_selection)\t\(.permissions | to_entries | map("\(.key):\(.value)") | join(","))"'
```

And per repository:

```bash
gh api "/repos/osapi-io/$r/collaborators?affiliation=direct" --jq '.[] | "\(.login)\t\(.role_name)"'
gh api "/repos/osapi-io/$r/keys" --jq '.[] | "\(.title)\tread_only=\(.read_only)\t\(.created_at[:10])"'
gh api "/repos/osapi-io/$r/hooks" --jq '.[] | "\(.config.url)\t\(.created_at[:10])"'
```

If the reader does not know one of these, it is a **STOP**: an account, an app
with `contents:write`, a deploy key that can write, or a webhook to an unknown
host. Org-level webhooks need the `admin:org_hook` scope. Without it, say that
the token cannot see them. Do not report none.

### Who did push

```bash
since=$(date -v-120d +%Y-%m-%dT00:00:00Z)   # GNU: date -d '120 days ago' +%FT00:00:00Z
gh api "/repos/osapi-io/$r/commits?sha=$def&since=$since&per_page=100" --paginate \
  --jq '.[] | "\(.author.login // .commit.author.email)|\(.committer.login // .commit.committer.email)|\(.commit.verification.verified)"' |
  sort | uniq -c | sort -rn
```

`web-flow` commits and signs merges through the web. An author who is not an org
member or `dependabot[bot]` is a **STOP**.

Unsigned commits by a member are **LOOK**, not STOP. A local rebase that
somebody pushes to the default branch removes the GitHub signature, also from
the commits of Dependabot. That is the usual cause here. List them with their
dates, and ask the reader to confirm that the group of commits was theirs:

```bash
gh api "/repos/osapi-io/$r/commits?sha=$def&since=$since&per_page=100" --paginate \
  --jq '.[] | select(.commit.verification.verified | not) | "\(.commit.committer.date[:10])\t\(.sha[:8])\t\(.author.login)\t\(.commit.message | split("\n")[0])"'
```

### What the code depends on

Check each lockfile on the default branch, and each version in it, against OSV:

```bash
s=.claude/skills/org-status/scripts
for r in $repos; do (cd ~/git/osapi-io/$r && git fetch -q origin); "$s/deps.sh" ~/git/osapi-io/$r; done |
  sort -u | "$s/osv-malicious.sh"
```

`deps.sh` reads `go.sum`, `bun.lock` and `package-lock.json` from `origin/HEAD`,
not from the working tree. Thus a local branch cannot hide what ships. On
stderr, it names each kind of lockfile that it cannot parse. Report those,
because a lockfile that nobody scanned is not clean.

`osv-malicious.sh` prints `MALICIOUS` for a version on the OpenSSF
malicious-packages list (`MAL-` ids). It also prints it for a version whose
advisory has CWE-506 (embedded malicious code), or whose summary says so. The
second test is important. A hijacked release of a real package often has a
`GHSA-` id, with a summary like "Critical severity vulnerability that affects
event-stream". A search for `MAL-` does not find it. Each `MALICIOUS` line is a
**STOP**.

It never reads the details of an advisory. Ordinary advisories say "a malicious
actor could". A match on those words reported an HTTP/2 denial of service in
`golang.org/x/net` as a hijack 47 times.

It also prints a count of versions with ordinary advisories.
[triage.md](triage.md) answers that question. Most of them are old versions that
`go.sum` keeps to resolve the graph and never builds. Do not report the count as
compromise.

You install nothing. It needs `curl` and `jq`. A scan of the full org takes
approximately two minutes.

### What CI runs

Third-party Actions:

```bash
grep -hoE 'uses:\s*[^ .][^ ]+' ~/git/osapi-io/*/.github/workflows/*.y*ml |
  awk '{print $2}' | cut -d@ -f1 | sort -u |
  while read -r a; do
    gh api "/advisories?ecosystem=actions&affects=$a&per_page=100" \
      --jq ".[] | \"$a\t\(.ghsa_id)\t\(.summary[:70])\""
  done
```

An advisory against an action in use is a **STOP**, until you confirm that the
version in use is outside the affected range. `tj-actions/changed-files` is a
known answer. Use it to test the query.

Workflow triggers that give a privileged token to PR code:

```bash
grep -nE 'pull_request_target|workflow_run' ~/git/osapi-io/*/.github/workflows/*.y*ml
```

`pull_request_target` runs with the token of the base repository. It is safe
while the job never checks out the head of the pull request. The labeler and
greetings workflows here do not check it out. A `pull_request_target` job with
an `actions/checkout` of `github.event.pull_request.head` is a **STOP**.

### What was released

```bash
cd ~/git/osapi-io/$r && git fetch -q --tags --force origin
for t in $(git tag); do git merge-base --is-ancestor "$t^{commit}" origin/HEAD || echo "$t"; done
```

A release tag that points to a commit that is not on the default branch is a
**STOP**. The release shipped code that nobody merged.

## Defences

These do not show that anything occurred. A missing defence is a hardening
finding. Report it as one block for the full org, because the fix is the same
edit in each repository.

### Every Dependabot entry has a cooldown

```bash
for r in $repos; do
  gh api "/repos/osapi-io/$r/contents/.github/dependabot.yml" --jq .content 2>/dev/null | base64 -d |
    ruby -ryaml -e 'y = YAML.load($stdin.read) || {}
      (y["updates"] || []).each { |u| puts "#{ARGV[0]}\t#{u["package-ecosystem"]}\t#{u["directory"] || u["directories"]}" unless u.dig("cooldown", "default-days").to_i >= 7 }' "$r"
done
```

Each line of output is a finding. Each line is an entry that proposes a release
on the day that it ships, before people can find and remove a hijacked release.
The convention is `default-days: 7` on each entry, and `semver-major-days: 14`
on the ecosystems that use semver (`gomod`, `bun`, `npm`, `swift`).

Never put the `semver-*` keys on `github-actions` or `docker`. Dependabot then
refuses the full file and runs no updates. The only sign is a failed
`.github/dependabot.yml` check on the commit that changed it. Security updates
ignore the cooldown. Thus it never makes a fix for an alert later.

After you edit `dependabot.yml`, confirm that Dependabot accepted it:

```bash
sha=$(gh api "/repos/$owner/$r/commits?path=.github/dependabot.yml&per_page=1" --jq '.[0].sha')
gh api "/repos/$owner/$r/commits/$sha/check-runs" \
  --jq '.check_runs[] | select(.name | test("dependabot")) | "\(.conclusion)\t\(.output.summary)"'
```

A `failure` here is a finding, because it means that the entries above do
nothing.

### Every lockfile is watched

A lockfile with no Dependabot entry gets no alerts and no bumps. Thus a
vulnerable version stays there, and the alert count still shows zero. Compare
the lockfiles that `deps.sh` found with the ecosystems that `dependabot.yml`
declares:

| Lockfile                  | Ecosystem it needs |
| ------------------------- | ------------------ |
| `go.sum`                  | `gomod`            |
| `bun.lock`                | `bun`              |
| `package-lock.json`       | `npm`              |
| `.github/workflows/*.yml` | `github-actions`   |
| `Dockerfile`              | `docker`           |

If no entry covers the directory of a lockfile, that is a finding. Name the
directory.

### Actions are pinned

The rule is in [Tooling](../../../../CONSTITUTION.md#tooling). Pin an action
from outside the organization by its full commit SHA, with its version in a
comment. Each other form is a finding:

```bash
grep -nE 'uses:\s*[^ .][^ ]+' ~/git/osapi-io/*/.github/workflows/*.y*ml |
  grep -vE '@[0-9a-f]{40}\s+#\s*v?[0-9]' | grep -v 'uses: *osapi-io/'
```

### Workflows declare their permissions

The rule is in [Tooling](../../../../CONSTITUTION.md#tooling). A workflow with
no `permissions:` block is a finding. A repository whose default token can write
is also a finding:

```bash
for r in $repos; do
  gh api "/repos/$owner/$r/actions/permissions/workflow" \
    --jq "select(.default_workflow_permissions != \"read\" or .can_approve_pull_request_reviews) | \"$r\tdefault token \(.default_workflow_permissions), approves PRs \(.can_approve_pull_request_reviews)\""
done
grep -LE '^\s*permissions:' ~/git/osapi-io/*/.github/workflows/*.y*ml
```

What each kind of workflow here needs:

| Workflow                             | Permissions                                               |
| ------------------------------------ | --------------------------------------------------------- |
| tests, lint, report card, docs build | `contents: read`                                          |
| commit lint                          | `contents: read`, `pull-requests: read`                   |
| stale                                | `actions: write`, `issues: write`, `pull-requests: write` |
| delete merged branch                 | `contents: write`                                         |

## Reporting

Compromise findings come first in the report, as blocks. When there are none,
say so in one line, with what you covered. Without that, "nothing found" means
little:

```
✅ no sign of compromise · 8 repos
   1 member, no outside collaborators, no deploy keys
   all commits by members or Dependabot · 2,888 dependency versions, none malicious
   24 actions, no advisories · every release tag on its default branch
```

Defences come next, as one block for each kind:

```
🟡 3 lockfiles unwatched by Dependabot · osapi
   docs/bun.lock · ui/bun.lock · Dockerfile
   → say "watch the osapi lockfiles" to add the entries
```

Never report a compromise finding as a public issue, because the issue tells an
attacker what you saw. It goes to a draft repository advisory, which only
maintainers can read:

```bash
jq -n --arg r "$r" --arg s "<one line>" --arg d "<what was found, where, since when>" \
  '{summary: $s, description: $d, severity: "critical",
    vulnerabilities: [{package: {ecosystem: "other", name: $r}}]}' |
  gh api -X POST "/repos/osapi-io/$r/security-advisories" --input -
```

A defence finding is not exploitable alone. It can be an issue.
