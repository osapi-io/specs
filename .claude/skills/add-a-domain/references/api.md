# API layer

Four things: the OpenAPI spec, the handlers, the registration, and one line of
startup wiring.

Node-targeted domains live under `internal/controller/api/node/{domain}/`,
controller-only domains directly under `internal/controller/api/{domain}/`.

## 1. Spec and generation

`internal/controller/api/node/{domain}/gen/` holds three hand-written files:

- `api.yaml` — paths, schemas, `BearerAuth` security, and the permission each
  endpoint requires
- `cfg.yaml` — oapi-codegen config, `strict-server: true`, import mapping for
  `common/gen`
- `generate.go` — the `//go:generate` directive

Everything else in `gen/` is generated. `mise exec -- just generate` regenerates
the server, joins the combined spec at `internal/controller/api/gen/api.yaml`
with redocly, and regenerates the SDK client and API doc pages.

### Verbs

| Verb | Use |
| --- | --- |
| `GET` | read or list |
| `POST` | create, key or name in the body |
| `PUT` | update, key or name in the path |
| `DELETE` | remove |

Never a combined set or upsert. Separate verbs are what give honest 404
semantics: update fails when absent, create succeeds unchanged when present.
`cron` is the reference.

### Paths

Nouns, with the action carried by the verb, nested under the node:

| Pattern | Example |
| --- | --- |
| `/node/{hostname}/{resource}` | `disk`, `ntp` |
| `/node/{hostname}/{resource}/{id}` | `sysctl/{key}` |
| `/node/{hostname}/{domain}/{resource}` | `network/dns` |
| `/node/{hostname}/{domain}/{resource}/{id}/{action}` | `service/{name}/start` |

Path parameters identify the target. Query parameters are for filtering and
pagination only, never for saying which resource to act on.

### Validation, declared in the spec

The spec is the source of truth for what is accepted.

**Body properties** carry tags that `validation.Struct()` enforces:

```yaml
properties:
  address:
    type: string
    x-oapi-codegen-extra-tags:
      validate: required,ip
```

**Query parameters** carry the tags at parameter level, a sibling of
`name`/`in`/`schema`, not inside `schema`:

```yaml
parameters:
  - name: limit
    in: query
    x-oapi-codegen-extra-tags:
      validate: omitempty,min=1,max=100
    schema:
      type: integer
      default: 20
```

**Path parameters** are the trap. `x-oapi-codegen-extra-tags` on a path
parameter generates nothing in strict-server mode, an upstream limitation. Keep
the tag as documentation, add a comment saying validation is manual, and
validate in the handler with a helper beside `validateHostname` in the domain's
`validate.go`. `format: uuid` is the exception: the router enforces it.

A custom rule belongs in `internal/validation` as a registered validator, with a
hint in `customHints` so the 400 says what shape was expected. `sysctl_key` and
`cron_schedule` are the pattern.

Every endpoint that takes user input needs: validate tags in the spec, a
`validation.Struct()` call in the handler, a `400` response declared in the
spec, and HTTP wiring tests. Where every field is `omitempty` and validation
cannot currently fail, keep the call and comment why, so a later field addition
does not silently land unvalidated.

## 2. Handlers

```
internal/controller/api/node/{domain}/
  types.go                    domain struct, dependency interfaces
  {domain}.go                 New(), var _ gen.StrictServerInterface = (*Domain)(nil)
  validate.go                 path-parameter validators
  handler.go                  Handler(): construct, wrap in auth, return routes
  {operation}_{verb}.go       one file per endpoint
  {operation}_{verb}_public_test.go
```

A handler validates, then delegates to the job client. It never touches the
operating system.

```go
jobID, resp, err := s.JobClient.Modify(
    ctx, hostname, "node", job.OperationSysctlCreate, data)
```

`Query`, `QueryBroadcast`, `Modify` and `ModifyBroadcast` are the whole
interface. Adding an operation adds no methods.

### Broadcast, mandatory for node-targeted operations

Every `/node/{hostname}/...` operation accepts `_all`, `_any`, a hostname, or a
`key:value` label selector, and returns the same shape either way:

```go
if job.IsBroadcastTarget(hostname) {
    return s.postOperationBroadcast(ctx, hostname, entry)
}
// single target: one result in the same collection envelope
```

```json
{
  "job_id": "...",
  "results": [
    {"hostname": "web-01", "error": "", "changed": true},
    {"hostname": "web-02", "error": "unsupported"}
  ]
}
```

Every result item carries `hostname` and `error`. A host that failed or skipped
appears as an entry with `error` set, not as a missing row. `IsBroadcastTarget`
has one implementation in `internal/job/subjects.go`; never write a second.

### What a caller sees when an agent does not answer

The job client synthesizes a result with the error text
`timeout: agent did not respond`. Domain code does not need to handle it, but
CLI and SDK output should not imply the operation ran.

## 3. Registration

`handler.go` exports `Handler()`, which builds the strict handler, wraps it in
`api.ScopeMiddleware` so declared permissions are enforced, and returns route
registration closures. The `Server` struct does not change. Copy the reference
domain's `handler.go` and change the package and type names.

Add `handler_public_test.go` covering route registration and that middleware
runs.

## 4. Startup

One line in `registerControllerHandlers` in `cmd/controller_setup.go`, plus the
import:

```go
handlers = append(handlers,
    {domain}API.Handler(log, jc, signingKey, customRoles)...)
```

## Permissions

An endpoint declares a `resource:verb` permission in its spec. Choosing one is a
decision, not a formality:

- Split by blast radius, not by endpoint group. Two operations that differ in
  how much damage they can do want two permissions, however similar their
  shape.
- A new permission must be added to the built-in role expansion, the permission
  constants, the SDK, and the roles tables in `features/authentication.md` and
  `usage/configuration.md`. See [docs.md](docs.md).
- A permission that exists in the spec but in no role reaches nobody.

## Tests

Each endpoint's public suite carries, beside the unit rows:

- `TestXxxHTTP` — raw HTTP through the full Echo middleware stack: valid input
  succeeds, invalid input returns 400 with the message.
- `TestXxxRBACHTTP` — no token is 401, a token without the permission is 403, a
  token with it succeeds.

Cover validation failure, success, a provider error surfaced from the job, and
the broadcast path. Where a status code is declared in the spec, the handler is
expected to be able to return it.
