# Main Project Specification

> **Revision**: 2026-09-26 — Seeded from the provider contract
> (`specs/001-provider-contract`): 3 user stories, 16 functional requirements, 5
> entities, 5 edge cases, 5 measurable outcomes, 4 assumptions.

> **Revision**: 2026-09-26 — Added the per-agent public key store
> (`specs/002-agent-key-store`): 3 user stories, 13 functional requirements, 4
> entities, 5 edge cases, 7 measurable outcomes, 5 assumptions. Nothing folded:
> the provider contract and agent identity share no ground.

> **Revision**: 2026-09-28 — Added building a domain
> (`specs/005-building-a-domain`): 3 user stories, 26 functional requirements, 4
> entities, 4 edge cases, 6 measurable outcomes, 5 assumptions. Nothing folded:
> the job system states what carries an operation, and this states what a domain
> consists of. Four gaps are recorded as gaps, not corrected. The job system's
> archival left no revision note here; this is noted rather than backfilled.

> **Revision**: 2026-09-28 — Amended building a domain after its completeness
> reading: FR-081 states the test obligations nothing held, FR-061 reconciles the six
> layers with the seven artifact kinds, FR-060 says what makes an operation
> node-targeted rather than only where its code lives, and FR-058 defines the
> combined specification.

> **Revision**: 2026-09-28 — Added the corpus backfill
> (`specs/003-corpus-backfill`), the parent of both subjects: 1 user story as US13, 12
> requirements as FR-082–FR-093, 4 entities, 3 edge cases and 2 outcomes. Four of its
> outcomes and two of its stories folded into entries its own subjects had already
> put here, which is what a method feature archived after its subjects should look
> like.

> **Revision**: 2026-09-29 — Added the embedded UI (`specs/007-the-embedded-ui`):
> 2 user stories as US14 and US15, 18 requirements as FR-095–FR-112, 4 entities, 3
> edge cases, 4 outcomes and 4 assumptions. Four folded: an operator story into
> US11, a split-page edge case into the backfill's paragraph case, and three
> outcomes into SC-016, SC-021 and SC-024, which already generalised beyond the
> subject that wrote them. The UI was the one part of osapi memory said nothing
> about; AS-003 had recorded it as out of scope and becoming its own feature, and
> this is that feature.

> **Revision**: 2026-09-29 — Three of that feature's own claims were wrong and are
> archived corrected, with what found each: a grep found a fourth copy of the
> architecture the classification had missed, a line count found the pointer at ten
> lines against a criterion of under ten, and the reading found FR-004 requiring a
> statement it did not make. None was found by re-reading the specification.

> **Revision**: 2026-09-28 — Added the SDK's method-naming convention as FR-094,
> derived from the 31 services that exist rather than decided in the abstract, once
> FR-073 had established that no convention was written anywhere. Its four deviations
> are recorded with it.

## User Scenarios & Testing

### User Story 1 - The contract can be read without reading a sibling provider (Priority: P1)

Someone adding a provider learns what a provider must do from the corpus: the
operations it exposes, what each reports when the desired state is already met,
and what happens on an OS family it does not support.

**Why this priority**: This is the feature. Everything else here is detail
underneath it.

**Independent Test**: A reader with no osapi knowledge, given only the corpus,
can say what creating an existing resource reports, and what the caller sees when
the provider does not support the host's OS family.

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

[Source: specs/001-provider-contract/spec.md -> User Story 1]

### User Story 2 - The four implementation patterns are distinguishable (Priority: P2)

A provider that runs commands, one that writes its own configuration files, one
that delegates file writes, and one that calls an external API are four different
shapes with different obligations. A contributor can tell which shape a new
domain needs before writing it.

**Why this priority**: Choosing the wrong shape is expensive to undo: it decides
whether the domain gets change tracking and drift detection for free, and whether
it has platform variants at all.

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

[Source: specs/001-provider-contract/spec.md -> User Story 2]

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
   reviewed, **Then** the corpus requires the secret to reach the command without
   appearing in its arguments.

[Source: specs/001-provider-contract/spec.md -> User Story 3]

### User Story 4 - The controller can tell a real agent's answer from a forged one (Priority: P1)

An operator asks for a command to run on a host. The result that comes back is
checked against the key of the agent that enrolled as that host, so a result
written by something else does not reach the operator as fact.

**Why this priority**: Agents already sign their responses. Nothing checked the
signature, so the signing was decorative. Everything else here builds on the
store this requires.

**Independent Test**: With the store in place, a response carrying a valid
signature is accepted, and the same response re-signed by a different key is
rejected, without the operator's request appearing to succeed.

**Acceptance Scenarios**:

1. **Given** an accepted agent, **When** it answers a job, **Then** the controller
   verifies the response against that agent's stored key before treating it as a
   result.
2. **Given** a response signed by a key that is not the stored key for that agent,
   **When** it arrives, **Then** it is rejected and the job does not report
   success.
3. **Given** an agent with no stored key, **When** a response claiming to be from
   it arrives, **Then** it is rejected rather than accepted unverified.

[Source: specs/002-agent-key-store/spec.md -> User Story 1]

### User Story 5 - A host's name cannot be claimed by another machine (Priority: P1)

Work targeted at `web-01` reaches the machine that enrolled as `web-01`. A second
machine that announces the same hostname does not receive that work, and does not
replace the first in the operator's view of the fleet.

**Why this priority**: Registration is what targeting reads. An unauthenticated
registration means the identity established at enrollment can be overridden
afterwards by anything able to write, which makes enrollment's guarantee
conditional on the transport alone.

**Independent Test**: A registration whose signature does not verify against the
stored key for its machine ID is not visible to targeting, and work aimed at that
hostname continues to reach the enrolled machine.

**Acceptance Scenarios**:

1. **Given** an enrolled agent, **When** it registers, **Then** the registration
   is signed and verified against its stored key before targeting will use it.
2. **Given** a registration claiming a hostname already held by a different
   enrolled machine, **When** it is verified, **Then** it does not displace the
   enrolled machine for targeting purposes.
3. **Given** a registration that is unsigned or fails verification, **When**
   targeting resolves a hostname or label, **Then** that registration is not among
   the candidates.

[Source: specs/002-agent-key-store/spec.md -> User Story 2]

### User Story 6 - Keys change without an outage, and leave when the agent does (Priority: P2)

An operator rotates an agent's key, or removes an agent, and neither action
requires re-enrolling the fleet or leaves a stale key behind that would still be
trusted.

**Why this priority**: A store that cannot be updated becomes a reason to turn
verification off. The controller key already has a rotation story with a grace
period; the agent key needs the equivalent.

**Independent Test**: After a rotation, messages signed with the new key verify,
messages signed with the previous key verify until the grace period lapses, and
messages signed with a key that was removed do not verify at all.

**Acceptance Scenarios**:

1. **Given** an agent that rotates its key, **When** it re-enrolls or presents the
   new key through the supported path, **Then** the stored key is replaced and
   subsequent messages verify against it.
2. **Given** a rotation in progress, **When** a message signed with the previous
   key arrives inside the grace period, **Then** it verifies, and after the grace
   period it does not.
3. **Given** an agent that is removed or rejected, **When** anything signed by its
   key arrives afterwards, **Then** it does not verify.

[Source: specs/002-agent-key-store/spec.md -> User Story 3]

### User Story 7 - A contributor adds an operation and knows what they are handed (Priority: P1)

Somebody adding an operation to a domain needs to know what carries their request,
what the agent is guaranteed to receive, and what the system does to them if the
network hiccups. They read the corpus, and they know before they write.

**Why this priority**: every domain added to osapi passes through the job system,
and until its mechanics are stated the add-a-domain skill either restates them or
sends the reader to a page written for an operator.
[Source: specs/004-job-system/spec.md -> User Story 1]

**Independent Test**: given the corpus alone, a reader can say which store holds a
job, which store holds its result, what a second delivery obliges the agent to do,
and what bounds how long the work may run.

**Acceptance Scenarios**:

1. **Given** the corpus, **When** a contributor asks how a request becomes work an
   agent runs, **Then** the path — store, notify, fetch, execute, record — is stated
   with the code that implements each step.
2. **Given** the corpus, **When** a contributor asks what happens when the same job
   arrives twice, **Then** the obligation is stated as an obligation, not as an
   observation about the current implementation.
3. **Given** the corpus, **When** a contributor asks what an operation may assume
   about time, **Then** the deadline, the backstop and what cancellation does not
   reach are all stated.

### User Story 8 - An agent implementer knows what the system will not do for them (Priority: P1)

Somebody writing the agent side needs the obligations: what to check before
executing, what to write and when, what to acknowledge, and which failures are
theirs to handle rather than the system's to retry.

**Why this priority**: the delivery guarantee is weaker than it looks, and an
implementer who assumes at-most-once will execute a reboot twice.
[Source: specs/004-job-system/spec.md -> User Story 2]

**Independent Test**: given the corpus alone, a reader can state what the agent
must check before running an operation, what it must record before acknowledging,
and which of a failure's causes it must not retry.

**Acceptance Scenarios**:

1. **Given** the corpus, **When** an implementer asks what to do with a redelivered
   message, **Then** the check that makes re-execution unnecessary is stated, along
   with what happens when the response cannot be written.
2. **Given** the corpus, **When** an implementer asks which failures terminate the
   message rather than letting it redeliver, **Then** the list is stated with its
   reason.

### User Story 9 - A rule that was wrong on the site is not wrong in the corpus (Priority: P2)

Somebody reading a number in the corpus — a timeout, a delivery count, a key format
— finds the number the code uses, or an explicit statement that the two disagree.

**Why this priority**: it is what makes a moved page a specification rather than a
copy. Three of the site page's statements were already untrue when the job system
was archived.
[Source: specs/004-job-system/spec.md -> User Story 3]

**Independent Test**: for each number and key format stated, the cited code says
the same thing, or the requirement records the disagreement.

**Acceptance Scenarios**:

1. **Given** a requirement naming a configured value, **When** the cited file is
   opened, **Then** it holds that value or the requirement says it does not.
2. **Given** a value the site stated wrongly, **When** the corpus is read, **Then**
   the correction is visible as a correction rather than silently different.


### User Story 10 - A contributor can add a domain from the corpus alone (Priority: P1)

Somebody adding a domain to osapi needs to know what artifacts a domain consists
of, in what order they are built, and which of the choices along the way are rules
rather than preferences. They read the corpus, and the `add-a-domain` skill cites
one statement rather than carrying a second.

**Why this priority**: it is the subject. Everything else about building a domain
supports it.
[Source: specs/005-building-a-domain/spec.md -> User Story 1]

**Independent Test**: given the corpus alone, a reader can say what a domain
consists of, what must be built before what, where user input is validated, and
what must be true of an operation targeting more than one machine.

**Acceptance Scenarios**:

