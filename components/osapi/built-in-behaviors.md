# Built-in behaviors

Each operation on a node of osapi is a [behavior](behaviors.md). This page has
the decisions in the behaviors that osapi ships: why each one reads or writes as
it does, and what a test on a real host found. The definition of a behavior, and
the docs page that osapi generates from it, tell what the behavior does. This
page tells why.

Each behavior replaced a hand-written domain. sysctl was the first
(osapi-io/osapi#731), and command was the last (osapi-io/osapi#1113). Where a
behavior answers differently from the domain that it replaced, this page says
so.

## The reads of a node

uptime, os, memory, load and disk moved together. Each one reads through
`host.Host`, not gopsutil, so that the fake host can run their examples.
hostname moved with them. Its `update` runs only on the Debian family, with
`.On`.

`status` is the summary of a node, at `GET /api/node/{hostname}/status`
(osapi-io/osapi#945). It requires the hostname, uptime, os, load, memory and
disk behaviors, and calls the `get` of each through `behavior.Call`. A read that
fails is in `errors`, and the other reads still answer.

gohai reads the timezone on each platform, and `timedatectl` sets it on the
Debian family (osapi-io/osapi#964).

## sysctl

`list` reads each parameter under `/proc/sys`, with an optional `prefix`. `get`
reads any key. Each entry tells if osapi manages it. `update` sets a parameter
and manages it, also when osapi did not manage it before.

A test of the first version on real hosts found that `list` and `get` read only
the parameters that osapi wrote. Thus a new host listed nothing, and `get`
answered 404 for a key that the kernel has. Ansible, Salt and Puppet read the
host as it is, and sysctl now does the same.

## Packages

Packages are two behaviors (osapi-io/osapi#964). `package` reads through gohai
on each platform, and installs and removes with `apt-get` on the Debian family.
Its Go package is `packages`, because `package` is a Go keyword.

`updatepackages` lists and refreshes the package index with apt. The index is
what the repositories have, not a fact about the host, so gohai does not read
it. A refresh reports `changed: true` only when the Release file of a repository
under `/var/lib/apt/lists` changed. The apt module of Ansible reports a change
on each update that runs, from the time stamp, and has `cache_valid_time` to
skip one. That breaks the rule that a second identical call changes nothing. The
`Get:` lines of `apt-get` do not tell either, because the CI runner prints them
on each run.

## Services

gohai reads the services of each Linux host with `systemctl`
(osapi-io/osapi#991). On the Debian family, `create` and `update` deploy an
uploaded object as `/etc/systemd/system/osapi-<name>.service`, through the
`object` and `managedfile` behaviors. `delete`, `start`, `stop`, `restart`,
`enable` and `disable` are actions on a service that osapi deployed.

An action reports `changed: true` only when systemd says that the service moved.
An `enable` of a unit with no `[Install]` section, which systemd calls static,
runs and changes nothing. On the lab, the hand-written domain reported a change
on each such `enable`.

The behavior does not have the main process of a service, because gohai does not
read it. gohai lists only the units that systemd loaded. Thus a service that is
stopped and disabled is not found until gohai reads the unit files too
(osapi-io/gohai#321).

## Files

File deploy is the `file` behavior (osapi-io/osapi#1109). Deploy is `update`
(`PUT`), undeploy is `delete` (`DELETE`), and `status` is a read, all at
`/api/node/{hostname}/file`, with the path in the body or the query. Deploy and
undeploy are writes, not actions, so that their permission is `file:write`. A
deploy writes each path as root. Thus the decision of osapi-io/osapi#999 gives
`file:write` to `automation`, not to `operator`.

On each Linux host, a deploy reads the object through the `object` behavior. It
renders a template with the facts of the agent, `.Vars` and `.Hostname`, and
writes the file through `managedfile`. Thus `managedfile` runs on each Linux
host, not only on the Debian family. Its record keeps the object and the content
type, and the stale list of the controller reads the object from that record.

- An `update` that writes the same file again reports `changed: false`.
- An undeploy removes the file through `managedfile`, which keeps the record and
  marks it undeployed.
- `status` compares the file with the checksum in the record. It reports
  `in-sync`, `drifted`, `missing` for a deployed file that is gone, or
  `unmanaged` for a path that osapi did not deploy or undeployed. It refuses a
  directory with a 400 (osapi-io/osapi#1174).
- A deploy with no content type uses the content type of the object.
- A deploy with no mode keeps the mode of a file that is there, and gives a new
  file 0644.
- The owner and the group are names, not numeric IDs.

The upload, list, get and delete of objects stay with the file endpoints of the
controller ([endpoints](endpoints.md)). `file` and `managedfile` run on macOS
too. There, `managedfile` reads the owner with BSD `stat -f %Su:%Sg`, because
BSD `stat` does not have `-c` (osapi-io/osapi#1119).

## Schedules

`schedule` writes cron files (osapi-io/osapi#1106). Its `create`, `update` and
`delete` get the object through `object`, and write the cron file through
`managedfile`, on the Debian family. Its `list` and `get` read the records of
`managedfile` for the files in `/etc/cron.d` and in
`/etc/cron.{hourly,daily,weekly,monthly}`. Thus they show only the entries that
osapi deployed. These entries are not facts of the host, so gohai does not read
them. A `create` refuses a file at a path that osapi did not deploy.

The writes are `AdminOnly()`, so only `admin` has `schedule:write`
([permissions](permissions.md#the-built-in-roles)). A template object reads the
facts of the agent through `host.Host.Facts`. The CLI takes the vars as
`--vars key=value`.

## Certificate authorities

`certificate` manages the CA trust store (osapi-io/osapi#1108). The
`ca_certificates` collector of gohai reads the trust store on each platform: the
directories of the family on Linux, and the system keychains on macOS. Each CA
has its subject, its SHA-256 fingerprint and its expiry. On Linux, `create` and
`update` deploy an uploaded object as `osapi-<name>.crt` through the `object`
and `managedfile` behaviors, and rebuild the trust store. This includes SUSE,
which has its own provider: it writes to `/etc/pki/trust/anchors` and runs
`update-ca-certificates` (osapi-io/osapi#1122). On macOS the writes report
`skipped`. osapi does not support Alpine, where the writes also report
`skipped`. The hand-written domain wrote only on the Debian family, and listed
only the names of the files.

The routes do not have the `/ca` segment of the hand-written domain:
`/api/node/{hostname}/certificate` and
`/api/node/{hostname}/certificate/{name}`. A `get` takes a name that one path
segment can hold. The router does not decode `%2F`. Thus a name with a slash,
such as the Debian system CA `mozilla/ISRG_Root_X1`, is in `list` only. The rule
`ca_name` refuses a slash and a `%`.

## Network

The network group has dns, interface, route and connectivity. The rule
`interface_name` is in the shared registry, because dns, interface and route
each use it. No hand-written code reads or writes netplan.

**dns** (osapi-io/osapi#988). gohai reads it on each platform. It writes through
`netplan`, an internal behavior that writes a file under `/etc/netplan`,
validates it with `netplan generate`, and applies it (osapi-io/osapi#987). When
`netplan generate` refuses the file, the file gets back its old content, or
`netplan` removes a new file.

A DNS write goes under the netplan ID of the definition that matches the
interface, such as the `all` of cloud-init for `en*`. netplan ignores a second
definition of the same interface. Thus on the Ubuntu image of the lab, a file
under the name of the interface changed nothing. `netplan status` lists only the
interfaces that netplan manages. Thus gohai, not netplan, tells if a host has an
interface. On the lab, a dummy interface that netplan did not manage was not in
the list of `netplan status`.

**interface** (osapi-io/osapi#989). Its Go package is `iface`, because
`interface` is a Go keyword. gohai reads each interface on each platform. A
write on the Debian family goes only under the own definition of the interface.
The behavior refuses an interface that a match defines, such as the `all` of
cloud-init. A static address under `all` changes each interface that the match
takes, now and later. On the lab that match took one interface, so a check that
counted the interfaces let the write through. The write examples run on
`osapi0`, a dummy interface that the integration job makes, and set no gateway.
A default route through `osapi0` would take the traffic of the runner.

**route** (osapi-io/osapi#990, osapi-io/osapi#998) is under the interface, with
`behavior.Of`: `osapi client node network interface route`, at
`/api/node/{hostname}/network/interface/{name}/route`. gohai reads the routes of
an interface on each platform. A write on the Debian family goes only under the
own definition of the interface, as for interfaces. It refuses a default route,
because the interface behavior sets the gateway.

Each call is one route, as `ip route add` and `ip route del` are, with a flag
for each value: `--destination` in CIDR notation, `--via` of the same family,
and an optional `--metric`. Each flag has its own `validate` rule. Only the
family of the gateway against the destination is for the provider to check. The
first version took a route as a string, as `ip route` writes it, and a call took
a list of them that replaced all the routes of the interface. That needed a rule
of its own to parse the string. The destination is in the body of an `update` or
a `delete`, not in the path. The router cannot match an encoded slash in a path
segment, so `10.0.0.0%2F8` has no route. The routes of the whole host are in the
facts of the agent, and the behavior has no list of them.

**connectivity** has the `ping` action (osapi-io/osapi#1110):
`osapi client node network connectivity ping --address <ip>`, at
`POST /api/node/{hostname}/network/connectivity/ping`. A behavior named `ping`
with an action `ping` gives the command `network ping ping`. Thus the behavior
has the name of what it reports. The provider runs the `ping` of the host
through `h.Exec` (iputils on Linux, `ping` and `ping6` on macOS) and reads its
summary. The agent does not use the pro-bing library, so the examples run on the
fake host. A host that does not answer is 100% loss, not an error.

## Users, groups and SSH keys

`group` moved alone (osapi-io/osapi#992). It reads `/etc/group` through gohai on
each platform, so Fedora and macOS answer `list` and `get`. It changes groups on
the Debian family. Its permissions are `group:read` and `group:write`, the name
of the behavior, not `user:read` and `user:write`. A custom role that named
`user:write` for groups must name `group:write`.

`user` moved after the group (osapi-io/osapi#992). Its `create` and `passwd`
hash the password on the controller, so the job has only the hash
([a step on the controller](behaviors.md#a-step-on-the-controller)). The
password route is `POST /user/{name}/passwd`, an action that always reports a
change. `passwd` is a word of `command.Actions`. The behavior reads through the
users collector of gohai on each platform, and changes users on the Debian
family. Its writes and `passwd` are `AdminOnly()`, because an account gets to
root.

`sshkey` is under `user`, with `behavior.Of` (osapi-io/osapi#993):
`osapi client node user sshkey`. It reads through the ssh collector of gohai,
and writes `~/.ssh/authorized_keys` on the Debian family. Its writes are
`AdminOnly()` too. The two behaviors declare `user:read` and `user:write`, which
are not built-in permissions now.

## Containers

Containers are two behaviors under `container` (osapi-io/osapi#994): `docker`,
at `/api/node/{hostname}/container/docker`, and `image`, at
`/api/node/{hostname}/container/image`. Their reads go through the docker
collector of gohai, which is an exception to the rule of gohai for the state of
a daemon ([collectors](../gohai/collectors.md#what-gohai-reads)). Their writes
run the docker CLI with sudo, not the Docker Engine API, because a provider runs
each command through `h.Exec`.

- `create` sends the environment on the standard input of docker, with
  `--env-file /dev/stdin`. Thus no value is in the arguments, which each user of
  the host can read.
- A container or an image that the host has is not made or pulled again, and
  reports `changed: false`. A pull compares the image ID before and after it.
- `exec` is an action with `.Always()`. The agent refuses it unless
  `agent.command.enabled` is true: `h.CommandEnabled` has that setting.
  `RunPrivilegedCmdFull` gives `exec` the standard output, the standard error
  and the exit code. An exit code that is not 0 is a result, not a failure.
- `exec` has `.PermitAs(behavior.VerbExec)`, so its permission is `docker:exec`,
  which only the admin role gets. `start` and `stop` keep `docker:execute`, and
  the `pull` of image has `image:execute`. The operator role gets both
  (osapi-io/osapi#1136, osapi-io/osapi#1115).

The write examples run on the container `osapitest`, from `alpine:3.20`.

## Logs

The log domain became two behaviors under the `log` group (osapi-io/osapi#1105):
`entry`, at `/api/node/{hostname}/log/entry`, and `source`, at
`/api/node/{hostname}/log/source`. A query of the journal and a query of one
unit are one `list` with a `unit` filter. journald gives the journal, so both
behaviors read with `journalctl`, and say so with `.NotAFact`. They run on each
Linux host, and skip in a container and on macOS. The hand-written domain ran on
the Debian family only.

Each filter goes to `journalctl` in one argument with its option, such as
`--unit=nginx.service`. The generated probe found that a value that starts with
`-` got to `journalctl` as an option. The permissions are `entry:read` and
`source:read`, the names of the behaviors (osapi-io/osapi#1115).

## NTP

`ntp` reads with `chronyc tracking` and `chronyc -c sources`, with `.NotAFact`
(osapi-io/osapi#1104). The sync status is the live state of chrony, not a fact
of the host, so it does not go through gohai. The lab found that the
hand-written domain ran `chronyc sources -c`, which prints the table and not
CSV. Thus each host returned no servers.

The writes go through `managedfile` to
`/etc/chrony/sources.d/osapi-ntp.sources`, so the file-state bucket records the
file. The rule `ntp_server` checks each server: a hostname or an IP address. The
hand-written domain checked only that the list was not empty, so a server with a
line break could add a directive to the file. In a container, which uses the
clock of its host, each method reports `skipped`.

## Processes

`process` moved after the `execute` verb (osapi-io/osapi#1112,
osapi-io/osapi#999). `list` and `get` read through the process collector of
gohai: `/proc` on Linux and `ps` on macOS. `get` reads one process, not the
list. `signal` is an action, so it needs `process:execute`. The `operator` role
has it, and the `automation` role does not. It runs `kill -<SIG> <pid>` through
sudo. It keeps the six signals of the hand-written domain, and refuses a PID
below 1. A PID that the host does not have is not found, because `signal` reads
the process first. Each row of a list is one process of one host.

No method of `process` starts a process for the signal to stop. Thus the example
of `signal` has `NotLive`, and the lab tests it by hand
([tests](behaviors.md#tests-a-behavior-gets-from-its-definition)).

## Power

`reboot` and `shutdown` are actions (osapi-io/osapi#1111), so their permission
is `power:execute`, and the `operator` role has it. On the Debian family each
one runs `shutdown -r -- +N` or `shutdown -h -- +N` through sudo. The `--` stops
a message that starts with `-` from becoming an option. A container, macOS and
the other Linux families report `skipped`. Each method has `.Disrupts`, so the
integration test does not run it on a live host.

## Command

`exec` and `shell` are actions of the `command` behavior, at the routes of the
hand-written domain (osapi-io/osapi#1113). `exec` is `AdminOnly()`, so its
permission is `command:execute`, for the admin role only. `shell` has
`.Shell()`, which gives the verb `shell`. Thus its permission is
`command:shell`, and only the admin role gets it. `AreaCommand` keeps the blocks
under Command in the UI.

The caller names the program, so `Runs(behavior.AnyProgram)` declares each
program. `h.Exec.RunCmdFull` runs a program as the user of the agent, in a
directory and with a timeout. It returns the output, the error output and the
exit code apart. `Exits` gives the exit code of a command on the fake host. The
provider refuses each command when `host.Host.CommandEnabled` is false, as
docker `exec` does, with the same `host.ErrCommandDisabled`. The generated probe
found that a command that starts with `-` got to `/bin/sh -c` as an option. Thus
the command field of each method has `startsnotwith=-`.

## What this page does not cover

How a behavior is defined, served and tested is in [behaviors](behaviors.md).
The roles and the permissions are in [permissions](permissions.md). The
operations that the controller answers itself are in [endpoints](endpoints.md).
