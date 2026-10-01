# The audit trail

Every request to an authenticated endpoint is recorded: who made it, what they
asked for, what came back, and which job it created. `audit:read` is one of the
seven [permissions](permissions.md) `write` does not hold, so what lands here is
something `admin` can see and `write` cannot.

## What an entry holds

Thirteen fields, in twelve rows below because `method` and `path` describe one
thing.

```sh
awk '/^type Entry struct/,/^}/' internal/audit/types.go | grep -cE '^\t[A-Z]'  # 13
```

| Field             | Is                                                     |
| ----------------- | ------------------------------------------------------ |
| `id`              | the entry's own identifier                             |
| `timestamp`       | when the request was processed                         |
| `user`            | the authenticated subject, from the JWT `sub` claim    |
| `roles`           | the roles the token carried                            |
| `method`, `path`  | the request                                            |
| `operation_id`    | the OpenAPI operation, where one is known              |
| `source_ip`       | the client                                             |
| `response_code`   | what came back                                         |
| `duration_ms`     | how long it took                                       |
| `trace_id`        | the OpenTelemetry trace, for correlation               |
| `job_id`          | the job the request created, if it created one         |
| `request_summary` | what the request asked for, with sensitive values gone |

`job_id` is what joins an audit entry to a job's own status timeline, so "who
asked for this" and "what happened to it" can be answered together.

## A read is recorded and not summarised

`request_summary` is filled only for `POST`, `PUT`, `PATCH` and `DELETE`. A
`GET` produces an entry with no summary at all.

That is deliberate: a read's body carries nothing worth keeping. But it has a
consequence worth knowing. **Who read the audit log is recorded; what they
searched for is not.** Same for any other query. If that matters, the entry is
not where to look for it.

## Redaction is a denylist, and that is the thing to watch

`Summarize` parses the body, walks it recursively through maps and slices, and
replaces the value of any field whose lowercased name is on this list with
`[redacted]`:

```
password    password_hash   passwordhash   secret
token       private_key     privatekey     key_data
stdin       content         authorization
```

Eleven names.

```sh
awk '/^var sensitiveFields/,/^}/' internal/audit/summary.go | grep -cE '^\t"'  # 11
```

`stdin` and `content` are the two that connect elsewhere: `stdin` is how
[running commands](exec.md) keeps a secret out of a command's arguments, and
`content` is a file body going to the deployer. Both would otherwise be stored
in full.

**A field not on that list is stored as sent.** A domain adding `api_key`,
`passphrase`, `credentials` or `bearer` gets none of them redacted, and nothing
in the build says so. Adding a field that carries a secret means adding its name
here, and there is no test that fails if you forget.

**Nothing currently leaks.** Every secret-bearing field in every domain's
request body today is covered: `password` is on the list, `content` is on the
list, and `node/user`'s `key` is an SSH *public* key. `job`'s `data` never
reaches redaction at all, because `Summarize` only ever sees a request body and
that field is in a response. So this is a footgun rather than a defect, and it
is recorded as osapi-io/osapi#551.

The match is on the field name only. A secret in a field called `value`, or
concatenated into a string that happens to be called something innocuous, is
stored.

## Two limits, and they behave differently

**64 KiB is the most the middleware will read.** A request body larger than that
is **not recorded at all**: the summary becomes
`[body over 65536 bytes, not recorded]` and nothing of the request is kept.

**2048 bytes is the most a summary keeps.** A body under 64 KiB is parsed,
redacted, and then truncated to this, and a truncated summary **says that it was
truncated** so a reader does not mistake part of a request for all of it.

The difference matters when reading an entry. A marker means the request was too
large to look at; a truncation marker means it was looked at and abbreviated. A
file deploy of a large template gets the first, so the audit trail records that
it happened and nothing about what was deployed.

## Where entries go

`Store` is an interface with four methods: `Write`, `Get`, `List` with a limit
and offset, and `ListAll`. The implementation is `StreamStore`, backed by a
**NATS JetStream stream** rather than a KV bucket, because an audit trail is an
append-only sequence and a stream is the shape that fits.

Retrieval has a five-second fetch timeout.

## The write outlives the request

The middleware writes the entry with `context.Background()` rather than the
request's context.

That is on purpose. A client that disconnects mid-request, or a request that
times out, would otherwise cancel its own audit entry, and **a request that
fails is exactly the one worth having a record of.** A write failure is logged
rather than returned, so auditing never fails a request that otherwise
succeeded.

## One job ID per entry, the first one

`RecordJobID` writes into a context sink, and the sink keeps the **first** job
ID it is given:

```go
if sink.id == "" {
    sink.id = jobID
}
```

A request that creates one job, which is almost all of them, records it. A
request that creates several records the first and loses the rest, so the audit
trail cannot reconstruct a fan-out from a single call.

## Where this connects

`audit:read` and why only `admin` has it is [permissions](permissions.md).

The `stdin` field that redaction protects, and why a secret goes there rather
than into an argument, is [running commands](exec.md).

The job the `job_id` points at, and its append-only status events, is
[the job system](job-system.md).

______________________________________________________________________

Written from `internal/audit/` and `internal/controller/api/middleware_audit.go`
rather than from a feature. No feature covers this package.
