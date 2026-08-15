## 1. Convert the modules

Each module: directory, README, flat prefixed recipes, **prefixed variables with
plain defaults**, shim deleted, inline section removed from the root README.
Consumers updated before the next module begins.

A variable that varies by repository is a plain assignment a consumer reassigns.
`env()` is kept only where the value varies by environment rather than by
repository.

- [ ] 1.1 `just` — conversion already written as osapi-justfiles#39
- [x] 1.2 `go` — osapi-justfiles#46
- [ ] 1.3 `bats`
- [ ] 1.4 `docker` — rename `image_name`, `image_tag`, `dockerfile` with the
  module prefix and make them plain assignments; unprefixed names collide in a
  shared scope
- [x] 1.5 `react` — osapi-justfiles#44
- [ ] 1.6 `docs` — rename `host` and `port` with the module prefix, and ensure
  its paths do not overlap with `md`. These two may keep `env()`: a dev server
  port varies by machine, not by repository

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
