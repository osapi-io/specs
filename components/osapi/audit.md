# The audit trail

osapi records each request to an authenticated endpoint. It records who made the
request, what the request asked for, what came back, and which job it made.
`audit:read` is an admin-only [permission](permissions.md). Only `admin` and
`auditor` have it. Thus these two roles can see these records, and the other
roles cannot.

## What an entry holds

An entry has thirteen fields. The table below has twelve rows, because `method`
and `path` describe one thing.

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

`job_id` joins an audit entry to the status timeline of a job. Thus you can
answer "who asked for this" and "what happened to it" together.

## A read is recorded and not summarised

osapi fills `request_summary` only for `POST`, `PUT`, `PATCH` and `DELETE`. A
`GET` makes an entry with no summary.

This is deliberate. The body of a read has nothing useful to keep. But there is
an effect to know. **osapi records who read the audit log. It does not record
what that person searched for.** The same is true for each other query. If you
need that information, the entry does not have it.

## Redaction is a denylist, and that is the thing to watch

`Summarize` parses the body. It goes through the maps and slices of the body
recursively. If the lowercase name of a field is on this list, it replaces the
value with `[redacted]`:

```
password    password_hash   passwordhash   secret
token       private_key     privatekey     key_data
stdin       content         authorization
```

There are eleven names.

`stdin` and `content` connect to other parts. [Running commands](exec.md) uses
`stdin` to keep a secret out of the arguments of a command. `content` is a file
body for the deployer. Without the list, osapi stores all of the two.

A behavior adds to the list, and you do not edit the list. osapi also redacts
each input field that the behavior tags `secret:"true"`, by name.
[Behaviors](behaviors.md#secret-inputs) describes this. The fixed list is for
the hand-written domains.

**osapi stores a field that is not on the list as it came.** If a domain adds
`api_key`, `passphrase`, `credentials` or `bearer`, osapi redacts none of them,
and nothing in the build tells you. When you add a field with a secret, add its
name here. No test fails if you forget.

**Nothing leaks now.** The list covers each field with a secret in the request
body of each domain:

- `password` is on the list.
- `content` is on the list.
- The `key` of `node/user` is an SSH *public* key.
- The `data` of `job` never gets to redaction. `Summarize` sees only a request
  body, and that field is in a response.

Thus this is a risk, not a defect. osapi-io/osapi#551 records it.

The match uses only the field name. osapi stores a secret in a field with the
name `value`. It also stores a secret that is joined into a string with a safe
name.

## Two limits, and they behave differently

**The middleware reads 64 KiB or less.** osapi **does not record** a request
body that is larger. The summary becomes
`[body over 65536 bytes, not recorded]`, and osapi keeps nothing of the request.

**A summary keeps 2048 bytes or less.** osapi parses and redacts a body under 64
KiB. Then it cuts the body to this size. A cut summary **says that it was cut**.
Thus a reader does not think that part of a request is all of it.

This difference is important when you read an entry. The first marker means that
the request was too large to examine. The second marker means that osapi
examined it and made it shorter. A file deploy of a large template gets the
first marker. Thus the audit trail records that the deploy occurred, and nothing
about the deployed file.

## Where entries go

`Store` is an interface with four methods: `Write`, `Get`, `List` with a limit
and an offset, and `ListAll`. The implementation is `StreamStore`. It uses a
**NATS JetStream stream**, not a KV bucket. An audit trail is a sequence that
only grows at the end, and a stream has that shape.

A read from the store has a five-second fetch timeout.

## Filters read the whole log

`GET /api/audit` and `osapi client audit list` take four filters: `writes` (each
method but GET), `user`, `operation` (text of the operation ID or of the path,
in any case) and `status`. An entry is listed when it matches each filter that
is set. The stream pages by sequence, so it cannot skip the entries that do not
match. Thus a request with a filter reads the whole log with `ListAll`, as an
export does, and the endpoint pages the entries that match. `total_items` is
then the count of the entries that match. A request with no filter reads only
its page with `List`.

The cost of a filter grows with the size of the log, which the retention of the
stream limits. An index by subject, such as one subject for each method, would
let JetStream filter with no full read. Nothing needs it yet.

## The write outlives the request

The middleware writes the entry with `context.Background()`, not with the
context of the request.

This is deliberate. Without it, a client that disconnects during a request
cancels its own audit entry, and so does a request that times out. **A request
that fails is the one that you most need a record of.** osapi logs a write
failure and does not return it. Thus an audit failure never makes a successful
request fail.

## One job ID per entry, the first one

`RecordJobID` writes into a context sink. The sink keeps the **first** job ID
that it gets:

```go
if sink.id == "" {
    sink.id = jobID
}
```

Almost all requests make one job, and osapi records it. If a request makes more
than one job, osapi records the first and loses the others. Thus the audit trail
cannot show all of the jobs that one call made.

## Where this connects

[Permissions](permissions.md) has `audit:read`, and why only `admin` and
`auditor` have it.

[Running commands](exec.md) has the `stdin` field that redaction protects, and
why a secret goes there and not into an argument.

[The job system](job-system.md) has the job that `job_id` points to, and its
status events.

______________________________________________________________________

Written from `internal/audit/` and
`internal/controller/api/middleware_audit.go`.