1. **Given** a contributor who has never added a domain, **When** they ask what a
   domain consists of across every layer, **Then** the corpus names the layers, the
   artifacts each one takes, and the consistency obligation that binds them.
2. **Given** a contributor partway through, **When** they ask whether a step may be
   skipped or reordered, **Then** the corpus distinguishes the steps whose order a
   tool forces from those merely done in that order by convention.
3. **Given** a contributor reading a rule the corpus states, **When** they ask why
   it is a rule, **Then** the corpus gives the reason or the file that enforces it,
   so the rule can be checked rather than believed.

### User Story 11 - An operator is not sent to a contributor's document (Priority: P1)

[Source: specs/003-corpus-backfill/spec.md -> User Story 2]

Somebody who bookmarked an architecture page finds it still resolves, and what
replaces it does not send them into a corpus written for somebody else.

**Why this priority**: a corpus statement that costs an operator their bookmark is
not an improvement.
[Source: specs/005-building-a-domain/spec.md -> User Story 2]

**Independent Test**: every removed address still resolves, and no surviving
operator page points into the corpus. For a split page: it answers what an operator
configures and sees, and reads as a whole page rather than a remainder.
[Source: specs/007-the-embedded-ui/spec.md -> User Story 2]

**Acceptance Scenarios**:

1. **Given** a bookmark to a removed contributor page, **When** it is opened after
   the change, **Then** it resolves to the contributor index rather than to a 404.
2. **Given** a page whose contributor half was removed, **When** an operator reads
   it, **Then** what they need is still there and the page reads as a whole rather
   than as a remainder.
3. **Given** the site after the UI architecture moved, **When** an operator asks how
   to disable the UI, **Then** `controller.ui.enabled` and its default are still
   there. [Source: specs/007-the-embedded-ui/spec.md -> User Story 2]

### User Story 12 - The rule has one home (Priority: P2)

[Source: specs/003-corpus-backfill/spec.md -> User Story 3]

Somebody reading the `add-a-domain` skill finds a rule's name and where it lives,
not a second statement of the rule that can drift from the first.

**Why this priority**: it is the point of the backfill, and it depends on the
corpus statement existing first.
[Source: specs/005-building-a-domain/spec.md -> User Story 3]

**Independent Test**: `just skill-lint` resolves every citation, and no rule the
corpus states appears in restated form in the skill's references.

**Acceptance Scenarios**:

1. **Given** the skill's references, **When** `skill-lint` runs, **Then** every
   citation resolves to a requirement in the corpus.
2. **Given** a rule the corpus states, **When** the references are grepped for it,
   **Then** the rule's name appears with a citation and its mechanics do not appear
   twice.

### User Story 13 - A question is answered from the corpus, not the site (Priority: P1)

Somebody with a question about how osapi is built looks in one place and finds the
answer there. The published site is for using osapi; the corpus is for building it.

**Why this priority**: it is the whole point of moving anything. The subjects carry
the content; this is the reason they moved.
[Source: specs/003-corpus-backfill/spec.md -> User Story 1]

**Independent Test**: a reader with no prior knowledge answers a subject's fixed
questions from the corpus alone, without opening the site.

**Acceptance Scenarios**:

1. **Given** a contributor's question about how osapi is built, **When** they consult
   the corpus, **Then** the answer is there rather than in a link to the site.
2. **Given** a page that told a contributor how to build something, **When** it is
   read after the move, **Then** it cites the corpus rather than restating it.

### User Story 14 - The UI's architecture is stated once (Priority: P1)

[Source: specs/007-the-embedded-ui/spec.md -> User Story 1]

Somebody changing the UI reads how it is built in one place, and what they read is
not contradicted by a second document they did not know existed.

**Why this priority**: two statements existed and they had diverged. Every day that
held, the chance grew that somebody read the stale one. Distinct from US13, which
asks *where* an answer lives; this asks *how many* answers exist.

**Independent Test**: one statement of the UI's architecture exists across the
corpus, the site and the repository; every other mention is a citation.

**Acceptance Scenarios**:

1. **Given** the corpus, **When** a contributor asks how the SPA reaches the binary,
   **Then** the embedding mechanism is stated with the file that implements it.
2. **Given** the repository, **When** somebody looks for UI architecture beside the
   code, **Then** they find a pointer to the corpus rather than a second account.

### User Story 15 - A disagreement between two documents is recorded, not silently resolved (Priority: P2)

[Source: specs/007-the-embedded-ui/spec.md -> User Story 3]

Somebody reading the corpus later can tell that two documents disagreed, which
sections each was missing, and which way the disagreement was settled.

**Why this priority**: the Correction principle. A merge that quietly picked a
winner would leave no trace that a rule had been in two places, and the next reader
would have no reason to check. Distinct from US9, which is a document disagreeing
with the *code*; this is two documents disagreeing with *each other*, which no gate
detects and no reader of either one can see.

### Edge Cases

- A host runs an OS family the provider does not implement. This is not a
  failure: the provider reports the shared unsupported outcome and the work is
  recorded as skipped, so the caller can tell "not available here" from "broken".
  Evidence: `internal/provider/errors.go:28`, `internal/agent/handler.go:414`.
  [Source: specs/001-provider-contract/spec.md -> "A host runs an OS family the provider does not implement"]
- A provider is constructed but never registered with the agent's registry. Facts
  are injected by walking registered providers, so its facts are absent and any
  fact-dependent operation fails when called rather than at startup. Evidence:
  `internal/provider/facts.go:64`, `internal/agent/agent.go`.
  [Source: specs/001-provider-contract/spec.md -> "A provider is constructed but never registered"]
- The same unit of work is delivered twice. The provider's idempotency is what
  makes the repeat harmless; delivery handling is specified separately.
  [Source: specs/001-provider-contract/spec.md -> "The same unit of work is delivered twice"]
- A request value arrives that the request path would now reject, because it was
  stored before that rule existed, or because something else wrote to the store.
  The provider's own validation is the only remaining check.
  [Source: specs/001-provider-contract/spec.md -> "A request value arrives that the request path would now reject"]
- A provider writes a file and the process dies mid-write. A partially written
  configuration file is worse than none, so the write does not happen in place.
  Evidence: `internal/provider/file/deploy.go`.
  [Source: specs/001-provider-contract/spec.md -> "A provider writes a file and the process dies mid-write"]

- An agent enrolled before the key store existed has no stored key. Which of
  "reject its messages" or "accept until it re-enrolls" applies is stated, and the
  same answer holds for responses and registrations, so an upgrade does not
  silently create a trusted-by-default class of agent.
  [Source: specs/002-agent-key-store/spec.md -> "An agent enrolled before this feature exists"]
- Two machines present the same hostname. Enrollment records identity by machine
  ID, so both can exist; targeting chooses deterministically rather than by
  iteration order.
  [Source: specs/002-agent-key-store/spec.md -> "Two machines present the same hostname"]
- A machine ID is reused, for example a restored VM image. The stored key is
  replaced only through an accepted enrollment, never by the arrival of a message
  signed with a different key.
  [Source: specs/002-agent-key-store/spec.md -> "A machine ID is reused"]
- The store is unavailable when a response or registration arrives. Verification
  does not silently pass, and the outcome is never "treat as verified".
  [Source: specs/002-agent-key-store/spec.md -> "The store is unavailable"]
- An agent is accepted while a previous registration for its hostname is still
  present. The older entry stops being authoritative once the new agent is
  accepted.
  [Source: specs/002-agent-key-store/spec.md -> "An agent is accepted while a previous registration"]

- A configured value has a default in code and a different value in the shipped
  config file. Stating one hides the other, so a requirement about a configured
  value names the default and the file that may override it.
  [Source: specs/004-job-system/spec.md -> "A configured value has a default in code"]
- An operation cannot be made idempotent — `command.exec`, `power.reboot`. The
  delivery guarantee cannot be strengthened for them, so the obligation lands on the
  agent, and the specification says which side owns it. Distinct from the provider
  idempotency case above: that one is about a provider making a repeat harmless, this
  one about work that cannot.
  [Source: specs/004-job-system/spec.md -> "An operation is not idempotent and cannot be made so"]
- A job outlives the controller's patience. Two clocks run, and each bounds a
  different thing, because an operator reading "timed out" will otherwise conclude
  the work did not happen.
  [Source: specs/004-job-system/spec.md -> "A job outlives the controller's patience"]
- A subject prefix is configurable per namespace, so a stated subject is a shape
  rather than a literal.
  [Source: specs/004-job-system/spec.md -> "A subject prefix is configurable per namespace"]

- A rule the provider contract already holds is reached from the contributor's
  direction. Providers are stated once, in the contract, and a document about
  adding a domain cites them rather than restating them from the other side.
  [Source: specs/005-building-a-domain/spec.md -> Edge Cases]
- A step's order is habit rather than a tool's requirement. Stating all of a
  sequence as obligations freezes a preference as a rule, so only the orderings a
  build actually breaks on are requirements.
  [Source: specs/005-building-a-domain/spec.md -> Edge Cases]
- A document defers to an authority that does not exist. Deferring to nothing is
  worse than stating nothing, because it reads as though the rule were settled
  elsewhere.
  [Source: specs/005-building-a-domain/spec.md -> Edge Cases]
- A page states a rule the code has outgrown. Both sides are named as a recorded
  gap rather than the page being silently corrected, so a reader can tell whether
  the page was wrong or they were.
  [Source: specs/005-building-a-domain/spec.md -> Edge Cases]
- A page serves both readers. Where its sections divide them it is **split**: what
  an operator configures and sees stays, how it is built goes, and the surviving
  page must read as a page rather than a remainder — the shape
  `system-architecture.md` and `architecture/ui.md` both took. Where a single
  *paragraph* serves both, splitting by section will not divide it: the paragraph is
  rewritten for the operator and the contributor's half restated in the corpus,
  rather than the page moving wholesale and taking operator content with it.
  [Source: specs/003-corpus-backfill/spec.md -> Edge Cases]
  [Source: specs/007-the-embedded-ui/spec.md -> "An operator section inside a contributor page"]
- The same architecture is stated in two prose documents and they have **diverged by
  addition**: each holds a section the other never got. There is no winner to pick,
  because neither is a summary of the other and neither states a rule the other
  denies. All the unshared sections are carried forward as a union, and the corpus
  records which copy each came from. Choosing the newer file would have lost two
  sections; choosing the site page would have lost one.
  [Source: specs/007-the-embedded-ui/spec.md -> "A section only one copy has"]
- Two copies share a section and word it differently. Where the substance agrees and
  only punctuation and capitalisation differ, that is evidence of copying rather than
  a disagreement to resolve: the corpus states the substance once and says the
  difference was punctuation, so nobody looks for a decision that was never made.
  [Source: specs/007-the-embedded-ui/spec.md -> "A section both have, worded differently"]
