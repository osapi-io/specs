# Least privilege

A plan, partly built. The agent runs as root today. This page records how it
runs as an `osapi` user that can do only what its enabled behaviors allow. Each
part moves into the subject page it belongs to when it is built, and this page
goes when the last part is built.

## Who the design protects against

Two attackers, and the design makes a different promise to each.

**A job sender** holds an API token or NATS credentials. The sender can only
queue jobs. The agent validates each job before it acts, so the sender can do
what the enabled behaviors allow and nothing more. Today the sender gets more:
command exec and docker exec run what the job says, as root.

**A taken-over agent** is code that runs as the `osapi` user, for example
through a bug in the agent. It skips the agent's validation and uses the agent's
grants directly. A grant is safe only when it is still safe without the agent's
checks.

The second attacker is why a narrow sudoers line is not enough on its own. With
`sysctl -p /etc/sysctl.d/osapi-*.conf` allowed, a taken-over agent writes
`kernel.core_pattern=|/tmp/x` into that directory, applies it, and the kernel
runs `/tmp/x` as root at the next crash. Every grant on this page is checked
against that attacker. A behavior whose grants are root whatever we do, such as
package install or user management, says so.

## Order of preference

For each operation that needs privilege, use the first that works:

1. **The agent's own files, or one narrow capability.** No sudo.
2. **A request to a systemd daemon over D-Bus.** hostnamed, timedated, logind
   and systemd itself run as root outside the agent's sandbox. Hostname,
   timezone, reboot and service actions go this way.
3. **sudo, for one privileged step of one behavior.** Only the steps below.

polkit can authorize step 2 without sudo. But polkitd is not on each
distribution, and it has two rule formats. Thus it is not the baseline.

## Privileged steps

A behavior declares the work that needs root as a privileged step. A privileged
step is a typed function that runs as root. sudo and the step both check its
arguments.

```go
behavior.Privileged("apply", Apply).
	Describe("Write osapi-<key>.conf and set the value in the kernel").
	Arg("key", `[a-z0-9_.-]+`).
	Arg("value", `[A-Za-z0-9_. -]{1,64}`).
	Refuses("kernel.core_pattern", "kernel.modprobe", "kernel.usermodehelper.*").
	Writes("/etc/sysctl.d/osapi-*.conf").
	Runs("sysctl"),
```

A write method calls `Escalate(ctx, "apply", input)`. When the agent is root,
`Escalate` calls `Apply`. When it is not, `Escalate` runs
`sudo /usr/bin/osapi agent privileged sysctl apply <key> <value>`. That command
is hidden from `--help`, and only sudo runs it. It decodes the arguments, checks
the patterns and the `Refuses` list again, and calls `Apply`. The same Go code
runs on the two sides of sudo. Thus root still makes the checks that a
taken-over agent skips, and the agent cannot skip them there.

`RootEquivalent()` marks a step that no pattern can make safe. The docs page of
the behavior says so, and the operator turns it on knowingly.

`Privileged` replaces `behavior.Sudo`, which names a program and nothing else.
Today only sysctl and managedfile declare `Sudo`. managedfile becomes a library
that `Apply` calls, because the agent no longer writes `/etc/sysctl.d` itself.

**The fake host enforces the declaration.** A behavior test fails when a method
writes a path that only root can write, outside a privileged step. It also fails
when a method runs a program that only root can run there. A sudo call that does
not match a declared step fails too. Thus the declaration and the code cannot
become different.

## What each behavior puts on a host

Two files per behavior that has privileged steps, both rendered from the
declaration:

