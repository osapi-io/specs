set allow-duplicate-variables

# Shared recipes are imported flat and prefixed (md-fmt, md-fmt-check).
# import? tolerates the files being absent so `just fetch` works on a fresh clone.

import? '.just/remote/md.just'

import? '.just/remote/just.just'

# No documentation site, so md formats every markdown file in the repository.
md_site_dir := ""

# Everything in this repository is markdown somebody wrote, so only the skills
# are excluded from formatting: .claude, by the shared recipe, and .agents/skills,
# which links to .claude/skills for Codex.
md_extra_excludes := "--exclude '**/.agents/**'"

# --- Fetch ---

# List the recipes
default:
    @just --list

# Fetch shared justfiles from osapi-justfiles
fetch:
    mkdir -p .just/remote
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/md/md.just -o .just/remote/md.just
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/just/just.just -o .just/remote/just.just

# --- Top-level orchestration ---

# Run all checks
test:
    just md-fmt-check
    just just-fmt-check
    just check-docs
    just check-counts

# --- Checks ---

# Check links, anchors, skill frontmatter and the documentation contract
check-docs:
    uv run --no-project --python 3.13 python scripts/check_docs.py

# Run each count a page states against the repository it describes
check-counts:
    uv run --no-project --python 3.13 python scripts/check_counts.py

# Format and lint before committing
ready:
    just md-fmt
    just just-fmt
