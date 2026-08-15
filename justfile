# Shared recipes are imported flat and prefixed (md-fmt, md-fmt-check).
# import? tolerates the files being absent so `just fetch` works on a fresh clone.

import? '.just/remote/md.just'

mod? just '.just/remote/just.mod.just'

# --- Fetch ---

# Fetch shared justfiles from osapi-justfiles
fetch:
    mkdir -p .just/remote
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/md/md.just -o .just/remote/md.just
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/just.mod.just -o .just/remote/just.mod.just
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/just.just -o .just/remote/just.just

# --- Specs ---

# Validate all changes and specs
validate:
    openspec validate --all --strict

# --- Top-level orchestration ---

# Run all checks
test:
    just md-fmt-check
    just just::fmt-check
    just validate

# Format and lint before committing
ready:
    just md-fmt
    just just::fmt
