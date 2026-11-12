#!/usr/bin/env bash
# Read "ecosystem name version" lines on stdin and ask OSV about every one.
# Prints two kinds of line:
#
#   MALICIOUS <ecosystem> <name> <version> <id> <summary>
#     the version is on the OpenSSF malicious-packages list (MAL- ids), or an
#     advisory against it describes planted code, a backdoor or a hijacked
#     release, which some publish under a GHSA id instead
#   VULNS <count>
#     how many versions carry an ordinary advisory, which is triage.md's
#     question rather than this one
#   VULN <ecosystem> <name> <version> <ids>
#     one per such version, only when OSV_LIST=1 is set. vet-pr.py sets it,
#     because a pull request's few versions are worth naming; an org scan's
#     hundreds are not
#
# Exits 1 when anything is MALICIOUS.
set -euo pipefail
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
cat > "$tmp/in"
split -l 900 "$tmp/in" "$tmp/c."
for c in "$tmp"/c.*; do
  jq -Rn '{queries: [inputs | split(" ") |
    {package: {name: .[1], ecosystem: .[0]}, version: (if .[0] == "Go" then (.[2] | ltrimstr("v")) else .[2] end)}]}' \
    < "$c" > "$c.json"
  curl -sf --max-time 120 -X POST https://api.osv.dev/v1/querybatch -d @"$c.json" |
    jq -r '.results[] | [.vulns[]?.id] | join(",")' | paste -d' ' "$c" -
done | awk 'NF > 3' > "$tmp/hits"
echo "VULNS $(wc -l < "$tmp/hits" | tr -d ' ')"
if [ "${OSV_LIST:-}" = 1 ]; then sed 's/^/VULN /' "$tmp/hits"; fi
bad=0
cut -d' ' -f4 "$tmp/hits" | tr ',' '\n' | sort -u | while read -r id; do
  rec=$(curl -sf --max-time 20 "https://api.osv.dev/v1/vulns/$id")
  s=$(jq -r '.summary // ""' <<< "$rec")
  # CWE-506 is Embedded Malicious Code. The summary is matched too, but never
  # the details: ordinary write-ups say "a malicious actor could", which
  # reads like a hijack to a pattern and is not one.
  text=$(jq -r '"\(.summary // "") \(.database_specific.cwe_ids // [] | join(" "))"' <<< "$rec")
  if [[ $id == MAL-* ]] || grep -qiE 'CWE-506|malware|backdoor|hijacked (release|package|version|account)|(account|maintainer) (takeover|compromise)|compromised (release|package|version)|exfiltrat|trojan|embedded malicious|malicious (code|version|package|release|dependency) in|malicious package' <<< "$text"; then
    grep -E "(^| |,)$id(,|$)" "$tmp/hits" | awk -v id="$id" -v s="$s" '{print "MALICIOUS", $1, $2, $3, id, s}'
  fi
done | tee "$tmp/bad"
[ ! -s "$tmp/bad" ]