- A page is wholly a contributor's. It moves entire and its address keeps a short
  index — prose, a citation table, and a pointer to the tool rather than the tool's
  commands. `adding-an-api-domain.md` and `ui-development.md` are both this shape.
  [Source: specs/007-the-embedded-ui/spec.md -> "A page that is wholly contributor"]
- A moved page is linked from outside the repository — a README, an issue, a
  bookmark, a search result. Deleting its address breaks those silently, and whoever
  moved it will not see the breakage.
  [Source: specs/003-corpus-backfill/spec.md -> Edge Cases]
- A subject is too small to be its own specification. A specification per page
  produces specifications nobody reads, so a small subject folds into a larger one.
  [Source: specs/003-corpus-backfill/spec.md -> Edge Cases]

## Requirements

### Functional Requirements

- **FR-001**: The corpus MUST state that a provider is the operations layer, runs
  in the agent process rather than the controller, receives its parameters from
  the unit of work, and returns a result; the controller never executes
  operations itself. Evidence: `internal/agent/processor_*.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-001]
- **FR-002**: The corpus MUST state the provider operation set and the
  context-first convention on every method, and the
  list/get/create/update/delete shape used where a domain is a collection of
  resources. Evidence: `internal/provider/node/sysctl/types.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-002]
- **FR-003**: The corpus MUST state that a mutation result carries whether
  anything changed, and that a per-resource error is reported in the result
  rather than replacing it, so one failing host does not hide the others.
  Evidence: `internal/provider/node/sysctl/types.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-003]
- **FR-004**: The corpus MUST state the idempotency contract as a rule: creating a
  resource that already exists reports no change and no error; deleting a
  resource that is absent reports no change and no error; updating a resource
  that is absent is an error. Evidence:
  `internal/provider/node/sysctl/debian.go`, its Create, Update and Delete.
  [Source: specs/001-provider-contract/spec.md -> FR-004]
- **FR-005**: The corpus MUST state that an operation unsupported on the host's OS
  family reports the shared unsupported outcome, and that this is distinct from
  reporting no change — it is recorded as skipped. Evidence:
  `internal/provider/errors.go:28`, `internal/agent/handler.go:414`.
  [Source: specs/001-provider-contract/spec.md -> FR-005]
- **FR-006**: The corpus MUST state the four implementation patterns, how to
  recognise which applies, and what each obliges: a direct provider that runs
  commands (`internal/provider/node/process`); a provider that delegates file
  writes to the file deployer and gains change tracking, idempotency and template
  rendering (`internal/provider/scheduled/cron`, `internal/provider/node/service`,
  `internal/provider/node/certificate`, `internal/provider/node/user`); a
  provider that manages its own configuration files and marks them with a
  reserved filename prefix so managed files are distinguishable from hand-written
  ones (`internal/provider/node/sysctl`); and a provider that calls an external
  API, has no platform variants, and establishes availability when constructed
  (`internal/provider/container`).
  [Source: specs/001-provider-contract/spec.md -> FR-006]
- **FR-007**: The corpus MUST state that platform-specific providers are selected
  outside the provider — by OS family, and by whether the process is
  containerised — and that the families a domain does not implement are present
  as stubs rather than absent. Evidence: `pkg/sdk/platform` `Detect` and
  `IsContainer`, consumed in `cmd/agent_setup.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-007]
- **FR-008**: The corpus MUST state how a provider obtains host facts: by
  embedding the shared facts holder, asserting the setter contract at compile
  time, and being registered so facts are injected at startup. Evidence:
  `internal/provider/facts.go:30`, `:41`, `:64`.
  [Source: specs/001-provider-contract/spec.md -> FR-008]
- **FR-009**: The corpus MUST state that validation on the request path does not
  discharge the provider's: any value that becomes a filesystem path, a filename,
  or a command argument is validated in the provider before use, because work
  executed from storage is a second caller. Evidence: GHSA-7fjw-v3g9-326g, fixed
  in `internal/provider/node/sysctl/debian.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-009]
- **FR-010**: The corpus MUST state that a secret reaches a command without
  appearing in its arguments, and that arguments are treated as logged and
  publicly visible. Evidence: GHSA-6gc6-px2x-q95j; the stdin-carrying variant in
  `internal/exec`, and the argument logging in `internal/exec/exec.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-010]
- **FR-011**: The corpus MUST state that a value supplied by a caller is never
  allowed to be parsed as an option by a command the provider runs.
  [Source: specs/001-provider-contract/spec.md -> FR-011]
