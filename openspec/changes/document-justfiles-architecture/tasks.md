## 1. Reference implementations

- [x] 1.1 Create the `md` module as a directory with its own README, flat
  prefixed recipes, and no shim
- [x] 1.2 Pin the tool and language runtime versions used by `md`
- [x] 1.3 Bring every environment variable in the repository under the `JUST_`
  prefix
- [x] 1.4 Convert the `just` module to a directory with flat prefixed recipes
  and remove its shim
- [x] 1.5 Convert the root README to an index that links to per-module READMEs
- [x] 1.6 Update the distribution image build to include nested module
  directories

## 2. Consumer migration for converted modules

- [ ] 2.1 Update `specs` to fetch `just/just.just` and call `just-fmt-check`
- [ ] 2.2 Update `osapi`, `gohai`, `nats-client`, and `nats-server` to fetch
  `just/just.just` and call `just-fmt-check`

## 3. Convert the remaining modules

Each module moves into a directory, gains a README, converts to flat prefixed
recipes, drops its shim, and loses its inline section in the root README.
Consuming repositories are updated before starting the next module.

- [ ] 3.1 Convert `go` and update every consuming repository
- [ ] 3.2 Convert `bats` and update every consuming repository
- [ ] 3.3 Convert `docker` and update every consuming repository
- [ ] 3.4 Convert `react` and update every consuming repository
- [ ] 3.5 Convert `docs` and update every consuming repository, ensuring its
  paths do not overlap with `md`

## 4. Verification

- [ ] 4.1 Confirm no `.mod.just` files remain and no repository references `::`
  recipe names
- [ ] 4.2 Confirm every module README documents its recipes, requirements,
  exclusions, and environment variables
- [ ] 4.3 Confirm the distribution image contains every module recipe file
- [ ] 4.4 Confirm every consuming repository's lint job passes
