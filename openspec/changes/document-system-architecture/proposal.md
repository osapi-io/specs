## Why

The corpus describes how each repository is laid out and configured. It says
nothing about how the repositories relate to one another — what depends on what,
how those dependencies are declared, or which module paths are canonical.

Because nothing described it, the prose that did drifted from reality. An audit
of the dependency graph found three claims that no longer hold:

- `nats-client` and `nats-server` documented themselves as "linked via `replace`
  in consuming project's `go.mod`". There are no `replace` directives in any
  repository.
- `gohai` describes itself as "built to be embedded in OSAPI". `osapi` has no
  dependency on `gohai` and no reference to it in any package.
- `osapi` declares `module github.com/retr0h/osapi` while living at
  `github.com/osapi-io/osapi`. Four of five Go modules match their repository
  location; this one does not, so `go get github.com/osapi-io/osapi` does not
  resolve.

## What Changes

- Establish the `module-dependencies` capability, recording the dependency graph
  and how dependencies are declared.
- Require a module path to match its repository location.
- Require documentation describing a dependency to match what `go.mod` declares.

## Capabilities

### New Capabilities

- `module-dependencies`: how osapi-io repositories depend on one another, and
  how those dependencies are declared.

### Modified Capabilities

None.

## Impact

- `osapi`: module path does not match its repository location. Changing it is a
  breaking change for `osapi-orchestrator`, which imports the current path.
- `gohai`: README describes a consumer relationship that does not exist.
- No other repository changes.
