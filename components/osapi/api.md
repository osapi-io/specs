# The API conventions

Each operation of the osapi API obeys the same rules: its status codes, its
error body, the shape of a list, and its name. This page states the rules.
`TestConventions`, in `internal/apicontract`, reads the joined spec and fails on
an operation that breaks one.

The CLI has its own page, [The CLI](cli.md). The two pages agree: a CLI command
is one operation, and `--json` prints its answer as it came.

## The status code tells what happened

The verb does not select the status code. The code tells the caller whether the
work is done, and what the body holds:

| Code | It means                                        | The body           |
| ---- | ----------------------------------------------- | ------------------ |
| 200  | The work is done.                               | The result         |
| 201  | The work is done, and a new resource exists.    | The new resource   |
| 204  | The work is done, and it has nothing to return. | None               |
| 4xx  | The request is not correct, or not permitted.   | `{"error": "..."}` |
| 5xx  | The controller failed, or a backend is not set. | `{"error": "..."}` |

A 201 has a `Location` header. The header names the resource that the request
created, such as `/api/job/7c9e6679-...` after a retry.

### No operation answers 202

A 202 tells the caller that the work is not done yet, and where to poll for it.
Each osapi operation answers when its work is done. A node operation sends a
job, waits for the agents, and returns their results. Thus no operation answers
202\.

A mode that sends a job and does not wait is the correct place for 202. Its
answer is the job ID, and its `Location` header is `/api/job/{id}`. osapi does
not have this mode.

### Node operations and controller operations

An operation under `/api/node/{hostname}` runs on one host or on many hosts. It
answers with the job ID and the result of each host, in `job_id` and `results`.
Thus each node operation answers 200, for each verb:

- A create is not 201. The request can go to many hosts, and an idempotent
  create changes nothing on a host that has the resource already. Each result
  has `changed`.
- A delete is not 204. Each result tells whether the host changed.

