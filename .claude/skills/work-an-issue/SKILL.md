---
name: work-an-issue
description: Pick up an open issue in an osapi-io repository and take it to a merged pull request. Decides whether the issue is a direct fix or a Spec Kit feature, verifies the issue still reproduces before anything is changed, branches, fixes with the test that proves it, runs the repository's own gate, and closes the issue through the pull request. Use when asked to fix, work, take, pick up, start or handle an issue or a bug by number, when asked what it would take to fix one, when handed an issue URL, and after a sweep reports an issue worth acting on.
compatibility: Requires the gh CLI authenticated against osapi-io, a checkout of the repository the issue belongs to, and mise for running the repository's recipes.
allowed-tools:
  - Bash(gh pr create:*)
  - Bash(gh pr merge:*)
  - Bash(gh issue close:*)
  - Bash(gh issue comment:*)
license: MIT
metadata:
  author: osapi-io
  source: https://github.com/osapi-io/specs
---

# Work an issue

An issue is a claim somebody made in the past, kept so the intent survived being
put down ([Tracking](../../../CONSTITUTION.md#tracking)). Nothing about it is
current. The code moved, the dependency moved, and sometimes the fix already
merged and nobody closed the issue.

So the first step is never the fix.

This skill ends at a merged pull request that closed the issue. Finding issues
and reporting them is [org-status](../org-status/SKILL.md); this one acts on one.

## 1. Read it, then read the code

```bash
r=<repo>
n=<issue>
gh issue view "$n" --repo "osapi-io/$r" --json state,title,body,labels,createdAt
gh api "repos/osapi-io/$r/issues/$n/comments" -q '.[] | "\(.user.login): \(.body)"'
```

Read the comments before planning anything. A greeting bot is the common case
and says nothing, but a human comment may have narrowed the problem or rejected
an approach already.

Then establish the claim still holds, by running what the issue carries rather
than by reading and agreeing. An issue here carries the command that found it
for exactly this reason
([Verification](../../../CONSTITUTION.md#verification)). Three answers, and each
sends the work somewhere different:

- **It reproduces.** Carry on to step 2.
- **It does not reproduce and the fix merged.** Close it against the pull
  request that fixed it. No branch, no change. Step 6 has the write.
- **It does not reproduce and nothing fixed it.** Say so with what you ran, and
  stop. A test that passed fifty times is evidence about the test run, not proof
  the bug is gone, and a flake is the case where those two look identical.

Check whether anything is already in flight before opening a branch:

```bash
gh pr list --repo "osapi-io/$r" --state open \
  --json number,closingIssuesReferences \
  -q '.[] | select(.closingIssuesReferences[].number == '"$n"') | .number'
```

An issue already named by an open pull request is somebody's work in progress.
Review it rather than starting a second one.

## 2. Size it

This is the decision the rest of the work hangs on, and the one to make
deliberately rather than by drifting into whichever path started first.

**A direct fix** is one commit plus its test, in one repository, changing nothing
a caller can see. A wrong constant, a flake, a tidy, an error that reads badly, a
guard that was never written. Branch and fix it.

**A Spec Kit feature** is anything that changes what a caller sees, touches a
stated contract, spans repositories, or needs a page written to be true.
`/speckit-specify` with the issue as its input, and the issue closes when the
feature's pull request merges.

The constitution draws this line for filing an issue, and it reads the same way
for working one: open an issue when the work is larger than the change in hand,
fix it directly when it is not. The failure to avoid is running the whole
specify, plan, tasks, implement pipeline over a two-line timeout change, which
costs more than the bug does.

Two cases that look like direct fixes and are not. A fix whose page in
`components/` now disagrees with the code is two changes, and the page is its own
([AGENTS.md](../../../AGENTS.md)). A fix that needs a new rule stated rather than
an existing one obeyed is a corpus change, so it belongs in this repository
before it belongs in the code.

## 3. Branch

Never on `main`. Branch names here are the conventional-commit type, a slash, and
a kebab-case description of what changes:

```bash
git checkout main && git pull
git checkout -b fix/kv-timeout-outruns-its-poll
```

Measured across the organization, the types in use are `fix/`, `feat/`, `docs/`,
`chore/`, `ci/` and `test/`. The description says what the change does, not which
issue asked for it: the issue number belongs in the pull request, which is where
GitHub reads it.

## 4. Fix it, with the test that proves it

The test comes with the fix in the same commit, and it has to be a test that
would have failed before it. A test written after the fix, against the fixed
code, proves the code does what it now does.

For a flake, that means the test fails reliably on the old code when run enough
times, rather than failing once in fifty. For a missing guard, it means the
input that got through.

Nothing else rides along. An unrelated thing found on the way is its own issue
in the repository it lands in, with the command that found it
([Tracking](../../../CONSTITUTION.md#tracking)). Widening the change buries the
fix in a diff about something else, and that is the part this organization gets
wrong most often.

## 5. Verify

```bash
mise exec -- just test
```

Through `mise`, always. A bare `just` resolves to whatever version is installed
globally, and a bare `go test` skips `go-mod-check` and the other recipes the
gate runs, which is how an untidy nested module reaches CI.

`just test` is the gate and it is not optional. A targeted loop is an addition to
it, never a replacement, and for a timing bug it is the only thing that
establishes anything:

```bash
go test -run 'TestName/subtest' -count=50 -race ./pkg/...
```

Two things CI has already taught this organization about believing a single run.
`go-mod-check` names only the first untidy module it finds, so one green line
after one fix can still be hiding five more. And a gomock expectation that
asserts a timing property passes or fails on which of two events the scheduler
reaches first, so one pass is a coin landing heads.

Report the command and its output. "Tests pass" is a claim rather than evidence.

## 6. Close it through the pull request

```bash
gh pr create --repo "osapi-io/$r" --fill --body "$(cat <<'EOF'
<what changed and why, with the evidence>

Closes #<n>
EOF
)"
```

`Closes #<n>` in the body is what closes the issue, and it is the step most often
missed. Without it the fix merges and the issue sits open looking like
outstanding work, which is how a done thing keeps appearing in every sweep.

Before pushing to any branch, confirm it has not already been squash-merged. A
squash rewrites history, so a commit pushed to a branch whose pull request
already merged is orphaned and nothing reports it as lost.

Every osapi-io repository allows squash and rebase and forbids merge commits
(verified across all eight), so merging is:

```bash
gh pr merge <pr> --squash --delete-branch
```

Then confirm both halves landed, because the second does not always follow the
first:

```bash
gh pr view <pr> --repo "osapi-io/$r" --json state,mergedAt
gh issue view "$n" --repo "osapi-io/$r" --json state,stateReason
```

An issue still open after its pull request merged is closed by hand, with the
pull request named:

```bash
gh issue close "$n" --repo "osapi-io/$r" --comment "Fixed in #<pr>."
```

## Rules

1. **Reproduce before fixing.** The issue is a claim from the past, and the cost
   of skipping this is a fix for a bug that moved.
2. **Nothing exploitable is worked in the open.** An issue is public from the
   moment it exists, so a security finding is a draft advisory on the repository
   it affects, and the fix is written against the advisory rather than against a
   public branch and a public pull request that names what it fixes.
3. **One issue, one change.** Side findings become their own issues. This is the
   rule agents break, and they break it while feeling productive.
4. **Closing is a write.** An issue is closed because its fix merged or because
   it no longer reproduces, never to shorten a list.
5. **An archived repository is read-only.** `osapi-ui` and `osapi-sdk` reject
   every write, closing a pull request included, so an issue there cannot be
   worked without unarchiving first. That is a decision to bring back, not one to
   make.
