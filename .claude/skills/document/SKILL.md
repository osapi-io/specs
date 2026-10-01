---
name: document
description: Write or change a design document in this repository. Figures out which component owns the subject, reads what already exists, writes the page in the house voice, updates the index, and runs the checks. Use when asked to document a design, write up how something works, add a page for a new subject, record a decision, correct a page that building proved wrong, or when starting work on a feature that needs designing first. Also use when asked where a subject belongs, whether a page already covers something, or to review a page against the house voice.
compatibility: Requires this repository with mise and just available. Commands run through `mise exec -- just`.
license: MIT
metadata:
  author: osapi-io
  source: https://github.com/osapi-io/specs
---

# Document

Design something by writing its page. Build it. Correct the page where building
proved it wrong. Same page all three times.

This skill covers the writing. It does not build anything.

## 1. Find out whether the page already exists

Almost always it does, and the job is an edit rather than a new file.

```bash
ls components/*/                      # every page, by component
grep -ril '<subject>' components/     # anything already covering it
```

Read the component's `README.md` and the pages it links before writing. A page
that repeats what a sibling says is the failure the one-statement rule exists to
prevent, and it is easier to cause than to notice.

## 2. Place it

Ask whether the subject is **how one repository behaves** or **an agreement two
of them must both keep**.

| Subject                                                    | Goes in                    |
| ---------------------------------------------------------- | -------------------------- |
| How one repository behaves                                 | `components/<name>/`       |
| Something two repositories must agree on                   | `ARCHITECTURE.md`          |
| A rule every repository follows                            | `CONSTITUTION.md`          |

Job retry logic is osapi's behaviour. The subject naming that osapi and
osapi-orchestrator both depend on belongs to neither, so it goes in
`ARCHITECTURE.md`. A change touching several repositories is not automatically an
agreement: if one repository's behaviour is the subject and the others consume it,
that repository owns the page.

Within a component, a new subject is a new page named for the subject,
`job-system.md`, `permissions.md`. A subject that outgrows one page becomes a
directory with its own `README.md` and pages beside it.

## 3. Work out what is true

Do not write from prose. Prose is a lead; the code is the source. The
constitution's Verification section is the rule, and it has caught real errors in
this repository more than once: a timeout documented as a fallback when it was a
ceiling, a field count of fourteen when the struct had thirteen, a role claimed to
differ by one permission when it differed by seven.

Read the code, then run something that would fail if you were wrong.

Where you state a number, state the command beside it:

```markdown
37 permissions, three built-in roles.

```sh
grep -cE '^\tPerm[A-Za-z]+ +Permission = ' pkg/sdk/client/permissions.go  # 37
```
```

`just check-counts` runs every one of those in the repository the page describes.
A command that needs the line above it to make sense fails, so each one stands
alone.

## 4. Write it

The voice: an engineer explaining a system to another engineer who has to work on
it. [references/voice.md](references/voice.md) has the specifics and the tells to
avoid.

What a page does, in order of what a reader needs:

- **What the thing is**, in one or two sentences, first.
- **What it does and how**, concretely. Name the files. Show the shape.
- **Why it is built this way**, where there was a real choice. Say what the
  tradeoff was and which side you took.
- **What will surprise somebody**, which is usually the most valuable part. A
  rule with a silent failure mode is worth more than three paragraphs of
  structure.
- **What the page does not cover**, so a gap is not mistaken for an oversight.

What never appears: requirement identifiers, "MUST", user stories, acceptance
scenarios, or commentary about the document. `just check-docs` fails on the first
four.

## 5. Link it

A page nobody links is a page nobody finds. Add a row to the component's
`README.md` table saying what question the page answers, and link siblings from
the body where a reader would want them.

Cross-component links are relative: `../gohai/collectors.md` from an osapi page,
`../../ARCHITECTURE.md` from any component page.

## 6. Check it

```bash
mise exec -- just md-fmt     # formatting, rewrites in place
mise exec -- just test       # counts, contract, links, skills
```

Then run `unslop` over what you wrote. It is not optional and it is not the same
as the checks above: `check-docs` catches em dashes and requirement labels,
`unslop` catches the prose.

The check that finds the most is a reader. Give somebody the page and nothing
else, ask them the question the page claims to answer, and fix what they could
not work out. Every time that has been run here it found something, including
four errors in pages that passed every script.

## Correcting a page

When building shows the page wrong, fix the page in its own commit, before or
alongside the fix. Say what it said, what is true, and how you found out. The
third part is the one people skip and the one worth most later.

A page that was wrong when written is different from one that went stale, and
saying which tells the next reader whether to trust the rest of it.
