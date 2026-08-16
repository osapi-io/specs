## Context

`go-code-standards` holds seven requirements. Two are policy no tool can check:
mocks are generated, and a test does not re-cover behavior through an exported
alias. Five state source formatting that `gofumpt`, `golines`, `goimports`,
`wrapcheck`, and `revive` already produce or reject.

The five repositories carrying Go code sit in three states. `osapi` and `gohai`
point at the capability without restating it. `nats-client` and `nats-server`
restate it under `Code style`. `osapi-orchestrator` has a removal open and held.
The conversion that produced this spread is half-finished, which is why the
question is worth settling now rather than after two more repositories move.

`osapi-justfiles` already distributes shared recipes: a consumer runs
`just fetch`, files land in `.just/remote/`, and `.gitignore` keeps them
untracked. The `justfiles` capability records this under "Recipes are
distributed as fetched files" and "Fetched files are not linted". A second kind
of shared content needs no new mechanism.

## Goals / Non-Goals

**Goals:**

- Keep in the corpus only what the corpus is for — decisions binding several
  repositories that no tool reports on.
- Leave every rule in force. Nothing here relaxes a convention; each moves to
  whichever of three homes can actually hold it.
- Let a repository be read on its own, by a person offline or an agent with one
  checkout.

**Non-Goals:**

- Changing any convention. Signatures still span lines, imports stay grouped,
  suites keep their names.
- Rewriting `.golangci.yml` to unify the per-repository exclusions. Those
  differences are legitimate and this change does not touch them.
- Deciding what `osapi-justfiles` names the fragment or which recipe fetches it.
  That is applying, not deciding.

## Decisions

### Three homes, chosen by what can hold a rule

A rule goes to the corpus if it is a decision with consequences and no tool
reports on it; to tool configuration if a tool can enforce it; to the shared
`CONTRIBUTING.md` fragment otherwise.

*Alternative: keep all seven in the corpus and add worked examples.* Rejected
after starting it. Adding Go snippets to a requirement makes it unambiguously
about implementation, which `config.yaml` says a requirement is not. It treats
the symptom — the capability is hard to apply without an example — while making
the category error harder to see.

*Alternative: move all seven out and retire the capability.* Rejected. "Mocks
are generated" is exactly what a cross-repository corpus is for: it is a
decision, it has a stated failure mode, no linter checks it, and three
repositories currently violate it. Retiring the capability would delete the two
requirements worth having.

### Distribute the fragment rather than point at the corpus

Each repository holds the shared conventions on disk, fetched from one source,
rather than naming a capability in another repository.

The failure that motivated this is recorded: `gohai` merged its removal while
`go-code-standards` existed only inside an unarchived change. For that period
the rules were stated once and that place was unreachable — a reader following
the pointer to `openspec/specs/` found nothing. A pointer is only as good as
what it resolves to, and it resolves across a repository boundary, over a
network, for every reader.

*Alternative: keep the pointer and deep-link the file.* Rejected as
insufficient. It fixes findability for a person with a browser and leaves the
offline reader and the single-checkout agent with a link they cannot follow.

*Alternative: git submodule for the corpus.* Rejected. It puts the whole spec
repository into every consumer to deliver one document, and submodules pin a
revision that then needs its own bumping.

### Configuration is the statement for anything a tool checks

Where `.golangci.yml` or a formatter decides a rule, documentation names where
the configuration lives instead of reproducing it.

The failure is already on disk. Every Go repository's `CONTRIBUTING.md` lists
"errcheck, errname, goimports, govet, prealloc, predeclared, revive,
staticcheck". Each `.golangci.yml` enables `unused`, which no prose mentions,
and puts `goimports` under `formatters` rather than among the linters. One stale
approximation, copied five times, of a file sitting beside it.

*Alternative: keep the prose list and add a check comparing it to the config.*
Rejected. Building a checker to keep a document honest about a file it
duplicates is more machinery than deleting the duplicate.

### The capability keeps its name and path

`go-code-standards` narrows rather than being renamed or split.

*Alternative: rename to `go-testing-policy` to match what survives.* Rejected.
Five repositories reference the name today, a rename invalidates every one of
them, and the capability may legitimately regain non-lintable Go policy later.

### Mocks gains a scenario rather than an exception

The `Mocks are generated` requirement is modified to say that a double carrying
a real implementation is not a mock.

Applying task 3.4 turned up three hand-written doubles. `gohai`'s
`fakeCollector` and `osapi-orchestrator`'s `mockRenderer` are scripted stand-ins
and do violate the rule. `osapi`'s `mockPKISigner` signs with a genuinely
generated ed25519 key pair — replacing it with a generated mock would swap
working cryptography for a canned return. The requirement did not distinguish
these, so applying it produced a finding against a test that is correct.

*Alternative: leave the requirement and record `mockPKISigner` as an accepted
exception.* Rejected. An exception recorded outside the requirement is invisible
at the point anyone reads the rule, and the next reviewer raises it again.

## Risks / Trade-offs

- **The fragment is fetched, so a repository read on GitHub shows a pointer
  rather than the conventions.** → The fetch mechanism already carries this
  trade-off for recipes and it is accepted there. What a browser reader loses is
  smaller than what an offline reader and a single-checkout agent gain, and the
  fragment is one fetch away rather than one repository away.

- **Two homes for Go conventions means a contributor must know which holds
  what.** → The split follows a line a contributor can apply without being told:
  if a tool rejects it, it is configuration; if a reviewer rejects it, it is
  written down.

- **Removing five requirements shrinks the corpus while the behavior
  capabilities queued elsewhere have not arrived, making it look emptier.** →
  The corpus is measured by what it governs, not its length. Five requirements
  restating a formatter make it longer without making it say more.

- **`gohai` is on `main` today with its conventions removed.** → Syncing the
  capability into the corpus already restored a reachable answer. This change
  determines what returns to the repository, and until it lands `gohai` is
  covered by the synced capability rather than by nothing.

- **`osapi-justfiles` becomes a dependency for reading a repository's
  conventions.** → It already is, for building and testing one. A repository
  that cannot fetch cannot run its checks either, so this adds no new failure
  mode.
