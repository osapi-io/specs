# Feature Specification: Provider contract

**Feature Branch**: `feat/provider-contract`

**Created**: 2026-09-17

**Status**: Draft

**Input**: User description: "The provider contract — the corpus description of
how an osapi provider behaves, so the specs corpus states it once and the
add-a-domain skill can point at it instead of restating it."

This is a retrospective specification. osapi has fourteen node domains plus
network, container, command, file and scheduled providers, all written against a
contract that has never been stated anywhere the workflow reads. Every
requirement below is written from evidence the repository already carries, and
names it. Where the published guide and the code disagreed, the code won.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The contract can be read without reading a sibling provider (Priority: P1)

Someone adding a provider learns what a provider must do from the corpus: the
operations it exposes, what each reports when the desired state is already met,
and what happens on an OS family it does not support. Today that knowledge is
recovered by opening an existing provider and inferring the rules from it.

**Why this priority**: This is the feature. Everything else here is detail
underneath it.

**Independent Test**: A reader with no osapi knowledge, given only the corpus,
can say what creating an existing resource reports, and what the caller sees
when the provider does not support the host's OS family.

**Acceptance Scenarios**:

1. **Given** the corpus alone, **When** a contributor asks what a provider must
   implement, **Then** the operation set, the context-first convention, and the
   result fields are stated without reference to a specific domain.
2. **Given** the corpus alone, **When** a contributor asks what makes an
   operation idempotent here, **Then** the three desired-state outcomes are
   stated as a rule rather than illustrated by one domain.
3. **Given** a provider that returns an error when deleting an absent resource,
   **When** it is reviewed against the corpus, **Then** the review cites a
   requirement rather than a sibling provider's behaviour.

______________________________________________________________________

### User Story 2 - The four implementation patterns are distinguishable (Priority: P2)

A provider that runs commands, one that writes its own configuration files, one
that delegates file writes, and one that calls an external API are four
different shapes with different obligations. A contributor can tell which shape
a new domain needs before writing it.

**Why this priority**: Choosing the wrong shape is expensive to undo: it decides
whether the domain gets change tracking and drift detection for free, and
whether it has platform variants at all.

**Independent Test**: Given a description of a new domain, a reader can name its
pattern from the corpus and say whether it needs stubs for the OS families it
does not implement.

**Acceptance Scenarios**:

1. **Given** a domain that manages a file under a well-known path, **When** the
   contributor consults the corpus, **Then** delegating writes to the file
   deployer is identified as the pattern, with what that delegation provides.
2. **Given** a domain that talks to an external daemon, **When** the contributor
   consults the corpus, **Then** no platform variants are expected and
   availability is established when the provider is constructed instead.

______________________________________________________________________

### User Story 3 - The trust boundary is stated where a provider is the second caller (Priority: P3)

A provider validates its inputs even though the request was already validated,
because the request path is not the only way a provider is reached: work is read
back from storage and executed later.

**Why this priority**: Three of the four critical findings in the September 2026
review were provider-side input handling. The rule existed in nobody's head as a
rule, so each domain decided for itself.

**Independent Test**: A reviewer can point at a requirement stating that a value
which becomes a path, a filename or a command argument is validated in the
provider, and check any domain against it.

**Acceptance Scenarios**:

1. **Given** a provider that builds a filesystem path from a request value,
   **When** it is reviewed against the corpus, **Then** validating that value in
   the provider is required, not optional hardening.
2. **Given** a provider that passes a secret to a command, **When** it is
   reviewed, **Then** the corpus requires the secret to reach the command
   without appearing in its arguments.

### Edge Cases

- A host runs an OS family the provider does not implement. This is not a
  failure: the provider reports the shared unsupported outcome and the work is
  recorded as skipped, so the caller can tell "not available here" from
  "broken". Evidence: `internal/provider/errors.go:28`,
  `internal/agent/handler.go:414`.
