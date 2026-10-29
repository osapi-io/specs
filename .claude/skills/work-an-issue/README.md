# work-an-issue

Takes an open issue to a merged pull request that closed it. Answers "is this a
fix or a feature, does it still reproduce, and what closes the issue" so picking
one up is a prompt rather than a procedure reinvented each time.

[org-status] finds issues and reports them. This skill is the other end of that
arrow: its blocks end with `→ say "fix 179"`, and this is what that phrase runs.

## Install

Nothing to install. The skill lives in this repository and any skills-aware agent
working from the repository root finds it. It needs the [gh] CLI authenticated
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

Six steps: read the issue and its comments, establish it still reproduces, size
it as a direct fix or a Spec Kit feature, branch, fix it with the test that
proves it, and close it through the pull request.

## What it is for

Four failures, three of them already on the record here.

**An issue is a claim from the past.** The code moved under it. Fixing what the
issue describes rather than what the code now does is the first trap, and
reproducing first is the only thing that catches it.

**The sizing decision gets made by drifting.** Running specify, plan, tasks and
implement over a two-line timeout change costs more than the bug does, and
hand-fixing something that changes a stated contract leaves the contract
unstated. Nothing routed that choice before this skill, so it got made by
whichever path started first.

**`Closes #n` is the step that gets missed.** Without it the fix merges and the
issue stays open, so a finished piece of work keeps appearing in every sweep as
outstanding. `nats-client` #179 sat from 27 October with nothing on it but the
greeting bot, which is the other half of the same problem: no path from a
reported issue to a worked one.

**A single green run is not evidence.** `go-mod-check` names only the first
untidy module it finds, so one fix and one green line can hide five more. And a
mock expectation that asserts a timing property is a coin flip, which is what
#179 is: a 20ms deadline against a 10ms poll interval, so the ticker tick and
the context deadline land on the same instant and `select` picks one.

## License

The [MIT](../../../LICENSE) License.

[gh]: https://cli.github.com
[mise]: https://mise.jdx.dev
[org-status]: ../org-status/README.md
[osapi-io]: https://github.com/osapi-io
