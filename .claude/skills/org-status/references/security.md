# Security

Resolve the repository set first, per [SKILL.md](../SKILL.md).

## Ask the organization, not each repository

All three alert systems have an org-level endpoint. One call each, covering
every repository:

```bash
for kind in dependabot secret-scanning code-scanning; do
  n=$(gh api "/orgs/osapi-io/$kind/alerts?state=open&per_page=100" --jq 'length' 2>/dev/null || true)
  printf "%-16s %s\n" "$kind" "${n:-not available}"
done
```

Three calls instead of three per repository. Use this first, and only drop to
per-repository queries when something is non-zero and you need to know where.

The org endpoints cover archived and private repositories too, so a count here
can exceed what the public non-archived repository set explains. That is not an
error.

## Dependabot alerts

A known vulnerability in a declared dependency. This is the one that usually has
findings.

```bash
gh api "/orgs/osapi-io/dependabot/alerts?state=open&per_page=100" \
  --jq 'group_by(.repository.name)[] | "\(.[0].repository.name)\t\(length) alert(s)"'
```

Then the detail for one repository:

```bash
gh api "/repos/osapi-io/$r/dependabot/alerts?state=open&per_page=100" \
  --jq '.[] | "\(.security_advisory.severity)\t\(.dependency.package.name)\t\(.security_vulnerability.first_patched_version.identifier // "NO PATCH")\t\(.created_at[:10])"'
```

**A count is not a finding.** Before reporting alerts as work, establish the
verdict in [triage.md](triage.md): whether a patch exists, and whether the
vulnerable code is reachable from this repository. An alert with no patch and no
reachable call path is not work, and listing it as work makes the report
dishonest.

Group by package. One dependency often carries several advisories, and listing
them separately turns one decision into three.

The page a human wants is `https://github.com/osapi-io/<repo>/security`. Print
that, bare.

An alert and a Dependabot PR are different things. An alert says a
vulnerability applies. A PR says a newer version exists. Either can exist
without the other.

## Code scanning alerts

Static analysis findings, from CodeQL or an uploaded SARIF file.

```bash
gh api "/repos/osapi-io/$r/code-scanning/alerts?state=open&per_page=100" --jq 'length'
```

This returns `{"message":"no analysis found",...,"status":"404"}` for a
repository that has never run a scan. That is not zero alerts. It means the
question does not apply there, and reporting it as clean is wrong. Detect it by
checking whether the response is an array:

```bash
out=$(gh api "/repos/osapi-io/$r/code-scanning/alerts?state=open&per_page=100" 2>/dev/null || true)
if printf '%s' "$out" | jq -e 'type == "array"' >/dev/null 2>&1; then
  printf '%s' "$out" | jq 'length'
else
  echo "not configured"
fi
```

The `|| true` matters. `gh api` exits non-zero on a 404, which kills the whole
loop under `set -e` and leaves the remaining repositories unqueried with nothing
to say they were skipped.

## Secret scanning alerts

A committed credential.

```bash
gh api "/repos/osapi-io/$r/secret-scanning/alerts?state=open&per_page=100" --jq 'length'
```

Same array check applies: the endpoint 404s when secret scanning is off for the
repository.

Treat any finding here as urgent, and do not paste the secret itself into the
conversation. Report the repository, the alert URL, and the secret type from
`.secret_type`.

## Permissions

All three endpoints need the `security_events` scope, or `repo` scope on a
private repository. A 403 means the token lacks it:

```bash
gh auth status
gh auth refresh -h github.com -s security_events
```

Do not report a 403 as "no alerts". Say the token cannot see them.
