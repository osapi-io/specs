# Quickstart: verifying the job system move

**Feature**: `004-job-system` | **Date**: 2026-09-28 | **Spec**:
[spec.md](spec.md)

Five success criteria. Two are commands, three are readings with fixed questions
so that "it looks complete" is not the answer.

## Prerequisites

```bash
cd ~/git/osapi-io/specs && mise install && just fetch
cd ~/git/osapi-io/osapi && mise install
```

## SC-002 — every cited file says what the requirement says

```bash
# Each requirement that names a value or a key format cites a file. Open the file.
cd ~/git/osapi-io/osapi

# FR-003, FR-004: the job key, and the status event key
grep -n 'kvKey := "jobs\."' internal/job/client/client.go
grep -n 'statusKey := fmt.Sprintf' internal/job/client/jobs.go internal/job/client/agent.go

# FR-014: the consumer defaults
grep -n 'agent.consumer.max_deliver\|agent.consumer.ack_wait' cmd/root.go

# FR-021: the bucket TTL
sed -n '/^  kv:/,/^  dlq:/p' configs/osapi.yaml

# FR-009: the redelivery check
grep -n 'HasJobResponse' internal/agent/handler.go

# FR-017: the backstop
grep -n 'DefaultCommandTimeout' internal/exec/types.go
```

Each must print. A citation that no longer resolves is a requirement describing
code that has moved, and the corpus is then stating a rule nobody can check.

## SC-003 — the corrections read as corrections

```bash
cd ~/git/osapi-io/specs
grep -n "Gap" components/osapi/specs/004-job-system/spec.md
```

Expected: three, at FR-004, FR-014 and FR-021, each naming both what the page
said and what the code does. A correction that reads as a plain statement leaves
the next reader wondering whether the page or the corpus is stale.

## SC-004 — one statement, and the citations resolve

```bash
# After the osapi change: the mechanics must be gone from the page.
cd ~/git/osapi-io/osapi
grep -n "MaxDeliver\|AckWait\|{status}.{uuid}\|24 hours" \
  docs/docs/sidebar/architecture/job-architecture.md
```

Expected: no output. Any match is a second statement of a rule the corpus now
holds — and for the first three, a second statement that is wrong.

```bash
# And the citations that replaced the restatements must resolve.
cd ~/git/osapi-io/specs
just test
```

`skill-lint` is the gate. 003's T005 measured it failing on a broken citation,
so a pass here means the citations point at something.

## SC-005 — nothing restates 001 or 002

```bash
cd ~/git/osapi-io/specs
grep -n "001-provider-contract\|002-agent-key-store" \
  components/osapi/specs/004-job-system/spec.md
```

Expected: FR-022 and FR-023, plus SC-005 itself. Then read the Security
Considerations requirements and confirm they cite rather than describe: a
sentence explaining how signing works is a restatement however it is introduced.

## SC-001 — a contributor answers from the corpus alone

Not automatable. Give somebody who has not read the site page only
`components/osapi/specs/004-job-system/spec.md`, and ask:

1. What carries a job from the API to an agent, and what guarantees its
   delivery?
2. What must an agent not do when the same job arrives twice, and what does it
   do instead?
3. What bounds how long an operation runs, and what happens when the controller
   stops waiting before the agent stops working?

All three must be answerable without opening the site. The third exists because
it is the newest content on the page and the easiest to leave behind — 003's
research Finding 2.

## The check that matters most

```bash
# Is the duplication over?
cd ~/git/osapi-io/osapi && git log --oneline -1 -- docs/docs/sidebar/architecture/job-architecture.md
```

If that commit predates the merge of `004`'s specification, the corpus and the
page both state these rules and three of the page's numbers are wrong. The
feature is not done, whatever the corpus says.
