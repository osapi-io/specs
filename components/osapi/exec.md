# Running commands

Each command that a provider runs goes through `internal/exec`. No code starts a
process directly. The reason is security, not order: two security advisories of
osapi were about how a command was built, and the two fixes are here.

```go
out, err := e.RunPrivilegedCmd(ctx, "sysctl", "-w", key+"="+value)
```

## Five ways to run something, and the one they share

| Method                      | For                                           |
| --------------------------- | --------------------------------------------- |
| `RunCmd`                    | the ordinary case                             |
| `RunCmdInDir`               | the same, from a working directory            |
| `RunCmdFull`                | a caller supplying its own timeout in seconds |
| `RunPrivilegedCmd`          | a command needing root                        |
| `RunPrivilegedCmdWithStdin` | a command needing root **and** a secret       |
| `RunCmdImpl`                | not an entry point: what the five above call  |

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
because this line is on each path. `Execute` and `ExecuteWithStdin` both call
`run`, and no other code runs a process.

Thus `DefaultCommandTimeout` is not the fallback for a command that gave no
deadline. It is the maximum time for each command. If an operation really needs
twenty minutes, osapi stops it at ten. Only the deadline of the caller can make
the time shorter.

`RunCmdFull` takes a timeout in seconds and applies its own
`context.WithTimeout`. That timeout is inside the ten-minute timeout. It can
make the time shorter. It cannot make the time longer.

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
