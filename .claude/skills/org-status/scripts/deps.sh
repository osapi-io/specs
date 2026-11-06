#!/usr/bin/env bash
# Print every dependency a repository locks, one "ecosystem name version" per
# line, read from a git ref rather than the working tree so a local branch
# cannot hide what the default branch ships.
#
#   deps.sh <clone> [ref]      ref defaults to origin/HEAD
#
# Covers go.sum (Go), bun.lock and package-lock.json (npm). A lockfile kind
# this does not parse is printed to stderr as "unparsed <path>", because a
# lockfile nobody scanned must not read as a clean one.
set -euo pipefail
dir=$1 ref=${2:-origin/HEAD}
cd "$dir"
git ls-tree -r --name-only "$ref" | grep -v node_modules | while read -r f; do
  case "$f" in
    go.sum | */go.sum)
      git show "$ref:$f" | awk '{v=$2; sub(/\/go\.mod$/, "", v); print "Go", $1, v}' ;;
    bun.lock | */bun.lock)
      git show "$ref:$f" |
        sed -nE 's/^[[:space:]]+"[^"]+": \["(@?[^@"]+)@([^"]+)".*/npm \1 \2/p' |
        grep -vE ' (workspace|file|link|github|git\+[^ ]*):' || true ;;
    package-lock.json | */package-lock.json)
      git show "$ref:$f" | jq -r '.packages // {} | to_entries[] | select(.key != "" and .value.version) |
        "npm \(.key | sub(".*node_modules/"; "")) \(.value.version)"' ;;
    bun.lockb | */bun.lockb | yarn.lock | */yarn.lock | pnpm-lock.yaml | */pnpm-lock.yaml | uv.lock | */uv.lock | Cargo.lock | */Cargo.lock)
      echo "unparsed $f" >&2 ;;
  esac
done | sort -u
