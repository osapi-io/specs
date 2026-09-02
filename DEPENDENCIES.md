# Cross-repository dependencies

Measured 2026-09-02 from each repository's `go.mod`.

```
osapi-orchestrator ──> osapi
osapi ─────────────┬─> nats-client
                   └─> nats-server
gohai ─────────────>   nothing in this organization
```

Every module path matches its repository location under `github.com/osapi-io/`,
and no repository uses a `replace` directive — each dependency is a pinned
version, so a local checkout is never silently substituted for a release.

`gohai` depends on nothing else here, and nothing here depends on it — no
`go.mod` and no Go source in this organization imports it. It stands alone.

## Reproducing this

```bash
for d in osapi gohai nats-client nats-server osapi-orchestrator; do
  grep -m1 "^module " "$d/go.mod"
  grep -E "osapi-io/" "$d/go.mod" | grep -v "^module"
done
```

Run it against the checkouts rather than trusting the diagram. This graph was
first recorded when `osapi` still declared itself `github.com/retr0h/osapi`; the
path was corrected in osapi-io/osapi#446, and the stale copy read as current
until someone measured it.
