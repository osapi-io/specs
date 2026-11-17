# How a collector gathers facts

gohai collects facts from other sources. It does not implement them again. A
collector wraps a well-maintained source and changes its output into a typed
struct. The source is a Go library, a provider SDK, or a small file or command
parser.

The 62 collectors share one contract, which [the entry point](README.md) states.
They also share the content of this page:

- how to select the source
- what the collector can add to it
- the names of the fields that result

## Choosing what to wrap

There are seven positions, in order. The order is the rule. A collector uses the
first position that covers what it needs.

1. **ghw**, for physical hardware topology: CPU and NUMA layout, memory DIMMs
   and page sizes, block devices with UUID, label and unmounted state, network
   drivers and speed, DMI, GPU and PCI. Use it for the static shape of the
   hardware.
2. **gopsutil**, for runtime state that changes: free and available memory, disk
   and network I/O counters, the process list, sessions, virtualization
   detection and host information. Use it for data that changes between
   collections.
3. **go-sysinfo**, where gopsutil is weaker on host, platform or kernel. Decide
   for each case. Never use it together with gopsutil for the same fact.
4. **procfs**, to parse raw `/proc` and `/sys` when no source above covers a
   field. Use it in place of a scanner that you write yourself.
5. **Official provider SDKs** for cloud collectors. If the SDK is too large, use
   plain `net/http` against the instance metadata endpoint.
6. **A gohai extension**, last. Use it only for the fields that the libraries
   above do not give.
7. **Ohai's plugins, as a reference for the method. Never import them.** Read
   them to learn which special cases exist. Then check the libraries above. Only
   the gap that remains becomes code here.

The order is more important than any one position. If you replace a library
because it does not have one field, you lose years of bug fixes and
cross-platform work. If a library really does not match what the collector
reports, replace it. The Data Sources page of the collector then tells why.

## What an extension may do

An extension adds to the output of the library. It does not replace it.

```go
info, err := upstream.Get(ctx)
if err != nil {
    return nil, err
}
if shouldAddOurBit(info) {
    info.OurField = readOurSource()
}
```

**An extension reads through `avfs.VFS` and runs commands through
`executor.Executor`. A `Collect` method never uses `os.ReadFile` or
`exec.Command`.** With these two seams, a test runs and does not touch the host.
If a collector uses the standard library directly, its tests need the machine
that they describe. A new collector breaks this rule most often. A reviewer must
look for it first.

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
  <name>.go                 Info, the Collector implementation, New()
  linux.go / darwin.go      per-OS structs
  debian.go / rhel.go       only where a distro diverges
  export_test.go            seams onto the upstream library
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

Tier three starts from the field name of the backing library in `snake_case`.
For data from `/proc` or `/sys`, it uses the name of the kernel. It adds a unit
suffix where the unit is not clear. Use only the universal abbreviations: `ip`,
`mac`, `pid`, `uid`, `gid`, `mtu`, `fqdn`, `uuid`, `cidr`, `arn`, `id`.

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

## Where this connects

[The entry point](README.md) has the collector contract, the registry, and what
occurs to a collector that is not registered. The pages for each collector under
`docs/collectors/` in the repository tell what each one returns.
`schemas/field-mapping.md` has the citations for each field, which the tier
table of this page counts.

______________________________________________________________________

Written from `pkg/gohai/collectors/` and `schemas/field-mapping.md`.
