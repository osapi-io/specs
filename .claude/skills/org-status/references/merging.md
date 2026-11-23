# Merging the queue

First, get the repository set, as [SKILL.md](../SKILL.md) tells.

A request to triage Dependabot is a request to finish the queue: vet each pull
request, merge the clean ones, rebase the others and merge them. Clear a LOOK or
a false STOP yourself when the evidence clears it. Report the result, not a list
of commands for the user.

Then vet each pull request in the queue with [vetting.md](vetting.md). A STOP
leaves the queue. A LOOK also leaves it, until the reader clears it.

The `allowed-tools` of the skill permit the writes here. Thus they run without a
prompt in the invocation that asked for them. That permission lasts one turn. A
queue over many turns needs a new invocation of the skill. This is a feature,
not a problem: each turn states the intent again.

## Run it

```bash
.claude/skills/org-status/scripts/merge-queue.py --dry-run <owner/repo> <number> ...
.claude/skills/org-status/scripts/merge-queue.py <owner/repo> <number> ...
```

Use one repository for each call, with any owner. Read the plan of the dry run
first. It tells which pull requests merge immediately, which wait for a rebase,
and which it left out and why. The real run then does what the rest of this page
describes:

- It vets each pull request with `vet-pr.py`, and merges only a `CLEAN` one.
  Thus it reports a human pull request, and never merges it from here.
- It merges a pull request when its checks pass, if it has no lockfile or module
  file in common with a pull request that merged before it.
- It puts the others in sequence. It sends `@dependabot rebase`, then
  `recreate` if a conflict stays or Dependabot ignores it. Then it vets again,
  because a rebase can move a bump to a newer release. Then it waits for the
  checks, and merges.
- It compares each pull request with what merged on the base branch after the
  pull request was built. Thus a merge by hand, or in an earlier run, still
  forces the rebase.
- It does not touch a red pull request, and names the failed check.
- It puts a root `go.mod` bump last in a repository with nested modules.

It runs while the rebases and checks run. Start it in the background, and report
what it prints. Do not wait for it in the foreground.

Run the repositories in parallel, with one call for each. The snippets below
show what the script does. They are here to help you read a failure, and for a
step that the script cannot do, for example a tidy of the examples of a root
bump.

## Order

A merge moves the default branch. Then each other pull request is behind it.
Thus:

1. **Human PRs that are already green.** They have the work. Bumps are noise
   around them.
2. **Rebase the bumps** onto the new default branch.
3. **Merge the bumps that come back green.**

The other order rebases everything two times.

## Merge

```bash
gh pr merge <number> --repo "$repo" --squash --delete-branch
```

Squash is the convention here. Each commit on a default branch reads
`type: subject (#number)`. `--delete-branch` keeps [branches.md](branches.md)
short.

## Rebase a Dependabot PR

```bash
gh pr comment <number> --repo "$repo" --body "@dependabot rebase"
```

Dependabot force-pushes the branch, and CI runs again. `@dependabot recreate`
builds the branch again from the start. A `CONFLICTING` mergeable state usually
needs that.

## One repository at a time, all repositories at once

Repositories are independent. Work on them in parallel. The pull requests in one
repository often are not independent.

Two bumps that touch the same file cannot both merge from the state where they
were built. The first merge moves the default branch. The second is then based
on something that does not exist now. Thus it conflicts. Or worse, it merges
without a conflict and loses the edit of the first one. `mergeable` says `CLEAN`
for both until the first one merges. That is why this error is easy to make.

Thus decide by the files, not by the color of the check mark:

```bash
gh pr view <number> --repo "$repo" --json files -q '.files[].path'
```

- **No overlap.** Merge them together. Four bumps, each on a different
  `examples/<name>/go.mod`, have no effect on each other.
- **Overlap.** Put them in sequence, one merge at a time:
  1. Merge the first.
  2. `@dependabot rebase` the next, and wait for its checks.
  3. Merge it, and do it again.

In a repository with `examples/`, a root bump overlaps everything. A new version
of the parent module makes each example that resolves it untidy. Thus the root
bump touches `go.mod`, `go.sum` and each example. Merge it **last**, alone.

**A bump that touches no module file needs none of this.** A workflow pin, an
action version, a Dockerfile base image: nothing else reads those. Merge it
directly.

## A root bump needs its examples tidied in the same pull request

CI does not tidy now. Thus a root bump is not complete alone. The examples
resolve the parent module. When it moves forward, each example becomes untidy,
and `go-mod-check` fails on the branch. Tidy on the branch and commit:

```bash
gh pr checkout <number> --repo "$repo"
mise exec -- just go-mod && git commit -am "chore: tidy the example modules after the bump" && git push
```

`gh pr checkout` uses an existing local branch with the same name again. It can
leave you on an old commit and not tell you. Thus make sure that the head is the
head of the pull request before you trust a check:

```bash
git fetch origin "refs/heads/<branch>" && git checkout -B <tmp> FETCH_HEAD
```

**After you push to the branch, use `@dependabot rebase`.** It applies the bump
again on the current default branch, and keeps the commits that you added,
for example the tidy above.

`@dependabot recreate` builds the branch again from the start, and **discards**
those commits. Thus you must do each manual fix again on the new head. Use it
only when a rebase leaves the pull request `CONFLICTING`, and expect to do the
tidy again.

## Wait for checks, correctly

```bash
for i in $(seq 1 45); do
  s=$(gh pr checks <number> --repo "$repo" --json name,bucket 2>/dev/null)
  if [ -n "$s" ] && echo "$s" | jq -e 'length > 0 and all(.[]; .bucket != "pending")' >/dev/null 2>&1; then
    break
  fi
  sleep 20
done
```

The `length > 0` is necessary. Immediately after a push, GitHub has no check
runs. Thus the array is empty, and `all` over an empty array is always true.
Without that guard, the loop stops immediately and reports "no checks
reported". That looks exactly like a repository with no CI.

## A rebase does not fix a red bump

`mergeable` and the check rollup answer different questions. If the checks of a
bump fail, read the failure first. A rebase does not fix the usual causes here:

- **`go-mod-check` failed.** The bump left the module untidy. Or the committed
  root module was already untidy, because `go get -tool` moved the golangci-lint
  dependencies upstream. If CI runs again on the same content, it fails the same
  way. Fix it on the branch:

  ```bash
  gh pr checkout <number> --repo "$repo"
  mise exec -- just go-mod && git commit -am "chore: tidy modules" && git push
  ```

  When the default branch is untidy, tidy it first, in its own pull request.
  Each bump stays red until that merges.

- **A real upstream break.** The log names a package and a line. The reader
  decides what to do. A rebase does not fix it.

Read the failure before you queue a rebase:

```bash
gh pr checks <number> --repo "$repo" --json name,bucket,link \
  -q '.[] | select(.bucket=="fail") | "\(.name)\t\(.link)"'
gh api "/repos/$repo/actions/jobs/<job id>/logs" |
  grep -iE "error:|FAIL|\.go:[0-9]+:"
```

`gh run view --log-failed` prints the git cleanup after the job, not the failed
step. It looks like output, but it tells nothing.

## Never

- **Merge, rebase or check out a pull request that nobody vetted.**
- **Merge red.** A bump is a convenience. A broken default branch is not.
- **Merge a human PR that nobody read**, only because a sweep listed it as
  green.
  Report that it is ready, and let the reader decide.
- **Force past a failed required check.**
