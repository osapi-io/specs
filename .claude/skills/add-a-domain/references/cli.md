# CLI commands

Anything the API can do has a CLI equivalent. The CLI is thin: parse flags, call
the SDK, print.

## Files

```
cmd/client_node_{domain}.go             parent command, registered under clientNodeCmd
cmd/client_node_{domain}_{operation}.go one per endpoint
```

Controller-only domains drop the `node` segment: `cmd/client_{domain}_*.go`.
One file per command, named for the command it implements.

## Flags

- `--target` carries the hostname, `_all`, `_any`, or a `key:value` label
  selector, so every command supports broadcast for free.
- Resource identifiers are flags, not positional arguments: `--key`,
  `--job-id`, `--audit-id`.
- `--json` prints the SDK's `RawJSON()` and exits, on every command.

## Output

Two helpers in `internal/cli/ui.go`:

- `cli.PrintKV` for a single resource, printed as inline key-value lines.
- `cli.PrintCompactTable` for multiple rows, which is what a broadcast returns.

A result row carries the hostname and, where the operation mutates, whether it
changed. Follow the reference domain's column choice rather than inventing one:
operators read these side by side.

## Status codes

Handle every code the spec declares:

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

## Exit codes

A command whose remote work failed exits non-zero. For `command exec` and
`command shell` the exit code is the remote command's, through
`cli.MaxExitCode(results)`, and it must be applied on every output path,
including `--json` and the default table. Scripts branch on this.

## Errors and exits

`cmd/` is the only place that may call `os.Exit`, and only at the top of a
command. Below that, return an error. Nothing panics.

## Tests

`cmd/` is excluded from the coverage gate by `.coverignore`, so unit tests are
not required there, which makes the integration suite the check:

```
test/integration/{domain}_test.go
```

Build-tagged `integration`, it starts a real binary and exercises the commands
end to end. Guard every mutating test with `skipWrite(s.T())`, so CI runs
read-only by default and `OSAPI_INTEGRATION_WRITES=1` enables the rest.

```bash
mise exec -- just go-unit-int
```

Assert the exit code, not just the output: the exit-code bug above was invisible
to tests that only read stdout.
