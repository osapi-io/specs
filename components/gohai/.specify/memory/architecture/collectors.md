# How a collector gathers facts

gohai is an aggregator rather than a reimplementation. A collector's job is to
wrap a well-maintained source, a Go library, a provider SDK, or a thin file or
command parser, and reshape its output into a typed struct. The 62 collectors
share one contract, which [the entry point](../spec.md) states; what they share
beyond that is this: how the source is chosen, what the collector may add on top,
and what the resulting fields are called.

## Choosing what to wrap

Seven positions, in order. The order is the content: a collector takes the first
one that covers what it needs.

1. **ghw**, for physical hardware topology. CPU and NUMA layout, memory DIMMs and
   page sizes, block devices including UUID, label and unmounted state, network
   drivers and speed, DMI, GPU, PCI. Anything about static hardware shape.
2. **gopsutil**, for dynamic runtime state. Memory free and available, disk and
   network I/O counters, process enumeration, sessions, virtualization detection,
   host info. Anything that changes between collections.
3. **go-sysinfo**, where gopsutil is weaker on host, platform or kernel. Judged
   case by case, and never stacked with gopsutil for the same fact.
4. **procfs**, for raw `/proc` and `/sys` parsing when nothing above covers a
   field. Preferred over a hand-rolled scanner.
5. **Official provider SDKs** for cloud collectors, or plain `net/http` against
   the instance metadata endpoint where the SDK is too heavy.
6. **A gohai extension**, last. Only the fields the libraries above do not expose.
7. **Ohai's plugins, as a methodology reference and never an import.** Read to
   learn which edge cases exist, then checked against the libraries above. Only
   the residual gap becomes code here.

The reason the order matters more than any one position: replacing a library
wholesale because it misses one field discards years of accumulated bug fixes and
cross-platform handling. A library that genuinely does not match what the
collector reports is replaced, and the collector's own Data Sources page says why.

## What an extension may do

An extension layers onto the library's output rather than substituting for it.

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
`executor.Executor`, never `os.ReadFile` or `exec.Command` in a `Collect`
method.** Those two seams are what let a test run without touching the host, so a
collector that reaches for the standard library directly is a collector whose
tests need the machine they describe. This is the rule a new collector is most
likely to break and the one a reviewer should look for first.

## Compiling everywhere

Collector code compiles on every target platform, with no `//go:build` tag
anywhere. So `go test ./...` on any machine compiles and runs every collector's
tests, and coverage is visible cross-platform rather than per-runner.

This is osapi's pattern, and
[its providers](../../../../osapi/.specify/memory/architecture/providers.md) state
why it is worth the cost: a platform a collector does not support is a stub that
returns the unsupported outcome, which makes an unsupported platform a
compile-time fact rather than a runtime nil.

The shape that follows:

```
pkg/gohai/collectors/<name>/
  <name>.go                 Info, the Collector implementation, New()
  linux.go / darwin.go      per-OS structs
  debian.go / rhel.go       only where a distro diverges
  export_test.go            seams onto the upstream library
  <name>_public_test.go     one table-driven TestCollect keyed by variant
```

One `TestCollect` per collector, table-driven by a variant column that builds the
right per-OS struct. Not one test file per platform, because that multiplies the
file count by the platform count and tests the dispatch once per file instead of
once.

## What a field is called

Three tiers, applied in order of precedence. A field takes its name from the first
tier that has an opinion.

| Tier | Authority                                | Fields | Share |
| ---: | ---------------------------------------- | -----: | ----: |
|    1 | OCSF                                     |    107 |   11% |
|    2 | OpenTelemetry resource semantic conventions |     91 |   10% |
|    3 | gohai convention                         |    752 |   79% |

```sh
grep -cE '^\|[^|]*\|[^|]*\|[^|]*\| T1 +\|' schemas/field-mapping.md   # 107
grep -cE '^\|[^|]*\|[^|]*\|[^|]*\| T2 +\|' schemas/field-mapping.md   # 91
grep -cE '^\|[^|]*\|[^|]*\|[^|]*\| T3 +\|' schemas/field-mapping.md   # 752
grep -cE '^\| [a-z]' schemas/field-mapping.md                          # 950
```

**Four fifths of the fields follow neither standard**, which is the number worth
knowing before reading the rules. The third tier is the common case and the first
two are the exception, so a contributor naming a new field is usually applying
gohai's own convention rather than looking up OCSF.

Tier three starts from the backing library's field name in `snake_case`, mirrors
the kernel's name for anything read from `/proc` or `/sys`, and adds a unit suffix
where the unit is ambiguous. Abbreviations are the universal ones only: `ip`,
`mac`, `pid`, `uid`, `gid`, `mtu`, `fqdn`, `uuid`, `cidr`, `arn`, `id`.

### The redundant-prefix rule

Output nests by collector, so `{"cpu": {"cpu_count": 4}}` states the collector
name twice. A JSON key takes the schema's leaf name with any parent prefix
stripped when that prefix duplicates the collector's name.

| Schema path          | Collector  | Key        |
| -------------------- | ---------- | ---------- |
| `device.cpu_count`   | `cpu`      | `count`    |
| `device.memory_size` | `memory`   | `size`     |
| `device.hostname`    | `hostname` | `name`     |
| `process.cmd_line`   | `process`  | `cmd_line` |
| `host.cpu.vendor.id` | `cpu`      | `vendor_id` |

The last two rows are the ones to read. `cmd_line` keeps its name because
`process` is not a prefix of it, and `vendor_id` keeps `vendor` because the parent
object is not the collector.

The Go field is the PascalCase rendering of the final key, except where Go idiom
on initialisms conflicts: OCSF's `cpu_id` becomes `CPUID` rather than `CpuId`, and
the JSON tag still follows the rule above. A name with no schema-mapping claim
behind it is invented, and the per-field citations in
`schemas/field-mapping.md` are what make that visible.

## What Ohai is for, and what it is not

Ohai is read for **collection approach**: which file or command to read, which
distro edge cases exist, where a fallback chain is needed. If it reads `/proc/X`
and falls back to a command on SUSE, gohai should too.

Ohai is not read for **output shape**. Its JSON is a Ruby artifact and pinning
gohai's structs to it byte for byte buys nothing. The same goes for node_exporter,
which is a reference for tricky `/proc` parsing and not for naming.

Where a specific choice needs attribution, the collector's own page says so
inline. The Data Sources pages are a description of gohai's behaviour rather than
a diff against Ohai's.

## Where this connects

[The entry point](../spec.md) has the collector contract, the registry, and what
happens to a collector that is never registered. The per-collector pages under
`docs/collectors/` in the repository say what each one returns.
`schemas/field-mapping.md` carries the per-field citations this document's tier
table counts.

______________________________________________________________________

Traced to `specs/002-move-contributor-docs/`, which moved the design rules out of
`docs/methodology.md` and left the procedure and the per-collector reference data
there. The tier counts were measured during that feature and corrected: the page
said roughly 108, 74 and 768, which summed correctly and was wrong in every
individual figure.