| File                                                              | Contents                                                                                                                                                          |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/etc/sudoers.d/osapi-<behavior>`                                 | One anchored rule per step: `osapi ALL=(root) NOPASSWD: ^/usr/bin/osapi agent privileged sysctl apply [a-z0-9_.-]+ [A-Za-z0-9_. -]{1,64}$`                        |
| `/etc/systemd/system/osapi-agent.service.d/osapi-<behavior>.conf` | The step's `Writes` as `ReadWritePaths=`, and any sandbox setting the step must relax. sysctl turns off `ProtectKernelTunables`, because `/proc/sys` is under it. |

A program that sudo runs stays in the agent's sandbox. Root does not escape
`ProtectSystem=strict`, so the unit must open each path a step writes. Opening
it in the sandbox does not let the `osapi` user write there: the directory is
still root-owned, and the agent does not hold `CAP_DAC_OVERRIDE`. Only the step,
as root, writes.

systemd adds up `ReadWritePaths` across drop-ins, so each behavior's file stands
alone. The base unit, `osapi-agent.service`, is static: `User=osapi`,
`ProtectSystem=strict`, the hardening settings, and the agent's own state in
`/var/lib/osapi` and `/etc/osapi/pki`.

The anchored `^...$` rule is a regular expression, which needs sudo 1.9.10 or
later. A plain sudoers `*` matches spaces, so `osapi-*.conf` also matches an
extra argument. The lab has Ubuntu 24.04 (1.9.15), Debian 13 (1.9.16), Fedora 42
(1.9.15) and macOS (1.9.17).

### Rendering them

`behavior get` renders both. They are part of what the behavior is, like its
methods. `--section` prints one part of `get`, so the default output stays a
short summary and never prints the files:

```sh
osapi behavior get --name sysctl                       # the summary, with a short Privileges part
osapi behavior get --name sysctl --section privileges  # the steps, what they write, run and refuse
osapi behavior get --name sysctl --section sudoers     # the sudoers file, styled to read
osapi behavior get --name sysctl --section systemd     # the drop-in, styled to read
osapi behavior get --name sysctl --section sudoers --json
# {"path": "/etc/sudoers.d/osapi-sysctl", "content": "..."}
```

The text output is styled for a person: headings, indents and color. It is not
the file. The file is the `content` field of the JSON, and installs use that.

The section names are the headings `get` prints today, `behavior`, `uses`,
`used-by`, `methods`, `types`, `settings` and `telemetry`, plus `privileges`,
`sudoers` and `systemd`. Without `--section`, `--json` gives every part,
`privileged`, `root_equivalent`, `sudoers` and `systemd` included.

The rule names the agent user and the binary path. They default to `osapi` and
`/usr/bin/osapi`, and `--agent-user` and `--binary` change them. `get` reads no
config, so its output depends only on the binary and the flags.

### Installing them

The admin installs them. The agent never writes its own grants.

```sh
osapi behavior get --name sysctl --section sudoers --json | jq -r '.content' > /tmp/osapi-sysctl
sudo visudo -cf /tmp/osapi-sysctl
sudo install -m 0440 -o root -g root /tmp/osapi-sysctl /etc/sudoers.d/osapi-sysctl

sudo mkdir -p /etc/systemd/system/osapi-agent.service.d
osapi behavior get --name sysctl --section systemd --json | jq -r '.content' \
  | sudo tee /etc/systemd/system/osapi-agent.service.d/osapi-sysctl.conf
sudo systemctl daemon-reload && sudo systemctl restart osapi-agent
```

`visudo -cf` comes first because a file in `sudoers.d` with a syntax error
breaks sudo for every user on the host. Ansible does the same with `copy` and
`validate: visudo -cf %s`. To turn a behavior off, remove its two files.

### macOS

launchd has no sandbox, so a behavior brings only its sudoers file, in
`/private/etc/sudoers.d`. The plist runs the agent with `UserName=osapi`, and it
is static. sysctl returns `ErrUnsupported` on macOS today, so its first
privileged step is Linux only.

## Checks

**`behavior validate`** sends probes to the rendered rule of each step, and to
the checks of the step. The probes are a space in an argument, an extra
argument, `;`, `|`, `../`, a refused value and a value that is too long. If a
probe gets through, that is a finding, and `just test` fails on it. `--json`
names the step and the probe:

```json
{"behavior": "sysctl", "step": "apply", "rule": "probe-passed",
 "probe": "net.x 1 kernel.core_pattern=|/tmp/x",
 "message": "an extra argument matches the sudoers pattern"}
