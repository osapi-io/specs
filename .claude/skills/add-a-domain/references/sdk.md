# SDK service

`pkg/sdk/client` is the public Go API. Its generated client comes from the same
combined spec as the server, so `just generate` covers it.

The binding rules are the `sdk-standards` capability in this repository, and
they bind `osapi-orchestrator` too. Where this file and that capability
disagree, the capability wins.

## Files, one service per domain

```
pkg/sdk/client/
  {domain}.go                     {Domain}Service struct and methods
  {domain}_types.go               result types, request types, gen -> SDK conversion
  {domain}_public_test.go         method tests
  {domain}_types_public_test.go   conversion tests
  osapi.go                        Client field, wired in New()
examples/sdk/client/{domain}.go   one runnable example
```

Never add methods or types to another service's files.

## Generated types stay inside

No `gen.*` type appears in a public signature. That is the whole reason the SDK
exists.

```go
// Wrong: the consumer now imports gen
func (s *DockerService) Create(
    ctx context.Context,
    hostname string,
    body gen.DockerCreateRequest,
) (*Response[Collection[DockerResult]], error)

// Right: an SDK type, converted internally
func (s *DockerService) Create(
    ctx context.Context,
    hostname string,
    opts DockerCreateOpts,
) (*Response[Collection[DockerResult]], error)
```

Build the `gen` request inside the method, mapping zero values to nil where the
generated type uses a pointer.

If a consumer has to import `gen`, the wrapper is incomplete.

## Result types

Every exported field carries a snake_case `json` tag. `StructToMap` converts by
JSON round-trip, so an untagged field arrives as PascalCase and matches nothing.

```go
type HostnameResult struct {
    Hostname string            `json:"hostname"`
    Error    string            `json:"error,omitempty"`
    Changed  bool              `json:"changed"`
    Labels   map[string]string `json:"labels,omitempty"`
}
```

`omitempty` on pointers, optional slices and maps, error strings and optional
strings. Not on `Changed`, and not on a required field: a mutation result must
say `"changed": false` rather than omitting it.

`Changed` travels provider to agent to API to SDK. Breaking the chain anywhere
makes every layer above it lie.

Multi-target operations return `Collection[T]`, holding `Results` and `JobID`.
Use `Collection.First()` rather than indexing.

## Responses and errors

Methods return `*Response[T]`: `Data` for the typed result, `RawJSON()` for the
CLI's `--json` mode.

```go
if err := checkError(
    resp.StatusCode(),
    resp.JSON400, resp.JSON401, resp.JSON403, resp.JSON500,
); err != nil {
    return nil, fmt.Errorf("{domain} create: %w", err)
}

if resp.JSON200 == nil {
    return nil, &UnexpectedStatusError{APIError{
        StatusCode: resp.StatusCode(),
        Message:    "nil response body",
    }}
}
```

Every status the spec declares gets a branch. Wrap with context at the boundary
so `errors.Is` and `errors.As` still work above it, and guard the nil body after
`checkError`: a 200 with no body is reachable.

## Examples

One file per service in `examples/sdk/client/`, named for the `Client` field in
lowercase.

- One service per file, nothing mixed in.
- Self-contained: read-only examples call and print; mutating examples clean up
  first so they can run twice.
- Print at least one result, so the example is not silent.
- Under about 100 lines excluding the licence header.
- `log.Fatalf` for unexpected errors; for an operation that may be unsupported
  on the host, print the message rather than crashing.
- Never import `gen`.

`examples/` holds its own module, so a new example means `just go-mod` and
committing the tidy result, which `just test` checks.

## Tests

- `httptest.Server` for the API.
- Every declared status path: 200, 400, 401, 403, 404, 500.
- The nil-body path and a transport error against an unreachable server.
- Every optional field branch in request conversion.
- 100% coverage on SDK packages, excluding `gen/`.
