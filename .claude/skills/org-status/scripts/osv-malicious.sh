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
bad=0
cut -d' ' -f4 "$tmp/hits" | tr ',' '\n' | sort -u | while read -r id; do
  rec=$(curl -sf --max-time 20 "https://api.osv.dev/v1/vulns/$id")
  s=$(jq -r '.summary // ""' <<< "$rec")
  text=$(jq -r '"\(.summary // "") \(.details // "") \(.database_specific.cwe_ids // [] | join(" "))"' <<< "$rec")
  if [[ $id == MAL-* ]] || grep -qiE 'CWE-506|malware|backdoor|hijack|exfiltrat|trojan|embedded malicious|(is considered|contains|added|introduced|published a) malicious|malicious (code|version|package|release|actor|dependency)' <<< "$text"; then
    grep -E "(^| |,)$id(,|$)" "$tmp/hits" | awk -v id="$id" -v s="$s" '{print "MALICIOUS", $1, $2, $3, id, s}'
  fi
done | tee "$tmp/bad"
[ ! -s "$tmp/bad" ]
