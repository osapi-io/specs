---
name: pr-review-model
description: The review model of each osapi-io pull request. Two independent agents review a pull request, one for the standards of the project and one for the code, and it merges only when both pass and its checks are green. Use it when you open a pull request, when a reviewer comment arrives on one, when you are the standards reviewer or the code reviewer, when you run the merge loop or send review findings to their authors as the lead, when someone asks who reviews or merges a pull request, and when you write the brief of an agent that will open pull requests.
compatibility: Requires the gh CLI, authenticated against osapi-io. All calls use the REST API through gh api.
allowed-tools:
  - Bash(gh api -X POST:*)
  - Bash(gh api -X DELETE:*)
  - Bash(gh api -X PUT:*)
license: MIT
metadata:
  author: osapi-io
  source: https://github.com/osapi-io/specs
---

# PR review model

The author of a pull request never certifies it. A standards reviewer and a code
reviewer, which are different agents from the author, review each pull request.
Each review has a queue label and a pass label. The merge loop merges a pull
request only when it has both pass labels and its checks are green.

| Review | It checks | Queue label | Pass label |
| --- | --- | --- | --- |
| Standards | the rules of CONTRIBUTING.md, AGENTS.md and the constitution | `needs-standards-review` | `standards-reviewed` |
| Code | that the change is correct and complete | `needs-code-review` | `code-reviewed` |

## Route

| You are, or you ask | Read |
| --- | --- |
| The author: open a pull request, read a review, fix it | [author.md](references/author.md) |
| The standards reviewer | [standards-review.md](references/standards-review.md) |
| The code reviewer | [code-review.md](references/code-review.md) |
| The lead: route findings, wake reviewers, run the merge loop | [lead.md](references/lead.md) |

## Rules

1. **Never certify your own pull request.** Only a reviewer adds a pass label.
2. **A rule that no document states is not a finding.** Cite the file and the
   section of each standards finding. Ask the lead to write a new rule first.
3. **An exploitable finding never goes in a comment.** A comment is public. Send
   it to the lead, who makes a private draft advisory.
4. **Use the REST API.** The `gh pr` commands use GraphQL, and all the agents
   share one quota. Poll at most every 5 minutes. An API error is an unknown
   state, not a result.

The owner made this model on 27 November 2026. Before that, fixes merged with
one-off test functions and with changes that broke the standards. Their authors
labelled them as checked. The owner asked: "who is verifying it's okay?"
