## 1. Convert the modules

Each module: directory, README, flat prefixed recipes, shim deleted, inline
section removed from the root README. Consumers updated before the next module
begins.

- [ ] 1.1 `just` — conversion already written as osapi-justfiles#39
- [ ] 1.2 `go` — also fixes osapi's coverage target: its justfile
  `export JUST_COVERAGE_TARGET` never reaches the shim module, so osapi runs
  against the default 100. A flat module with
  `set allow-duplicate-variables := true` lets the consumer override the default
  directly
- [ ] 1.3 `bats`
- [ ] 1.4 `docker`
- [x] 1.5 `react` — osapi-justfiles#44
- [ ] 1.5a `react`, `go` — restore `env()` defaults so both lint standalone, and
  move consumer overrides to a dotenv file
- [ ] 1.6 `docs` — ensure its paths do not overlap with `md`

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
