# Merging the queue

Resolve the repository set first, per [SKILL.md](../SKILL.md).

The writes here are granted by the skill's own `allowed-tools`, so they run
without a prompt during the invocation that asked for them. That grant lasts
one turn. A queue spanning several turns needs the skill invoked again, which
is a feature rather than a nuisance: each turn re-states the intent.

## Order

Merging moves the default branch, which puts every other pull request behind
it. So:

1. **Human PRs that are already green.** They carry the work; bumps are noise
   around them.
2. **Rebase the bumps** onto the new default branch.
3. **Merge the bumps that come back green.**

The other order rebases everything twice.

## Merge

```bash
gh pr merge <number> --repo "osapi-io/$r" --squash --delete-branch
```

Squash is the house style: every commit on a default branch here reads
`type: subject (#number)`. `--delete-branch` is what keeps
[branches.md](branches.md) short.

## Rebase a Dependabot PR

```bash
gh pr comment <number> --repo "osapi-io/$r" --body "@dependabot rebase"
```

Dependabot force-pushes the branch and CI re-runs. `@dependabot recreate`
rebuilds the branch from scratch instead, which is what a `CONFLICTING`
mergeable state usually needs.

## One repository at a time, all repositories at once

Repositories are independent: work them in parallel. Pull requests inside one
repository often are not.

Two bumps that touch the same file cannot both be merged from the state they
were built in. The first merge moves the default branch and the second is now
based on something that no longer exists, so it conflicts — or worse, merges
cleanly and drops the first one's edit. `mergeable` says `CLEAN` for both right
up until the first one lands, which is what makes this easy to get wrong.

So decide by the files, not by the colour of the tick:

```bash
gh pr view <number> --repo "osapi-io/$r" --json files -q '.files[].path'
```

- **No overlap** — merge them together. Four bumps each touching a different
  `examples/<name>/go.mod` do not interact.
- **Overlap** — serialize, one merge at a time:
  1. merge the first
  2. `@dependabot rebase` the next, and wait for its checks
  3. merge it, and repeat

A root bump overlaps everything in a repository with `examples/`: moving the
parent module's version leaves every example that resolves it untidy, so the
root bump touches `go.mod`, `go.sum` and each example. Merge it **last**, alone.

**A bump that touches no module file needs none of this.** A workflow pin, an
action version, a Dockerfile base image: nothing else is reading those, so merge
it outright.

## A root bump needs its examples tidied in the same pull request

Once CI stops tidying, a root bump is not complete on its own. The examples
resolve the parent module, so advancing it leaves each of them untidy and
`go-mod-check` fails on the branch. Tidy on the branch and commit:

```bash
gh pr checkout <number> --repo "osapi-io/$r"
mise exec -- just go-mod && git commit -am "chore: tidy the example modules after the bump" && git push
```

`gh pr checkout` reuses an existing local branch of the same name and will
silently leave you on a stale commit, so confirm the head matches the pull
request before trusting what a check tells you:

```bash
git fetch origin "refs/heads/<branch>" && git checkout -B <tmp> FETCH_HEAD
```

**Pushing to a Dependabot branch takes it away from Dependabot.** It ignores
`@dependabot rebase` on a branch carrying commits it did not write, silently —
no comment, no refusal. Use `@dependabot recreate` there instead, which rebuilds
the branch from scratch and discards the manual commits, then redo the tidy on
the new head.

## Wait for checks, correctly

```bash
for i in $(seq 1 45); do
  s=$(gh pr checks <number> --repo "osapi-io/$r" --json name,bucket 2>/dev/null)
  if [ -n "$s" ] && echo "$s" | jq -e 'length > 0 and all(.[]; .bucket != "pending")' >/dev/null 2>&1; then
    break
  fi
  sleep 20
done
```

The `length > 0` is load-bearing. Immediately after a push GitHub has
registered no check runs, so the array is empty, and `all` over an empty array
is vacuously true. Without that guard the loop exits at once and reports "no
checks reported", which reads exactly like a repository that has no CI.

## A rebase does not fix a red bump

`mergeable` and the check rollup answer different questions. A bump whose
checks fail needs the failure read first, because the common causes here are
not fixed by rebasing:

- **`go-mod-check` failed.** Either the bump left the module untidy, or the
  committed root module was already untidy because `go get -tool` moved the
  golangci-lint dependencies upstream. Re-running CI on the same content fails
  the same way. Fix it on the branch:

  ```bash
  gh pr checkout <number> --repo "osapi-io/$r"
  mise exec -- just go-mod && git commit -am "chore: tidy modules" && git push
  ```

  When the default branch is the untidy one, tidy that first in its own pull
  request: every bump stays red until it lands.

- **A genuine upstream break.** The log names a package and a line. That is
  the reader's call, not a rebase.

Read the failure before queuing a rebase:

```bash
gh pr checks <number> --repo "osapi-io/$r" --json name,bucket,link \
  -q '.[] | select(.bucket=="fail") | "\(.name)\t\(.link)"'
gh api "/repos/osapi-io/$r/actions/jobs/<job id>/logs" |
  grep -iE "error:|FAIL|\.go:[0-9]+:"
```

`gh run view --log-failed` prints the post-job git cleanup rather than the
failing step, which looks like output and says nothing.

## Never

- **Merge red.** A bump is convenience; a broken default branch is not.
- **Merge a human PR nobody has read** because a sweep listed it as green.
  Report it as ready and let the reader decide.
- **Force past a failing required check.**