A request to one host for an item that the host does not have answers 404, such
as `user get` for a user that does not exist. The error names the item. A
request to many hosts answers 200, and the result of each host that does not
have the item says so. [Providers](providers.md#the-not-found-rule) tells how a
provider reports an absent item.

An operation of the controller itself, such as an agent, a job, a file or the
audit log, changes one resource:

| The operation                                       | It answers           |
| --------------------------------------------------- | -------------------- |
| A read                                              | 200                  |
| A create                                            | 201, with `Location` |
| A write to a resource that exists already           | 200                  |
| A delete                                            | 204                  |
| An action with only a confirmation, such as `drain` | 204                  |

A create is a POST, and a replace is a PUT. The files show both:

- `POST /api/file` creates a file. A new name answers 201. A name that exists
  with the same content answers 200, `changed: false`. A name that exists with
  other content is a 409.
- `PUT /api/file/{name}` replaces a file. It answers 200, and `changed` tells
  whether the content changed. A new name answers 201.

A flag never turns a create into a replace. Thus the CLI has `file upload` for
the POST and `file update` for the PUT, one command for each operation.

## Each error is `{"error": "..."}`

Each 4xx and each 5xx has the same body, `{"error": "..."}`. This includes a
path or query parameter that does not bind. The error handler of the API server,
in `internal/controller/api/server.go`, writes the body for each error that a
route returns. Without it, echo writes `{"message": "..."}`.

A 500 tells only its status text, `Internal Server Error`. The cause goes to the
log, and not to the caller.

### The exception: the readiness probe

`GET /api/health/ready` answers 503 with its own body, `ReadyResponse`, when the
controller cannot take traffic. A load balancer reads the 503, and a person
reads the reason in the body. This is the only non-2xx answer that is not an
error body.

`GET /api/health/status` is not a probe. It is a report for a person and the
CLI. When a component is not healthy, it answers 200, and its overall status is
`degraded`. A non-2xx answer tells that the request failed, and this request did
not fail.

## A list is `items` and `total_items`

A list of the controller answers with its things in `items`, and their count in
`total_items`. The agents, the pending agents, the audit log, the fact keys, the
files, the stale deployments and the jobs all use this shape.

A node operation answers `results`, which is not a list of things. It is the
answer of each host.

## A read is a GET

A read is a GET, with its input in the path and the query. A read never has a
body. `GET /api/node/{hostname}/file/status?path=...` was a POST with a body.

## Names

- **operationId** is Pascal case, such as `GetJobs` or `DeleteAgent`. The Go SDK
  and the UI client get their function names from it. The endpoint DSL makes
  this name when a method does not set one, and
  `osapi controller endpoint validate` refuses a name that starts with a small
  letter.
- **Response schemas of a node operation** use the names that the behavior DSL
  gives: `...CollectionResponse` for a list, `...GetResponse`,
  `...CreateResponse`, `...UpdateResponse` and `...DeleteResponse`. A
  hand-written node group gets these names when it moves to a behavior. Until
  then, some hand-written groups use other names, such as `...ListResponse` and
  `...MutationResponse`.

## Each error says why

An error answer is `ErrorResponse`:
`{"error": "<message>", "reason": "<word>"}`. The HTTP status is the class of
the problem. `reason` is the cause, a word that a program branches on. `error`
is the message for a person, and its words can change between releases. The
schema lists each reason, with what it means:

| `reason`          | Status | Means                                                                    |
| ----------------- | ------ | ------------------------------------------------------------------------ |
| `invalid_request` | 400    | the request breaks a rule, such as a missing field                       |
| `unauthorized`    | 401    | no token, or a token that is not valid                                   |
| `forbidden`       | 403    | the token does not have the permission                                   |
| `not_found`       | 404    | the host or osapi does not have what the request names                   |
| `not_managed`     | 409    | the item is there, but osapi did not deploy it, so it does not change it |
| `not_installed`   | 409    | the host does not have a program that the request needs                  |
| `conflict`        | 409    | the state of the item blocks the request                                 |
| `unavailable`     | 503    | a part that osapi depends on is down, such as NATS                       |
| `server_error`    | 500    | the controller failed; its log has the cause                             |

The generated routes take the reason from the error that the method maps
(`endpoint.NotFound`, `.Conflict(...).Because(endpoint.ReasonNotManaged)`). The
hand-written handlers take it from `apierr`, and the error handler of the API
takes it from the status. The agent already names the cause of a failed job
(`internal/job/errors.go`), and the reason carries it to the caller. A test
fails when `endpoint.Reasons` and the enum of the schema differ, or when the
schema does not say what a reason means.

Two answers changed with the reason. A not found on a method with no key, such
as a create whose object is not in the Object Store, was a 500. Not managed and
not installed were a 404 that said "not found". The `ErrorResponse` before it
had an integer `code`, which repeated the status, and almost nothing set it.

## The test

`TestConventions` checks the joined spec,
`internal/controller/api/gen/api.yaml`. It fails when:

- an operationId starts with a small letter
- an operation answers 202
- a 201 has no `Location` header
- a 4xx or a 5xx is not `ErrorResponse`, except the readiness probe
- a delete of the controller does not answer 204
- a list of the controller does not answer `items` and `total_items`

Its first run, on `main` before these changes, found 30 failures.

## Changed on 17 November 2026

The audit made these changes, and kept no old forms, because nothing outside
osapi used them:

| Was                                                                    | Now                                       |
| ---------------------------------------------------------------------- | ----------------------------------------- |
| `getAgents`, `removeAgent`, and 7 more camel-case IDs                  | `GetAgents`, `DeleteAgent`, and so on     |
| `agents` and `total`, `files` and `total`, `stale` and `total`, `keys` | `items` and `total_items`                 |
| 202 on 13 node writes                                                  | 200                                       |
| 201 without `Location`                                                 | 201 with `Location`                       |
| A file upload of an existing name: 201                                 | 200                                       |
| `POST /api/file?force=true`, and `file upload --force`                 | `PUT /api/file/{name}`, and `file update` |
| `DELETE /api/file/{name}`: 200, `{"deleted": true}`                    | 204                                       |
| Agent delete, accept, reject, drain, undrain: 200, a message           | 204                                       |
| `POST /api/node/{hostname}/file/status` with a body                    | `GET ...?path=`                           |
| A parameter that does not bind: `{"message": "..."}`                   | `{"error": "..."}`                        |
| `GET /api/health/status` degraded: 503                                 | 200, `degraded`                           |
