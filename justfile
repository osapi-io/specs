set allow-duplicate-variables

# Shared recipes are imported flat and prefixed (md-fmt, md-fmt-check).
# import? tolerates the files being absent so `just fetch` works on a fresh clone.

import? '.just/remote/md.just'

import? '.just/remote/just.just'

# No documentation site, so md formats every markdown file in the repository.
md_site_dir := ""

# Everything in this repository is markdown somebody wrote, so nothing is excluded
# from formatting.
md_extra_excludes := ""

# --- Fetch ---

# Fetch shared justfiles from osapi-justfiles
fetch:
    mkdir -p .just/remote
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/md/md.just -o .just/remote/md.just
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/just/just.just -o .just/remote/just.just

# --- Checks ---

# Validate every SKILL.md against the Agent Skills specification
[group('lint')]
skill-lint:
    uvx --with pyyaml python scripts/validate-skills.py

# Run every count in components/ against the command stated beside it
[group('lint')]
check-counts:
    python3 scripts/check-counts.py

# Links resolve, pages are linked, no em dashes
[group('lint')]
check-docs:
    python3 scripts/check-docs.py

# --- Top-level orchestration ---

# Run all checks
test:
    just md-fmt-check
    just just-fmt-check
    just skill-lint
    just check-counts
    just check-docs

# Format and lint before committing
ready:
    just md-fmt
    just just-fmt
    just skill-lint
    just check-counts
    just check-docs
