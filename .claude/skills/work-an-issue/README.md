# work-an-issue

Takes an open issue to a merged pull request that closed it. Answers "is this a
fix or a feature, does it still occur, and what closes the issue". Thus work on
an issue needs one prompt, not a new procedure each time.

[org-status] finds issues and reports them. This skill is the other end of that
arrow: its blocks end with `→ say "fix 179"`, and this is what that phrase runs.

## Install

You install nothing. The skill is in this repository. Each agent that reads
skills finds it when it works from the repository root. It needs the [gh] CLI
authenticated
against [osapi-io], a checkout of the repository the issue belongs to, and
[mise] for the recipes.

## Usage

Ask in plain language, or invoke it directly with `/work-an-issue`.

| Ask                              | You get                                                            |
| -------------------------------- | ------------------------------------------------------------------ |
| "fix nats-client 179"            | Reproduction, the fix with its test, a pull request that closes it  |
| "what would it take to fix 179?" | The sizing decision and the cause, without a branch                |
| an issue URL pasted on its own   | The same, for whichever repository it belongs to                   |
| "pick up the oldest open bug"    | The issue read first, then worked or reported as already fixed     |

## What it does

There are six steps:

1. Read the issue and its comments.
1. Make sure that the problem still occurs.
1. Decide if it is a direct fix or a Spec Kit feature.
1. Make a branch.
1. Fix it, with the test that proves it.
1. Close it through the pull request.

## What it is for

Four failures, three of them already on the record here.

**An issue is a claim from the past.** The code changed after it. The first
error is to fix what the issue describes, not what the code does now. Only a
test of the problem first finds that error.

**Without a decision, the size is an accident.** The full specify, plan, tasks
and implement pipeline for a two-line timeout change costs more than the bug. A
fix by hand to something that changes a stated contract leaves the contract
without a statement. Before this skill, nothing made that decision. Thus the
path that started first decided.

**People forget `Closes #n` most often.** Without it, the fix merges and the
issue stays open. Thus completed work shows in each sweep as work that remains.
`nats-client` #179 stayed open from 27 October with only a comment from the
greeting bot. That is the other half of the same problem: no path from a
reported issue to work on it.

**One green run is not evidence.** `go-mod-check` names only the first untidy
module that it finds. Thus one fix and one green line can hide five more. A mock
expectation that asserts a timing property is a coin toss. #179 is that case: a
20ms deadline against a 10ms poll interval. The ticker tick and the context
deadline occur at the same time, and `select` selects one.

## License

The [MIT](../../../LICENSE) License.

[gh]: https://cli.github.com
[mise]: https://mise.jdx.dev
[org-status]: ../org-status/README.md
[osapi-io]: https://github.com/osapi-io
