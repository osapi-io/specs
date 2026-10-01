# API layer

Four things: the OpenAPI spec, the handlers, the registration, and one line of
startup wiring.

Node-targeted domains live under `internal/controller/api/node/{domain}/`,
controller-only domains directly under `internal/controller/api/{domain}/`.

## The rules are in the corpus, not here

Every rule this layer obeys is stated in
[005-building-a-domain](../../../../components/osapi/domains.md).
Read it before writing an endpoint. This file holds only what that specification
does not: where the files go, what they are called, and the scaffolding to start
from.

The split is deliberate. A rule restated here would drift from the one in the
corpus, and the copy an agent happened to load would win — which is the failure
[003-corpus-backfill](../../../../CONSTITUTION.md)
exists to end.

| What you need to know | Where |
| --- | --- |
| The spec is the source of truth for validation, and the three places a tag goes | FR-011 |
| Path parameters are the trap, and what actually validates one | FR-012 |
| Separate verbs for create and update, and why a combined upsert is forbidden | FR-013 |
| The six API design guidelines, including path versus query parameters | FR-014 |
| What `{hostname}` accepts — a literal, `_any`, `_all`, a label selector | FR-015 |
| Broadcast is mandatory, and both paths return the same collection shape | FR-016 |
| The job client has four methods, and an operation adds none | FR-017 |
| `Handler()` returns route closures, and the `Server` struct does not change | FR-018 |
| What verifies a finished domain, and what Step 8 alone misses | FR-024 |

What a caller sees when an agent does not answer is the job system's, not this
layer's:
[004-job-system](../../../../components/osapi/job-system.md)
FR-019 for the four per-host statuses and FR-016 for the two clocks. Domain code
does not handle the timeout; CLI and SDK output must not imply the operation ran.

Read the reference domain's package alongside the specification. The
specification says what must hold; `sysctl` and `cron` show it holding.

## File layout

```
internal/controller/api/node/{domain}/
  types.go                    domain struct, dependency interfaces
  {domain}.go                 New(), var _ gen.StrictServerInterface = (*Domain)(nil)
  validate.go                 path-parameter validators
  handler.go                  Handler(): construct, wrap in auth, return routes
  {operation}_{verb}.go       one file per endpoint
  {operation}_{verb}_public_test.go
  gen/
    api.yaml                  paths, schemas, BearerAuth, the permission each endpoint needs
    cfg.yaml                  oapi-codegen config, strict-server: true
    generate.go               the //go:generate directive
```

Everything else in `gen/` is generated. `mise exec -- just generate` regenerates
the server, joins the combined spec at `internal/controller/api/gen/api.yaml`
with redocly, and regenerates the SDK client and the API doc pages.

## Scaffolding

A handler validates, then delegates to the job client. It never touches the
operating system.

```go
jobID, resp, err := s.JobClient.Modify(
    ctx, hostname, "node", job.OperationSysctlCreate, data)
```

```go
if job.IsBroadcastTarget(hostname) {
    return s.postOperationBroadcast(ctx, hostname, entry)
}
// single target: one result in the same collection envelope
```

Registration and startup: copy the reference domain's `handler.go`, change the
package and type names, and add one line to `registerControllerHandlers` in
`cmd/controller_setup.go` with its import:

```go
handlers = append(handlers,
    {domain}API.Handler(log, jc, signingKey, customRoles)...)
```

## Three rules the corpus does not yet hold

Stated here because they are real and nothing else states them. Both belong in
the corpus and neither is there, which is recorded rather than left to be
discovered — the same treatment FR-019 gives the absent `sdk-standards`
capability.

**A custom validation rule is a registered validator.** It belongs in
`internal/validation` with a hint in `customHints`, so the 400 says what shape
was expected rather than naming the tag. `sysctl_key` and `cron_schedule` are the
pattern.

**`IsBroadcastTarget` has one implementation and never a second.** FR-015 cites
it at `internal/job/subjects.go:306`, so the corpus names where it lives; what the
corpus does not say is that a domain must not write its own target parser.

**A permission is chosen by blast radius, not by endpoint group.** Two operations
that differ in how much damage they can do want two permissions however similar
their shape. A new one must be added to the built-in role expansion, the
permission constants, the SDK, and the roles tables in
`features/authentication.md` and `usage/configuration.md` — see
[docs.md](docs.md). A permission that exists in the spec but in no role reaches
nobody.

## Tests

Testing conventions are osapi's `CONTRIBUTING.md`, under "Testing". What this
layer adds to a public suite:

- `TestXxxHTTP` — raw HTTP through the full Echo middleware stack: valid input
  succeeds, invalid input returns 400 with the message.
- `TestXxxRBACHTTP` — no token is 401, a token without the permission is 403, a
  token with it succeeds.

Cover validation failure, success, a provider error surfaced from the job, and
the broadcast path. Where a status code is declared in the spec, the handler is
expected to be able to return it.
