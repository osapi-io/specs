# CLI commands

Anything the API can do has a CLI equivalent. The CLI is thin: parse flags, call
the SDK, print.

## The rules are in the corpus, not here

The obligations this layer carries are stated in
[005-building-a-domain](../../../../components/osapi/domains.md).

| What you need to know | Where |
| --- | --- |
| One parent command per domain, one subcommand per endpoint | FR-021 |
| `--json` on every command, and flags rather than positional arguments for IDs | FR-021 |
| `cli.PrintKV` for a single resource, `cli.PrintCompactTable` for rows | FR-021 |
| Every response code the spec declares handled in the status switch | FR-021 |
| What `--target` accepts, a literal, `_any`, `_all`, a label selector | FR-015 |
| What verifies a finished domain, and what Step 8 alone misses | FR-024 |

## Files

```
cmd/client_node_{domain}.go             parent command, registered under clientNodeCmd
cmd/client_node_{domain}_{operation}.go one per endpoint
```

Controller-only domains drop the `node` segment: `cmd/client_{domain}_*.go`. One
file per command, named for the command it implements.

## Scaffolding

```go
switch resp.StatusCode() {
case http.StatusOK:
    // print
case http.StatusBadRequest, http.StatusNotFound,
     http.StatusInternalServerError:
    handleUnknownError(...)
case http.StatusUnauthorized, http.StatusForbidden:
    handleAuthError(...)
}
```

A code the spec declares and the switch omits becomes a silent success.

A result row carries the hostname and, where the operation mutates, whether it
changed. Follow the reference domain's column choice rather than inventing one:
operators read these side by side.

## Three rules the corpus does not yet hold

Stated here because they are real and nothing else states them, not the corpus,
not osapi's `CONTRIBUTING.md`. Recorded as unstated rather than left to be
discovered, the same treatment FR-019 gives the absent `sdk-standards`
capability.

**A command whose remote work failed exits non-zero.** For `command exec` and
`command shell` the exit code is the remote command's, through
`cli.MaxExitCode(results)`, and it must be applied on every output path including
`--json` and the default table. Scripts branch on this.

**`cmd/` is the only place that may call `os.Exit`**, and only at the top of a
command. Below that, return an error. Nothing panics.

**Assert the exit code, not just the output.** The exit-code rule above was
broken once and invisible to tests that read only stdout.

## Tests

`cmd/` is excluded from the coverage gate by `.coverignore`, so unit tests are not
required there, which makes the integration suite the check:

```
test/integration/{domain}_test.go
```

Build-tagged `integration`, it starts a real binary and exercises the commands end
to end. Guard every mutating test with `skipWrite(s.T())`, so CI runs read-only by
default and `OSAPI_INTEGRATION_WRITES=1` enables the rest.

```bash
mise exec -- just go-unit-int
```
