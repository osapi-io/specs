## 1. Convert the modules

Each module: directory, README, flat prefixed recipes, **prefixed variables with
plain defaults**, shim deleted, inline section removed from the root README.
Consumers updated before the next module begins.

A variable that varies by repository is a plain assignment a consumer reassigns.
`env()` is kept only where the value varies by environment rather than by
repository.

- [ ] 1.1 `just` — conversion already written as osapi-justfiles#39
- [x] 1.2 `go` — osapi-justfiles#46
- [ ] 1.3 `bats` — remove instead of converting. Nothing fetches it, no `.bats`
  file exists in the organization, and it appears only as an example in the root
  README
- [ ] 1.4 `docker` — remove instead of converting. Only `osapi` loads it and
  nothing invokes its recipes; images are published by goreleaser. Its
  `dockerfile` default is `Dockerfile.local`, which `osapi` does not have —
  evidence it has not run in a long time. Drop `osapi`'s `mod? docker` line
- [x] 1.5 `react` — osapi-justfiles#44
- [ ] 1.6 `docs` → `docusaurus` — rename the module for what it manages, prefix
  its recipes and variables, and give it the site path as configuration. It
  keeps its formatting recipes: the site contains MDX and component syntax that
  mdformat cannot parse
- [ ] 1.6a `md` — exclude the site directory, taken as configuration rather than
  assumed
- [ ] 1.6b Confirm no markdown file falls inside both formatters' paths

## 2. Update consumers

Done immediately after the module each depends on converts, not batched.

Converting a consumer is not finished when its recipes run. Each one covers:

1. Justfile — swap `mod?` for `import?`, rename call sites, declare or reassign
   the module's variables
2. Workflows — rename call sites, and provision the tool the new module needs
3. Delete the configuration of any tool the change removes, including lockfiles
4. `.mise.toml` — drop tools no longer used, add tools now used
5. `CONTRIBUTING.md` — name the tools actually in use, in prerequisites and in
   the commands it shows. A guide naming a removed tool is a defect under
   `correct-documentation-drift`
6. Confirm every reference link in the files touched resolves to a definition

Steps 5 and 6 were missed on `gohai` and caught in review: its guide still
described Prettier via Bun and listed `just docs::fmt`, and four references had
no definition so they rendered as literal text.

- [ ] 2.1 `specs` — `just` module
- [ ] 2.2 `gohai` — gohai#150
- [ ] 2.3 `nats-client`
- [ ] 2.4 `nats-server`
- [ ] 2.5 `osapi` — react done (osapi#436); still consumes `go`, `docs`, `just`,
  `docker` as shims

## 3. Verification

- [ ] 3.0 Confirm no `CONTRIBUTING.md` names a tool its repository does not
  install, and that every reference link in it resolves

- [ ] 3.1 Confirm no `.mod.just` file remains

- [ ] 3.2 Confirm no repository invokes a `::` namespaced recipe

- [ ] 3.3 Confirm every consuming repository's lint job passes

- [ ] 3.4 Confirm the root README contains no inline module sections
