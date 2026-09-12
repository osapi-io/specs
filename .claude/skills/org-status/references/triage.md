# Triage

Reached when the user asks what to do about an alert, whether the org is
actually exposed, or pastes a `/security` URL. Also the required first step
before any fix.

A `https://github.com/osapi-io/<repo>/security` URL is a valid input on its
own. Take the repository from the path and start at step 1.

## The question Dependabot cannot answer

Dependabot knows a vulnerable version is in `go.mod`. It does not know whether
the vulnerable code runs. That gap is the whole job here, and getting it wrong
in either direction is expensive: a dismissed alert that was real, or weeks
spent migrating away from code nothing calls.

Every alert resolves to exactly one of four verdicts. Establish which before
reporting anything as work.

## Step 1: gather

```bash
gh api "/repos/osapi-io/$r/dependabot/alerts?state=open&per_page=100" --jq '.[] |
  "\(.number)\t\(.security_advisory.ghsa_id)\t\(.security_advisory.cve_id)\t\(.security_advisory.severity)\t\(.security_advisory.cvss.score)\t\(.dependency.package.name)\t\(.dependency.scope)\t\(.security_vulnerability.first_patched_version.identifier // "NONE")\t\(.security_advisory.summary)"'
```

Note `scope`. A `development` dependency is not in the shipped binary, which
usually settles the question on its own.

## Step 2: is there a patch

```bash
gh api "/repos/osapi-io/$r/dependabot/alerts?state=open" \
  --jq '.[] | "\(.security_advisory.ghsa_id) patch=\(.security_vulnerability.first_patched_version.identifier // "NONE")"'

curl -s "https://proxy.golang.org/<module path>/@latest" | jq -r '.Version, .Time'
```

The proxy call matters. `first_patched_version: null` means GitHub's advisory
names no fixed release, and comparing against the newest published version
tells you whether upstream has shipped anything at all. If the newest version
is already inside the vulnerable range, waiting will not help and the verdict
cannot be UPGRADE AVAILABLE.

## Step 3: does the vulnerable code run

Read the advisory summary and ask which component it describes, then check what
the repository imports from that module:

```bash
cd ~/git/osapi-io/$r
grep -rhoE '"<module path>[a-z/]*"' --include='*.go' . | sort | uniq -c | sort -rn
grep -rlE '"<module path>' --include='*.go' . | head
```

A module can hold both a client and a server. Importing
`github.com/docker/docker/client` and `api/types/*` is a client that talks to a
daemon. A CVE in the daemon's request handlers does not apply to it. The same
split appears in database drivers, Kubernetes libraries, and anything shipping
an agent alongside its API types.

Say which import paths you checked when you report a NOT AFFECTED verdict. A
verdict with no evidence behind it is a guess wearing a label.

## Step 4: is it one problem or many

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  hit=$(gh api "/repos/osapi-io/$r/contents/go.mod" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | grep -c '<module path>' || true)
  [ "${hit:-0}" -gt 0 ] && echo "$r depends on it"
done
```

Reachability only needs establishing once per module. Report it once and name
every repository it covers.

## The four verdicts, and the fix for each

### UPGRADE AVAILABLE

A patched version exists. The fix is mechanical.

```bash
cd ~/git/osapi-io/$r
git checkout -b fix/bump-<package>
go get <module path>@<first patched version>
go mod tidy
just ready && just test
```

If Dependabot already opened the PR, merging it is the fix and there is nothing
to write by hand. Check first.

### NOT AFFECTED

A patch does not exist, or does but the vulnerable code is unreachable from
this repository. The fix is to dismiss with `not_used`, which records the
reasoning where the next reader will find it.

```bash
gh api -X PATCH "/repos/osapi-io/$r/dependabot/alerts/<number>" \
  -f state=dismissed \
  -f dismissed_reason=not_used \
  -f dismissed_comment="<which import paths were checked, and why the CVE's component is not among them>"
```

Valid reasons are `fix_started`, `inaccurate`, `no_bandwidth`, `not_used` and
`tolerable_risk`. A reason is required when state is `dismissed`. The token
needs `security_events`.

Write the comment as evidence, not as a verdict. "Imports only
`docker/docker/client` and `api/types/*`; the CVE is in the daemon's archive
handler" survives being read in a year. "Not applicable" does not.

### EXPOSED, NO PATCH

The vulnerable code is reachable and upstream has shipped nothing. There is no
mechanical fix, so do not invent one. Present the options and stop:

- narrow the dependency so the vulnerable component is no longer imported
- replace it
- accept the risk, and dismiss as `tolerable_risk` with the reasoning

This is the user's decision. Bring them the reachability evidence, the CVSS
score, and how long the alert has been open.

### ALREADY DISMISSED

Nothing to do. It will not appear in an `state=open` query, so this verdict
only comes up when someone asks about a specific alert.

## Rules

1. **Never dismiss to shorten a list.** A dismissal is a claim that the code is
   not reachable, and it hides the alert from everyone who looks later. It needs
   the evidence from step 3 behind it.
2. **Confirm before writing.** Show the verdict, the evidence, and the exact
   command, then wait. This holds even when the user has said fix: they are
   approving a verdict they have not seen yet.
3. **Dismiss one alert at a time.** Each takes its own alert number and its own
   comment, because each CVE has its own reachability argument even when they
   share a package.
4. **A CVE the tools cannot reason about is still the user's call.** Say so
   rather than picking a verdict to be decisive.
