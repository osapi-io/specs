## 1. Record the requirement

- [x] 1.1 Audit every repository's labels against the kinds of file it holds
- [x] 1.2 Write the requirements
- [x] 1.3 Record the decisions and their rejected alternatives in design.md

## 2. Agree the shared names

- [x] 2.1 Settle the label for justfiles — `kind/just`
- [x] 2.2 Settle the label for TypeScript — `kind/ts`
- [x] 2.3 Settle the label for container files — `kind/docker`
- [x] 2.4 Rename `github/action` to `kind/action`, and scope `kind/yaml` to
  exclude what it covers
- [x] 2.5 Broaden `kind/docs` to `**/*.md`; it matched `docs/**` only, leaving
  every README and contributing guide unlabelled

## 3. Apply to each repository

- [ ] 3.1 `osapi` — add `kind/just`, `kind/ts`, `kind/docker`
- [ ] 3.2 `gohai` — add `kind/just`
- [ ] 3.3 `nats-client` — add `kind/just`
- [ ] 3.4 `nats-server` — add `kind/just`
- [ ] 3.5 `osapi-orchestrator` — add `kind/just`
- [ ] 3.6 `specs` — add `kind/just`, remove `test/unit`
- [ ] 3.7 `osapi-justfiles` — add `kind/just`, remove `kind/bats` and `kind/go`

## 4. Verification

- [ ] 4.1 Confirm every label in a repository matches at least one file it holds
- [ ] 4.2 Confirm every kind of file a repository holds has a label
- [ ] 4.3 Confirm the same kind carries the same label name in every repository
- [ ] 4.4 Confirm no two labels match the same file as a matter of course
