## Context

See proposal.md - Why.

```
                     examples/   README Examples section
nats-client               5              yes
nats-server               4              yes
osapi-orchestrator        2              yes
gohai                     0              no
```

`gohai`'s `.gitignore` carries rules for `examples/*/*` with negations for
`.go`, `.mod`, and `.sum` — the directory was planned and never created.

## Goals / Non-Goals

**Goals**

- A reader can run something rather than only read about it.
- Examples stay compiling, because they are part of the public surface.

**Non-Goals**

- Prescribing how many examples, or what they cover. That depends on the
  library.
- Requiring examples of repositories that are not Go libraries.

## Decisions

### Require the directory, not just the README section

A README section can point anywhere — at tests, at documentation, at nothing.
Requiring `examples/` means the thing a reader runs actually exists and is
compiled by the same toolchain as the library.

*Alternative considered:* require only the README section, letting a library
satisfy it by pointing at collector docs or tests. That would let `gohai` comply
without writing anything, which is the outcome the requirement exists to
prevent.

### One example per usage shape

`nats-client`'s five examples each cover a different authentication mode or
storage pattern. That is the useful shape: a reader picks the one matching their
situation. A single example with commented-out alternatives is a tutorial, not a
runnable program.

*Alternative considered:* leave the granularity unspecified. The existing
libraries already converged on one-per-shape; recording it stops the next
library from shipping one monolithic example.

## Risks / Trade-offs

- **Examples rot.** They are separate modules and can stop compiling without
  anyone noticing. → The requirement says they are updated in the same change
  that breaks them; whether CI builds them is a separate question.

- **`gohai` needs real work.** Writing SDK usage programs is not restructuring.
  → Tracked as its own task rather than folded into a docs conversion.

## Migration Plan

`gohai` writes examples covering distinct usage shapes — collecting with
defaults, selecting specific collectors, consuming stored facts — and adds the
README section linking them.

## Open Questions

- Should CI compile the examples? Nothing currently does, so an example can
  break silently. `dependabot.yml` already tracks the example modules in
  `nats-client` and `nats-server`, which suggests they are treated as real
  modules.
