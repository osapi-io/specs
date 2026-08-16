## 1. Record the architecture

- [x] 1.1 Map the dependency graph and how each dependency is declared
- [x] 1.2 Write the `module-dependencies` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Correct the module path

Sequenced: `osapi` renames and publishes before `osapi-orchestrator` moves.

- [x] 2.1 Search for consumers of `github.com/retr0h/osapi` outside the
  organization
- [x] 2.2 `osapi` — rename the module to `github.com/osapi-io/osapi` and update
  its own imports
- [x] 2.3 `osapi-orchestrator` — update its `require` and importing files once
  the new path is published

## 3. Correct the documentation

- [x] 3.1 `gohai` — describe the consumer relationship it has, not the one
  intended

- [x] 3.2 Confirm no repository documents a `replace`-based linkage

- [x] 3.3 Confirm no `go.mod` contains a `replace` directive pointing outside
  its own repository

- [x] 3.4 `osapi` — `docs/docusaurus.config.ts` declares
  `organizationName: 'retr0h'` three lines below `url: 'osapi-io.github.io'`

- [x] 3.5 `osapi` — `contributing.md` links Discussions to `retr0h/go-gilt`, a
  different project

## 4. Verification

- [x] 4.1 Confirm every module path matches its repository location
- [x] 4.2 Confirm every `replace` directive points within the repository that
  holds it
- [x] 4.3 Confirm every documented dependency appears in the corresponding
  `go.mod`
- [x] 4.4 Confirm no repository names an owner or project other than its own,
  excluding attribution of a person
