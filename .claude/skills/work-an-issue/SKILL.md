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

An issue is a claim that somebody made in the past. It keeps an intent when
nobody works on it ([Tracking](../../../CONSTITUTION.md#tracking)). Nothing
about it is current. The code changed, the dependency changed, and sometimes the
fix already merged and nobody closed the issue.

Thus the first step is never the fix.

Do not start an issue that has the `architecture` label unless the user names
it. Only the owner starts that work ([Labels](../../../CONTRIBUTING.md#labels)).

This skill ends at a merged pull request that closed the issue.
[org-status](../org-status/SKILL.md) finds and reports issues. This skill acts
on one.

## 1. Read it, then read the code

```bash
r=<repo>
n=<issue>
gh issue view "$n" --repo "osapi-io/$r" --json state,title,body,labels,createdAt
gh api "repos/osapi-io/$r/issues/$n/comments" -q '.[] | "\(.user.login): \(.body)"'
```

Read the comments before you make a plan. Usually the only comment is from a
greeting bot, and it says nothing. But a human comment can make the problem
smaller, or refuse an approach.

Then make sure that the claim is still true. Run what the issue gives. Do not
only read it and agree. For this reason, an issue here has the command that
found it ([Verification](../../../CONSTITUTION.md#verification)). There are
three answers, and each sends the work to a different location:

- **It occurs again.** Continue to step 2.
- **It does not occur again, and the fix merged.** Close it with the pull
  request that fixed it. Make no branch and no change. Step 6 has the write.
- **It does not occur again, and nothing fixed it.** Say so, with what you ran,
  and stop. A test that passed fifty times is evidence about the test run. It
  does not prove that the bug is gone. A flake is the case where these two look
  the same.

Before you open a branch, check if somebody already works on it:

```bash
gh pr list --repo "osapi-io/$r" --state open \
  --json number,closingIssuesReferences \
  -q '.[] | select(.closingIssuesReferences[].number == '"$n"') | .number'
```

If an open pull request names the issue, that is the work in progress of a
different person. Review it. Do not start a second one.

## 2. Size it

The rest of the work depends on this decision. Make it deliberately. Do not
continue on the path that started first.

**A direct fix** is one commit and its test, in one repository. It changes
nothing that a caller can see. Examples are an incorrect constant, a flake, a
tidy, an error with bad words, and a guard that nobody wrote. Make a branch and
fix it.

**A Spec Kit feature** is a change that does one of these things:

- changes what a caller sees
- touches a stated contract
- changes more than one repository
- needs a new page to be true

Run `/speckit-specify` with the issue as its input. The issue closes when the
pull request of the feature merges.

The constitution draws this line for a new issue, and it reads the same way for
work on an issue. Open an issue when the work is larger than the current change.
Fix it directly when it is not. Do not run the full specify, plan, tasks and
implement pipeline for a two-line timeout change. That costs more than the bug.

Two cases look like direct fixes but are not:

- A fix that makes a page in `components/` disagree with the code is two
  changes. The page gets its own change ([AGENTS.md](../../../AGENTS.md)).
- A fix that needs a new rule, not an existing rule, is a change to the corpus.
  It goes in this repository before it goes in the code.

## 3. Branch

Never work on `main`. A branch name here is the conventional-commit type, a
slash, and a kebab-case description of the change:

```bash
git checkout main && git pull
git checkout -b fix/kv-timeout-outruns-its-poll
```

A measurement of the organization found these types: `fix/`, `feat/`, `docs/`,
`chore/`, `ci/` and `test/`. The description tells what the change does, not
which issue asked for it. The issue number goes in the pull request, where
GitHub reads it.

## 4. Fix it, with the test that proves it

The test comes with the fix, in the same commit. It must be a test that fails
on the code before the fix. A test that you write after the fix, against the
fixed code, only proves that the code does what it now does.

For a flake, the test must fail on the old code each time that it runs enough
times, not one time in fifty. For a missing guard, the test uses the input that
got through.

Add nothing else. If you find an unrelated problem, it gets its own issue in the
repository where its fix goes, with the command that found it
([Tracking](../../../CONSTITUTION.md#tracking)). A larger change hides the fix
in
a diff about a different subject. This organization makes this error most
often.

## 5. Verify

```bash
mise exec -- go test -cover ./<each package that you changed>
```

Run only the checks that can find a problem in the change, as
[Check a change](../../../AGENTS.md#check-a-change) tells. CI runs the full
gate on the pull request. The full suite of osapi takes approximately ten
minutes, so do not run it. In specs, `mise exec -- just test` is fast, and it is
the gate.

Always run tools through `mise`. A bare `just` runs the version that is
installed globally. A change to a nested module under `examples/` also needs
`just go-mod-check`, because a bare `go test` does not tidy it. For a timing
bug, only a loop proves anything:

```bash
go test -run 'TestName/subtest' -count=50 -race ./pkg/...
```

CI has taught this organization two reasons not to believe a single run:

- `go-mod-check` names only the first untidy module that it finds. Thus one
  green result after one fix can still hide five more.
- A gomock expectation that asserts a timing property passes or fails by which
  of two events the scheduler gets to first. Thus one pass is a coin that showed
  heads.

Report the command and its output. "Tests pass" is a claim, not evidence.

## 6. Close it through the pull request

```bash
gh pr create --repo "osapi-io/$r" --fill --body "$(cat <<'EOF'
<what changed and why, with the evidence>

Closes #<n>
EOF
)"
```

`Closes #<n>` in the body closes the issue. People forget this step most often.
Without it, the fix merges and the issue stays open, and it looks like work that
remains. Thus a completed item shows again in each sweep.

Before you push to a branch, make sure that nobody already squash-merged it. A
squash writes the history again. Thus a commit that you push to a branch whose
pull request already merged is lost, and nothing reports it.

Each osapi-io repository permits squash and rebase, and forbids merge commits.
This was verified on all eight. Thus a merge is:

```bash
gh pr merge <pr> --squash --delete-branch
```

Then make sure that the two halves occurred, because the second does not always
come after the first:

```bash
gh pr view <pr> --repo "osapi-io/$r" --json state,mergedAt
gh issue view "$n" --repo "osapi-io/$r" --json state,stateReason
```

If an issue is still open after its pull request merged, close it by hand, and
name the pull request:

```bash
gh issue close "$n" --repo "osapi-io/$r" --comment "Fixed in #<pr>."
```

## Rules

1. **Make the problem occur again before you fix it.** The issue is a claim from
   the past. If you skip this, you can fix a bug that moved.
2. **Do not work on an exploitable problem in public.** An issue is public from
   the time that it exists. Thus a security finding is a draft advisory on the
   repository that it affects. Write the fix against the advisory, not on a
   public branch with a public pull request that names what it fixes.
3. **One issue, one change.** Side findings become their own issues. Agents
   break this rule most often, and they feel productive when they do.
4. **To close an issue is a write.** Close an issue because its fix merged, or
   because it does not occur now. Never close it only to make a list shorter.
5. **An archived repository is read-only.** `osapi-ui` and `osapi-sdk` refuse
   each write, also the close of a pull request. Thus nobody can work on an
   issue
   there without an unarchive first. A person must decide to bring the
   repository back. You do not make that decision.