- **FR-012**: The corpus MUST state that filesystem access goes through the
  virtual filesystem abstraction rather than the standard library or a
  substitute, so a provider is testable in memory and with injected failures, and
  that commands go through the shared exec manager rather than being spawned
  directly. Evidence: `CONTRIBUTING.md` "Filesystem access"; the constructors in
  `internal/provider/*/debian.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-012]
- **FR-013**: The corpus MUST state that a file a provider writes is not written
  in place, so a crash cannot leave a half-written configuration file behind, and
  that the mode and ownership a caller asked for are applied even when the content
  is unchanged. Evidence: `internal/provider/file/deploy.go`; osapi-io/osapi#498.
  [Source: specs/001-provider-contract/spec.md -> FR-013]
- **FR-014**: The corpus MUST state the testing obligations belonging to the
  contract rather than to house style: each of the three idempotency outcomes is
  covered; every stub family is asserted to report the unsupported outcome; and
  each rejection required by FR-009 through FR-011 is covered by a case proving
  no command ran and no file was written. Evidence:
  `internal/provider/node/sysctl/debian_public_test.go`,
  `internal/provider/node/*/darwin_public_test.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-014]
- **FR-015**: The corpus MUST state what a provider does not touch: it adds no
  message subject, stream, consumer or key-value bucket, and nothing in the
  provider layer depends on the sibling messaging libraries. Evidence: no file
  under `internal/provider/` imports `osapi-io/nats-client`; buckets and streams
  are declared in `internal/job/config.go`.
  [Source: specs/001-provider-contract/spec.md -> FR-015]
- **FR-016**: The `add-a-domain` skill MUST cite these requirements rather than
  restating them, so the corpus is the single statement and the skill routes to
  it. [Source: specs/001-provider-contract/spec.md -> FR-016]

- **FR-017**: The system MUST retain an accepted agent's public key beyond the
  lifetime of its enrollment request, keyed by machine ID, so the key remains
  available for every later verification.
  [Source: specs/002-agent-key-store/spec.md -> FR-001]
- **FR-018**: The system MUST record the key only as part of accepting an
  enrollment. No message, registration or heartbeat may introduce or change a
  stored key. [Source: specs/002-agent-key-store/spec.md -> FR-002]
- **FR-019**: The controller MUST verify an agent's job response against that
  agent's stored key before the response is treated as a result, and MUST NOT
  fall back to accepting an unverified response.
  [Source: specs/002-agent-key-store/spec.md -> FR-003]
- **FR-020**: The agent MUST sign what it registers, and the controller MUST
  verify that signature against the stored key before the registration is used
  for targeting, labels, facts or fleet status.
  [Source: specs/002-agent-key-store/spec.md -> FR-004]
- **FR-021**: A registration that is unsigned, unverifiable, or signed by a key
  other than the stored key for its machine ID MUST NOT be visible to target
  resolution, and MUST NOT replace the entry of an enrolled machine.
  [Source: specs/002-agent-key-store/spec.md -> FR-005]
- **FR-022**: Where a hostname is claimed by more than one machine, target
  resolution MUST be deterministic and MUST prefer the enrolled machine, rather
  than depending on iteration order.
  [Source: specs/002-agent-key-store/spec.md -> FR-006]
- **FR-023**: The system MUST support replacing a stored key through an accepted
  enrollment, and MUST accept the previous key for a bounded grace period after
  replacement, so a rotation does not reject messages signed just before it.
  [Source: specs/002-agent-key-store/spec.md -> FR-007]
- **FR-024**: The system MUST remove a stored key when its agent is removed or its
  enrollment is rejected, after which nothing signed by that key verifies.
  [Source: specs/002-agent-key-store/spec.md -> FR-008]
- **FR-025**: Enforcement MUST be something the operator turns on per side, and
  MUST NOT begin as a side effect of upgrading. Once enforcement is on for a side,
  a message from an agent with no stored key MUST be refused there. Until it is
  on, such a message is handled as it is today. "Treat as verified" is never an
  outcome. [Source: specs/002-agent-key-store/spec.md -> FR-009]
- **FR-026**: Verification failures MUST be distinguishable by cause: no stored
  key, signature mismatch, and store unavailable are different conditions and MUST
  be reported differently, so an operator can tell "not enrolled yet" from
  "something is forging messages".
  [Source: specs/002-agent-key-store/spec.md -> FR-010]
- **FR-027**: The behaviour MUST be governed by the existing PKI switches rather
  than a new one, and with PKI disabled the system MUST behave exactly as it does
  today. [Source: specs/002-agent-key-store/spec.md -> FR-011]
- **FR-028**: Operators MUST be able to see which agents have a stored key, and
  its fingerprint, so a fleet can be checked before verification is enforced.
  [Source: specs/002-agent-key-store/spec.md -> FR-012]
- **FR-029**: The documentation MUST state the rollout order, the failure modes
  from FR-026, and what an operator does when an agent reports no stored key.
  [Source: specs/002-agent-key-store/spec.md -> FR-013]

#### The job system

- **FR-030**: A job MUST be stored before it is announced: the definition is written
  to the `job-queue` KV bucket under `jobs.{job-id}`, and only then is a notification
  published to the `JOBS` stream. Evidence: `internal/job/client/client.go`.
  [Source: specs/004-job-system/spec.md -> FR-001]
- **FR-031**: The notification MUST carry the job's identity rather than its content.
  An agent receives an ID on a subject and fetches the definition from KV. Evidence:
  `internal/job/client/client.go`, `internal/agent/handler.go`.
  [Source: specs/004-job-system/spec.md -> FR-002]
- **FR-032**: Status MUST be recorded as append-only events rather than a mutated
  field. Each event is its own key, `status.{job-id}.{state}.{source}.{unix-nano}`,
  and a job's status is computed from them by priority. Evidence:
  `internal/job/client/jobs.go`, `internal/job/client/agent.go`,
  `job.StatusPriority` in `internal/job/types.go`.
  [Source: specs/004-job-system/spec.md -> FR-003]
- **FR-033**: The corpus MUST state that the job definition key is `jobs.{job-id}`,
  and MUST record that the published site said `{status}.{uuid}` — a shape the code
  does not use, which described the status-event keys as though they were the job
  key. Evidence: `internal/job/client/client.go`.
  [Source: specs/004-job-system/spec.md -> FR-004]
- **FR-034**: Results MUST be stored separately from the job, in the `job-responses`
  bucket, so a caller reading a result does not read the job's history to find it.
  Evidence: `internal/config/nats.go`.
  [Source: specs/004-job-system/spec.md -> FR-005]
- **FR-035**: Operations MUST be routed by a dot-notation subject under one of two
  prefixes, `jobs.query` for reads and `jobs.modify` for writes, so a consumer can
  subscribe to one class of work without filtering the other. Evidence:
  `internal/job/subjects.go`.
  [Source: specs/004-job-system/spec.md -> FR-006]
- **FR-036**: The subject prefix MUST be treated as namespaced rather than literal:
  both prefixes are built from a base a deployment can change, so a stated subject
  names a shape. Evidence: `internal/job/subjects.go`.
  [Source: specs/004-job-system/spec.md -> FR-007]
- **FR-037**: A target MUST be resolvable as a hostname, a machine ID, a broadcast
  (`_all`, `_any`) or a label selector, and the rules deciding which agents a
  broadcast expects MUST be stated. Evidence: `internal/job/subjects.go`,
  `job.ExpectedAgentHostnames`.
  [Source: specs/004-job-system/spec.md -> FR-008]
- **FR-038**: The corpus MUST state that delivery is at-least-once, not
  at-most-once, and the obligation that follows: before executing, an agent checks
  whether it has already recorded a response for that job, and if it has,
  acknowledges without re-executing. Evidence: `HasJobResponse` in
  `internal/job/client/types.go`, used in `internal/agent/handler.go`.
  [Source: specs/004-job-system/spec.md -> FR-009]
- **FR-039**: The corpus MUST name the operations that make that obligation
  load-bearing rather than theoretical: `command.exec`, `command.shell`,
  `power.reboot` and `power.shutdown` are not safe to run twice. Evidence:
  `internal/agent/processor_command.go`.
  [Source: specs/004-job-system/spec.md -> FR-010]
- **FR-040**: The corpus MUST state that a job which has run is terminal: the agent
  acknowledges after recording a response, success or failure, so a failed operation
  is not retried by redelivery. Evidence: `internal/agent/handler.go`.
  [Source: specs/004-job-system/spec.md -> FR-011]
- **FR-041**: The corpus MUST state what happens when the response cannot be written
  after the operation ran — the failure is recorded best-effort and the message is
  still acknowledged, because leaving it unacknowledged would redeliver it and run
  the operation a second time. Evidence: `internal/agent/handler.go`.
  [Source: specs/004-job-system/spec.md -> FR-012]
- **FR-042**: The corpus MUST state which failures terminate a message instead of
  letting it redeliver — a malformed payload, an unparsable subject, a failed
  signature — and why: none can succeed on retry. A failure to read the job data
  itself is treated as possibly transient and left to redeliver. Evidence:
  `internal/agent/handler.go`.
  [Source: specs/004-job-system/spec.md -> FR-013]
- **FR-043**: The corpus MUST state the consumer's delivery settings as defaults a
  deployment may override, and MUST record that the published site stated different
  values: it said `MaxDeliver: 3` and `AckWait: 30s`; the defaults are `5` and `2m`.
  Evidence: `cmd/root.go`, `configs/osapi.yaml`, `internal/agent/consumer.go`.
  [Source: specs/004-job-system/spec.md -> FR-014]
- **FR-044**: The corpus MUST state that an operation outliving `AckWait` is not
  redelivered mid-flight, because the agent extends the deadline while it runs.
  Evidence: the in-progress keepalive in `internal/agent/handler.go`.
  [Source: specs/004-job-system/spec.md -> FR-015]
- **FR-045**: The corpus MUST state that two clocks bound a job, that they bound
  different things, and MUST give each one's duration rather than only its name:
  `controller.api.job_timeout`, `30s` by default, bounds how long the controller waits
  for a response, and the agent's command deadline bounds how long the work itself
  may run. The gap between them is the point — the controller stops waiting long
  before the work must stop. Evidence: `cmd/root.go` and `configs/osapi.yaml` for the
  `30s`, `internal/job/client/client.go`, `internal/exec/types.go`.
  [Source: specs/004-job-system/spec.md -> FR-016]
- **FR-046**: The corpus MUST state that a command with no deadline of its own is
  bounded by a backstop rather than left to run forever, and MUST give both its name
  and its duration: `DefaultCommandTimeout`, `10m`. A name alone does not answer what
  an operation may assume about time. Evidence: `DefaultCommandTimeout` in
  `internal/exec/types.go`, applied in `internal/exec/exec.go`.
  [Source: specs/004-job-system/spec.md -> FR-017]
- **FR-047**: The corpus MUST state that cancelling the originating API request does
  not stop a running agent operation, and that `job delete` removes the queue entry
  rather than the process. An operation is stopped by its own deadline, the backstop,
  or the agent shutting down. Evidence: `internal/job/client/client.go`,
  `internal/exec/exec.go`.
  [Source: specs/004-job-system/spec.md -> FR-018]
- **FR-048**: The corpus MUST state that a per-host result carries one of four
  statuses — `ok`, `failed`, `skipped`, `timeout` — and what distinguishes them: a
  failure ran and did not succeed, a skip does not apply to that OS family, and a
  timeout says nothing about whether it ran. Evidence: `pkg/sdk/client/status.go`,
  `internal/job/client/client.go`.
  [Source: specs/004-job-system/spec.md -> FR-019]
- **FR-049**: The corpus MUST state that a failure carries a machine-readable cause
  beside its message, and that a cause the reader does not recognise is treated as an
  ordinary failure rather than guessed at. Evidence: `internal/job/errors.go`,
  `job.Response.ErrorCode` in `internal/job/types.go`.
  [Source: specs/004-job-system/spec.md -> FR-020]
- **FR-050**: The corpus MUST state the KV bucket TTLs as configured values, naming
  the file that sets them, and MUST record that the published site stated a different
  one: it said 24 hours for completed and failed jobs, where the shipped
  configuration sets one TTL of `1h` for the whole `job-queue` bucket. Evidence:
  `configs/osapi.yaml`.
  [Source: specs/004-job-system/spec.md -> FR-021]
- **FR-051**: Where the job system's specification reaches signing, response
  verification or agent identity, it MUST cite the requirements stating them rather
  than describing them again.
  [Source: specs/004-job-system/spec.md -> FR-022]
- **FR-052**: Where it reaches what a provider must return or how a provider
  behaves, it MUST cite the provider contract's requirements.
  [Source: specs/004-job-system/spec.md -> FR-023]
- **FR-053**: After the job system's specification merges, the `add-a-domain` skill
  MUST cite its requirements rather than restating the mechanics, and the contributor
  half of the site page MUST be removed in the same change that adds those citations.
  [Source: specs/004-job-system/spec.md -> FR-024]
- **FR-054**: The corpus MUST state what happens once redelivery is exhausted,
  because FR-040 through FR-044 describe at-least-once delivery and stop short of its
  terminal case. After `MaxDeliver` attempts JetStream emits a `MAX_DELIVERIES`
  advisory, and a dedicated `<stream>-DLQ` stream subscribes to those advisories and
  retains them — `168h` and 1000 messages by default. What the dead letter queue holds
  is the **advisory** rather than the job: the job's own definition stays in the
  `job-queue` bucket until that bucket's TTL expires it (FR-050), so a reader who
  expects to retrieve the failed job from the DLQ will not find it there. The depth is
  surfaced as `dlq_count` on queue statistics and in `osapi client health status`.
  Evidence: `cmd/nats_setup.go`, `configs/osapi.yaml` under `nats.dlq`,
  `internal/job/client/jobs.go`.
  [Source: specs/004-job-system/spec.md -> FR-025]

#### Building a domain

- **FR-055**: The corpus MUST state what a domain consists of across every layer, and MUST state the consistency obligation: a domain appears in every place an existing domain appears, and the check is to pick a completed domain and search for it. Evidence: `docs/docs/sidebar/development/adding-an-api-domain.md`, "Cross-Layer Consistency".
  [Source: specs/005-building-a-domain/spec.md -> FR-001]
- **FR-056**: Where the corpus reaches provider types, file structure, the provider interface, naming, platform variants or the idempotency obligation, it MUST cite the provider contract rather than stating the rule a second time. Memory is not exempt from the one-statement test.
  [Source: specs/005-building-a-domain/spec.md -> FR-002]
- **FR-057**: Where it reaches delivery semantics, the two clocks, the dead letter queue or any other job mechanic, it MUST cite the job system; where it reaches signing, response verification or agent identity, it MUST cite the agent key store.
  [Source: specs/005-building-a-domain/spec.md -> FR-003]
- **FR-058**: The corpus MUST state the build order and MUST distinguish the parts a tool forces from the parts that are convention. The forced ones: the OpenAPI specification precedes generation, because generation reads it; generation precedes the handler, because the handler implements a generated interface; the combined specification precedes the SDK client, because the SDK generates from the combined file. The combined specification is `internal/controller/api/gen/api.yaml`, which `redocly join` assembles from every domain's own `gen/api.yaml` inside `just generate`; a domain absent from it is invisible to the SDK however complete its own spec is. Evidence: the `//go:generate` directives under `internal/controller/api/*/gen/`, the `redocly join` step in `just generate`, and `go generate ./pkg/sdk/client/gen/...`.
  [Source: specs/005-building-a-domain/spec.md -> FR-004]
- **FR-059**: The corpus MUST state the eight steps as a walkthrough rather than as eight requirements, because a numbered requirement per step would be renumbered every time a tool changes. What is stated as a requirement is what must be true of the result.
  [Source: specs/005-building-a-domain/spec.md -> FR-005]
- **FR-060**: The corpus MUST state where a domain's code goes **and what decides
  it**, because the directory is the consequence rather than the rule. An operation is
  **node-targeted** when the work happens on a managed machine: addressed to a host,
  dispatched through the job system, carried out by a provider on an agent. It is
  **controller-only** when the controller answers it itself from state it holds — the
  job queue, the audit log, enrollment, health, the object store — with no agent
  executing anything. Node-targeted operations live under
  `internal/controller/api/node/{domain}/` and carry `/node/{hostname}`;
  controller-only ones live under `internal/controller/api/{domain}/` and do not.
  The provider goes under `internal/provider/{domain}/` or
  `internal/provider/{category}/{domain}/`. A domain name can appear in **both**,
  which is why the test is functional rather than nominal:
  `internal/controller/api/file/` uploads to the object store at `/api/file`, and
  `internal/controller/api/node/file/` deploys to a host at
  `/api/node/{hostname}/file/deploy`.
  [Source: specs/005-building-a-domain/spec.md -> FR-006]
- **FR-061**: The corpus MUST state the component map, the entry points, the six
  layers — CLI, REST API, job system, provider, agent lifecycle, configuration — and
  the request flow, because that is what a contributor reads immediately before the
  domain instructions. It MUST also state how those six relate to the seven artifact
  kinds a domain contributes (FR-055), because the two lists differ and a reader who
  takes them for one list will hunt for a layer that is not there. The layers
  describe **the running system**; the artifacts describe **what a domain adds to
  it**. Four artifacts land in a layer — provider, agent processor, API handler, CLI
  commands. Three are not layers: the SDK service is a *client* of the REST API
  rather than a layer, and documentation and tests are not runtime code. The
  configuration and job system layers exist already for every domain.
  [Source: specs/005-building-a-domain/spec.md -> FR-007]
- **FR-062**: The corpus MUST state the request path an operation takes, `CLI → SDK → REST API → Job Client → NATS → Agent → Provider`, and that the provider runs on the agent rather than the controller. Evidence: `internal/job/client/client.go`.
  [Source: specs/005-building-a-domain/spec.md -> FR-008]
- **FR-063**: The corpus MUST state that two files connect a provider to the agent — a processor file under `internal/agent/` and the registration in `cmd/agent_setup.go` — and MUST state what does not change: `agent/types.go`, `agent/agent.go` and the `JobClient` interface, because the registry handles dispatch and facts wiring. Evidence: `ProviderRegistry.Register` at `internal/agent/registry.go:51`, `AllProviders` at `:74`, and the single `provider.WireProviderFacts` call at `internal/agent/agent.go:90`.
  [Source: specs/005-building-a-domain/spec.md -> FR-009]
- **FR-064**: The corpus MUST state the `FactsAware` obligation — embed `provider.FactsAware`, add the compile-time `FactsSetter` check — and MUST cite the provider contract rather than restating what it already holds. Evidence: `WireProviderFacts` at `internal/provider/facts.go:64`.
  [Source: specs/005-building-a-domain/spec.md -> FR-010]
- **FR-065**: The corpus MUST state that the OpenAPI specification is the source of truth for input validation, and MUST state the three places a tag goes and the one place it does not: `x-oapi-codegen-extra-tags` on request body properties, at *parameter* level for query parameters rather than inside `schema:`, `format: uuid` for UUID path parameters, and **not** on path parameters in strict-server mode, where oapi-codegen generates no tags.
  [Source: specs/005-building-a-domain/spec.md -> FR-011]
- **FR-066**: The corpus MUST state that a path parameter needing validation beyond `format: uuid` is validated by hand in the handler, and MUST state where that validator actually lives. **Gap**: the site said "a shared helper like `node.validateHostname()`". There is no shared helper and that call does not compile across packages — `validateHostname` is unexported and exists three times, at `internal/controller/api/agent/validate.go:30`, `internal/controller/api/node/validate.go:30` and `internal/controller/api/node/power/validate.go:30`. What is shared is `validation.Var(hostname, "required,min=1,valid_target")`. Owner: osapi, as a Go change.
  [Source: specs/005-building-a-domain/spec.md -> FR-012]
- **FR-067**: The corpus MUST state the verb mapping and that a mutable domain uses separate verbs for create and update — `POST` creates with the name in the body, `PUT /{name}` updates from the path — and MUST state the reason: it is what gives 404 semantics a meaning. A combined set or upsert endpoint is forbidden.
  [Source: specs/005-building-a-domain/spec.md -> FR-013]
- **FR-068**: The corpus MUST state the API design guidelines: endpoints grouped by functional domain under their own top-level prefix, resource-oriented paths with sub-resources nested under their parent, an area expected to grow split into its own category early, everything targeting a managed machine under `/node/{hostname}`, and path parameters for identification with query parameters only for filtering and pagination. **Gap**: the corpus backfill recorded five guidelines to fold in; the page stated **six**. The sixth, path-versus-query parameters, is included. The page had not drifted — the count was taken from memory rather than read.
  [Source: specs/005-building-a-domain/spec.md -> FR-014]
- **FR-069**: The corpus MUST state that `{hostname}` accepts a literal hostname, the reserved values `_any` and `_all`, or a `key:value` label selector. Evidence: `IsBroadcastTarget` at `internal/job/subjects.go:306`, which is the single implementation.
  [Source: specs/005-building-a-domain/spec.md -> FR-015]
- **FR-070**: The corpus MUST state that every operation under `/node/{hostname}/...` supports broadcast targeting, that the single-target and broadcast paths return the same collection shape, and that every result item carries `hostname` and `error`. A single target returns one result; a broadcast returns as many as there are agents, with failed and skipped ones present as entries rather than absent.
  [Source: specs/005-building-a-domain/spec.md -> FR-016]
- **FR-071**: The corpus MUST state that the `JobClient` interface has four generic methods — `Query`, `QueryBroadcast`, `Modify`, `ModifyBroadcast` — and that adding an operation needs none added, because a handler passes a category string and an operation constant. Evidence: `internal/job/client/types.go`, lines 146, 153, 160 and 167.
  [Source: specs/005-building-a-domain/spec.md -> FR-017]
- **FR-072**: The corpus MUST state that a domain package exports a `Handler()` function returning route-registration closures, that it wraps the handler in scope middleware itself, and that the `Server` struct does not change. Startup wiring is one appended line in `registerControllerHandlers`. Evidence: `cmd/controller_setup.go`.
  [Source: specs/005-building-a-domain/spec.md -> FR-018]
- **FR-073**: The corpus MUST state the SDK obligations — four files per service, a field on the `Client` struct, an example under `examples/sdk/client/`, a doc page in the matching category, and the navbar entry — and MUST NOT defer to an authority that does not exist. **Gap**: three documents claimed SDK naming and error handling were "specified in the `sdk-standards` capability", that it bound `osapi-orchestrator`, and that it won any disagreement. No such capability was ever written. The three were the site's domain page, the skill's `references/sdk.md`, and the site's SDK guidelines page; all three now name it as unwritten. Owner: this repository, as a feature of its own.
  [Source: specs/005-building-a-domain/spec.md -> FR-019]
  **Method naming is stated nowhere** — not in the corpus, not on the site's SDK
  guidelines page, and not in the capability nobody wrote; it was named only in the
  deferral, so for one of that deferral's four subjects there was no rule to collect.
  The other three — type exposure, JSON tags, error wrapping — are FR-074. There were
  three copies of the claim, not two. `osapi-orchestrator` does depend on `osapi`, so
  the cross-repository claim was true in substance, but the SDK is osapi's own public
  API and the orchestrator consumes it, which makes this osapi's behaviour rather than
  an agreement between repositories.
- **FR-074**: The corpus MUST state the SDK rules that are verifiable: no `gen` type in a public method signature, JSON tags on every result type, errors wrapped with context, and one service per file with no methods added to another service's files.
  [Source: specs/005-building-a-domain/spec.md -> FR-020]
- **FR-094**: The corpus MUST state the SDK's method-naming convention, and it MUST
  record that the convention was **derived from the existing surface** — 31 services
  and roughly 110 exported methods in `pkg/sdk/client/` — rather than decided in the
  abstract, because none had ever been written down (FR-073). Four rules:

  1. The five CRUD verbs are exactly `List`, `Get`, `Create`, `Update`, `Delete` —
     never `GetAll`, `Fetch`, `Set`, `Put`, or `Remove` for the service's own
     resource. Eleven services use them and none deviates.
  2. A method acting on the service's own resource takes the **bare verb**, no object:
     `Service.Start`, not `StartService`; `Power.Reboot`, `Agent.Accept`, `Job.Retry`.
  3. A method acting on a **sub-resource** takes verb then object: `User.AddKey`,
     `User.ListKeys`, `Agent.ListPending`, `Package.ListUpdates`, `Log.QueryUnit`.
  4. A getter is named `Get` and nothing else, taking its subject from the service.

  5. When a service exposes **several** distinct reads, each takes verb then object
     under rule 3; rule 4's bare `Get` applies only where there is exactly one read.

  Seven methods do not conform and MUST be renamed rather than excepted:
  `Docker.ImageRemove` → `RemoveImage`, `Ping.Do` → `Send`, `File.Stale` →
  `ListStale`, `File.Changed` → `GetChanged`, and `Health.Liveness`/`Ready`/`Status`
  → `GetLiveness`/`GetReady`/`GetStatus`. The SDK carries no released version and the
  one external consumer pins a pseudo-version commit, so these are renames now and
  breaking changes after the first tag — twenty-six call sites in osapi and three in
  the orchestrator is the whole cost. `Docker.Pull` is deliberately not renamed:
  pull applies to nothing but images, so the object adds length without removing
  ambiguity.

  Two of the seven were first recorded as permitted deviations, described as
  predicates read off their names rather than their signatures, which return a list
  and a single record. That is FR-090 failing against the analysis that stated it.
  [Source: specs/005-building-a-domain/spec.md -> FR-028]
- **FR-075**: The corpus MUST state the CLI obligations: one parent command per domain and one subcommand per endpoint, `--json` on every command, `cli.PrintKV` for key-value output and `cli.PrintCompactTable` for tabular, flags rather than positional arguments for resource IDs, and every response code the OpenAPI specification declares handled in the status switch. Evidence: `PrintCompactTable` at `internal/cli/ui.go:198`, `PrintKV` at `:413`.
  [Source: specs/005-building-a-domain/spec.md -> FR-021]
- **FR-076**: The corpus MUST state all **eight** design principles, each with what it constrains, so a principle can decide a question rather than decorate a page. **Gap**: the corpus backfill recorded five; the page stated eight. The three never named were Reliability and Stability, CLI Parity with API, and Least Privilege Mode. The recorded line count was right, so the page had not grown — the count of principles was wrong when written.
  [Source: specs/005-building-a-domain/spec.md -> FR-022]
- **FR-077**: The corpus MUST record that each of the eight principles was checked against `.charter/fragments/global/` and this project's constitution before being stated. All eight are unstated there: the first five were checked when the backfill was planned, and the remaining three were checked by reading the fragment text rather than the headings, because that finding's own first version had claimed two were charter rules read from their headings.
  [Source: specs/005-building-a-domain/spec.md -> FR-023]
- **FR-078**: The corpus MUST state what verifies a finished domain, and MUST NOT reproduce the site's command list as sufficient. **Gap**: the page's last step gave `just generate`, `go build ./...`, `just go-unit` and `just go-vet`. All four exist, and none covers the previous step, which edits eight documentation files: `docusaurus-fmt-check` and `docusaurus-build` run in `just test`. A contributor following that list exactly can hand in work that fails continuous integration on the documentation the step before told them to write. The gate is `just ready` and `just test`. Owner: osapi.
  [Source: specs/005-building-a-domain/spec.md -> FR-024]
- **FR-079**: The `add-a-domain` skill MUST cite these requirements rather than restating the mechanics, as a relative link four `../` levels up from a reference file, named to a requirement rather than to a document.
  [Source: specs/005-building-a-domain/spec.md -> FR-025]
- **FR-080**: In the same change that adds those citations, the contributor half of the site MUST be removed: the domain page reduced to an index with a citation table and a pointer to the skill; the API guidelines and principles pages removed with their addresses redirected; and the system architecture page's component map, entry points, layers and request flow removed. Adding the citations without removing the pages leaves two statements.
  [Source: specs/005-building-a-domain/spec.md -> FR-026]
- **FR-081**: The corpus MUST state a domain's test obligations, or cite where they
  are stated, and MUST NOT leave tests as the one artifact kind FR-055 names with no
  requirement behind it. They are osapi's `CONTRIBUTING.md`'s, under "Testing", cited
  rather than copied: `testify/suite` table tests with one suite method per function
  under test, `*_public_test.go` in a `_test` package as the default, coverage gated
  at 99.9% with `.coverignore` narrowing what the figure covers, and the two HTTP
  wiring methods a public suite carries. One obligation is specific to this subject:
  a new API domain includes a `{domain}_test.go` smoke suite under
  `test/integration/`, with every mutating test guarded by `skipWrite(s.T())` so
  continuous integration runs read-only by default. Evidence: `CONTRIBUTING.md`,
  "Testing", "Test file conventions" and "Test layers"; `.coverignore`.
  [Source: specs/005-building-a-domain/spec.md -> FR-027]

#### Where knowledge lives

- **FR-082**: A page holding contributor knowledge MUST be classified as moving wholly, splitting, or staying, and the classification MUST be justified by **who reads it** rather than by where it currently sits.
  [Source: specs/003-corpus-backfill/spec.md -> FR-001]
- **FR-083**: Content telling a contributor or an agent how osapi is built MUST end up in the corpus. Content telling an operator how to use osapi MUST stay on the published site.
  [Source: specs/003-corpus-backfill/spec.md -> FR-002]
- **FR-084**: A page serving both readers MUST be split so the operator's half is a coherent page in its own right, not the remainder left after the contributor's half was removed.
  [Source: specs/003-corpus-backfill/spec.md -> FR-003]
- **FR-085**: Moved content MUST be grouped by **subject** rather than by the page it came from, and each subject MUST be large enough to be worth a specification of its own. A subject too small to stand alone MUST be folded into a larger one.
  [Source: specs/003-corpus-backfill/spec.md -> FR-004]
- **FR-086**: Where subjects are moved in sequence, the largest body of contributor knowledge MUST go first — it is the one the skills lean on most, so it is where the pattern is worth proving.
  [Source: specs/003-corpus-backfill/spec.md -> FR-005]
- **FR-087**: No page address that existed before a move MUST 404 after it. Per moved page, it MUST be stated whether the address keeps a user-facing page or redirects, and why that choice fits that page.
  [Source: specs/003-corpus-backfill/spec.md -> FR-006]
- **FR-088**: A skill needing a moved rule MUST cite the corpus requirement rather than restate it: a table mapping each rule to the requirement stating it, as a relative link the skill linter resolves.
  [Source: specs/003-corpus-backfill/spec.md -> FR-007]
- **FR-089**: After a subject moves, **exactly one statement** of each of its rules MUST exist across the corpus, the site and the skills. Every other mention MUST be a citation.
  [Source: specs/003-corpus-backfill/spec.md -> FR-008]
- **FR-090**: A moved rule MUST be checked against the code before it is written into the corpus, and a rule the code does not match MUST be recorded as a **gap** rather than restated as though it held. This is the requirement that caught five gaps across the two subjects, and the one this feature's own record broke: its page inventories were right about line counts and wrong about the count of items inside two pages, because those were taken from prose rather than measured.
  [Source: specs/003-corpus-backfill/spec.md -> FR-009]
- **FR-091**: Each subject MUST move in a single change per repository that moves the content, updates the citations, and leaves every address resolving — so no state exists where a reader finds two disagreeing statements of the same rule.
  [Source: specs/003-corpus-backfill/spec.md -> FR-010]
- **FR-092**: The corpus statement of a moved rule MUST cite the code it describes, so a reader can check the rule rather than trust it.
  [Source: specs/003-corpus-backfill/spec.md -> FR-011]
- **FR-093**: The published site MUST NOT send an operator to the corpus. A citation is for contributors and agents; an operator page answering with "see the specifications repository" has lost its reader.
  [Source: specs/003-corpus-backfill/spec.md -> FR-012]

#### The embedded UI

- **FR-095**: osapi ships a single-page application embedded in the controller binary and served from the same host and port as the REST API, so enabling it adds no network configuration. Evidence: `ui/embed.go`, and the `controller.api.port` it shares.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-001]
- **FR-096**: The UI is disabled by `controller.ui.enabled: false`; the default is true, and when disabled the controller skips registering the SPA handler and serves only the REST API. This is the one rule in the set an **operator** acts on, and it stays on the published site as well — cited there, stated here.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-002]
- **FR-097**: The UI's stack is stated as what each part is for rather than as a version list: React with TypeScript for the application, Vite to build it, Tailwind for styling, React Router for navigation, and orval to generate the API client. Versions are evidence and date; the roles do not.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-003]
- **FR-098**: There are four kinds of UI component, and **what separates them is what each one knows** rather than what it is called — which is the boundary a contributor places a new file against. A primitive knows no osapi resource: none of the 34 files in `ui/src/components/ui/` imports the generated client. A domain component knows exactly one: 38 of the 43 files in `ui/src/components/domain/` import the client or a hook. Layout knows none and holds the page's chrome. A hook holds state or fetches data and renders nothing — every one of the 14 files in `ui/src/hooks/` is `.ts` rather than `.tsx`, so none of them can contain markup. A new file goes where its knowledge puts it: markup with no resource is a primitive, markup with one resource is a domain component, a resource with no markup is a hook. Reproduce with `cd ui/src && grep -rl "sdk/" components/ui | wc -l` (expect 0), `grep -rl "sdk/\|hooks/" components/domain | wc -l` (expect 38 of 43), and `ls hooks | sed 's/.*\.//' | sort -u` (expect `ts`).
  [Source: specs/007-the-embedded-ui/spec.md -> FR-004]
- **FR-099**: The UI's API client is **generated from the same specification as the Go SDK** — the combined file FR-058 defines — so an endpoint added to a domain reaches both, and a fetch mutator adapts it to the browser. This is the fact that makes the UI part of osapi rather than a separate application. Generation itself is FR-058's; this states the second consumer, not a second mechanism.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-005]
- **FR-100**: The built assets are compiled into the Go binary, which is why there is no separate deployment. Evidence: `ui/embed.go`, `ui/dist/`.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-006]
- **FR-101**: The UI authenticates with the same JWT the rest of osapi uses, and the asymmetry is stated plainly: the UI decodes the token client-side **without verifying it**, because verification is the server's job. A contributor who read only the client would otherwise take the decode for a check. Found by reading the code — the site page carried it as a parenthetical aside rather than a rule.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-007]
- **FR-102**: The UI's permission model is osapi's, not a second one: three built-in roles and `resource:verb` permissions matching the Go model. Where this reaches what those permissions mean it cites rather than restates. **The statement it cites is on the published site**, in the surviving RBAC section of `architecture/ui.md`, because what the roles permit is what an operator configures; the corpus holds no second account of it.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-008]
- **FR-103**: The UI's development obligations — where the dev server runs, how a production build is produced, the component and file-naming conventions, and what regenerating the SDK requires — are stated as the contract a contributor obeys rather than as a transcript of commands. Commands belong in the justfile: `global/documentation` says a rule a tool enforces is not restated as prose.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-009]
- **FR-104**: `ui/` is excluded from the coverage gate by `.coverignore`, so the UI's correctness rests on its own checks rather than on Go coverage. Evidence: `/ui/` in `.coverignore`. A contributor who assumed the gate covered it would be wrong in a way nothing would tell them. Found by reading the code; stated in neither prose document.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-010]
- **FR-105**: The UI's architecture was stated twice and the two copies had diverged before this was corrected. `docs/docs/sidebar/architecture/ui.md`, 264 lines, last touched 2026-08-15, held `Configuration` and `Embedding Mechanism`. `ui/docs/architecture.md`, 263 lines, last touched 2026-09-02, held `Feature flags`. Each held a section the other never got, eighteen days apart, and no gate detected it.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-011]
- **FR-106**: The three unshared sections were carried forward as a **union rather than by choosing a winner**: `Feature flags` from the copy beside the code, `Configuration` and `Embedding Mechanism` from the site page. Recency tracks *editing*, not accuracy — the site page was not edited because nobody remembered it existed, which says nothing about whether what it held was still true.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-012]
- **FR-107**: The two copies' shared sections agreed in substance and differed in punctuation, and that is recorded as evidence of copying rather than as a disagreement requiring judgement. A reader who found the phrasing difference logged as a conflict would look for a decision that was never needed.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-013]
- **FR-108**: `docs/docs/sidebar/architecture/ui.md` was **split**. `Configuration`, the RBAC model and `Pages` stay and read as an operator's page; the embedding mechanism, application structure, stack, component architecture, auth flow and SDK generation went to the corpus. 82 lines of 264 remain — not the 80 the plan measured, because the `[orval]` link definition sat inside the staying range while its only reference sat inside the moving one, so removing the orphan took two lines the plan had counted as staying.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-014]
  [Source: specs/007-the-embedded-ui/tasks.md -> T013]
- **FR-109**: `docs/docs/sidebar/features/management-dashboard.md` lost its `## Architecture` account of the stack and the embedding mechanism, which restated FR-097 and FR-100. What an operator acts on there stays: the dashboard is served at `/` with an `index.html` fallback, which is why API endpoints are prefixed `/api/`. **This document was missed by the classification.** It was found by a grep after the move had merged, not by the plan — see AS-026.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-014a]
- **FR-110**: `development/ui-development.md` moved **entire**, its address keeping a short contributor index with a citation table — the shape `adding-an-api-domain.md` took. Its links are absolute GitHub addresses, for the reason the citation contract's sanctioned exception gives, and the page says so.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-015]
- **FR-111**: `ui/docs/architecture.md` was **replaced by a pointer** rather than deleted, and is the one place in the programme where a file beside the code survives that way: its location is its value. A contributor working in `ui/` looks for architecture beside the code, and an absent file there sends them searching. The pointer states that it is a pointer rather than a summary — a file somebody can edit back into a document, and that sentence is the only thing guarding against it.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-016]
- **FR-112**: The `add-a-domain` skill gains no UI reference. A domain's UI work is not part of adding a domain today — no domain has any — and inventing a citation for work nobody does would be the rule invented to fill a template that `global/correction` warns about. If UI work becomes part of adding a domain, the citation is added by the change that makes it true.
  [Source: specs/007-the-embedded-ui/spec.md -> FR-017]
  [Source: specs/007-the-embedded-ui/research.md -> "Decision 4"]