- A provider is constructed but never registered with the agent's registry.
  Facts are injected by walking registered providers, so its facts are absent
  and any fact-dependent operation fails when called rather than at startup.
  Evidence: `internal/provider/facts.go:64`, `internal/agent/agent.go`.
- The same unit of work is delivered twice. The provider's idempotency is what
  makes the repeat harmless; delivery handling is specified separately.
- A request value arrives that the request path would now reject, because it was
  stored before that rule existed, or because something else wrote to the store.
  The provider's own validation is the only remaining check.
- A provider writes a file and the process dies mid-write. A partially written
  configuration file is worse than none, so the write does not happen in place.
  Evidence: `internal/provider/file/deploy.go`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The corpus MUST state that a provider is the operations layer,
  runs in the agent process rather than the controller, receives its parameters
  from the unit of work, and returns a result; the controller never executes
  operations itself. Evidence: `internal/agent/processor_*.go`.
- **FR-002**: The corpus MUST state the provider operation set and the
  context-first convention on every method, and the list/get/create/update/
  delete shape used where a domain is a collection of resources. Evidence:
  `internal/provider/node/sysctl/types.go`.
- **FR-003**: The corpus MUST state that a mutation result carries whether
  anything changed, and that a per-resource error is reported in the result
  rather than replacing it, so one failing host does not hide the others.
  Evidence: `internal/provider/node/sysctl/types.go`.
- **FR-004**: The corpus MUST state the idempotency contract as a rule: creating
  a resource that already exists reports no change and no error; deleting a
  resource that is absent reports no change and no error; updating a resource
  that is absent is an error. Evidence:
  `internal/provider/node/sysctl/debian.go`, its Create, Update and Delete.
- **FR-005**: The corpus MUST state that an operation unsupported on the host's
  OS family reports the shared unsupported outcome, and that this is distinct
  from reporting no change — it is recorded as skipped. Evidence:
  `internal/provider/errors.go:28`, `internal/agent/handler.go:414`.
- **FR-006**: The corpus MUST state the four implementation patterns, how to
  recognise which applies, and what each obliges: a direct provider that runs
  commands (`internal/provider/node/process`); a provider that delegates file
  writes to the file deployer and gains change tracking, idempotency and
  template rendering (`internal/provider/scheduled/cron`,
  `internal/provider/node/service`, `internal/provider/node/certificate`,
  `internal/provider/node/user`); a provider that manages its own configuration
  files and marks them with a reserved filename prefix so managed files are
  distinguishable from hand-written ones (`internal/provider/node/sysctl`); and
  a provider that calls an external API, has no platform variants, and
  establishes availability when constructed (`internal/provider/container`).
- **FR-007**: The corpus MUST state that platform-specific providers are
  selected outside the provider — by OS family, and by whether the process is
  containerised — and that the families a domain does not implement are present
  as stubs rather than absent. Evidence: `pkg/sdk/platform` `Detect` and
  `IsContainer`, consumed in `cmd/agent_setup.go`.
- **FR-008**: The corpus MUST state how a provider obtains host facts: by
  embedding the shared facts holder, asserting the setter contract at compile
  time, and being registered so facts are injected at startup. Evidence:
  `internal/provider/facts.go:30`, `:41`, `:64`.
- **FR-009**: The corpus MUST state that validation on the request path does not
  discharge the provider's: any value that becomes a filesystem path, a
  filename, or a command argument is validated in the provider before use,
  because work executed from storage is a second caller. Evidence:
  GHSA-7fjw-v3g9-326g, fixed in `internal/provider/node/sysctl/debian.go`.
- **FR-010**: The corpus MUST state that a secret reaches a command without
  appearing in its arguments, and that arguments are treated as logged and
  publicly visible. Evidence: GHSA-6gc6-px2x-q95j; the stdin-carrying variant in
  `internal/exec`, and the argument logging in `internal/exec/exec.go`.
