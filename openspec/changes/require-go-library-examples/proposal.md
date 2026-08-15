## Why

`go-library-standards` specifies configuration but says nothing about a library
shipping runnable examples. Examples appear only obliquely, in the table
explaining why `dependabot.yml` is permitted to vary — "which example modules
that library contains" — which assumes they exist without requiring them.

Three of four libraries ship them: `nats-client` has five, `nats-server` four,
`osapi-orchestrator` two. `gohai` has none, though its `.gitignore` carries four
rules for an `examples/` directory that was never created.

`gohai`'s README also has no `Examples` section, which the Go library README
requirement already mandates. Nothing detected either, because a requirement
about examples was never written.

## What Changes

- Require every Go library to ship runnable examples under `examples/`.
- Require the README's `Examples` section to link them.

## Capabilities

### Modified Capabilities

- `go-library-standards`: gains a requirement covering examples.

## Impact

- `gohai`: needs examples written — standalone programs demonstrating SDK usage.
  Real work, not restructuring.
- `nats-client`, `nats-server`, `osapi-orchestrator`: already conform.
