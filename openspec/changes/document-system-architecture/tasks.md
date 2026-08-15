## 1. Record the architecture

- [x] 1.1 Map the dependency graph and how each dependency is declared
- [x] 1.2 Write the `module-dependencies` capability
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Correct the module path

Sequenced: `osapi` renames and publishes before `osapi-orchestrator` moves.

- [ ] 2.1 Search for consumers of `github.com/retr0h/osapi` outside the
  organization
- [ ] 2.2 `osapi` — rename the module to `github.com/osapi-io/osapi` and update
  its own imports
- [ ] 2.3 `osapi-orchestrator` — update its `require` and importing files once
  the new path is published

## 3. Correct the documentation

- [ ] 3.1 `gohai` — describe the consumer relationship it has, not the one
  intended
- [ ] 3.2 Confirm no repository documents a `replace`-based linkage
- [ ] 3.3 Confirm no `go.mod` contains a `replace` directive

## 4. Verification

- [ ] 4.1 Confirm every module path matches its repository location
- [ ] 4.2 Confirm no `replace` directive points outside its own module
- [ ] 4.3 Confirm every documented dependency appears in the corresponding
  `go.mod`