```

**Preflight** fails the agent only when sudo cannot run without a password at
all. A program with no rule, or a missing capability, is a warning, because it
fails only the operations that need it. It lists the rules once with
`sudo -n -l`. It does not check each program with `sudo -l <program>`, because
that fails for a rule that limits the arguments.

## Command exec and docker exec

Off by default. The agent refuses the job unless `agent.command.enabled` is
true, so a forged NATS message is refused too, not only an API call. Either one
is a root shell for a job sender when the agent is root, and near-root when it
is not. A missing operation becomes a behavior, which is typed, validated and
safe to run twice.

## Skills

The skill that builds a behavior asks first whether a write needs root. If it
does, the skill declares a privileged step, never sudo in the write, and runs
`behavior validate --json` until it reports nothing.

A new skill, `break-a-behavior`, reads
`behavior get --section privileges --json` and tries to escape each rule. Each
escape it finds becomes a probe in `behavior validate`.

## Hand-written providers

They stay as they are and need root. An audit of them under `User=osapi` and
`ProtectSystem=strict` found the reads work, and most writes do not:

| Works unprivileged                                                     | Fails                                                                                    |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Reads: services, NTP, timezone, packages, DNS, routes, logs, ping      | cron (`/etc/cron.d`), service unit files (`/etc/systemd/system`)                         |
| hostname, timezone, power and service actions, through sudo over D-Bus | certificates (`/usr/local/share/ca-certificates`), NTP sources (`/etc/chrony/sources.d`) |
| process signal, with `CAP_KILL`                                        | netplan (`/etc/netplan`, `/run`), packages, users and groups, SSH keys (`ProtectHome`)   |

Some sudo grants they use are root whatever the arguments: `chown` of any path,
`apt-get install`, `systemctl start` of any unit, `useradd -u` and `-G`,
`chpasswd -e`. A provider gets least privilege when it moves to a behavior,
which is one more reason to move it.

## Not planned yet

AppArmor, as an optional profile rendered from the same `Writes` and `Runs`. It
can only remove permissions. Thus it limits a root agent, but it does not
replace sudo. SELinux, when somebody asks: its rules are labels, not paths, and
harder to render. polkit, as above.

## Order of work

1. Done: preflight runs one `sudo -n -l` and gives warnings, not a refusal
   (osapi #693, #694).
2. Command exec and docker exec off by default.
3. `Privileged`, `Escalate` and `osapi agent privileged`, with sysctl first. The
   silent apply failure is fixed (osapi #692).
4. The probes in `behavior validate`; `--section`, the files and the flags in
   `behavior get`.
5. The base unit, the `osapi` user and the files for each behavior, in Packer
   and osapi-lab. Prove them on the lab. A sysctl set must work. A
   `kernel.core_pattern` attempt and an extra argument must fail.
6. One customer page that replaces `architecture/security.md`'s privilege part
   and `features/agent-hardening.md`, whose sudoers examples grant root.
7. The skills.

Two problems found during this work are fixed. The agent no longer replaces a
key that it cannot read (osapi #695). `osapi client agent remove` removes the
key of an enrolled agent (osapi #696).

## Where this connects

[Running commands](exec.md) tells what runs a command and when sudo applies.
[Behaviors](behaviors.md) has the declarations that the steps join.
[Moving domains to behaviors](behavior-migration.md) has the order of the
domains. [Agent identity](agent-identity.md) tells which messages the controller
believes. That is a different question from what the agent can do.

______________________________________________________________________

Written from `internal/agent/preflight.go`, `internal/exec/`,
`internal/behaviors/sysctl/` and a by-hand run on the lab's debian-1.
