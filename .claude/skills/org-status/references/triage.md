# Triage

Use this page when the user asks what to do about an alert, or if the org is
really exposed, or pastes a `/security` URL. It is also the necessary first step
before each fix.

A `https://github.com/osapi-io/<repo>/security` URL is a valid input alone. Get
the repository from the path and start at step 1.

## The question Dependabot cannot answer

Dependabot knows that a vulnerable version is in `go.mod`. It does not know if
the vulnerable code runs. This page closes that gap. An error in either
direction is expensive. One error is a dismissed alert that was real. The other
is weeks of work to remove code that nothing calls.

Each alert gets exactly one of four verdicts. Find the verdict before you report
anything as work.

## Step 1: gather

```bash
gh api "/repos/osapi-io/$r/dependabot/alerts?state=open&per_page=100" --jq '.[] |
  "\(.number)\t\(.security_advisory.ghsa_id)\t\(.security_advisory.cve_id)\t\(.security_advisory.severity)\t\(.security_advisory.cvss.score)\t\(.dependency.package.name)\t\(.dependency.scope)\t\(.security_vulnerability.first_patched_version.identifier // "NONE")\t\(.security_advisory.summary)"'
```

Note `scope`. A `development` dependency is not in the shipped binary. Usually,
that alone answers the question.

## Step 2: is there a patch

```bash
gh api "/repos/osapi-io/$r/dependabot/alerts?state=open" \
  --jq '.[] | "\(.security_advisory.ghsa_id) patch=\(.security_vulnerability.first_patched_version.identifier // "NONE")"'

curl -s "https://proxy.golang.org/<module path>/@latest" | jq -r '.Version, .Time'
```

The proxy call is important. `first_patched_version: null` means that the GitHub
advisory names no fixed release. A comparison with the newest published version
tells you if upstream shipped anything. If the newest version is already in the
vulnerable range, a wait does not help, and the verdict cannot be UPGRADE
AVAILABLE.

## Step 3: does the vulnerable code run

Read the advisory summary, and find which component it describes. Then check
what the repository imports from that module:

```bash
cd ~/git/osapi-io/$r
grep -rhoE '"<module path>[a-z/]*"' --include='*.go' . | sort | uniq -c | sort -rn
grep -rlE '"<module path>' --include='*.go' . | head
```

A module can have a client and a server. Code that imports
`github.com/docker/docker/client` and `api/types/*` is a client that connects to
a daemon. A CVE in the request handlers of the daemon does not apply to it. The
same split occurs in database drivers, Kubernetes libraries, and each module
that ships an agent together with its API types.

When you report a NOT AFFECTED verdict, say which import paths you checked. A
verdict with no evidence is a guess with a label.

## Step 4: is it one problem or many

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  hit=$(gh api "/repos/osapi-io/$r/contents/go.mod" --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | grep -c '<module path>' || true)
  [ "${hit:-0}" -gt 0 ] && echo "$r depends on it"
done
```

You need to find reachability only one time for each module. Report it one time,
and name each repository that it covers.

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

If Dependabot already opened the PR, the merge of that PR is the fix, and you
write nothing by hand. Check first.

### NOT AFFECTED

No patch exists, or a patch exists but this repository cannot get to the
vulnerable code. The fix is a dismissal with `not_used`. It records the reason
where the next reader finds it.

```bash
gh api -X PATCH "/repos/osapi-io/$r/dependabot/alerts/<number>" \
  -f state=dismissed \
  -f dismissed_reason=not_used \
  -f dismissed_comment="<which import paths were checked, and why the CVE's component is not among them>"
```

The valid reasons are `fix_started`, `inaccurate`, `no_bandwidth`, `not_used`
and `tolerable_risk`. A reason is necessary when the state is `dismissed`. The
token needs `security_events`.

Write the comment as evidence, not as a verdict. "Imports only
`docker/docker/client` and `api/types/*`; the CVE is in the daemon's archive
handler" is still useful to a reader in a year. "Not applicable" is not.

### EXPOSED, NO PATCH

The repository can get to the vulnerable code, and upstream shipped nothing.
There is no mechanical fix, so do not invent one. Give the options and stop:

- make the dependency smaller, so that the code does not import the vulnerable
  component
- replace it
- accept the risk, and dismiss it as `tolerable_risk`, with the reason

The user decides. Give the user the reachability evidence, the CVSS score, and
how long the alert has been open.

### ALREADY DISMISSED

Do nothing. It does not show in a `state=open` query. Thus this verdict occurs
only when somebody asks about a specific alert.

## Say the phrase in the report

Each verdict ends its block with the words that act on it, in quotes, exactly as
the reader must type them:

| Verdict           | Action line                                                          |
| ----------------- | -------------------------------------------------------------------- |
| UPGRADE AVAILABLE | `-> say "bump <package>" to open the PR`                             |
| NOT AFFECTED      | `-> say "dismiss the <package> alerts" to close all <n> as not_used` |
| EXPOSED, NO PATCH | `-> your call: narrow, replace, or accept. No upgrade exists.`       |
| ALREADY DISMISSED | no action line                                                       |

The verdict tells the reader what is true. The action line tells the reader what
to type. Without it, the report becomes a status board, and the reader must ask
more questions. The reader cannot guess the phrase.

## Rules

1. **Never dismiss an alert to make a list shorter.** A dismissal is a claim
   that the code is not reachable. It hides the alert from each person who looks
   later. It needs the evidence from step 3.
2. **Confirm before you write.** Show the verdict, the evidence and the exact
   command, then wait. This is true also when the user said fix. The user then
   approves a verdict that the user did not see yet.
3. **Dismiss one alert at a time.** Each takes its own alert number and its own
   comment. Each CVE has its own reachability argument, also when two CVEs are
   in the same package.
4. **If the tools cannot decide about a CVE, the user decides.** Say so. Do not
   select a verdict only to look decisive.
