---
name: pr-review-model
description: The review model that every osapi-io pull request goes through before it merges. Each pull request gets two independent reviews, a standards review and a code review, tracked with labels, and merges only when both pass and its checks are green. Use when opening a pull request, when asked who reviews or merges a pull request, when acting as a standards or code reviewer, when a reviewer comment arrives on a pull request, when running a merge loop, and when briefing an agent that will open pull requests.
compatibility: Requires the gh CLI authenticated against osapi-io. Uses the REST API through gh api.
license: MIT
metadata:
  author: osapi-io
  source: https://github.com/osapi-io/specs
---

# PR review model

The author of a pull request never certifies it. Two other agents review it, and
a pull request merges only when both pass.

| Review | Checks | Queue label | Pass label |
| --- | --- | --- | --- |
| Standards | the rules in CONTRIBUTING.md, AGENTS.md and the constitution | `needs-standards-review` | `standards-reviewed` |
| Code | correctness, bugs, edge cases, error handling, concurrency, and that the change fixes its issue | `needs-code-review` | `code-reviewed` |

A pull request merges when it has both pass labels, GitHub reports it as
mergeable, each check is green, and its specs pull request merged first.

## Why

On 27 November 2026 the owner saw fixes merge with one-off test functions and
with fixes that did not follow the standards. The agents that wrote them had
also labelled them as checked. The owner asked: "who is verifying it's okay?"
An author misses what it wrote, so a different agent reviews each change.

## The author

1. Open the pull request ready, not as a draft. Its title is 50 characters or
   fewer, because the squash merge makes the title the commit subject.
2. Add both queue labels:

   ```bash
   gh api -X POST repos/osapi-io/$r/issues/$n/labels \
     -f 'labels[]=needs-standards-review' -f 'labels[]=needs-code-review'
   ```

3. Watch the comments on the pull request. GitHub does not let an account
   request changes on its own pull request. Thus a reviewer posts its findings
   as a comment that starts with "Standards review" or "Code review".
4. Fix each point, push, and add the queue label of that review again.

Never add a pass label yourself.

## The reviewer

1. Read the rules first: the CONTRIBUTING.md, AGENTS.md and CLAUDE.md of the
   repository, and the AGENTS.md and the constitution of specs.
2. Read the whole diff. Read the files of the branch where you need context.
3. If the pull request passes, add the pass label, remove the queue label, and
   write a short comment that lists what you checked.
4. If it fails, write one comment that starts with "Standards review" or "Code
   review". Give each finding with its `file:line`, the rule or the defect, and
   the fix. Remove the queue label, and tell the lead.

Cite the source of each rule. A rule that no document states is not a finding.
Ask the lead to add it to the documents first.

## The lead

- Send each finding to the agent that wrote the pull request.
- A reviewer that cannot wait between rounds does not poll. Start it again
  when pull requests are in the queue.
- Run the merge loop. It merges only a pull request that has both pass labels.

## The API quota

All the agents use one GitHub account, so they share its API quota.

- Use the REST API (`gh api`). The `gh pr` commands use GraphQL, and on 27
  November 2026 the watchers of many agents used up its quota.
- Poll at most every 5 minutes.
- An API error is an unknown state. Try again in the next round. Do not read
  the error as a merge, a pass or a failure.
