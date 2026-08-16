## Context

`osapi` publishes a Go SDK at `pkg/sdk/client`. `osapi-orchestrator` consumes it
by pinned version — every operation it exposes is an SDK call, and its
`internal/engine` and `pkg/orchestrator` packages import it directly.

The rules governing that SDK live in `osapi`:

| Rule                                     | Stated in                             |
| ---------------------------------------- | ------------------------------------- |
| Method names are clean verbs             | `CLAUDE.md`                           |
| No generated type in a public signature  | `docs/docs/sidebar/sdk/guidelines.md` |
| JSON tags on every exported result field | `docs/docs/sidebar/sdk/guidelines.md` |
| Errors wrapped, nil bodies guarded       | `docs/docs/sidebar/sdk/guidelines.md` |

Both documents are addressed to people working inside `osapi`. Neither is
visible to the repository that depends on them.

## Goals / Non-Goals

**Goals.** Record what the SDK guarantees, so a consumer can read the contract
rather than infer it.

**Non-Goals.** Changing the SDK. The rules already hold — this records them.

## Decisions

### Recording, not correcting

Every rule was checked against the code before being written down:

- No service method repeats its service name.
- No public method signature contains a `gen` type. Generated types appear only
  inside method bodies, where they are constructed from SDK types.
- No exported field on a result type lacks a `json` tag.
- `osapi-orchestrator` never imports the generated package.

A requirement written from documentation alone records what someone intended. A
requirement checked against the code records what is true.

*Alternative considered:* write the requirements from the two documents and
verify afterwards. Rejected — the verification is what distinguishes a rule that
holds from one that was aspirational, and doing it first meant the requirement
could be phrased around what the code actually does.

### The tags are load-bearing

`JSON tags required` reads like style until you find what depends on it: results
are converted to generic maps by marshalling to JSON and unmarshalling into a
map. An untagged field arrives under its Go name — `Hostname` rather than
`hostname` — which does not match the key the API returned, so the lookup misses
and the value is silently absent.

The requirement states that dependency, because a rule whose reason is invisible
is one a future contributor will relax.

### `omitempty` is a semantic choice

The distinction the requirement draws is between a field whose absence carries
meaning and one whose value must always be readable. `Changed` is the example
that matters: omitted when false, a consumer cannot distinguish "this mutation
changed nothing" from "this SDK version does not report changes".

*Alternative considered:* require `omitempty` on all optional fields and leave
it there. Rejected — that is a rule about pointers and slices, and it misses the
case the SDK actually gets wrong.

### Scope stops at the SDK boundary

This capability covers what `pkg/sdk` guarantees its consumers. It does not
cover how the API those methods call is designed, how a provider behaves when
one runs, or how Go is written across the organization. Those are separate
capabilities with separate readers.

*Alternative considered:* one capability covering the SDK and the API it wraps.
Rejected — the SDK's audience is a consuming repository, and the API's audience
is someone adding an endpoint. A capability serving both would be read by
neither.

## Risks / Trade-offs

- **A recorded rule is harder to change than an undocumented one.** That is the
  intent: the SDK has a consumer, and a contract that can be changed without
  noticing is what breaks it.
- **The five resource verbs may not fit a future operation.** The requirement
  allows an action verb where none of the five describes the operation, rather
  than forcing a bad fit.

## Migration Plan

None. The rules hold; this records them. The two source documents stay in place
and point at the capability.

## Open Questions

- Should `osapi-orchestrator` state that it consumes this contract? It would
  make the dependency visible from the consumer's side, but every repository
  naming the capabilities it depends on is a larger convention than this change
  should introduce.
