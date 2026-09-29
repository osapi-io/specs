# Quickstart: verifying the move

**Feature**: `005-building-a-domain` | **Date**: 2026-09-28

Phase 1. Every check below is a command or a fixed procedure, not an instruction
to look. A check somebody has to interpret is one that passes when they are
tired.

## Prerequisites

Both repositories cloned as siblings, and `mise` used to invoke tools:

```bash
cd ~/git/osapi-io && ls -d specs osapi
```

## SC-004 — the corpus statement holds together

```bash
cd specs && mise exec -- just test
```

Runs mdformat, just-fmt and `scripts/validate-skills.py`. The last is the one
that matters: it resolves every relative link in the skill's references. A
citation at the wrong depth fails **by name** — three `../` levels lands in
`.claude/` and the message says which file and which path, which is how the
four-level rule came to be recorded.

## SC-002 — every removed address still resolves

Two pages are deleted. After the osapi change:

```bash
cd osapi && mise exec -- just docusaurus-build
grep -A3 "createRedirects\|redirects:" docs/docusaurus.config.ts
```

The build fails on a link to a missing page, which covers the internal links.
The grep confirms both addresses are listed as redirects rather than only one:

| Address                                | Redirects to         |
| -------------------------------------- | -------------------- |
| `/sidebar/architecture/api-guidelines` | the contributor page |
| `/sidebar/architecture/principles`     | the contributor page |

Then confirm no link to either survives anywhere:

```bash
cd osapi && grep -rn "api-guidelines\|principles" docs/docs docs/docusaurus.config.ts | grep -v redirect
```

Expected: nothing outside the redirect configuration. `system-architecture.md`'s
Further Reading list is the known offender — it links both pages today.

## SC-003 — no operator page points into the corpus

```bash
cd osapi && grep -rn "osapi-io/specs" docs/docs | grep -v "development/adding-an-api-domain.md"
```

Expected: nothing. The contributor page is the single exception and its reader
is a contributor, which is why it is excluded by name rather than by judgement.

## SC-005 — the rule is stated once

```bash
cd specs && grep -rn "MaxDeliver\|IsBroadcastTarget\|x-oapi-codegen-extra-tags\|StrictServerInterface" .claude/skills/add-a-domain/
```

Expected: each appears inside a citation row naming a requirement, never inside
a paragraph explaining the mechanism. A reference that explains how validation
tags work is a second statement, whatever it links to.

## SC-006 — the check that matters most

```bash
cd osapi && git log -1 --format=%cI -- docs/docs/sidebar/development/adding-an-api-domain.md
cd ../specs && gh pr view <the 005 spec PR> --json mergedAt -q .mergedAt
```

The page's last commit must postdate the specification's merge. If it does not,
the corpus and the site both state these rules and this feature is unfinished
whatever the corpus says. This is the check Subject A ran as its T016, and it is
the one that distinguishes a finished backfill from a corpus with a duplicate.

## SC-001 — the reading

Not a command. The procedure, from [research.md](research.md) Decision 5:

Give a reader **only** `components/osapi/specs/005-building-a-domain/spec.md` —
no repository, no site, no other specification, no session context — and an
explicit instruction not to answer from general knowledge of Go, REST or
OpenAPI. Ask the four questions, and ask for ANSWERABLE or NOT ANSWERABLE on
each with the requirements used:

1. What does a domain consist of, and how would I know one was incomplete?
2. What must be built before what, and which of those orderings is forced?
3. Where does user input get validated, and what happens to a path parameter?
4. What must be true of an operation that targets more than one machine?

A person is preferred. A fresh agent is the fallback that makes this runnable
rather than aspirational.

**What a pass proves, and what it does not.** It proves the answers are in the
text rather than in the author's head. It does not prove a person would succeed:
an agent reads more literally, does not skim, and does not stop at a heading and
guess. Necessary, not sufficient — and Subject A's reading is the evidence it is
worth running anyway, since it found two real gaps the author had read past
twice.

## Definition of done

| #      | Check                          | Passes when                                      |
| ------ | ------------------------------ | ------------------------------------------------ |
| SC-001 | The reading                    | Four questions ANSWERABLE from `spec.md` alone   |
| SC-002 | Addresses resolve              | Both redirects present; build green              |
| SC-003 | No operator sent to the corpus | grep returns nothing but the contributor page    |
| SC-004 | `just test` in specs           | Green, `skill-lint` resolving every citation     |
| SC-005 | One statement per rule         | No mechanism explained in the skill's references |
| SC-006 | The page postdates the spec    | `git log` timestamp is later than the merge      |
