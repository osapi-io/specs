# Running commands

Every command a provider runs goes through `internal/exec`. Nothing spawns a
process directly, and the reason is not tidiness: two of osapi's security
advisories were about how a command was constructed, and both fixes live here.

```go
out, err := e.RunPrivilegedCmd(ctx, "sysctl", "-w", key+"="+value)
```

## Six ways to run something

| Method                       | For                                                       |
| ---------------------------- | --------------------------------------------------------- |
| `RunCmd`                     | the ordinary case                                         |
| `RunCmdInDir`                | the same, from a working directory                        |
| `RunCmdFull`                 | a caller supplying its own timeout in seconds             |
| `RunPrivilegedCmd`           | a command needing root                                    |
| `RunPrivilegedCmdWithStdin`  | a command needing root **and** a secret                   |
| `RunCmdImpl`                 | the implementation the others call                        |

"Privileged" means sudo when sudo is enabled: the command becomes an argument to
`sudo` rather than being invoked directly. When it is not enabled the command runs
as whatever the agent runs as, so a provider cannot assume it has root by asking
for it.

## Ten minutes is a ceiling, not a fallback

This is the part most likely to be misunderstood, including by osapi's own
documentation until it was checked.

`run` wraps the caller's context unconditionally:

```go
ctx, cancel := context.WithTimeout(ctx, DefaultCommandTimeout)
```

`context.WithTimeout` derives from the context it is given, so the effective
deadline is whichever comes first. A caller passing a shorter deadline gets the
shorter one. **A caller wanting longer than ten minutes cannot have it**, because
this line is on every path: `Execute` and `ExecuteWithStdin` both call `run`, and
nothing else runs a process.

So `DefaultCommandTimeout` is not the backstop for a command that supplied no
deadline. It is the maximum any command can be given. A long-running operation
that legitimately needs twenty minutes will be killed at ten, and the caller's own
deadline is the only thing that can make it shorter.

`RunCmdFull` takes a timeout in seconds and applies its own
`context.WithTimeout`, which then sits inside the ten-minute one. It can shorten
and cannot lengthen.

## A secret never reaches a command through its arguments

Arguments are logged. `run` logs the command name and its arguments, and they are
visible in the process table besides, so anything in them is public.

`RunPrivilegedCmdWithStdin` exists for the case where a command needs a secret.
The secret goes to the process's standard input, and **stdin is never logged.**
The doc comment on `ExecuteWithStdin` says so, and `run` logs arguments and output
and not stdin.

A provider that needs to pass a password and reaches for `RunPrivilegedCmd`
has put it in a log file. GHSA-6gc6-px2x-q95j is what that cost, and the stdin
variant is the fix.

## A caller's value is never parsed as an option

A value that begins with a dash and reaches a command unguarded becomes a flag.
The provider is responsible for preventing that before it calls anything here,
because this package passes arguments through.

This is the other advisory, GHSA-7fjw-v3g9-326g, and it is why
[providers](providers.md) states that validation on the request path does not
discharge the provider's own. A value that was safe when it was stored arrives
here later, and this package will not save it.

## Why a provider cannot go around it

The executor is an interface, so a provider takes one rather than importing
`os/exec`. That makes a provider testable without running anything, and it makes
command construction reviewable in one place rather than in 224 provider files.

A provider that spawns a process directly loses the timeout ceiling, the argument
logging, the stdin path for secrets, and its own testability, and nothing in the
build will tell it.

## Where this connects

The rules a provider owes about arguments and secrets, and what the file deployer
does instead of writing files directly, are [providers](providers.md).

The clock a caller sees and how a command outliving it is reported are
[the job system](job-system.md).

______________________________________________________________________

Written from `internal/exec/` rather than from a feature. No feature covers this
package, which is why the ten-minute ceiling was described as a fallback for
nearly a year.
