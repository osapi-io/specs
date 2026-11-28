# Running commands

Each command that a provider runs goes through `internal/exec`. No code starts a
process directly. The reason is security, not order: two security advisories of
osapi were about how a command was built, and the two fixes are here.

```go
out, err := e.RunPrivilegedCmd(ctx, "sysctl", "-w", key+"="+value)
```

## Six ways to run something

| Method                      | For                                                                             |
| --------------------------- | ------------------------------------------------------------------------------- |
| `RunCmd`                    | the ordinary case                                                               |
| `RunCmdFull`                | a caller that supplies its own timeout in seconds, with stdout and stderr apart |
| `RunReadCmd`                | a read, with the timeout and the output limit of gohai                          |
| `RunPrivilegedCmd`          | a command that needs root                                                       |
| `RunPrivilegedCmdWithStdin` | a command that needs root **and** a secret                                      |
| `RunPrivilegedCmdFull`      | a command that needs root, with stdout, stderr and the exit code apart          |

`RunCmd`, `RunPrivilegedCmd` and `RunPrivilegedCmdWithStdin` call `RunCmdImpl`,
which is not an entry point. The others have their own run.

"Privileged" means sudo, when sudo is on. The command becomes an argument to
`sudo`. When sudo is off, the command runs as the user of the agent. Thus a
provider does not get root only because it asks for root.

## Ten minutes is a ceiling, not a fallback

People misunderstand this part most often. The documentation of osapi also had
it incorrect until somebody checked it.

`run` always wraps the context of the caller:

```go
ctx, cancel := context.WithTimeout(ctx, DefaultCommandTimeout)
```

`context.WithTimeout` comes from the context that it gets. Thus the deadline
that comes first applies. A caller that gives a shorter deadline gets the
shorter deadline. **A caller that wants more than ten minutes cannot get it**,
because this line is on each path through `run`. `Execute` and
`ExecuteWithStdin` both call `run`.

Thus `DefaultCommandTimeout` is not the fallback for a command that gave no
deadline. It is the maximum time for each command. If an operation really needs
twenty minutes, osapi stops it at ten. Only the deadline of the caller can make
the time shorter.

`RunCmdFull` and `RunPrivilegedCmdFull` do not go through `run`. `RunCmdFull`
takes a timeout in seconds and applies its own `context.WithTimeout`, so that
timeout is its ceiling. A timeout of 0 is `DefaultCommandTimeout`.
`RunPrivilegedCmdFull` always gives 0, so `docker exec` gets ten minutes. Until
osapi-io/osapi#1788, 0 was 30 seconds.

## Output stops at 1 MiB

Each run keeps at most `MaxCommandOutput`, 1 MiB, of the output of a command:
the combined output of `run`, and each of stdout and stderr of a full run. The
command runs to its end. osapi counts the bytes that it does not keep, and adds
a last line: `[N more bytes of output not kept]`.

Without the limit, `command exec -- yes` could fill the memory of the agent
before the timeout. The answer of a job goes into a NATS message, which cannot
hold more than that.

## A stopped command is an error

When the caller's context ends while the command runs, osapi kills the process
group, and the run returns the error of the context, with exit code -1. A
command that osapi killed does not look like a command that ran.

## A secret never reaches a command through its arguments

osapi logs the arguments. `run` logs the command name and its arguments. The
process table also shows them. Thus all of the arguments are public.

`RunPrivilegedCmdWithStdin` is for a command that needs a secret. The secret
goes to the standard input of the process, and **osapi never logs stdin.** The
doc comment on `ExecuteWithStdin` says so. `run` logs the arguments and the
output, but not stdin.

If a provider gives a password to `RunPrivilegedCmd`, the password goes into a
log file. GHSA-6gc6-px2x-q95j was the cost of that error. The stdin variant is
the fix.

## A caller's value is never parsed as an option

If a value starts with a dash and gets to a command without a guard, it becomes
a flag. The provider must prevent that before it calls this package, because
this package gives the arguments to the command without a change.

This is the other advisory, GHSA-7fjw-v3g9-326g. Because of it,
[providers](providers.md) states that validation on the request path does not
replace the validation of the provider. A value that was safe when osapi stored
it gets here later, and this package does not make it safe.

## Why a provider cannot go around it

The executor is an interface. Thus a provider gets an executor and does not
import `os/exec`. You can then test a provider without a real command. You can
also review how commands are built in one location, not in 212 provider files.

A provider that starts a process directly loses these things:

- the timeout ceiling
- the argument log
- the stdin path for secrets
- its own tests

Nothing in the build tells the provider about the loss.

## Where this connects

[Providers](providers.md) has the rules about arguments and secrets that a
provider must obey. It also tells what the file deployer does in place of
writing files directly.

[The job system](job-system.md) has the clock that a caller sees, and how osapi
reports a command that runs longer than it.

______________________________________________________________________

Written from `internal/exec/`.