- **FR-011**: The corpus MUST state that a value supplied by a caller is never
  allowed to be parsed as an option by a command the provider runs.
- **FR-012**: The corpus MUST state that filesystem access goes through the
  virtual filesystem abstraction rather than the standard library or a
  substitute, so a provider is testable in memory and with injected failures,
  and that commands go through the shared exec manager rather than being spawned
  directly. Evidence: `CONTRIBUTING.md` "Filesystem access"; the constructors in
  `internal/provider/*/debian.go`.
- **FR-013**: The corpus MUST state that a file a provider writes is not written
  in place, so a crash cannot leave a half-written configuration file behind,
  and that the mode and ownership a caller asked for are applied even when the
  content is unchanged. Evidence: `internal/provider/file/deploy.go`;
  osapi-io/osapi#498.
- **FR-014**: The corpus MUST state the testing obligations belonging to the
  contract rather than to house style: each of the three idempotency outcomes is
  covered; every stub family is asserted to report the unsupported outcome; and
  each rejection required by FR-009 through FR-011 is covered by a case proving
  no command ran and no file was written. Evidence:
  `internal/provider/node/sysctl/debian_public_test.go`,
  `internal/provider/node/*/darwin_public_test.go`.
- **FR-015**: The corpus MUST state what a provider does not touch: it adds no
  message subject, stream, consumer or key-value bucket, and nothing in the
  provider layer depends on the sibling messaging libraries. Evidence: no file
  under `internal/provider/` imports `osapi-io/nats-client`; buckets and streams
  are declared in `internal/job/config.go`.
- **FR-016**: The `add-a-domain` skill MUST cite these requirements rather than
  restating them, so the corpus is the single statement and the skill routes to
  it.

### Key Entities

- **Provider**: A domain's operations, running in the agent, selected by OS
  family. Exposes the operation set in FR-002 and honours FR-004.
- **Result**: What an operation returns: the resource identity, whether anything
  changed, and a per-resource error when one occurred.
- **Unsupported outcome**: The shared signal meaning "not available on this OS
  family", distinct from a failure and from no change.
- **Facts**: Host attributes collected by the agent and injected into registered
  providers.
- **File deployer**: The narrow contract a provider delegates file writes to in
  order to gain change tracking, idempotency and template rendering.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A contributor states all three idempotency outcomes and the
  unsupported outcome from the corpus alone, without opening a provider.
- **SC-002**: Every existing provider can be checked against the contract, and
  each deviation is expressible as a named requirement it fails rather than as a
  difference from a sibling.
- **SC-003**: The `add-a-domain` skill's provider reference contains no restated
  mechanics: what remains is routing plus citations into this corpus.
- **SC-004**: A new domain's provider is reviewable against the corpus with no
  appeal to "look at how sysctl does it".
- **SC-005**: Someone asking whether a provider needs to know about the
  messaging layer gets a stated answer rather than inferring one from imports.

## Assumptions

- The audience is contributors and agents working on osapi, not operators. What
  each domain does for a user stays in the published documentation; this states
  how a provider behaves. File paths and named errors appear as evidence for
  requirements, which the constitution's Verification principle requires.
- Requirements state current behaviour. Two known gaps are recorded rather than
  specified away: the option-parsing rule in FR-011 is not yet enforced for user
  and group names (recorded on GHSA-6gc6-px2x-q95j), and the atomic-write and
  mode-application rules in FR-013 are not yet honoured by the file deployer
  (osapi-io/osapi#498). A requirement the code does not yet meet is a gap in the
  code, not an error in the corpus.
- The job system, the request, SDK and CLI layers, and the UI are out of scope
  and become their own features. This covers only what a provider is and must
  do.
- The four patterns are the four in the codebase today. A fifth would amend this
  spec rather than being decided locally in one domain.
- `osapi-orchestrator` consumes osapi through its SDK and implements no
  providers, so nothing here binds it.
