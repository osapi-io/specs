## 1. Record the requirement

- [x] 1.1 Write the requirement
- [x] 1.2 Record the decisions and their rejected alternatives in design.md

## 2. Apply to each repository

- [x] 2.1 `osapi` — `AGENTS.md` written as part of its layout conversion
  (osapi-io/osapi#450)
- [x] 2.2 `gohai`
- [x] 2.3 `nats-client`
- [x] 2.4 `nats-server`
- [x] 2.5 `osapi-orchestrator`
- [x] 2.6 `specs`
- [x] 2.7 `osapi-justfiles`

## 3. Verification

- [x] 3.1 Confirm every `AGENTS.md` states how tools are invoked. All seven
  carry the `mise exec -- just test` form and the explanation of why a bare
  `just` resolves differently for an agent
- [ ] 3.2 Confirm every repository declares the tools its recipes invoke. Six of
  seven do. `osapi` was missing `uv`, which `just md-fmt` invokes through `uvx`;
  it is now declared (osapi-io/osapi#450). One gap remains: `osapi`'s `generate`
  recipe invokes `redocly`, which no repository file declares — it resolves from
  whatever the developer installed globally. Declaring it is not a one-line fix:
  the version mise supplies (2.46.1) quotes YAML scalars differently from the
  version currently on the developer's path (2.19.1), so the committed combined
  spec and both generated SDKs change the first time anyone runs `just generate`
  against it. That regeneration is its own change, and nothing in continuous
  integration runs `generate`, so the drift is invisible until someone does
