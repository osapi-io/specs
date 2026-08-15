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

- [ ] 2.1 `specs` — `just` module
- [ ] 2.2 `gohai`
- [ ] 2.3 `nats-client`
- [ ] 2.4 `nats-server`
- [ ] 2.5 `osapi` — react done (osapi#436); still consumes `go`, `docs`, `just`,
  `docker` as shims

## 3. Verification

- [ ] 3.1 Confirm no `.mod.just` file remains
- [ ] 3.2 Confirm no repository invokes a `::` namespaced recipe
- [ ] 3.3 Confirm every consuming repository's lint job passes
- [ ] 3.4 Confirm the root README contains no inline module sections
