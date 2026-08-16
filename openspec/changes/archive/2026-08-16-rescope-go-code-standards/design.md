## Context

`repo-standards` fixes the opening and closing sections of `CONTRIBUTING.md` and
says of the rest: "The middle varies by repository, because what a contributor
needs to know differs." That sentence is why the five Go repositories disagree.
What a contributor needs to know does differ between a collector library and a
REST service — but not about function signatures, and the free middle allowed
the common part to drift along with the specific part.

`go-code-standards` holds seven requirements. Two are policy no tool reports on.
Five state source formatting that `gofumpt`, `golines`, `goimports`,
`wrapcheck`, and `revive` already produce or reject.

Neither capability was in `openspec/specs/` when repositories began citing them.
`go-code-standards` was synced in osapi-io/specs#88. `repo-standards` is still
inside two unarchived changes, so a delta against it has nothing to land on
until it is synced too.

## Goals / Non-Goals

**Goals:**

- Make the five Go repositories' `CONTRIBUTING.md` files structurally identical
  where their subject is identical.
- Keep every convention in force, readable inside the repository it binds.
- Leave in the corpus only what the corpus is for.

**Non-Goals:**

- Changing any convention. Signatures still span lines, imports stay grouped,
  suites keep their names. This moves rules and standardizes headings; it does
  not relax anything.
- Unifying the per-repository `.golangci.yml` exclusions. Those differences are
  legitimate.
- Making the repository-specific sections uniform. A collector guide and an API
  domain walkthrough should not be forced into a shared shape.

## Decisions

### Committed copies, not a fetched fragment

Each repository holds the shared conventions as committed text, identical across
the five.

*Alternative: distribute a fragment through `just fetch`, the way shared recipes
already arrive.* Rejected. It gives one source that cannot drift, but the file
is incomplete until fetched: `CONTRIBUTING.md` renders on GitHub as a
placeholder, and a reviewer reading a pull request in a browser sees nothing.
The mechanism suits recipes, which are executed rather than read, and suits
documentation badly for the same reason.

*Alternative: keep the pointer to the corpus.* Rejected — this is what produced
the failure. A pointer resolves across a repository boundary over a network, for
every reader, and `gohai` spent a period pointing at a capability that was not
there.

The cost is accepted deliberately: five copies drift unless someone notices.
That is what the structure requirement is for — identical headings make a
diverging body visible, where free-form sections hid it.

### Fix the middle rather than describe it

The middle becomes a named, ordered set with repository-specific sections placed
after `Testing`.

*Alternative: require only that shared conventions live under `Code standards`,
leaving order free.* Rejected as too weak to catch what actually went wrong. The
NATS pair put signatures under `Code style`, `gohai` put `Go Patterns` beneath
`Testing`, and three of five had no `Code standards` at all. Naming the sections
without fixing their order leaves a reader comparing two files by search rather
than by position.

### Sentence case, stated as its own requirement

*Alternative: leave casing to the formatter.* Rejected — `mdformat` does not
touch heading case, so nothing would enforce it. It is a small rule, but it is
the difference a reader sees first, and it is currently wrong in three
repositories.

### `go-code-standards` narrows rather than being retired

*Alternative: retire it and move all seven requirements into `CONTRIBUTING.md`.*
Rejected. "Mocks are generated" is what a cross-repository corpus is for: a
decision, with a stated failure mode, that no linter checks and that three
repositories currently violate. Retiring it would delete the two requirements
worth having.

*Alternative: keep all seven and add worked code examples.* Rejected after
starting it. A requirement containing a Go snippet is unambiguously about
implementation, which is what `config.yaml` says a requirement is not. It treats
the symptom — the capability is hard to apply without an example — while making
the category error harder to see. The examples belong in `CONTRIBUTING.md`,
beside the command that applies them.

### The capability keeps its name and path

*Alternative: rename to match what survives.* Rejected. Five repositories cite
the name, a rename invalidates every citation, and the capability may
legitimately regain non-lintable Go policy later.

### Mocks gains a scenario rather than an exception

Applying the mocking requirement turned up three hand-written doubles. `gohai`'s
`fakeCollector` and `osapi-orchestrator`'s `mockRenderer` are scripted stand-ins
and do violate it. `osapi`'s `mockPKISigner` signs with a genuinely generated
ed25519 key pair — replacing it with a generated mock would swap working
cryptography for a canned return. The requirement did not distinguish these, so
applying it produced a finding against a correct test.

*Alternative: record `mockPKISigner` as an accepted exception outside the
requirement.* Rejected. An exception recorded elsewhere is invisible where the
rule is read, and the next reviewer raises it again.

## Risks / Trade-offs

- **Five committed copies drift.** → Identical structure is what makes drift
  reviewable: when every file carries the same headings in the same order, a
  body that differs shows up in a side-by-side read. The free middle is what let
  the current divergence go unnoticed.

- **A shared convention now needs five pull requests to change.** → It needed
  five before; the difference is that they were not kept in step. The
  requirement that repositories state a common convention identically makes the
  omission a defect rather than an oversight.

- **Fixing the middle constrains repositories whose subject genuinely differs.**
  → Only the common sections are fixed. Anything a repository invents for itself
  keeps its own name and sits after `Testing`, which is where `gohai`'s
  collector guide and `osapi`'s domain walkthrough already are.

- **`repo-standards` is not in the corpus, so this change cannot be archived
  until it is.** → Syncing it is task 1.5, ahead of any repository work, and the
  same step was already taken for `go-code-standards`.

- **`gohai` sits on `main` with its conventions removed while this is
  reviewed.** → It is first in the apply order. Until then it is covered by the
  synced capability rather than by nothing.
