# How a collector gathers facts

A collector reads files and commands of a host, as Ohai reads them, and changes
the result into a typed struct. It reads only through the sources that the
caller gives it: a filesystem, a command runner, a clock and the platform
family. Thus a caller can give it a fake host, and the collector reads the fake
host as it reads a real one.

The 62 collectors share one contract, which [the entry point](README.md) states.
They also share the content of this page:

- how to select the source
- what the collector can add to it
- the names of the fields that result

## The sources

`pkg/gohai/source` has the type `Sources`:

| Field      | Type                       | A zero value is                               |
| ---------- | -------------------------- | --------------------------------------------- |
| `FS`       | `avfs.VFS`                 | the filesystem of the host                    |
| `Exec`     | `source.Runner`            | the commands of the host                      |
| `Now`      | `func() time.Time`         | `time.Now`                                    |
| `Family`   | string, `pkg/gohai/family` | the family of `FS`, or of the host            |
| `Resolver` | `source.Resolver`          | `net.DefaultResolver`: `/etc/hosts`, then DNS |
| `HTTP`     | `http.RoundTripper`        | one transport that uses no proxy              |

A zero `Family` with a given `FS` is the family that the `/etc/os-release` of
that `FS` names. It is not the family of the real host. Thus a fake filesystem
and the variant that reads it agree. A caller that gives a macOS filesystem
gives `darwin`, because macOS has no `/etc/os-release`. With no `FS`, a zero
`Family` is `family.Detect()` of the host. `gohai.New` finds the family one time
and gives it to each collector.

Each collector has `NewWith(src)`. `NewWith` selects the variant from the family
of `src`. `collector.Wire` gives the variant the `FS`, `Exec`, `Now` and
`Resolver` of `src`. A variant field with one of those names and a different
type makes `Wire` panic. Without the panic, the collector reads the real host
under a fake host, and nothing tells the caller. A test in `pkg/gohai` checks
that each field of each built-in collector that has a source type gets the
source that the caller gave. `New()` is `NewWith(source.Sources{})`, the real
host. `gohai.New(gohai.WithSources(src))` gives the same sources to each
collector.

The cloud collectors read the metadata service of their provider, such as
`http://169.254.169.254`, through the `HTTP` of `src`. A fake host gives a
transport that answers the metadata URLs, so a test reads no network. The tests
of gohai use `internal/sourcetest.HTTP`. A zero `HTTP` is one transport that all
the cloud collectors share. It uses no proxy, because the metadata addresses are
link-local. Some cloud collectors also read the host: azure reads the waagent
binary and the dhclient leases, linode reads the apt sources and runs
`ip -o -4 addr show`, openstack reads `/etc/passwd`, and scaleway reads
`/proc/cmdline`. They read through `FS` and `Exec`.

osapi gives the sources of `host.Host`. Thus a behavior of osapi calls a
collector, and the example of the behavior runs on the fake host.

## What gohai reads

