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

Design something when you write its page. Build it. Correct the page where the
build showed an error. It is the same page all three times.

This skill covers the page. It does not build anything.

## 1. Find out whether the page already exists

Almost always it does, and the job is an edit rather than a new file.

```bash
ls components/*/                      # every page, by component
grep -ril '<subject>' components/     # anything already covering it
```

Read the `README.md` of the component and the pages that it links first. The
usual failure here is two pages that state the same rule. A person who did not
read the first page always writes the second.

## 2. Place it

Ask whether the subject is **how one repository behaves** or **an agreement two
of them must both keep**.

| Subject                                                    | Goes in                    |
| ---------------------------------------------------------- | -------------------------- |
| How one repository behaves                                 | `components/<name>/`       |
| Something two repositories must agree on                   | `ARCHITECTURE.md`          |
| A rule every repository follows                            | `CONSTITUTION.md`          |

Job retry logic is the operation of osapi. osapi and osapi-orchestrator both
depend on the subject names, but neither owns them. Thus they go in
`ARCHITECTURE.md`. A change to more than one repository is not always an
agreement. If the subject is the operation of one repository, and the others use
it, that repository owns the page.

Within a component, a new subject is a new page named for the subject,
`job-system.md`, `permissions.md`. A subject that outgrows one page becomes a
directory with its own `README.md` and pages beside it.

## 3. Work out what is true

Read the code, not the existing prose. Then run something that fails if you are
wrong.

That method found three errors, all in pages that looked correct:

- a timeout that a page called a fallback, but that is a maximum
- fourteen audit fields, but the struct has thirteen
- a role that a page described as `admin` minus one permission, but that is
  minus seven

## 4. Write it

The voice: an engineer who explains a system to a different engineer who must
work on it. [references/voice.md](references/voice.md) has the details, and the
signs to avoid. Each sentence obeys Simplified Technical English. Check the page
with [ste-100](../ste-100/SKILL.md) before the `unslop` pass.

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
scenarios, or commentary about the document. `just check-docs` fails on the
first
four.

## 5. Link it

Add a row to the `README.md` of the component. The row tells what question the
page answers. Link sibling pages from the body where a reader needs them. Nobody
reads a page without links to it.

Cross-component links are relative: `../gohai/collectors.md` from an osapi page,
`../../ARCHITECTURE.md` from any component page.

## 6. Check it

```bash
mise exec -- just md-fmt     # formatting, rewrites in place
mise exec -- just test       # counts, contract, links, skills
```

Then run `unslop` over what you wrote. The scripts catch em dashes and
requirement labels; `unslop` catches the prose.

Last, give a person only the page. Ask the question that the page says it
answers. Fix what the person could not find. This test found four errors in
pages that passed each script.

## Correcting a page

When building shows the page wrong, fix the page in its own commit. Say what it
said, what is true, and how you found out. People skip the last one; it is what
makes the correction checkable.

Say whether it was wrong when written or went stale. That tells the next reader
whether to trust the rest of the page.
