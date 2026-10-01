# Feature Specification: Corpus backfill from the published site

**Feature Branch**: `003-corpus-backfill`

**Created**: 2026-09-26

**Status**: Archived 2026-09-28

**Input**: User description: "Move the domain knowledge out of the Docusaurus
site and into the specs corpus, so the skills read it from the corpus and the
site keeps only what a user needs."

The corpus holds two specifications against roughly twenty domains. The
knowledge that should be in it is in two other places instead: the
`add-a-domain` skill, which only whoever loads it benefits from, and the
published site, where a contributor's rules sit beside an operator's
instructions. This specifies which site content belongs in the corpus, what
stays, and what happens to a page whose contents move.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A contributor answers a question from the corpus alone (Priority: P1)

Someone adding an endpoint needs to know how a request becomes work an agent
runs: what carries it, what guarantees delivery, what happens on a retry. They
read the corpus and get an answer, without opening the published site and
without loading a skill.

**Why this priority**: This is the feature. The corpus is meant to be what makes
the skills useful; while the knowledge lives elsewhere, every skill either
restates it or routes to a page written for a different reader.

**Independent Test**: Given only the corpus, a reader can state how work reaches
an agent, what is guaranteed about delivery, and what a second delivery of the
same work must not cause.

**Acceptance Scenarios**:

1. **Given** the corpus alone, **When** a contributor asks how work reaches an
   agent, **Then** the answer is stated in the corpus rather than linked to the
   published site.
2. **Given** the corpus alone, **When a** contributor asks what a retry may do,
   **Then** the delivery guarantee and the idempotency obligation are both
   stated.
3. **Given** a skill that needs one of these rules, **When** it is read,
   **Then** it cites the corpus requirement rather than restating the rule.

______________________________________________________________________

### User Story 2 - An operator still finds what they need on the site (Priority: P1)

Someone running osapi opens the site and finds how to use it: what each domain
does, how to call it, what the responses mean. Nothing they relied on has
disappeared, and no page answers them with "see the specifications repository".

**Why this priority**: Equal to the first. A backfill that empties the site of
things operators use has moved a problem rather than solved one, and the damage
is invisible to the person doing the moving.

**Independent Test**: Every task in the site's usage and feature documentation
can still be completed from the site alone, and no surviving page sends an
operator to the corpus.

**Acceptance Scenarios**:

1. **Given** a page whose contributor content moved, **When** an operator opens
   its old address, **Then** they reach something useful rather than a missing
   page.
2. **Given** the site after the move, **When** an operator looks for how a
   domain behaves for them, **Then** it is still on the site.
3. **Given** a page that served both readers, **When** it is split, **Then** the
   operator's half stays and reads as a whole page rather than a remainder.

______________________________________________________________________

### User Story 3 - A rule has one home, and drift becomes impossible (Priority: P2)

A rule about how osapi is built is stated once. A reader who finds it twice
finds a citation the second time, not a copy that may already disagree.

**Why this priority**: Lower than the two above because it is the durable payoff
rather than the immediate one, but it is why moving beats copying: the provider
contract already proved a restated rule drifts, and the copy an agent happens to
load wins.

**Independent Test**: For each moved subject, exactly one statement of each rule
exists across the corpus, the site and the skills; every other mention is a
citation.

**Acceptance Scenarios**:

1. **Given** a moved rule, **When** the site, the corpus and the skills are
   searched, **Then** one statement and any number of citations are found.
2. **Given** a citation that names a requirement, **When** the gate runs,
   **Then** a citation whose target does not exist fails the build.

### Edge Cases

- A page serves both readers in the same paragraph rather than in separate
  sections. Splitting by section will not divide it, so the specification must
  say what happens: the paragraph is rewritten for the operator and the
  contributor's half restated in the corpus, rather than the page moving
  wholesale and taking operator content with it.
- A moved page is linked from outside the repository — a README, an issue, a
  bookmark, a search result. Deleting its address breaks those silently, and the
  person who moved it will not see the breakage.
- The site and the corpus disagree during the move, because a page is moved in
  one change and its citation added in another. A reader in between finds two
  statements, which is the state this feature exists to end.
- A subject is too small to be its own specification. Four of the six candidate
  pages are under 350 lines, and one is 46; a specification per page would
  produce specifications nobody reads.
- A rule on the site is wrong, or describes behaviour the code no longer has.
  Moving it moves a falsehood into the corpus, where it carries more authority
  than it did on the site.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each candidate page MUST be classified as moving wholly,
  splitting, or staying, and the classification MUST be justified by who reads
  it rather than by where it currently sits. Evidence: the six pages named in
  the Assumptions.
- **FR-002**: Content that tells a contributor or an agent how osapi is built
  MUST end up in the corpus. Content that tells an operator how to use osapi
  MUST stay on the site.
- **FR-003**: A page that serves both readers MUST be split so that the
  operator's half is a coherent page in its own right, not the remainder left
  after the contributor's half was removed.
- **FR-004**: Moved content MUST be grouped by subject rather than by the page
  it came from, and each subject MUST be large enough to be worth a
  specification of its own. A subject too small to stand alone MUST be folded
  into a larger one rather than given its own.
