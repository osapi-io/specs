# Research: Repository inventory

**Phase 0** | **Date**: 2026-09-02

The spec carried no `NEEDS CLARIFICATION` markers into planning. What follows
are the decisions the plan depends on, each with the measurement behind it.

## Decision 1: One manifest, in `osapi-io/.github`, at the repository root

**Decision**: A single `repos.json` at the root of the `osapi-io/.github`
repository, listing all eight repositories.

**Rationale**: `gh reposync`'s documented model is one manifest per organization
committed to that organization's `.github` repository. Its config discovery
checks `--config`, then `$GH_REPOSYNC_CONFIG`, then `./repos.json`, then
`./.github/repos.json` — so the root is found first and needs no flag. Putting a
`.github/` directory inside the repository named `.github` reads as an error.

**Alternatives considered**: Keeping per-repository manifests, which is the
status quo and leaves nothing enumerating the organization — the gap this
feature exists to close. A hybrid of per-repository manifests plus a separate
index, rejected because it creates a second document describing repositories,
which FR-002 forbids and which would need its own reconciliation.

## Decision 2: The merge is mechanical

**Decision**: The merged manifest is one shared `settings` / `security` /
`branch_protection` block plus one `repos[]` entry per repository, each carrying
only `name`, `description` and `topics`.

**Rationale**: Measured — the three shared blocks are identical across all seven
existing manifests:

```bash
for f in ~/git/osapi-io/{gohai,nats-client,nats-server,osapi,osapi-orchestrator,osapi-justfiles,specs}/.github/repos.json; do
  jq -S -c '{settings,security,branch_protection}' "$f"
done | sort -u | wc -l
# => 1
```

This matters because `gh reposync`'s schema applies those blocks to every
repository and offers no per-repository override. Consolidation is only possible
because the values already agree. If a repository later needs different branch
protection, the manifest cannot express it and the tool would need to change.

**Alternatives considered**: None viable. The schema does not support per-repo
overrides for these blocks.

## Decision 3: Include the `.github` repository itself

**Decision**: `osapi-io/.github` is the eighth entry in its own manifest.

**Rationale**: It is a real, public, non-archived repository with a description
and a topic, and it is already protected identically to the shared block:

```
.github  enforce_admins=true strict=true reviews=0 conv=true force=false del=false block=true restrictions=1
gohai    enforce_admins=true strict=true reviews=0 conv=true force=false del=false block=true restrictions=1
```

Including it therefore introduces no drift, and leaving it out would mean the
one file that lists the organization's repositories omits the repository it
lives in.

## Decision 4: Archived repositories are excluded, not marked

**Decision**: `osapi-ui`, `osapi-sdk` and `osapi-io-taskfiles` are absent from
the manifest. Absence is what marks a repository as unmanaged.

**Rationale**: `gh reposync`'s schema has no concept of an archived repository —
a repository is in `repos[]` or it is not. Listing them would make `--check`
attempt to read them, and at least one cannot be read at all:

```
gh api repos/osapi-io/osapi-ui/branches/main/protection
# => 403 Upgrade to GitHub Pro or make this repository public
```

`osapi-ui` carries a manifest today; it is deleted with the rest rather than
merged in.

**Alternatives considered**: Adding an `archived` flag, which would require
changing `gh-reposync`. Out of scope, and the tool is not this feature's to
change.

## Decision 5: The rule goes in a charter fragment, not `constitution.md`

**Decision**: A new fragment at `.charter/fragments/global/repositories.md`,
added to `system/.specify/charter/state.yml`, then recomposed.

**Rationale**: `constitution.md` is generated. Its section markers
(`<!-- [F] global/documentation SECTION -->`) show it is assembled from the five
fragments listed in `state.yml`. A direct edit is overwritten by the next
compose. The fragment lives in `.charter/`, shared across projects, because the
rule binds any work spanning repositories, not only `system`.

**Alternatives considered**: Editing `constitution.md` directly — silently
reverted on the next recompose, which is exactly the class of failure this
feature is about.

## Decision 6: Nothing runs automatically

**Decision**: `gh reposync --check` is run by hand when it matters. No scheduled
workflow, no notification, no stored credential.

**Rationale**: Automating it means a workflow on GitHub's runners, which cannot
use a developer's `gh` login. It would need a stored organization-wide token and
somewhere for failures to land. The check takes seconds by hand.

The counter-argument is real and recorded rather than dismissed: the `specs`
topic drifted because nobody ran the check for months, and the constitution says
that where a check can be automated it is automated. The judgement is that one
drifted topic in a one-person organization does not yet justify an org-wide
token. If it happens again, that is the evidence the Correction principle asks
for, and the decision gets revisited with it in hand.

**Alternatives considered**: A scheduled workflow with a fine-grained read-only
token; a GitHub App minting short-lived tokens. Both deferred, not rejected.

## Decision 7: The manifest wins the `specs` topic drift

**Decision**: Apply the manifest. GitHub gets `spec-kit`; `openspec` is dropped.

**Rationale**: osapi-io/specs#103 retired OpenSpec and replaced the topic in the
manifest. The pull request merged; the change was never applied. The manifest
records the intended state and the live topic is the stale one.
