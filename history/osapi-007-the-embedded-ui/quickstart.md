# Quickstart: verifying the move

**Feature**: `007-the-embedded-ui` | **Date**: 2026-09-29

Phase 1. Four of these are commands. The two that matter most are not, and this
file says so rather than letting a green build stand in for them.

## Prerequisites

```bash
cd ~/git/osapi-io && ls -d specs osapi
```

## SC-006 — the gates

```bash
cd specs && mise exec -- just test
cd ../osapi && mise exec -- just docusaurus-fmt-check && mise exec -- just docusaurus-build
```

The site build fails on a link left pointing at removed content, which is what
catches a cross-reference into a moved section. It does **not** catch a page
that reads as a remainder; that is review.

## SC-002 — one statement, not three

The check the whole feature exists for.

```bash
cd ~/git/osapi-io && grep -rniE "react 19|tailwind|class-variance|orval" \
  osapi/docs/docs osapi/ui/docs specs/components/osapi 2>/dev/null | grep -v node_modules
```

Expected: hits in the corpus statement, and **nothing** in `osapi/ui/docs` or
under `osapi/docs/docs`. The stack is the sharpest probe because it is the
section both former copies held and neither needed.

```bash
cd ~/git/osapi-io && grep -rn "Embedding Mechanism\|Component Architecture\|Fetch mutator" \
  osapi/docs/docs osapi/ui/docs 2>/dev/null
```

Expected: nothing. Those three headings are the moved half by name.

## SC-004 — the pointer is a pointer

```bash
cd ~/git/osapi-io/osapi && wc -l ui/docs/architecture.md
```

Expected: under 10. If this grows later, it has stopped being a pointer and the
programme has two statements again — which is why the file says so in its own
text.

## SC-003 — the surviving page is an operator's page

```bash
cd ~/git/osapi-io/osapi && grep -E "^## " docs/docs/sidebar/architecture/ui.md
```

Expected exactly: `## Configuration`, `## Authentication & Authorization`,
`## Pages`. Three headings, and none of the six that moved.

Then read it. The command proves the sections; only a reader proves it holds
together. The introduction is the part most likely to be wrong, because it
currently introduces a contributor's document and deletion alone will not fix
that.

## SC-007 — no Go changed

```bash
cd ~/git/osapi-io/osapi && git diff --stat main | grep -vE "\.md" || echo "markdown only"
```

Expected: `markdown only`.

## SC-001 — the reading

Not a command, and the one that answers whether the corpus statement is any
good.

Give a reader who has seen neither UI page the corpus statement alone — no
repository, no site, no session context — and three questions:

1. How does the UI reach a user's browser?
2. Where does a new component go?
3. What does the UI verify about a token?

Each would mislead a contributor if unanswered. The first invites assuming a
separate deployment. The second is the boundary a new file is placed against.
The third is the one to watch: the client decodes the token and does **not**
verify it, and a reader who learned only "decodes" would take that for a check.

**What a pass proves.** That the answers are in the text. Not that a person
would enjoy finding them, and an agent is more patient than a contributor
mid-task. Every reading in this repository has carried that caveat and found
real gaps anyway.

## SC-005 — the divergence survived being resolved

```bash
cd specs && grep -c "Feature flags\|Embedding Mechanism\|Configuration" \
  components/osapi/specs/007-the-embedded-ui/spec.md
```

All three unshared sections must appear in the corpus statement. The point is
not that they are mentioned but that **none was lost to the merge**:
`Feature flags` came from the copy beside the code, the other two from the site
page, and a merge that picked either copy as authoritative would have dropped
one or two of them.

## Definition of done

| #      | Check           | Passes when                                             |
| ------ | --------------- | ------------------------------------------------------- |
| SC-001 | The reading     | Three questions answered from the corpus alone          |
| SC-002 | One statement   | Stack and moved headings appear only in the corpus      |
| SC-003 | Operator's page | Three headings, and it reads as a whole                 |
| SC-004 | The pointer     | Under 10 lines                                          |
| SC-005 | Union preserved | All three unshared sections present                     |
| SC-006 | Gates           | `just test`, `docusaurus-fmt-check`, `docusaurus-build` |
| SC-007 | No code         | Diff is markdown only                                   |
