# Feature Specification: Building a domain

**Feature Branch**: `005-building-a-domain`

**Created**: 2026-09-28

**Status**: Archived 2026-09-28, amended twice 2026-09-28 — FR-028 states the
SDK's method-naming convention, derived from the existing surface once it was
established that none had been written. Earlier that day — the SC-001 reading
(T021) found that nothing stated a domain's test obligations, that FR-007's six
layers and FR-001's seven artifact kinds did not reconcile, and that FR-006
split node-targeted from controller-only operations by directory without saying
what decides it. FR-027 is new; the amendment is recorded in
[changelog.md](../../.specify/memory/changelog.md).

**Input**: Subject B of [003-corpus-backfill](../003-corpus-backfill/spec.md) —
the second and last subject of the corpus backfill. 003's `data-model.md`
assigns this subject `adding-an-api-domain.md` wholly, `api-guidelines.md` and
`principles.md` folded in, and `system-architecture.md`'s component map, entry
points, layers and request flow.

## What this specification is

A corpus specification, like [004](../004-job-system/spec.md). Every requirement
below takes the form *the corpus MUST state X*. Nothing in osapi's Go source
changes. What changes is where a contributor reads the answer: today it is a
654-line site page, and afterwards it is this corpus with the page reduced to a
citation table.

Each requirement was checked against the repository before being written — 003's
FR-009 — and cites the file it describes — 003's FR-011. Where the page says
something the code has outgrown, it is recorded below as a **Gap** naming both
sides rather than corrected in passing. Four such gaps were found, and they are
the reason this specification is worth more than a copy of the page.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A contributor can add a domain from the corpus alone (Priority: P1)

Somebody adding a domain to osapi needs to know what artifacts a domain consists
of, in what order they are built, and which of the choices along the way are
rules rather than preferences. Today that lives on a site page. They should be
able to answer it from the corpus, so the `add-a-domain` skill can cite one
statement rather than carry a second.

**Why this priority**: this is the subject. Everything else here supports it.

**Independent Test**: SC-001 — a reader who has not seen the site page answers
the four fixed questions from the corpus alone.

**Acceptance Scenarios**:

1. **Given** a contributor who has never added a domain, **When** they ask what
   a domain consists of across every layer, **Then** the corpus names the
   layers, the artifacts each one takes, and the consistency obligation that
   binds them — without their needing the site.
2. **Given** a contributor partway through, **When** they ask whether a step may
   be skipped or reordered, **Then** the corpus distinguishes the steps whose
   order is forced by a tool from the steps merely conventionally done in that
   order, and says which is which.
3. **Given** a contributor reading a rule the corpus states, **When** they ask
   why it is a rule, **Then** the corpus gives the reason or the file that
   enforces it, so the rule can be checked rather than believed.

______________________________________________________________________

### User Story 2 - An operator is not sent to a contributor's document (Priority: P1)

`api-guidelines.md` and `principles.md` are addresses an operator may have
bookmarked or found in search. Removing them must not leave a dead link, and
what replaces them must not send an operator into the corpus, which is not
written for them.

**Why this priority**: the same rule 004 obeyed. A corpus statement that costs
an operator their bookmark is not an improvement.

**Independent Test**: SC-002 and SC-003 — every removed address still resolves,
and no surviving operator page points into the corpus.

**Acceptance Scenarios**:

1. **Given** a bookmark to `architecture/api-guidelines.md` or
   `architecture/principles.md`, **When** it is opened after this change,
   **Then** it resolves to the contributor page rather than to a 404.
2. **Given** `system-architecture.md` after its contributor half is removed,
   **When** an operator reads it, **Then** health checks, authentication,
   authorization, CORS and external dependencies are all still there and the
   page reads as a whole rather than as a remainder.

______________________________________________________________________

### User Story 3 - The rule has one home (Priority: P2)

