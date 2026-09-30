# Data Model: The embedded UI

**Feature**: `007-the-embedded-ui` | **Date**: 2026-09-29

Phase 1. Three documents, three dispositions. The line ranges live in
[plan.md](plan.md); what replaces each file lives here, concretely enough that
implementation invents nothing.

## The three documents

| Document                                          | Now       | After         | Disposition                   |
| ------------------------------------------------- | --------- | ------------- | ----------------------------- |
| `docs/docs/sidebar/architecture/ui.md`            | 264 lines | 80            | Split — operator's half stays |
| `docs/docs/sidebar/development/ui-development.md` | 200 lines | a short index | Moves entire                  |
| `ui/docs/architecture.md`                         | 263 lines | under 10      | Replaced by a pointer         |

## What the surviving site page contains

`architecture/ui.md`, about 80 lines, four parts and no fifth:

**The introduction**, one sentence of editing. It currently introduces a
contributor's document; afterwards it introduces an operator's, and says where
the architecture went.

**`## Configuration`** unchanged — `controller.ui.enabled`, its default, and
that the UI shares the API's host and port so there is no additional network
configuration.

**`## Authentication & Authorization`**, its opening and the RBAC model. The
opening names the shared JWT; the model names three built-in roles and the
`resource:verb` permission shape. The auth *flow* goes, because how the client
handles a token is not something an operator acts on.

**`## Pages`** unchanged — Dashboard, Configure, Roles, Enrollment, SignIn, and
what each shows.

What it must **not** contain afterwards: the stack, the component kinds, the
embedding mechanism, the application structure, SDK generation, or the auth
flow. Those are the 184 lines that move.

## What the contributor index contains

`development/ui-development.md`, replaced. Three parts, the shape
`adding-an-api-domain.md` took:

1. **What developing the UI involves** — under ten lines of prose. Names that
   the UI is a React SPA embedded in the controller binary, that its client is
   generated, and that its conventions are stated in the corpus.
2. **A citation table** into this feature's requirements, by absolute GitHub
   address, because the corpus is a separate repository and is not published as
   part of the site. One sentence says so, as the domain index does.
3. **A pointer to the justfile** for the commands, rather than the commands.
   FR-009 and `global/documentation`: a rule a tool enforces is not restated as
   prose.

## What the pointer contains

`ui/docs/architecture.md`, under ten lines. It says what it is, where the
statement lives, and — explicitly — that it is a pointer rather than a summary,
so the next person to open it does not start adding paragraphs.

```markdown
# Architecture

The UI's architecture is stated in the osapi-io specifications repository, not here:
<absolute link to 007's spec>

This file is a pointer, not a summary. It exists because a contributor working in `ui/`
looks for architecture beside the code, and an absent file sends them searching. Adding
an account of the architecture here would put it in two places again, which is what the
statement above replaced.
```

That last paragraph is the guard [research.md](research.md) Decision 2 names: a
pointer is a file somebody can edit back into a document, and the only thing
preventing it is the file saying so.

## The corpus statement

This feature's `spec.md`, archived into `.specify/memory/` like every other
feature's. No new subject file, and no `add-a-domain` reference — FR-017 and
[research.md](research.md) Decision 4.

Where it reaches osapi's permission model it cites rather than restates, because
`resource:verb` and the three roles are osapi's and already stated. Where it
reaches the generated client it cites [005](../005-building-a-domain/spec.md)'s
account of the combined specification, since the UI generates from the same
file.

## Entities

- **Site page**: a published page, classified by who reads it. Two are affected.
- **Pointer**: a file kept for its location rather than its content. One, and
  the programme's only.
- **Unshared section**: a section one former copy held and the other did not.
  Three, all carried forward.
