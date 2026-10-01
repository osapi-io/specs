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

Read the component's `README.md` and the pages it links first. Two pages stating
the same rule is the common failure here, and the second one is always written by
somebody who did not read the first.

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

Read the code, not the existing prose. Then run something that would fail if you
were wrong.

Three errors found that way, all in pages that read as authoritative: a timeout
documented as a fallback when it is a ceiling, fourteen audit fields when the
struct has thirteen, and a role described as `admin` minus one permission when it
is minus seven.

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
it. [VOICE.md](../../../VOICE.md) has the specifics and the tells to avoid.

What a page does, in order of what a reader needs:

- **What the thing is**, in one or two sentences, first.
- **What it does and how**, concretely. Name the files. Show the shape.
- **Why it is built this way**, where there was a real choice. Say what the
  tradeoff was and which side you took.
- **What will surprise somebody.** Usually the most useful part of the page. A
  rule that fails silently matters more than a complete description of the
  package layout.
- **What the page does not cover**, so a gap is not mistaken for an oversight.

What never appears: requirement identifiers, "MUST", user stories, acceptance
scenarios, or commentary about the document. `just check-docs` fails on the first
four.

## 5. Link it

Add a row to the component's `README.md` saying what question the page answers,
and link siblings from the body where a reader would want them. An unlinked page
does not get read.

Cross-component links are relative: `../gohai/collectors.md` from an osapi page,
`../../ARCHITECTURE.md` from any component page.

## 6. Check it

```bash
mise exec -- just md-fmt     # formatting, rewrites in place
mise exec -- just test       # counts, contract, links, skills
```

Then run `unslop` over what you wrote. The scripts catch em dashes and
requirement labels; `unslop` catches the prose.

Last, give somebody the page and nothing else and ask them the question it claims
to answer. Fix what they could not work out. That has found four errors in pages
that passed every script.

## Correcting a page

When building shows the page wrong, fix the page in its own commit. Say what it
said, what is true, and how you found out. People skip the last one; it is what
makes the correction checkable.

Say whether it was wrong when written or went stale. That tells the next reader
whether to trust the rest of the page.