The `add-a-domain` skill currently carries the domain-building knowledge itself.
After this it cites the corpus, in the shape
[003's citation contract](../003-corpus-backfill/contracts/citation.md) defines.

**Why this priority**: this is the point of the backfill, but it depends on the
corpus statement existing first.

**Independent Test**: SC-004's `just test`, and SC-005's grep.

**Acceptance Scenarios**:

1. **Given** the skill's references after this change, **When**
   `just skill-lint` runs, **Then** every citation resolves to a requirement in
   this specification.
2. **Given** a rule this specification states, **When** the skill's references
   are grepped for it, **Then** the rule's name appears with a citation and its
   mechanics do not appear twice.

### Edge Cases

- **A rule 001 already holds.** Provider types, file structure, the provider
  interface, naming, platform variants and the idempotency obligation are the
  provider contract's. Subject B reaches the same files from the other
  direction, so it cites rather than restates — see FR-002.
- **A rule that turns out to be wrong.** Four already have; they are the Gaps
  below. The rule is to record both sides, because a silent correction leaves
  nobody able to tell whether the site was wrong or the reader was.
- **A step whose order is not actually forced.** The page presents eight
  numbered steps. Some orderings are imposed by code generation and some are
  habit. Stating the second kind as a requirement would freeze a preference —
  FR-004.
- **An authority that does not exist.** The page defers to a specification that
  is not in this repository. Deferring to nothing is worse than stating nothing,
  because it reads as though the rule has been settled elsewhere — Gap in
  FR-019.

## Requirements *(mandatory)*

### Scope and method

- **FR-001**: The corpus MUST state what a domain consists of across every
  layer, and MUST state the consistency obligation as the page states it: a
  domain appears in every place an existing domain appears, and the check is to
  pick a completed domain and search for it. Evidence:
  `docs/docs/sidebar/development/adding-an-api-domain.md`, "Cross-Layer
  Consistency (MANDATORY)".
- **FR-002**: Where this subject reaches provider types, file structure, the
  provider interface, naming, platform variants or the idempotency obligation,
  the corpus MUST cite [001](../001-provider-contract/spec.md) rather than
  stating the rule a second time. The provider contract holds fifteen
  requirements about providers already, and memory is not exempt from the
  one-statement test 003's FR-008 applies to the site.
- **FR-003**: Where it reaches delivery semantics, the two clocks, the dead
  letter queue or any other job mechanic, the corpus MUST cite the job system in
  [004](../004-job-system/spec.md) and the memory it produced. Where it reaches
  signing, response verification or agent identity, it MUST cite
  [002](../002-agent-key-store/spec.md).

### The order of the work

- **FR-004**: The corpus MUST state the build order, and MUST distinguish the
  parts of it that a tool forces from the parts that are convention. The forced
  ones are: the OpenAPI specification precedes generation, because generation
  reads it; generation precedes the handler, because the handler implements a
  generated interface; the combined specification precedes the SDK client,
  because the SDK generates from the combined file. **The combined
  specification** is `internal/controller/api/gen/api.yaml`, which
  `redocly join` assembles from every domain's own `gen/api.yaml` inside
  `just generate`; a domain absent from it is invisible to the SDK however
  complete its own spec is. The rest — documentation after the CLI, verification
  last — is convention, and stating it as a requirement would freeze a
  preference as a rule. Evidence: the `//go:generate` directives under
  `internal/controller/api/*/gen/`, the `redocly join` step in `just generate`,
  and `go generate ./pkg/sdk/client/gen/...`.
- **FR-005**: The corpus MUST state the eight steps as a walkthrough rather than
  as eight requirements, because the sequence is the part most likely to change
  and a numbered requirement per step would have to be renumbered every time a
  tool changes. What is stated as a requirement is what must be true of the
  result — FR-004's forced orderings, and the per-layer obligations below.

### Layers, and what each one takes

- **FR-006**: The corpus MUST state where a domain's code goes **and what
  decides it**, because the directory is the consequence rather than the rule.
  An operation is **node-targeted** when the work happens on a managed machine:
  it is addressed to a host, dispatched through the job system, and carried out
  by a provider on an agent. It is **controller-only** when the controller
  answers it itself, from state it holds — the job queue, the audit log,
  enrollment, health, the object store — with no agent executing anything.
  Node-targeted operations live under `internal/controller/api/node/{domain}/`
  and carry `/node/{hostname}` in their path; controller-only ones live under
  `internal/controller/api/{domain}/` and do not. The provider goes under
  `internal/provider/{domain}/` or `internal/provider/{category}/{domain}/`.

  A domain name can appear in **both**, which is why the test is functional
  rather than nominal: `internal/controller/api/file/` uploads a file to the
  object store at `/api/file`, and `internal/controller/api/node/file/` deploys
  one to a host at `/api/node/{hostname}/file/deploy`. Same noun, different
  machine doing the work. Evidence: those two `gen/api.yaml` files, and the
  directory listings of `internal/controller/api/` and
  `internal/controller/api/node/`.

- **FR-007**: The corpus MUST state the component map, the entry points, the six
  layers — CLI, REST API, job system, provider, agent lifecycle, configuration —
  and the request flow, because that is what a contributor reads immediately
  before the domain instructions.

  It MUST also state how those six relate to the seven artifact kinds a domain
  contributes (FR-001), because the two lists differ and a reader who takes them
  for one list will hunt for a layer that is not there. The layers describe
  **the running system**; the artifacts describe **what a domain adds to it**.
  Four artifacts land in a layer — the provider in the provider layer, the agent
  processor in the agent lifecycle, the API handler in the REST API, the CLI
  commands in the CLI. Three are not layers at all: the SDK service is a
  *client* of the REST API rather than a layer of the system, and documentation
  and tests are not runtime code. The configuration and job system layers exist
  already for every domain and are not something a domain adds. Evidence:
  `docs/docs/sidebar/architecture/system-architecture.md`, lines 12–174 and
  241–266.

- **FR-008**: The corpus MUST state the request path a domain's operation takes,
  `CLI → SDK → REST API → Job Client → NATS → Agent → Provider`, and that the
  provider runs on the agent rather than the controller. Evidence: the page's
  "Step 0"; `internal/job/client/client.go`.

### Agent wiring

- **FR-009**: The corpus MUST state that two files connect a provider to the
  agent — a processor file under `internal/agent/` and the registration in
  `cmd/agent_setup.go` — and MUST state what does *not* change:
  `agent/types.go`, `agent/agent.go` and the `JobClient` interface, because the
  registry handles dispatch and facts wiring. Evidence:
  `ProviderRegistry.Register` at `internal/agent/registry.go:51`, `AllProviders`
  at `:74`, and the single
  `provider.WireProviderFacts(a.GetFacts, registry.AllProviders()...)` call at
  `internal/agent/agent.go:90`.
- **FR-010**: The corpus MUST state the `FactsAware` obligation as the page
  states it — embed `provider.FactsAware`, add the compile-time
  `var _ provider.FactsSetter` check — and MUST cite rather than restate where
  001 already holds it. Evidence: `WireProviderFacts` at
  `internal/provider/facts.go:64`.

### The API surface

- **FR-011**: The corpus MUST state that the OpenAPI specification is the source
  of truth for input validation, and MUST state the three places a tag goes and
  the one place it does not: `x-oapi-codegen-extra-tags` on request body
  properties, at *parameter* level for query parameters rather than inside
  `schema:`, `format: uuid` for UUID path parameters, and **not** on path
  parameters in strict-server mode, where oapi-codegen generates no tags.
  Evidence: the page's "Validation in OpenAPI Specs"; the `cfg.yaml` files under
  `internal/controller/api/*/gen/`.
- **FR-012**: The corpus MUST state that a path parameter needing validation
  beyond `format: uuid` is validated by hand in the handler, and MUST state
  where that helper actually lives. **Gap**: the page says "a shared helper like
  `node.validateHostname()`". There is no shared helper and that call does not
  compile from another package — `validateHostname` is unexported and exists
  three times, at `internal/controller/api/agent/validate.go:30`,
  `internal/controller/api/node/validate.go:30` and
  `internal/controller/api/node/power/validate.go:30`. What is shared is
  `validation.Var(hostname, "required,min=1,valid_target")`, which all three
  call. The corpus states the shared validator and names the duplication rather
  than repeating the page's call.
- **FR-013**: The corpus MUST state the verb mapping and that a mutable domain
  uses separate verbs for create and update — `POST` creates with the name in
  the body, `PUT /{name}` updates from the path — and MUST state the reason: it
  is what gives 404 semantics a meaning. A combined set or upsert endpoint is
  forbidden. Evidence: the page's "HTTP Verb Conventions"; the cron domain's
  `gen/api.yaml`.
- **FR-014**: The corpus MUST state the API design guidelines: endpoints grouped
  by functional domain under their own top-level prefix, resource-oriented paths
  with sub-resources nested under their parent, an area expected to grow split
  into its own category early, everything targeting a managed machine under
  `/node/{hostname}`, and path parameters for identification with query
  parameters only for filtering and pagination. **Gap**: 003's `data-model.md`
  lists five guidelines to fold in;
  `docs/docs/sidebar/architecture/api-guidelines.md` states **six**. The sixth,
  "Path Parameters Over Query Parameters", is included above. Nothing was
  dropped, but 003's record of this page was incomplete and the next reader
  should know the count was checked rather than copied.
- **FR-015**: The corpus MUST state that `{hostname}` accepts a literal
  hostname, the reserved values `_any` and `_all`, or a `key:value` label
  selector. Evidence: `IsBroadcastTarget` at `internal/job/subjects.go:306`.

### Broadcast

- **FR-016**: The corpus MUST state that every operation under
  `/node/{hostname}/...` supports broadcast targeting, that both the
  single-target and the broadcast path return the same collection shape, and
  that every result item carries `hostname` and `error`. A single target returns
  one result; a broadcast returns as many as there are agents, with failed and
  skipped ones present as entries rather than absent. Evidence: the page's
  "Broadcast Support"; `internal/job/client/client.go`.
- **FR-017**: The corpus MUST state that the `JobClient` interface has four
  generic methods — `Query`, `QueryBroadcast`, `Modify`, `ModifyBroadcast` — and
  that adding an operation needs none added, because a handler passes a category
  string and an operation constant. Evidence: `internal/job/client/types.go`,
  lines 146, 153, 160 and 167.

### Registration and the SDK

- **FR-018**: The corpus MUST state that a domain package exports a `Handler()`
  function returning route-registration closures, that it wraps the handler in
  scope middleware itself, and that the `Server` struct does not change. Startup
  wiring is one appended line in `registerControllerHandlers`. Evidence:
  `cmd/controller_setup.go`.

- **FR-019**: The corpus MUST state the SDK obligations: four files per service,
  a field on the `Client` struct, an example under `examples/sdk/client/`, a doc
  page in the matching category, and the navbar entry — and MUST NOT defer to an
  authority that does not exist. **Gap**: the page says method naming, type
  exposure, result-field tags and error handling "are specified in the
  `sdk-standards` capability in osapi-io/specs", and that where the two disagree
  the specification wins. There is no `sdk-standards` capability in this
  repository. The only other mention of it is
  `.claude/skills/add-a-domain/references/sdk.md:6`, which makes the same claim.
  Two documents defer to a specification nobody has written, which reads as
  settled and is not. The corpus states the conventions it can verify and
  records this as unstated rather than repeating the deferral.

  **Amended: there was a third, and one of the four subjects has no rule at
  all.** The site's SDK guidelines page carried the same claim, so three
  documents deferred to it rather than two; all three now name it as unwritten.
  And the deferral named four subjects — method naming, type exposure,
  result-field tags, error handling. Three are real and stated: type exposure,
  JSON tags and error wrapping are FR-020, and the guidelines page shows each
  working. **Method naming is stated nowhere** — not here, not on that page,
  whose sections are package structure, generated types, result types, the
  response pattern and error handling, and not in the capability nobody wrote.
  It was named only in the deferral. So the missing authority was not a document
  that would have collected existing rules; for one of its four subjects there
  was nothing to collect.

  Owner of the remainder: this repository, and this project rather than
  `system`. `osapi-orchestrator` does depend on `github.com/osapi-io/osapi`, so
  the claim that these rules reach a second repository was true in substance.
  But the SDK is osapi's own public API and the orchestrator consumes it, which
  by the test under "Where a change belongs" makes it osapi's behaviour rather
  than an agreement between repositories. A method-naming convention is worth
  stating only once somebody decides what it is, rather than inferring one from
  the method names that happen to exist.

- **FR-020**: The corpus MUST state the rules an SDK service obeys that *are*
  verifiable: no `gen` types in a public method signature, JSON tags on every
  result type, errors wrapped with context, and one service per file with no
  methods added to another service's files. Evidence: `pkg/sdk/client/`, and
  `docs/docs/sidebar/sdk/guidelines.md`.

### The CLI, and the principles

- **FR-021**: The corpus MUST state the CLI obligations: one parent command per
  domain and one subcommand per endpoint, `--json` on every command,
  `cli.PrintKV` for key-value output and `cli.PrintCompactTable` for tabular,
  flags rather than positional arguments for resource IDs, and every response
  code the OpenAPI specification declares handled in the status switch.
  Evidence: `PrintCompactTable` at `internal/cli/ui.go:198` and `PrintKV` at
  `:413`.
- **FR-022**: The corpus MUST state all **eight** design principles, each with
  what it constrains, so that a principle can decide a question rather than
  decorate a page. **Gap**: 003's `data-model.md` and its research Finding 1
  both say `principles.md` states **five**;
  `docs/docs/sidebar/architecture/principles.md` states eight. The three 003
  never named are Reliability and Stability, CLI Parity with API, and Least
  Privilege Mode. The line count 003 recorded — 46 — is right, so the page has
  not grown; the count of principles was wrong when written.
- **FR-023**: The corpus MUST record that each of the eight was checked against
  `.charter/fragments/global/` and this project's constitution before being
  stated, and MUST cite
  [003's research Finding 1](../003-corpus-backfill/research.md) for the five it
  covers rather than re-running a check that feature already closed. The three
  principles Finding 1 does not cover MUST be checked the same way, because
  Finding 1's own history is the argument for doing so: its first version
  claimed two principles were already charter rules, read from the headings
  rather than the text, and its T002 found all five unstated.

### Verification

- **FR-024**: The corpus MUST state what verifies a finished domain, and MUST
  NOT reproduce the page's command list as sufficient. **Gap**: the page's "Step
  8" gives `just generate`, `go build ./...`, `just go-unit` and `just go-vet`.
  All four recipes exist, but they do not cover Step 7, which edits eight
  documentation files: `docusaurus-fmt-check` and `docusaurus-build` run in
  `just test`, not in any of the four. A contributor who follows Step 8 exactly
  can hand in work that fails continuous integration on the documentation Step 7
  told them to write. The corpus states the gate as `just ready` and
  `just test`, naming what each covers. Evidence: the recipe list from
  `just --list`.

### Citing rather than restating

- **FR-027**: The corpus MUST state a domain's test obligations, or cite where
  they are stated — and MUST NOT leave tests as the one artifact kind FR-001
  names with no requirement behind it. They are osapi's `CONTRIBUTING.md`'s,
  under "Testing", and are cited rather than copied: `testify/suite` table tests
  with one suite method per function under test, `*_public_test.go` in a `_test`
  package as the default, coverage gated at 99.9% with `.coverignore` narrowing
  what the figure covers, and the two HTTP wiring methods a public suite
  carries. One obligation there is specific to this subject and MUST be cited as
  such: **a new API domain includes a `{domain}_test.go` smoke suite under
  `test/integration/`**, with every mutating test guarded by `skipWrite(s.T())`
  so continuous integration runs read-only by default. Evidence:
  `CONTRIBUTING.md`, "Testing", "Test file conventions" and "Test layers";
  `.coverignore`.

  This requirement exists because the SC-001 reading found the hole. Every other
  artifact kind had a requirement — the CLI FR-021, the SDK FR-019 and FR-020,
  registration FR-018 — and tests had none, so a reader of this specification
  alone saw an omission where a deferral was intended. The deferral was real and
  recorded in [data-model.md](data-model.md); it was simply not here.

- **FR-028**: The corpus MUST state the SDK's method-naming convention. It was
  derived from the 31 services and roughly 110 exported methods that exist in
  `pkg/sdk/client/`, rather than decided in the abstract, because no convention
  had ever been written down — FR-019 records that. Four rules describe what is
  there:

  1. **The five CRUD verbs are exactly `List`, `Get`, `Create`, `Update`,
     `Delete`.** Never `GetAll`, `Fetch`, `Set`, `Put` or `Remove` for the
     service's own resource. Eleven services use some or all of them and none
     deviates.
  2. **A method acting on the service's own resource takes the bare verb, with
     no object.** `Service.Start`, not `Service.StartService`; `Power.Reboot`,
     `Agent.Accept`, `Job.Retry`, `Package.Install`, `Docker.Pull`.
  3. **A method acting on a *sub*-resource takes verb then object.**
     `User.AddKey`, `User.ListKeys`, `User.RemoveKey`, `User.ChangePassword`,
     `Agent.ListPending`, `Package.ListUpdates`, `Log.QueryUnit`.
  4. **A getter is named `Get` and nothing else.** Six services expose a single
     read — `Disk`, `Load`, `Memory`, `OS`, `Status`, `Uptime` — and each names
     it `Get`, taking its subject from the service.

  The corpus MUST also record the four places the existing surface departs from
  these rules, because a convention derived from code is only honest if it names
  what it does not cover:

  | Method                            | Departs how                                                                                                                                                                                        |
  | --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `Docker.ImageRemove`              | Object then verb, where rule 3 says verb then object. The only such method in the SDK; `RemoveImage` would conform. Renaming it is a breaking change to a public API and is **not** proposed here. |
  | `Ping.Do`                         | `Do` names no action. It exists because `Ping.Ping` stutters, which is the case rule 2 cannot express when the service name *is* the verb.                                                         |
  | `File.Changed`, `File.Stale`      | Adjectives rather than verbs. Both are predicates answering a question about state, which none of the four rules covers.                                                                           |
  | `Health.Liveness`, `Health.Ready` | Probe names rather than verbs, taken from the endpoints they call.                                                                                                                                 |

  These are recorded as **deviations, not defects**. Each is either a real
  limitation of the rules or a public API that should not be renamed to satisfy
  a convention written after it.

- **FR-025**: After this specification merges, the `add-a-domain` skill MUST
  cite its requirements rather than restating the mechanics, in the shape
  [003's citation contract](../003-corpus-backfill/contracts/citation.md)
  defines — a relative link four `../` levels up from a reference file, named to
  a requirement rather than to a document.

- **FR-026**: In the same change that adds those citations, the contributor half
  of the site MUST be removed: `adding-an-api-domain.md` reduced to what adding
  a domain involves, a citation table, and a pointer to the skill;
  `api-guidelines.md` and `principles.md` removed with their addresses
  redirected; and `system-architecture.md`'s component map, entry points, layers
  and request flow removed. Adding the citations without removing the page
  leaves two statements, which is the condition this feature exists to end.

### Key Entities

- **Domain**: a coherent area of system behavior exposed as API endpoints, whose
  artifacts span provider, agent processor, API handler, SDK service, CLI
  commands, documentation and tests.
- **Layer**: one of the six the system is built from, each taking a defined
  artifact from a domain.
- **Step**: one unit of the build sequence. Some orderings are forced by code
  generation and some are convention — FR-004 separates them.
- **Gap**: a rule the site states that the repository does not bear out,
  recorded with both sides named. Four are recorded here.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader who has not seen the site page answers all four questions
  from the corpus alone: *what does a domain consist of, and how would I know
  one was incomplete?*; *what must be built before what, and which of those
  orderings is forced?*; *where does user input get validated, and what happens
  to a path parameter?*; *what must be true of an operation that targets more
  than one machine?* Each is a question that would break a domain if unanswered
  — an incomplete domain, a generation step run out of order, an unvalidated
  input, a broadcast handler that returns the wrong shape.
- **SC-002**: Every address removed from the site resolves after the change. Two
  are removed and both redirect.
- **SC-003**: No page an operator reads points into the corpus. The contributor
  page is the one exception, and its reader is a contributor.
- **SC-004**: `just test` passes in the specs repository, `skill-lint` resolving
  every citation this specification's requirements are cited by.
- **SC-005**: No rule this specification states appears in restated form in the
  skill's references. The skill states a rule's name and where it lives.
- **SC-006**: The site page's last commit postdates this specification's merge.
  If it does not, the corpus and the page both state these rules and the feature
  is unfinished whatever the corpus says.

## Assumptions

- The reader of the corpus is a contributor or an agent, not an operator. That
  is what makes a citation the right form here and the wrong form on a feature
  page.
- The four gaps are recorded, not fixed. Correcting the site's `sdk-standards`
  deferral, the duplicated `validateHostname`, 003's principle count and Step
  8's command list is each its own change; three of them touch osapi and this
  feature touches no code.
- `@docusaurus/plugin-client-redirects` is available for the two redirects.
  003's T015 adds it, so this feature depends on that task rather than
  duplicating it.
- Memory holds three archived features when this is implemented — 001, 002 and
  004 — so every overlap named in FR-002 and FR-003 has something to cite.
- The line counts in 003's `data-model.md` were re-measured on 2026-09-28 and
  all four match. What did not match is the *contents* of two of those pages,
  which is what FR-014 and FR-022 record.