- **FR-005**: The job system MUST be the first subject moved, because it is the
  largest body of contributor knowledge on the site and the one the
  `add-a-domain` skill leans on most.
- **FR-006**: No page address that exists before this feature MUST 404 after it.
  The specification MUST state, per moved page, whether its address keeps a
  user-facing page or redirects, and why that choice fits that page.
- **FR-007**: A skill that needs a moved rule MUST cite the corpus requirement
  rather than restate it, following the pattern the provider contract set: a
  table mapping each rule to its requirement.
- **FR-008**: After a subject moves, exactly one statement of each of its rules
  MUST exist across the corpus, the site and the skills. Every other mention
  MUST be a citation.
- **FR-009**: A moved rule MUST be checked against the code before it is written
  into the corpus, and a rule the code does not match MUST be recorded as a gap
  rather than restated as though it held.
- **FR-010**: Each subject MUST move in a single change that moves the content,
  updates the citations, and leaves the page's address resolving — so no state
  exists where a reader can find two disagreeing statements of the same rule.
- **FR-011**: The corpus statement of a moved rule MUST cite the code it
  describes, so a reader can check the rule rather than trust it.
- **FR-012**: The published site MUST NOT send an operator to the corpus. A
  citation is for contributors and agents; an operator page that answers with
  "see the specifications repository" has lost them.

### Key Entities

- **Candidate page**: A page on the published site holding contributor or agent
  knowledge. Six are identified, totalling 1,898 lines.
- **Subject**: A body of related knowledge that becomes one corpus specification
  — the job system, for example — independent of which pages it came from.
- **Citation**: A reference from a skill or a page to a corpus requirement,
  replacing a restatement. Validated by the gate: a citation whose target does
  not exist fails the build.
- **Reader**: Either an operator, who uses osapi, or a contributor or agent, who
  changes it. Every classification decision turns on which one is being served.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A contributor with no prior knowledge can state how work reaches
  an agent, what delivery guarantees hold, and what a retry must not cause,
  using the corpus alone.
- **SC-002**: Every task in the site's usage and feature documentation can still
  be completed from the site alone, and no surviving page refers an operator to
  the corpus.
- **SC-003**: No address that resolved before this feature fails to resolve
  after it.
- **SC-004**: For every moved subject, one statement of each rule exists and
  every other mention is a citation.
- **SC-005**: The `add-a-domain` skill shrinks, and what remains is routing plus
  citations rather than restated mechanics — the same outcome the provider
  contract produced for its provider reference.
- **SC-006**: Every rule moved into the corpus cites the code it describes, and
  any rule the code does not match is recorded as a gap rather than stated as
  fact.

## Assumptions

- The six candidate pages are `development/adding-an-api-domain.md` (654 lines),
  `architecture/job-architecture.md` (630),
  `architecture/system-architecture.md` (330), `architecture/architecture.md`
  (204), `architecture/api-guidelines.md` (61) and `architecture/principles.md`
  (46), totalling 1,925 of the site's 16,938 lines. The remaining 15,013 lines —
  thirty feature pages, the usage and SDK documentation — are user-facing and
  out of scope.

  **Corrected 2026-09-28.** Three of this feature's own records were wrong, and
  each was found by the work rather than by re-reading this file. They are
  corrected here, ahead of archival, because a specification archived with wrong
  inventories records the error as knowledge.

  | This said                                 | It is     | Found by                                                                                                                                                             |
  | ----------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | `job-architecture.md` is 603 lines        | **630**   | Subject A's research. The page grew by an Error Handling section added while closing the September review — the newest and most precise contributor knowledge on it. |
  | `api-guidelines.md` holds five guidelines | **six**   | Subject B, verifying before writing. The sixth is path-versus-query parameters.                                                                                      |
  | `principles.md` holds five principles     | **eight** | Subject B. The three never named are Reliability and Stability, CLI Parity with API, and Least Privilege Mode.                                                       |

  The pattern in the last two is worth naming, because it is the argument for
  FR-009. **Every line count in this list was right**; both pages are exactly as
  long as recorded. What was wrong was the count of *items inside* two of them,
  which was taken from reading about the pages rather than from the pages. A
  measurement is evidence and a recollection is not, which is why FR-009
  requires each requirement checked against the repository before it is written
  rather than transcribed from prose.

- The thirty feature pages stay where they are. Each describes what a domain
  does for an operator, which is the site's job.

- Not every candidate page moves. The classification in FR-001 is the work, and
  the answer for at least one page is expected to be "stays" or "splits" rather
  than "moves".

- No Go code changes. This moves and cites prose.

- The site is formatted by Prettier and checked by a site formatting gate that
  runs with the tests rather than with the pre-commit checks; the corpus is
  formatted by a Markdown formatter that excludes the skills directory; and the
  skills are validated by a checker that resolves every relative link. A
  citation into the corpus that does not resolve therefore fails the build,
  which is what makes FR-008 enforceable rather than aspirational.

- The provider contract is the precedent for how this is done: its rules live in
  the corpus and its skill reference cites them, which cut that reference from
  171 lines to 127.

- Which subjects the moved content becomes is decided during planning, not here.
  This specification requires grouping by subject and names the first one; it
  does not enumerate the rest, because that decision needs the pages read in
  full.