### Key Entities

- **Provider**: A domain's operations, running in the agent, selected by OS
  family. Exposes the operation set in FR-002 and honours FR-004.
  [Source: specs/001-provider-contract/spec.md -> Provider]
- **Result**: What an operation returns: the resource identity, whether anything
  changed, and a per-resource error when one occurred.
  [Source: specs/001-provider-contract/spec.md -> Result]
- **Unsupported outcome**: The shared signal meaning "not available on this OS
  family", distinct from a failure and from no change.
  [Source: specs/001-provider-contract/spec.md -> Unsupported outcome]
- **Facts**: Host attributes collected by the agent and injected into registered
  providers. [Source: specs/001-provider-contract/spec.md -> Facts]
- **File deployer**: The narrow contract a provider delegates file writes to in
  order to gain change tracking, idempotency and template rendering.
  [Source: specs/001-provider-contract/spec.md -> File deployer]

- **Stored agent key**: An accepted agent's public key, held against its machine
  ID, with the fingerprint recorded at acceptance and, during rotation, the
  previous key and the moment it stops being accepted.
  [Source: specs/002-agent-key-store/spec.md -> Stored agent key]
- **Registration**: What an agent publishes about itself — hostname, labels,
  machine ID and status — which targeting reads. Authenticated under FR-020.
  [Source: specs/002-agent-key-store/spec.md -> Registration]
