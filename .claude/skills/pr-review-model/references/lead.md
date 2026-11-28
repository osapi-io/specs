# The lead

You coordinate the authors and the reviewers. You do not review, and you do not
add a pass label.

## Route the findings

When a reviewer tells you about a finding, send it to the agent that opened the
pull request. Give the repository, the number and the comment to read. When you
do not know which agent opened it, read the branch name and the description.

## Wake the reviewers

Some agents cannot wait between two rounds. Such a reviewer does one round and
stops. Watch the queue, and start the reviewer again when a pull request is in
it:

```bash
for r in $repos; do
  gh api "repos/osapi-io/$r/issues?state=open&labels=needs-standards-review" \
    -q '[.[] | select(.pull_request)] | length'
done
```

Send an advisory fix to the front of the queue. Keep the time short between its
public pull request and its published advisory.

## Sweep the queue

Put each open pull request that is not a draft, and that has no review yet, in
both queues. Do not queue a pull request again when its last result asks for
changes and its author pushed nothing since.

## Run the merge loop

The loop merges a pull request when each of these is true:

- It has both `standards-reviewed` and `code-reviewed`.
- It is not a draft.
- `mergeable_state` is `clean`.
- Each check run of its head commit is `completed`, with no `failure`,
  `cancelled` or `timed_out`, and it has at least one check run. While CI has a
  backlog, a "Local gate: passed (head <sha8>)" comment for the current head
  can replace the checks that are still in the queue. A failed check always
  stops the merge.
- Each pass label is current: the newest "Standards review: approved (head
  <sha8>)" and "Code review: approved (head <sha8>)" comments name the
  current head commit.
- When its description has `Specs: <url>`, that specs pull request merged. A
  specs pull request that closed without a merge does not count.
- When its description has a line `Depends: osapi-io/<repo>#<n>`, that pull
  request merged.

A security fix reverses the order of the specs pull request. Its code pull
request has no `Specs:` line and merges first. Its specs pull request has
`Depends:` on the code pull request.

A pass label whose approval names a different head is stale. Do not compare
dates: the date of a commit is the time of the commit, not of the push. The loop removes it
and puts the pull request back in the queue of that review:

```bash
gh api -X DELETE repos/osapi-io/$r/issues/$n/labels/code-reviewed
gh api -X POST repos/osapi-io/$r/issues/$n/labels -f 'labels[]=needs-code-review'
```

It merges with a squash through REST, then deletes the branch:

```bash
gh api -X PUT repos/osapi-io/$r/pulls/$n/merge -f merge_method=squash
gh api -X DELETE repos/osapi-io/$r/git/refs/heads/$branch
```

## The API quota

All the agents use one GitHub account, so they share its quota.

- Use the REST API (`gh api`). The `gh pr` commands use GraphQL. On 27 November
  2026 the watchers of many agents used up the GraphQL quota for one hour.
- Poll at most every 5 minutes, also in the merge loop.
- An API error is an unknown state. Try again in the next round. Never read an
  error as a merge, a pass or a failure.
- Check the quota with `gh api rate_limit`.
- GitHub also has a secondary limit on content, such as comments and labels. Do
  not post many comments in a short time. Wait some seconds between two
  comments, and wait one minute when GitHub refuses one.