gohai has facts about the host: what is installed, what the hardware is, and how
the host is configured. The resolver configuration, the accounts and their
authorized keys, the installed packages, and the certificate authorities that
the host trusts (\`ca_certificates\`) are facts. So are the services: each unit,
its description, and whether it starts at boot. "Enabled" is the state of the
unit file, not whether the unit runs now. The list has each installed unit, also
one that systemd has not loaded, such as a stopped and disabled unit. Such a
unit comes from `systemctl list-unit-files`, with the state `dead`, and its
`unit_file_state` says why it does not start: `disabled`, `static` or `masked`.
On macOS, the services are the launchd daemons of the system domain, from
`launchctl print system`. Each user can read that domain, so the agent reads it
without sudo. There, "enabled" is the override that launchd keeps for the label.
A daemon that launchd has not loaded, and that has an override, is in the list
with the state `dead`.

The live state of a service that osapi manages is not a fact. Examples are the
sync status of chrony, and the package updates that the repository index has.
That state stays in the osapi domain that manages the service, next to the
writes that change it. It still runs on each family, because the family selects
only writes. Ohai is the test when it is not clear: a read that Ohai has no
plugin for, and that a daemon or a remote index answers, is not gohai's.

The `docker` collector is an exception to this rule. The Docker daemon answers
it, and Ohai has no plugin for it, but the owner of osapi decided that osapi
reads containers through gohai (osapi-io/osapi#994). The reason is that a
container on a host is a fact for each caller of gohai, as a package is, not
only state that osapi manages. One collector also gives one shape and one fake
host for the tests, and the docker and image behaviors of osapi read it. The
collector runs `docker version`, `docker ps -a --no-trunc`, one `docker inspect`
for each container, and `docker images`. It returns the names of the environment
variables of a container, never their values, because the values often hold
secrets (osapi-io/gohai#327). A host where `docker version` does not answer has
no docker facts.

## What each collector is, from the binary

`gohai.Collectors()` describes each built-in collector, and `gohai collector`
prints the same data. The commands have the shape of the DSL commands of osapi:

| Command                          | Shows                                                                |
| -------------------------------- | -------------------------------------------------------------------- |
| `gohai collector list`           | each collector, its category, its default and its dependencies       |
| `gohai collector get --name <c>` | its package, its constructor, the fields of its facts, and its reads |
| `gohai collector spec get`       | each part of a collector, what it does and when to use it            |
| `gohai collector validate`       | the problems of each collector against the rules, each with its fix  |

osapi mounts the same command as `osapi agent collector`, through
`cmd.NewCollectorCommand(path)` (gohai v1.13.0). `path` is the command path that
the examples and the hints name. Thus the two binaries print the same collectors
from the same code. A change to the output goes in gohai first.

The constructor is `<package>.NewWith(src)` for a collector that reads the host,
and `<package>.New()` for a cloud collector. The fields come from the field of
`gohai.Facts` whose JSON name is the name of the collector.

The reads are not written by hand. `gohai.Collectors()` runs each collector on
an empty host of debian, rhel and darwin, through `internal/readlog`, which logs
each file that the collector opens or looks at and each command that it runs.
Thus the list agrees with the code, and it cannot be stale. The empty host is
the limit: a collector reads under these paths when they have content, such as
each device under `/sys/class/net`, and the list does not show those reads. A
cloud collector reads the metadata service of its provider over HTTP, which
`readlog` does not log. Thus it is not run, and its entry names the service.

`validate` checks four rules: a name of lowercase letters, digits and
underscores, with no two the same; a category of the roster; a field of
`gohai.Facts` for the facts; and dependencies that are other registered
collectors. osapi reads `gohai.Collectors()` to tell an author of a behavior
which facts exist (osapi-io/osapi#1016).

## Choosing what to read

There are four positions, in order. A collector uses the first position that
covers what it needs.

1. **A file**, through `FS`: `/proc`, `/sys` and `/etc` on Linux.
2. **A command**, through `Exec`, such as `sysctl`, `ioreg`, `system_profiler`,
   `ps` and `df` on macOS, and `ip`, `lscpu` and `ethtool` on Linux. On macOS
   the users and the ssh collectors read the accounts and their homes from the
   directory service with `dscl`, because `/etc/passwd` has only the system
   accounts (gohai v1.12.1).
3. **A library**, only when it reads through the sources, or reads nothing from
   the host. Official provider SDKs, or plain `net/http`, are for the cloud
   collectors.
4. **Ohai's plugins, as a reference for the method. Never import them.** They
   tell which files and commands to read, and which special cases exist.

A library that reads the host itself cannot read a fake host. For this reason,
gohai stopped using gopsutil (osapi-io/gohai#292), then ghw, pcidb and
go-sysconf (osapi-io/gohai#295). These changes kept the value of each fact that
the library gave, for example `cached` with `SReclaimable` in it, and
`"unknown"` for a DMI string that cannot be read. The cost is that gohai keeps
these parsers, including one for `pci.ids`, and gets no bug fixes from a
library.

Every host collector now reads through its sources. A user lookup reads
`/etc/passwd`, the current user is `id -u`, and a program on the `PATH` is
`sh -c 'command -v <name>'`. The FQDN of the hostname collector comes from the
`Resolver`, as Ohai and Ansible get it from the system resolver: the canonical
name of the host, then a reverse lookup. Only the FQDN needs it. The hostname is
the output of `hostname`, with no lookup (osapi-io/gohai#316).

**A `Collect` method never uses `os.ReadFile`, `exec.Command` or `time.Now`.**
It uses `FS`, `Exec` and `Now`. A test gives the files and the command output
through `internal/sourcetest`, and does not touch the host. The command runner
of a test is `MockRunner` in `pkg/gohai/source/mocks`, which mockgen generates.
It is exported, so a caller such as osapi tests its own use of gohai with the
same double, and nobody writes a runner by hand (osapi-io/gohai#314). A new
collector breaks this rule most often. A reviewer must look for it first.

Two facts changed on purpose, to follow Ohai. On Linux, `machine_id` reads
`/etc/machine-id` first, then `/var/lib/dbus/machine-id`, then DMI
`product_uuid`. gopsutil read `product_uuid` first, so on a VM the ID is now the
machine ID, not the DMI UUID. The `opts` of a mount have each option of
`/proc/mounts`, as Ohai's `mount` reports them, not only the options of the
mount point. The other Linux facts are the same as v1.2.0 on an Ubuntu host
(osapi-io/gohai#300).

## Compiling everywhere

Collector code compiles on each target platform, and no file has a `//go:build`
tag. Thus `go test ./...` on any machine compiles and runs the tests of each
collector. Coverage shows for all platforms together, not for each runner.

osapi uses the same pattern, and [its providers](../osapi/providers.md) tell why
it is worth the cost. On a platform that a collector does not support, a stub
returns the unsupported result. Thus an unsupported platform is a compile-time
fact, not a runtime nil.

The shape that follows:

```
pkg/gohai/collectors/<name>/
  <name>.go                 Info, the Collector interface, New(), NewWith(src)
  linux.go / darwin.go      per-OS structs, with FS, Exec and Now fields
  debian.go / rhel.go       only where a distro diverges
  <name>_public_test.go     one table-driven TestCollect keyed by variant
```

Each collector has one `TestCollect`. It uses a table with a variant column that
makes the correct struct for each OS. There is not one test file for each
platform. That makes the file count larger by the number of platforms, and tests
the dispatch one time in each file, not one time in total.

## What a field is called

There are three tiers, in order of precedence. A field gets its name from the
first tier that has a name for it.

| Tier | Authority                                   | Fields | Share |
| ---: | ------------------------------------------- | -----: | ----: |
|    1 | OCSF                                        |    107 |   11% |
|    2 | OpenTelemetry resource semantic conventions |     91 |   10% |
|    3 | gohai convention                            |    752 |   79% |

**Four fifths of the fields obey neither standard.** Know this number before you
read the rules. The third tier is the usual case, and the first two are the
exception. Thus a contributor who names a new field usually uses the convention
of gohai, and does not look in OCSF.

Tier three starts from the name of the source in `snake_case`. For data from
`/proc` or `/sys`, it uses the name of the kernel. It adds a unit suffix where
the unit is not clear. Use only the universal abbreviations: `ip`, `mac`, `pid`,
`uid`, `gid`, `mtu`, `fqdn`, `uuid`, `cidr`, `arn`, `id`.

### The redundant-prefix rule

The output nests by collector. Thus `{"cpu": {"cpu_count": 4}}` gives the
collector name two times. A JSON key uses the leaf name of the schema. If a
parent prefix is the same as the name of the collector, remove that prefix.

| Schema path          | Collector  | Key         |
| -------------------- | ---------- | ----------- |
| `device.cpu_count`   | `cpu`      | `count`     |
| `device.memory_size` | `memory`   | `size`      |
| `device.hostname`    | `hostname` | `name`      |
| `process.cmd_line`   | `process`  | `cmd_line`  |
| `host.cpu.vendor.id` | `cpu`      | `vendor_id` |

Read the last two rows. `cmd_line` keeps its name, because `process` is not a
prefix of it. `vendor_id` keeps `vendor`, because the parent object is not the
collector.

The Go field is the PascalCase form of the last key. The exception is where the
Go convention for initialisms is different. The `cpu_id` of OCSF becomes
`CPUID`, not `CpuId`, and the JSON tag still obeys the rule above. A name
without a schema-mapping claim is invented. The citations for each field in
`schemas/field-mapping.md` make that visible.

## What Ohai is for, and what it is not

Read Ohai for the **collection method**: which file or command to read, which
distribution has special cases, and where a fallback chain is necessary. If Ohai
reads `/proc/X` and uses a command as a fallback on SUSE, gohai must do the
same.

Do not read Ohai for the **output shape**. Its JSON comes from Ruby. If you make
the structs of gohai match it exactly, you get nothing. The same is true of
node_exporter. It is a reference for difficult `/proc` parsing, not for names.

Where a specific choice needs attribution, the page of the collector gives it in
the text. The Data Sources pages describe how gohai operates. They are not a
diff against Ohai.

## The platform and its family

`pkg/gohai/family` names a host as Ohai does. `family.Platform` is Ohai's
`platform_id_remap`: the ID of `/etc/os-release`, with a few IDs changed, such
as `rhel` to `redhat` and `amzn` to `amazon`. `family.Of` is Ohai's
`platform_family_from_platform`: the first family whose match is part of the
platform name. `rhel` is strict: only rebuilds that track the versions of RHEL.
Fedora, and other RPM distributions, are `fedora`. Amazon Linux is `amazon`.

`family.Detect` is the family of the host. A collector selects its variant with
the family of its sources, and with `family.Detect` when the sources have none.
The platform collector reports it. osapi names the platforms of its behaviors
with the same values.

One difference from Ohai is on purpose. On macOS the platform and the family are
`darwin`, the name of Go and of the kernel, not Ohai's `mac_os_x`.

Before this, gohai had two lists that did not agree. Its `Detect` put Fedora and
Amazon in `rhel`, and did not know most of the Debian family. The table of the
platform collector put Amazon in `rhel`, and on macOS the family was the value
of `gopsutil`, not a family.

## What will surprise you

**A link on the host can be relative.** On Ubuntu, `/etc/localtime` links to
`../usr/share/zoneinfo/Etc/UTC`, not to an absolute path. A collector that reads
a link resolves a relative target from the directory of the link before it
compares it with a prefix. The fake host of a test gives an absolute link, so
only a live host showed this (osapi-io/osapi#970).

## Where this connects

[The entry point](README.md) has the collector contract, the registry, and what
occurs to a collector that is not registered. The pages for each collector under
`docs/collectors/` in the repository tell what each one returns.
`schemas/field-mapping.md` has the citations for each field, which the tier
table of this page counts.

______________________________________________________________________

Written from `pkg/gohai/collectors/` and `schemas/field-mapping.md`.