- **Job response**: What an agent returns for a unit of work. Authenticated under
  FR-019. [Source: specs/002-agent-key-store/spec.md -> Job response]
- **Enrollment acceptance**: The only event that may create or replace a stored
  key. [Source: specs/002-agent-key-store/spec.md -> Enrollment acceptance]

- **Job**: An immutable definition stored under `jobs.{job-id}`, plus the
  append-only status events describing what happened to it.
  [Source: specs/004-job-system/spec.md -> Key Entities]
- **Notification**: A subject-routed message carrying a job ID, not its content.
  [Source: specs/004-job-system/spec.md -> Key Entities]
- **Response**: An agent's answer, stored in its own bucket, carrying a status, a
  message and a machine-readable cause.
  [Source: specs/004-job-system/spec.md -> Key Entities]
- **Target**: What a job is addressed to — a hostname, a machine ID, a broadcast or a
  label selector.
  [Source: specs/004-job-system/spec.md -> Key Entities]
- **Obligation**: Something the system does not guarantee and the agent must
  therefore do. At-least-once delivery creates the one that matters in the job
  system.
  [Source: specs/004-job-system/spec.md -> Key Entities]

- **Domain**: A coherent area of system behaviour exposed as API endpoints, whose
  artifacts span provider, agent processor, API handler, SDK service, CLI commands,
  documentation and tests. It is complete when it appears everywhere an existing
  domain appears.
  [Source: specs/005-building-a-domain/spec.md -> Key Entities]
