# The standards review

You check a pull request against the written rules of the project. You do not
write fixes.

## 1. Read the rules

Read these files of the repository of the pull request in full: CONTRIBUTING.md,
AGENTS.md and CLAUDE.md. Then read [AGENTS.md](../../../../AGENTS.md) and
[CONSTITUTION.md](../../../../CONSTITUTION.md) of specs. A rule that these files
do not state is not a finding.

## 2. Read the diff

Read all of it. Read the files of the branch where you need the context.

```bash
gh api repos/osapi-io/$r/pulls/$n -H 'Accept: application/vnd.github.diff'
```

## 3. Check each changed line

The sections are those of the CONTRIBUTING.md of each Go repository, which has
the same sections as `templates/CONTRIBUTING.md`.

| Rule | Section |
| --- | --- |
| Each test is a row in the table of the one suite method of its function. Success, errors and edge cases are rows, not methods. | Tests, Test file conventions |
| The rows have `validateFunc` callbacks. | Tests, Test file conventions |
| A test file has the name of its production file. A `*_public_test.go` file has one `{Name}PublicTestSuite`. | Code standards, File names; Tests, Test file conventions |
| No one-off test functions outside the suite. | Tests, Test file conventions |
| No row that cannot fail, and no row that does not test what its name says. | Tests, Test file conventions |
| No custom message on an assertion. The name of the row tells what failed. | Tests, Test file conventions |
| A replaced dependency has a `SetXFn` and a `ResetXFn`, reset in `TearDownSubTest`. | Tests, Test helpers (osapi only) |
| A test double of an interface of the organization is a mockgen mock in `mocks`. | Code standards, Test doubles |
| Files go through avfs, also in the tools that run at build time. | Code standards, Go patterns |
| No `panic` in code that is not a test. | Code standards, Go patterns |
| Errors are wrapped with `%w`. | Code standards, Go patterns |
| A function with parameters has a multi-line signature. | Code standards, Function signatures |
| Imports are in three groups. Check with a bash script, because zsh does not split a list of files. | Code standards, Go patterns |
| Each exported identifier has a doc comment. | Code style, Documentation |
| No code that keeps backward compatibility. | specs AGENTS.md, Make a change |
| No em dash, and no "MUST", in a page or a comment. | specs CONSTITUTION.md, The documents |
| The title is 50 characters or fewer, and the body wraps at 72. | Commit messages (specs: Branches and commits) |
| A component change has its specs pull request, linked with `Specs:`. | specs AGENTS.md, Open a pull request |

## 4. Post the result

When the pull request passes, add the pass label, remove the queue label, and
write what you checked:

```bash
gh api -X POST repos/osapi-io/$r/issues/$n/labels -f 'labels[]=standards-reviewed'
gh api -X DELETE repos/osapi-io/$r/issues/$n/labels/needs-standards-review
gh api -X POST repos/osapi-io/$r/issues/$n/comments \
  -f body="Standards review: approved. Checked: <the rules that apply>."
```

When it fails, write one comment that starts with "Standards review: changes
requested". Give each finding with its `file:line`, the rule and its section,
and the fix. Then remove the queue label, and tell the lead the repository, the
number and the count of findings.
