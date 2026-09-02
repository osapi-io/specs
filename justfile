set allow-duplicate-variables

# Shared recipes are imported flat and prefixed (md-fmt, md-fmt-check).
# import? tolerates the files being absent so `just fetch` works on a fresh clone.

import? '.just/remote/md.just'

import? '.just/remote/just.just'

# No documentation site, so md formats every markdown file in the repository.
md_site_dir := ""

# Spec Kit is run through uvx rather than installed, and pinned so the artifacts
# it generates do not change under whoever runs it. Bump deliberately.

speckit_version := "1.0.3"

# Spec Kit vendors templates and a constitution scaffold into each project's
# .specify/. Those are restored by `specify init --force`, so formatting them
# produces churn that the next re-init discards.
md_extra_excludes := "--exclude '**/.specify/**'"

# --- Fetch ---

# Fetch shared justfiles from osapi-justfiles
fetch:
    mkdir -p .just/remote
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/md/md.just -o .just/remote/md.just
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/just/just.just -o .just/remote/just.just

# --- Spec Kit ---

# Run a Spec Kit CLI command against a component, e.g. `just spec osapi extension list`
[group('spec')]
spec component *args:
    SPECIFY_INIT_DIR=components/{{ component }} uvx --from specify-cli=={{ speckit_version }} specify {{ args }}

# --- Top-level orchestration ---

# Run all checks
test:
    just md-fmt-check
    just just-fmt-check

# Format and lint before committing
ready:
    just md-fmt
    just just-fmt