- **Layer**: One of the six the system is built from — CLI, REST API, job system,
  provider, agent lifecycle, configuration — each taking a defined artifact from a
  domain.
  [Source: specs/005-building-a-domain/spec.md -> Key Entities]
- **Step**: One unit of the build sequence. Some orderings are forced by code
  generation and are requirements; the rest are convention and are a walkthrough.
  [Source: specs/005-building-a-domain/spec.md -> Key Entities]
- **Gap**: A rule a document states that the repository does not bear out, recorded
  with both sides named and an owner, never silently corrected. Four are recorded
  against building a domain.
  [Source: specs/005-building-a-domain/spec.md -> Key Entities]
- **Candidate page**: A published-site page holding contributor or agent knowledge.
  Six were identified across the backfill, totalling 1,925 lines of the site's
  16,938.
  [Source: specs/003-corpus-backfill/spec.md -> Key Entities]
- **Subject**: A body of related knowledge that becomes one corpus specification,
  independent of which pages it came from. Two were moved: the job system and
  building a domain.
  [Source: specs/003-corpus-backfill/spec.md -> Key Entities]
- **Citation**: A reference from a skill or a page to a corpus requirement, replacing
  a restatement. Validated by the gate: a citation whose target does not exist fails
  the build.
  [Source: specs/003-corpus-backfill/spec.md -> Key Entities]
- **Reader**: Either an operator, who uses osapi, or a contributor or agent, who
  changes it. Every classification decision turns on which one is being served.
  [Source: specs/003-corpus-backfill/spec.md -> Key Entities]

- **Embedded UI**: A single-page application compiled into the controller binary and
  served from the REST API's port.
  [Source: specs/007-the-embedded-ui/spec.md -> Key Entities]
- **Component kind**: One of four — primitive, domain, layout, hook — the boundary a
  new file is placed against, decided by what the file knows rather than what it is
  called. [Source: specs/007-the-embedded-ui/spec.md -> Key Entities]
- **Generated client**: The UI's API access, produced from the same OpenAPI
  specification as the Go SDK.
  [Source: specs/007-the-embedded-ui/spec.md -> Key Entities]
- **Divergent copy**: One of two statements of the same architecture, each holding a
  section the other lacked. Distinct from a *candidate page*, which is a page
  classified by its reader: a divergent copy is identified by what it disagrees with,
  and two of them can both be contributor pages.
  [Source: specs/007-the-embedded-ui/spec.md -> Key Entities]

## Success Criteria

### Measurable Outcomes

- **SC-001**: A contributor states all three idempotency outcomes and the
  unsupported outcome from the corpus alone, without opening a provider.
  [Source: specs/001-provider-contract/spec.md -> SC-001]
- **SC-002**: Every existing provider can be checked against the contract, and
  each deviation is expressible as a named requirement it fails rather than as a
  difference from a sibling. [Source: specs/001-provider-contract/spec.md -> SC-002]
- **SC-003**: The `add-a-domain` skill's provider reference contains no restated
  mechanics: what remains is routing plus citations into this corpus.
  [Source: specs/001-provider-contract/spec.md -> SC-003]
- **SC-004**: A new domain's provider is reviewable against the corpus with no
  appeal to "look at how sysctl does it".
  [Source: specs/001-provider-contract/spec.md -> SC-004]
- **SC-005**: Someone asking whether a provider needs to know about the messaging
  layer gets a stated answer rather than inferring one from imports.
  [Source: specs/001-provider-contract/spec.md -> SC-005]

- **SC-006**: A response or registration signed by a key other than the one
  recorded at acceptance is rejected in every case, and never reaches an operator
  as a result or as fleet state.
  [Source: specs/002-agent-key-store/spec.md -> SC-001]
- **SC-007**: Work targeted at a hostname reaches the machine that enrolled under
  that hostname, including when another machine is publishing the same hostname.
  [Source: specs/002-agent-key-store/spec.md -> SC-002]
- **SC-008**: An operator can determine, for any agent, whether the controller
  holds its key and which key that is, without reading storage directly.
  [Source: specs/002-agent-key-store/spec.md -> SC-003]
- **SC-009**: Rotating an agent's key causes no rejected messages for correctly
  behaving agents, and messages signed with the old key stop verifying once the
  grace period lapses. [Source: specs/002-agent-key-store/spec.md -> SC-004]
- **SC-010**: With PKI disabled, behaviour is unchanged from before the key store
  existed. [Source: specs/002-agent-key-store/spec.md -> SC-005]
- **SC-011**: Every rejection is attributable to one of the stated causes, and no
  rejection is reported only as a generic failure.
  [Source: specs/002-agent-key-store/spec.md -> SC-006]
- **SC-012**: An operator can enable enforcement on one side, see which agents
  would be refused, re-enrol them, and complete the rollout without the fleet
  refusing work at a moment they did not choose.
  [Source: specs/002-agent-key-store/spec.md -> SC-007]

- **SC-013**: A contributor with no prior knowledge answers, from the corpus alone,
  what carries a job and guarantees its delivery, what a second delivery obliges the
  agent to do, and what bounds how long an operation runs.
  [Source: specs/004-job-system/spec.md -> SC-001]
  [Source: specs/003-corpus-backfill/spec.md -> SC-001]
- **SC-014**: Every requirement naming a configured value or a key format cites a
  file, and opening that file confirms the value or finds the gap the requirement
  records.
  [Source: specs/004-job-system/spec.md -> SC-002]
  Generally: every rule moved into the corpus cites the code it describes, and a rule
  the code does not match is recorded as a gap rather than stated as fact.
  [Source: specs/003-corpus-backfill/spec.md -> SC-006]
- **SC-015**: The three gaps between the published site and the code — the job key
  shape, the consumer defaults, the bucket TTL — are stated as corrections rather
  than silently differing from the page they came from.
  [Source: specs/004-job-system/spec.md -> SC-003]
- **SC-016**: One statement of each job system rule exists across the corpus, the
  site and the skills, with the citations resolving under `just skill-lint`.
  [Source: specs/004-job-system/spec.md -> SC-004]
  This holds for every moved subject, not only the job system.
  [Source: specs/003-corpus-backfill/spec.md -> SC-004]
  The probe is a **grep across the directories**, not a check of a list of files: for
  the UI, grepping the stack terms, the moved headings and the embedding mechanism
  across `docs/docs`, `ui/docs` and the corpus must return the corpus statement and
  citations and nothing else. A classification enumerates what somebody thought of; a
  grep finds what is there, which is how the fourth copy of the UI's architecture was
  found after the move had merged.
  [Source: specs/007-the-embedded-ui/spec.md -> SC-002]
- **SC-017**: No job system requirement restates a rule the provider contract or the
  agent key store already states.
  [Source: specs/004-job-system/spec.md -> SC-005]

- **SC-018**: A reader who has not seen the site page answers four questions from the
  corpus alone: what a domain consists of and how an incomplete one is recognised;
  what must be built before what and which orderings are forced; where user input is
  validated and what happens to a path parameter; and what must be true of an
  operation targeting more than one machine.
  [Source: specs/005-building-a-domain/spec.md -> SC-001]
- **SC-019**: Every address removed from the site resolves after the change.
  [Source: specs/005-building-a-domain/spec.md -> SC-002]
  More broadly: no address that resolved before a move fails to resolve after it.
  [Source: specs/003-corpus-backfill/spec.md -> SC-003]
- **SC-020**: No page an operator reads points into the corpus. The contributor index
  and the SDK development guidelines are the exceptions, and both have contributor
  readers.
  [Source: specs/005-building-a-domain/spec.md -> SC-003]
- **SC-021**: `just test` passes in the specifications repository, `skill-lint`
  resolving every citation into the corpus.
  [Source: specs/005-building-a-domain/spec.md -> SC-004]
  In osapi, `just docusaurus-fmt-check` and `just docusaurus-build` pass — and, for a
  change touching a markdown file outside `docs/`, `just md-fmt-check` as well. The
  two formatters are divided by path and passing one says nothing about the other.
  [Source: specs/007-the-embedded-ui/spec.md -> SC-006]
  [Source: specs/007-the-embedded-ui/tasks.md -> T013]
