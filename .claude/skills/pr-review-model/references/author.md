# The author

You wrote the change. You open the pull request, put it in the queue of each
review, and fix what the reviewers find. You never add a pass label.

## 1. Open the pull request

- Open it ready, not as a draft.
- Give it a title of 50 characters or fewer. The squash merge makes the title
  the commit subject, and the subject has the 50/72 rule
  ([CONTRIBUTING.md](../../../../CONTRIBUTING.md), Commit messages).
- When the change has a specs pull request, open that one first, and put
  `Specs: <url>` in the description ([AGENTS.md](../../../../AGENTS.md), Open a
  pull request).

Open it through REST:

```bash
gh api -X POST repos/osapi-io/$r/pulls \
  -f title="$title" -f head="$branch" -f base=main -f body="$body"
```

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

## 4. Fix the findings

Fix each point. Push only when the pull request is still open, because a squash
merge orphans a commit that comes after it. Then put the pull request back in
the queue of the review that failed, and only that one:

```bash
gh api -X POST repos/osapi-io/$r/issues/$n/labels \
  -f 'labels[]=needs-code-review'
```

Do not argue with a finding in a new commit. When you think that a finding is
wrong, reply on the pull request with the file and the section of the rule, and
tell the lead.
