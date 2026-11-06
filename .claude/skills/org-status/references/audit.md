# Audit

Resolve the repository set first, per [SKILL.md](../SKILL.md).

Reached when the user asks whether anything has been hacked, exploited or
compromised, and as part of every sweep. [vetting.md](vetting.md) judges a pull
request before it lands. This page asks the same question of what already
landed, and checks that the defences which make vetting cheap are still in
place.

It answers in two parts. **Compromise** looks for evidence that something
happened. **Defences** looks for a missing guard, which is not evidence of
anything but makes the next attack easier. Report them separately. A missing
cooldown is not a breach, and putting the two in one list makes either look
like the other.

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

Anything the reader does not recognise is a **STOP**: an account, an app with
`contents:write`, a deploy key that can write, a webhook to an unknown host.
Org-level webhooks need the `admin:org_hook` scope. Without it, say the token
cannot see them rather than reporting none.

### Who did push

```bash
since=$(date -v-120d +%Y-%m-%dT00:00:00Z)   # GNU: date -d '120 days ago' +%FT00:00:00Z
gh api "/repos/osapi-io/$r/commits?sha=$def&since=$since&per_page=100" --paginate \
  --jq '.[] | "\(.author.login // .commit.author.email)|\(.committer.login // .commit.committer.email)|\(.commit.verification.verified)"' |
  sort | uniq -c | sort -rn
```

Merges through the web are committed by `web-flow` and signed. An author who is
not an org member or `dependabot[bot]` is a **STOP**.

Unsigned commits by a member are **LOOK**, not STOP. A local rebase pushed to
the default branch strips GitHub's signature, Dependabot's commits included,
and that is the usual cause here. List them with their dates and ask the reader
to confirm the burst was theirs:

```bash
gh api "/repos/osapi-io/$r/commits?sha=$def&since=$since&per_page=100" --paginate \
  --jq '.[] | select(.commit.verification.verified | not) | "\(.commit.committer.date[:10])\t\(.sha[:8])\t\(.author.login)\t\(.commit.message | split("\n")[0])"'
```

### What the code depends on

Every lockfile on the default branch, every version in it, against OSV:

```bash
s=.claude/skills/org-status/scripts
for r in $repos; do (cd ~/git/osapi-io/$r && git fetch -q origin); "$s/deps.sh" ~/git/osapi-io/$r; done |
  sort -u | "$s/osv-malicious.sh"
```

`deps.sh` reads `go.sum`, `bun.lock` and `package-lock.json` from
`origin/HEAD`, not the working tree, so a local branch cannot hide what ships.
It names any lockfile kind it cannot parse on stderr. Report those, because a
lockfile nobody scanned is not a clean one.

`osv-malicious.sh` prints `MALICIOUS` for a version on the OpenSSF
malicious-packages list (`MAL-` ids), and for one whose advisory carries
CWE-506 (embedded malicious code) or whose summary says so. The second test
matters. A hijacked release of a real package is often published under a
`GHSA-` id with a summary like "Critical severity vulnerability that affects
event-stream", which a search for `MAL-` misses. Any `MALICIOUS` line is a
**STOP**.

It never reads an advisory's details. Ordinary write-ups say "a malicious actor
could", and matching on that flagged an HTTP/2 denial of service in
`golang.org/x/net` as a hijack 47 times.

It also prints a count of versions with ordinary advisories. That is
[triage.md](triage.md)'s question, and most of them are old versions `go.sum`
keeps for graph resolution and never builds. Do not report the count as
compromise.

Nothing to install. It needs `curl` and `jq`, and a full org scan takes about
two minutes.

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

An advisory against an action in use is a **STOP** until the version in use is
confirmed outside the affected range. `tj-actions/changed-files` is a known
answer to test the query against.

Workflow triggers that hand PR code a privileged token:

```bash
grep -nE 'pull_request_target|workflow_run' ~/git/osapi-io/*/.github/workflows/*.y*ml
```

`pull_request_target` runs with the base repository's token. It is safe while
the job never checks out the pull request's head. The labeler and greetings
workflows here do not. A `pull_request_target` job with an `actions/checkout`
of `github.event.pull_request.head` is a **STOP**.

### What was released

```bash
cd ~/git/osapi-io/$r && git fetch -q --tags --force origin
for t in $(git tag); do git merge-base --is-ancestor "$t^{commit}" origin/HEAD || echo "$t"; done
```

A release tag that points at a commit off the default branch is a **STOP**: the
release shipped code nobody merged.

## Defences

These do not show that anything happened. A missing one is a hardening finding,
reported as one block for the whole org because the fix is the same edit in each
repository.

### Every Dependabot entry has a cooldown

```bash
for r in $repos; do
  gh api "/repos/osapi-io/$r/contents/.github/dependabot.yml" --jq .content 2>/dev/null | base64 -d |
    ruby -ryaml -e 'y = YAML.load($stdin.read) || {}
      (y["updates"] || []).each { |u| puts "#{ARGV[0]}\t#{u["package-ecosystem"]}\t#{u["directory"] || u["directories"]}" unless u.dig("cooldown", "default-days").to_i >= 7 }' "$r"
done
```

Any output is a finding. Each line is an entry that proposes a release the day it ships,
before a hijacked one has had time to be noticed and pulled. The house setting
is `default-days: 7` and `semver-major-days: 14`. Security updates ignore the
cooldown, so it never delays a fix for an alert.

### Every lockfile is watched

A lockfile with no Dependabot entry gets no alerts and no bumps, so a
vulnerable version sits there and the alert count still reads zero. Compare the
lockfiles `deps.sh` found against the ecosystems `dependabot.yml` declares:

| Lockfile | Ecosystem it needs |
| --- | --- |
| `go.sum` | `gomod` |
| `bun.lock` | `bun` |
| `package-lock.json` | `npm` |
| `.github/workflows/*.yml` | `github-actions` |
| `Dockerfile` | `docker` |

A lockfile whose directory no entry covers is a finding. Name the directory.

### Actions are pinned

`uses: actions/checkout@v7` follows a tag, and a tag can be moved to different
code by whoever controls the action's repository. A commit SHA cannot. A tag
pin is a finding. Dependabot updates SHA pins and keeps the version in a
trailing comment, so pinning costs nothing in upkeep.

## Reporting

Compromise findings lead, as blocks, ahead of everything else in the report.
When there are none, say so in one line with what was covered, because "nothing
found" means little without it:

```
✅ no sign of compromise · 8 repos
   1 member, no outside collaborators, no deploy keys
   all commits by members or Dependabot · 2,888 dependency versions, none malicious
   24 actions, no advisories · every release tag on its default branch
```

Defences follow as one block per kind:

```
🟡 3 lockfiles unwatched by Dependabot · osapi
   docs/bun.lock · ui/bun.lock · Dockerfile
   → say "watch the osapi lockfiles" to add the entries
```

A compromise finding is never filed as a public issue, because the issue tells
an attacker what was noticed. It goes to a draft repository advisory, which only
maintainers can read:

```bash
jq -n --arg r "$r" --arg s "<one line>" --arg d "<what was found, where, since when>" \
  '{summary: $s, description: $d, severity: "critical",
    vulnerabilities: [{package: {ecosystem: "other", name: $r}}]}' |
  gh api -X POST "/repos/osapi-io/$r/security-advisories" --input -
```

A defence finding is not exploitable on its own and can be an issue.