- **SC-022**: No rule the corpus states appears in restated form in the skill's
  references. The skill states a rule's name and where it lives.
  [Source: specs/005-building-a-domain/spec.md -> SC-005]
- **SC-023**: The site page's last commit postdates the specification's merge. If it
  does not, the corpus and the page both state these rules.
  [Source: specs/005-building-a-domain/spec.md -> SC-006]
- **SC-024**: Every task in the site's usage and feature documentation can still be
  completed from the site alone. This is the half of the operator test that address
  resolution does not cover: a page can resolve and still have lost what somebody
  needed from it.
  [Source: specs/003-corpus-backfill/spec.md -> SC-002]
  A split page is checked by its headings and then read: the UI page must keep
  exactly `Configuration`, `Authentication & Authorization` and `Pages`, and answer
  how to disable the UI, what each screen shows and what the three roles permit. The
  grep proves the sections; only a reader proves it holds together, and the
  introduction is the part most likely to be wrong, because deletion alone leaves one
  that still introduces a contributor's document.
  [Source: specs/007-the-embedded-ui/spec.md -> SC-003]
- **SC-025**: The `add-a-domain` skill shrinks, and what remains is routing plus
  citations rather than restated mechanics. Measured across both subjects its
  references went from 704 lines to 692, a net 12 — narrow, because five rules turned
  out to have no home in the corpus and were kept in place with a note saying so
  rather than deleted to improve the figure. The measure that shows what the backfill
  achieved is the site, where 950 lines of contributor knowledge left `docs/`.
  [Source: specs/003-corpus-backfill/spec.md -> SC-005]

- **SC-026**: A reader who has seen neither UI page answers three questions from the
  corpus alone: how does the UI reach a user's browser, where does a new component
  go, and what does the UI verify about a token? Each would mislead a contributor if
  unanswered — a separate deployment assumed, a file placed wrongly, a client-side
  decode taken for a check. **Two of the three passed on the first reading**; the
  second failed, because FR-004 required a statement of what separates the component
  kinds and did not make one. It has not been re-read since that was fixed.
  [Source: specs/007-the-embedded-ui/spec.md -> SC-001]
  [Source: specs/007-the-embedded-ui/tasks.md -> T015]
- **SC-027**: `ui/docs/architecture.md` is a pointer of under ten lines. It is nine.
  If it grows, it has stopped being a pointer and the UI's architecture is stated
  twice again, which is why the file says so in its own text.
  [Source: specs/007-the-embedded-ui/spec.md -> SC-004]
- **SC-028**: Both disagreements between the two former copies are recorded with what
  each held, and all three unshared sections survive in the corpus. The point is not
  that they are mentioned but that none was lost to the merge: a merge picking either
  copy as authoritative would have dropped one or two of them.
  [Source: specs/007-the-embedded-ui/spec.md -> SC-005]
- **SC-029**: The UI move changed no Go code. `git diff --stat` touches only
  markdown, `ui/` included — the directory was touched for the documentation file it
  carries and nothing else.
  [Source: specs/007-the-embedded-ui/spec.md -> SC-007]

## Assumptions

- **AS-001**: The audience is contributors and agents working on osapi, not
  operators. What each domain does for a user stays in the published
  documentation; this states how a provider behaves. File paths and named errors
  appear as evidence for requirements, which the constitution's Verification
  principle requires.
  [Source: specs/001-provider-contract/spec.md -> "The audience is contributors and agents"]
- **AS-002**: Requirements state current behaviour. Two known gaps are recorded
  rather than specified away: the option-parsing rule in FR-011 is not yet
  enforced for user and group names (recorded on GHSA-6gc6-px2x-q95j), and the
  atomic-write and mode-application rules in FR-013 are not yet honoured by the
  file deployer (osapi-io/osapi#498). A requirement the code does not yet meet is
  a gap in the code, not an error in the corpus.
  [Source: specs/001-provider-contract/spec.md -> "Requirements state current behaviour"]
- **AS-003**: The job system, the request, SDK and CLI layers, and the UI are out
  of scope and become their own features. This covers only what a provider is and
  must do. [Source: specs/001-provider-contract/spec.md -> "The job system, the request, SDK and CLI layers"]
- **AS-004**: The four patterns are the four in the codebase today. A fifth would
  amend this. [Source: specs/001-provider-contract/spec.md -> "The four patterns are the four in the codebase today"]
- **AS-005**: Enrollment remains the only trust anchor. The key store makes the
  identity established there durable and checkable; it does not change how an
  agent is accepted, nor introduce a second way to become trusted.
  [Source: specs/002-agent-key-store/spec.md -> "Enrollment remains the only trust anchor"]
- **AS-006**: Agents hold a key pair and sign responses, and the controller holds
  a key pair and signs jobs.
  [Source: specs/002-agent-key-store/spec.md -> "Agents already hold a key pair"]
- **AS-007**: The grace period for an agent key follows the pattern already used
  for the controller key rather than inventing a second mechanism.
  [Source: specs/002-agent-key-store/spec.md -> "The grace period for an agent key"]
- **AS-008**: Transport credentials are not identity. NATS credentials control who
  may connect; the key store decides whose messages are believed once connected.
  [Source: specs/002-agent-key-store/spec.md -> "Transport credentials are not identity"]
- **AS-009**: Controller key rotation, the enrollment handshake itself, and NATS
  authorization are out of scope, the last being deployment configuration rather
  than osapi behaviour.
  [Source: specs/002-agent-key-store/spec.md -> "Out of scope"]
- **AS-010**: The operator half of the job system's site page stays where it is: the
  job states as observed, polling, the CLI reference, and the metrics worth watching.
  [Source: specs/004-job-system/spec.md -> Assumptions]
- **AS-011**: The job system page was 630 lines when it was archived, not the 603 the
  corpus backfill's specification recorded. The 27 extra lines are its error handling
  section, which is the most precisely sourced content on the page.
  [Source: specs/004-job-system/spec.md -> Assumptions]
- **AS-012**: Archiving the job system changed no Go code. It states what the code
  already does, and records where the published site said otherwise.
  [Source: specs/004-job-system/spec.md -> Assumptions]
- **AS-013**: Three gaps were found by reading the code behind three of the page's
  statements. Others may exist in statements not yet checked; every requirement
  citing the file it describes is what lets the next reader find them rather than
  trust the corpus.
  [Source: specs/004-job-system/spec.md -> Assumptions]

- **AS-014**: The reader of the domain-building corpus is a contributor or an agent,
  not an operator. That is what makes a citation the right form there and the wrong
  form on a feature page.
  [Source: specs/005-building-a-domain/spec.md -> "The reader of the corpus"]
- **AS-015**: The four gaps recorded against building a domain are recorded, not
  fixed. Each has an owner: the unexported and triplicated hostname validator and
  the incomplete verification command list are osapi's, the absent SDK standards
  capability is this repository's own feature, and two miscounted inventories are
  the backfill's own record.
  [Source: specs/005-building-a-domain/spec.md -> "The four gaps are recorded"]
- **AS-016**: The redirects plugin is available for the two removed addresses. It was
  added by this work rather than inherited: building a domain is the only subject in
  the backfill that deletes a page, and therefore the only one that needs a redirect.
  [Source: specs/005-building-a-domain/spec.md -> "@docusaurus/plugin-client-redirects"]
- **AS-017**: Building a domain changed no Go code. It states what the code does and
  cites the file for each claim.
  [Source: specs/005-building-a-domain/spec.md -> "any Go code change"]
- **AS-018**: Page line counts were re-measured before anything moved and all four
  matched what the backfill recorded. What did not match was the *contents* of two of
  those pages, which is why a count taken from prose is not evidence.
  [Source: specs/005-building-a-domain/spec.md -> "The line counts"]

- **AS-019**: Six candidate pages held 1,925 lines of contributor knowledge, of the
  site's 16,938. The other 15,013 — thirty feature pages, the usage and SDK
  documentation — are user-facing and were never in scope.
  [Source: specs/003-corpus-backfill/spec.md -> "The six candidate pages"]
- **AS-020**: The thirty feature pages stay where they are. Each describes what a
  domain does for an operator, which is the site's job.
  [Source: specs/003-corpus-backfill/spec.md -> "The thirty feature pages stay"]
- **AS-021**: Not every candidate page moved. Two moved wholly, two were split, two
  were deleted with their addresses redirected — the classification was the work, and
  "stays" and "splits" were both real answers.
  [Source: specs/003-corpus-backfill/spec.md -> "Not every candidate page moves"]
- **AS-022**: This feature's own page inventories were wrong in three places and were
  corrected before it was archived. Every line count was right; the count of items
  inside two pages was taken from prose rather than measured. It is the argument for
  FR-090 written by the feature that stated it.
  [Source: specs/003-corpus-backfill/spec.md -> "Corrected 2026-09-28"]

- **AS-023**: The union of the two UI copies' unshared sections needed no
  adjudication. All three describe things that exist — feature flags, the enable
  switch, the embedding — so none is a claim the other copy contradicted. The copies
  diverged by addition rather than by disagreement, which is what made a union
  correct rather than a compromise.
  [Source: specs/007-the-embedded-ui/spec.md -> "The union of the unshared sections"]
  [Source: specs/007-the-embedded-ui/research.md -> "Decision 1"]
- **AS-024**: `ui/`'s own `AI_POLICY.md` is policy rather than architecture and was
  out of scope. [Source: specs/007-the-embedded-ui/spec.md -> "ui/'s own AI_POLICY.md"]
- **AS-025**: The UI move changed no Go code. It states what the code already does
  and cites the file for each claim; two of its requirements came from the code
  rather than from either prose document, and a reader who trusted the prose would
  have had neither.
  [Source: specs/007-the-embedded-ui/spec.md -> "Counts were measured"]
  [Source: specs/007-the-embedded-ui/research.md -> "Decision 3"]
- **AS-026**: Three of that feature's own claims were wrong and were corrected before
  it was archived, and **each was found by a different one of its own checks, none by
  re-reading the specification**. A grep found a **fourth** copy of the architecture
  where the classification had recorded three — `features/management-dashboard.md`,
  which sat eight lines above a sentence the same change had just edited, so being in
  the file was not enough. A line count found the pointer at ten lines against a
  criterion of under ten, the bare corpus address taking a line of its own once
  mdformat wraps at 80. And the reading found FR-004 requiring the corpus to state
  what separates the component kinds and then not stating it. Counts were measured on
  `b003df6` in specs and `0cca62060` in osapi; the line counts will date, what the
  sections are will not.
  [Source: specs/007-the-embedded-ui/spec.md -> "Corrected 2026-09-29"]
