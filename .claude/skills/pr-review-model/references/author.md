# The author

You wrote the change. You open the pull request, put it in the queue of each
review, and fix what the reviewers find. You never add a pass label.

## 1. Open the pull request

- Open it ready, not as a draft.
- Give it a title of 50 characters or fewer. The squash merge makes the title
  the commit subject, and the subject has the 50/72 rule
  ([CONTRIBUTING.md](../../../../CONTRIBUTING.md), Branches and commits).
- When the change has a specs pull request, open that one first, and put
  `Specs: <url>` in the description. The component pull request merges only
  after the specs pull request merged ([AGENTS.md](../../../../AGENTS.md), Open a
  pull request).

Open it through REST:

```bash
gh api -X POST repos/osapi-io/$r/pulls \
  -f title="$title" -f head="$branch" -f base=main -f body="$body"
```

- A security fix is the exception to the specs pull request first. The code
  merges first, and its advisory is published. Then the specs pull request
  merges, with `Depends:` on the code pull request.
- When the change needs a pull request in a different repository to merge
  first, put a line `Depends: osapi-io/<repo>#<n>` in the description. The merge
  loop waits for that pull request.

## 2. Put it in both queues

```bash
gh api -X POST repos/osapi-io/$r/issues/$n/labels \
  -f 'labels[]=needs-standards-review' -f 'labels[]=needs-code-review'
```

## 3. Watch the comments

GitHub does not let an account request changes on its own pull request. All the
agents use one account. Thus a reviewer posts its result as a comment. A comment
that starts with "Standards review" or "Code review" is a result.

Read the comments through REST every 5 minutes:

```bash
gh api "repos/osapi-io/$r/issues/$n/comments?per_page=100" \
  -q '.[] | select(.body | test("^(Standards|Code) review")) | .body'
```

A result that came before your last push is of an old head. Do not fix it
again. Reply on the pull request with the commit that fixed each point.

A reviewer that passes the pull request writes "Standards review: approved
(head <sha8>)" or "Code review: approved (head <sha8>)". The SHA is the head
commit that it reviewed.

## When CI is slow

This rule is temporary. It applies only while the lead says that CI has a
backlog. Run the full gate of the repository on the head commit, then write:

```bash
gh api -X POST repos/osapi-io/$r/issues/$n/comments \
  -f body="Local gate: passed (head $sha8). <the command that you ran>"
```

The merge loop can then merge without waiting for the checks in the queue. It
never merges with a check that failed.

## 4. Fix the findings

Fix each point. Push only when the pull request is still open, because a squash
merge orphans a commit that comes after it. Then put the pull request back in
the queue of the review that failed.

Each push makes the approvals before it stale. An approval counts only when the
SHA in its comment is the current head. The date of a commit does not help,
because it is the time of the commit, not of the push. Thus after a push, both reviews run
again, and the merge loop puts the pull request back in each queue. Put it back
in the queue of the review that failed yourself:

```bash
gh api -X POST repos/osapi-io/$r/issues/$n/labels \
  -f 'labels[]=needs-code-review'
```

Do not argue with a finding in a new commit. When you think that a finding is
wrong, reply on the pull request with the file and the section of the rule, and
tell the lead.
