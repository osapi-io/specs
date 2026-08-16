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

- [x] 3.2 Confirm every repository declares the tools its recipes invoke. Six of
  seven did. `osapi` was missing `uv`, which `just md-fmt` invokes through
  `uvx`, and it is now declared (osapi-io/osapi#450).

  `redocly` was declared nowhere at all. Tracing it found the source: the shared
  `docusaurus` module installed it globally and unpinned, so the binary lived on
  the developer's path rather than in the project and its version was whatever
  the registry served that day. Since redocly versions quote YAML scalars
  differently, the combined specification a repository commits depended on when
  its author last ran `just deps` — and nothing in continuous integration runs
  `generate`, so it never surfaced. On one machine the installed version was
  2.19.1 while the registry served 2.46.1.

  Resolved as two changes: the shared module stops installing a global
  (osapi-io/osapi-justfiles#61), and `osapi` pins the version where it invokes
  it (osapi-io/osapi#456), through `bunx` because `bun` is the declared runner
  and `bunx` already runs the other JavaScript tooling. Pinned to the version
  that produced the committed specification, so it is byte-identical and nothing
  regenerates. The same pass removed the last `npx` invocation in any module.

  The distinction this settled: a **runner** is declared in `.mise.toml` — `go`,
  `just`, `bun`, `uv` — and a **payload** it fetches is pinned where it is
  invoked. `mdformat` forces that split rather than illustrating it: its GFM
  plugin has to be injected into the same environment, which `.mise.toml` cannot
  express, and without it every table in the repository is silently reflowed
