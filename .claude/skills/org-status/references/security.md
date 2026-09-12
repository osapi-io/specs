# Security

Resolve the repository set first, per [SKILL.md](../SKILL.md).

Three separate systems answer "is anything wrong". They fail differently, so
query them separately and report them separately.

## Dependabot alerts

A known vulnerability in a declared dependency. This is the one that usually has
findings.

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  n=$(gh api "/repos/osapi-io/$r/dependabot/alerts?state=open&per_page=100" --jq 'length' 2>/dev/null)
  printf "%-22s %s\n" "$r" "${n:-query failed}"
done
```

Then pull the detail for any repository with a non-zero count:

```bash
gh api "/repos/osapi-io/$r/dependabot/alerts?state=open&per_page=100" \
  --jq '.[] | "\(.security_advisory.severity)\t\(.dependency.package.name)\t\(.dependency.manifest_path)\t\(.security_advisory.summary)"'
```

Sort by severity: `critical`, `high`, `medium`, `low`. Group by package, because
one dependency often carries several advisories and reporting them as separate
problems overstates the work.

The human page is `https://github.com/osapi-io/<repo>/security/dependabot`. Give
that URL alongside the counts.

An alert and a Dependabot PR are different things. An alert says a vulnerability
applies. A PR says a newer version exists. A repository can have alerts with no
PR, which usually means the fix needs a manual bump, and that is worth saying
out loud.

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
