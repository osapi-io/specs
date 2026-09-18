# Contract: the key store and its callers

Phase 1. The store is internal, so this states the behavioural contract its
callers depend on rather than a wire format.

## The store

Three operations, all keyed by machine ID.

| Operation | Called by                                          | Contract                                                                                                                                                                           |
| --------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Record    | Enrollment acceptance only                         | Creates or replaces the record. On replacement, the outgoing key becomes the superseded key with an expiry set from the configured grace period. Never called by any message path. |
| Look up   | Response and registration verification, fleet view | Returns the record, or a distinct "no record" answer. A failure to read is its own answer and never resembles "no record".                                                         |
| Remove    | Enrollment rejection, agent removal                | Deletes the record. After it returns, nothing signed by the removed key verifies.                                                                                                  |

**Concurrency**: acceptance and removal are rare and serialised through
enrollment; lookups are frequent and read-only. A cached lookup must be
invalidated by record and remove, not by elapsed time.

## Response verification

| Condition                                                | Result                           |
| -------------------------------------------------------- | -------------------------------- |
| Controller not enforcing                                 | Unchanged from today             |
| Signature verifies against current key                   | Response is a result             |
| Signature verifies against superseded key, inside grace  | Response is a result             |
| Signature verifies against superseded key, grace expired | Rejected, signature mismatch     |
| Signature absent or malformed                            | Rejected, distinct from mismatch |
| No stored record                                         | Rejected, "no stored key"        |
| Store unreadable                                         | Rejected, "store unavailable"    |

Rejection is never a silent drop on a single-target call: the job reports
failure. For a broadcast, the response does not count as that agent's reply and
the agent is reported as not having answered.

## Registration verification

| Condition                                                     | Result                                     |
| ------------------------------------------------------------- | ------------------------------------------ |
| Controller not enforcing                                      | Unchanged from today                       |
| Signature verifies, hostname and fingerprint match the record | Resolvable                                 |
| Signature verifies, hostname differs from the record          | Not resolvable; the record's hostname wins |
| Signature absent, malformed, or mismatched                    | Not resolvable                             |
| No stored record                                              | Not resolvable                             |
| Store unreadable                                              | Not resolvable                             |

"Not resolvable" means invisible to target resolution, label matching, facts and
fleet status. It is not an error returned to the agent — the agent keeps
heartbeating, and the fleet view shows why it is not authoritative.

## Target resolution

| Situation                                       | Behaviour                                                                    |
| ----------------------------------------------- | ---------------------------------------------------------------------------- |
| One resolvable registration claims the hostname | Resolves to it                                                               |
| Several resolvable registrations claim it       | Deterministic choice, preferring the enrolled machine; never iteration order |
| Only unresolvable registrations claim it        | Resolves to nothing; the caller is told the target is unknown                |
| Controller not enforcing                        | Unchanged from today                                                         |

## Fleet view

Each agent in the list reports whether a key is stored and, when it is, the
fingerprint. An operator can therefore see, before enabling enforcement, exactly
which agents would be refused.

## Rollout

Enforcement is per side and opt-in (FR-009). Enabling the controller first makes
responses and registrations verifiable while agents that have not re-enrolled
are visible in the fleet view. Enabling agents makes them refuse unsigned jobs,
which the GHSA-3jh4 fix already implements. Neither switch flips as a
consequence of upgrading.
