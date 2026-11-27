# The crypto of each process

Each process of osapi reports its crypto: the controller, the NATS server and
each agent. FIPS 140-3 mode is a setting of a process, not of the fleet.
`GODEBUG=fips140` sets it when the process starts. Thus the report is per
process.

## What a report has

The package `internal/cryptoreport` makes the report. A process makes it at its
start, and sends it in each heartbeat. The report has:

- the Go version, and the version of the Go Cryptographic Module, from
  `crypto/fips140.Version()`;
- the mode: `off`, `on`, or `only`, from `fips140.Enabled()` and
  `fips140.Enforced()`;
- each TLS listener of the process: its lowest TLS version, its suites and its
  groups;
- each use of crypto, such as the seal or the API tokens, with `approved` and
  `only_mode`;
- the gaps: each reason that the process is not in FIPS 140-3 mode with only
  approved algorithms.

The fleet view shows the report. `osapi client health status` has a FIPS column
for each component. `osapi client agent get` has the report of the agent. The
dashboard and the agent card in the UI show a FIPS line, with each gap in its
tooltip. `osapi pki list` and `osapi pki key list` say whether FIPS 140-3
approves the algorithm of each key.

## Where the facts come from

The report reads what the process does, not a list that a person keeps:

- **The mode** comes from `crypto/fips140` of the running process.
- **A listener** comes from `config.ServerTLS.Negotiation()`. The server serves
  the same `tls.Config` through `ServerTLS.Config()`. Thus the two cannot
  disagree.
- **A certificate** comes from `pki.ReadCerts`, which reads the key and the
  signature algorithm of the certificate that the process serves.
- **The key of `osapi pki key`** names its use of crypto, and the use says
  whether FIPS 140-3 approves its algorithm.

A listener that sets no groups uses the default groups of crypto/tls. Go does
not export that list. Outside FIPS 140-3 mode it includes X25519, which FIPS
140-3 does not approve. Thus such a listener is approved only in FIPS 140-3
mode, where crypto/tls negotiates only approved suites and groups.

## How a test holds `only_mode` true

An approved algorithm can still fail in FIPS 140-3 only mode. The cause is code
that calls the module in a way that the mode refuses. Two uses do this now:

| Use                 | Why it fails in only mode                   | Issue               |
| ------------------- | ------------------------------------------- | ------------------- |
| NATS JWTs           | nkeys makes a key from a seed with a reader | osapi-io/osapi#1527 |
| The JetStream store | nats-server picks its own GCM nonce         | osapi-io/osapi#1549 |

The `fips140=only` CI job runs the tests of `go_fips_packages`. It holds each
claim:

- A use that claims to work in only mode is in a package that the job tests. A
  unit test reads `go_fips_packages` from the justfile and fails when the
  package is not there.
- For each use that fails, the job runs the same call that nkeys or nats-server
  makes, and expects it to fail. When a fix upstream makes the call work, the
  test fails until the use says that it works.

## Not covered

The report does not validate osapi. A validation is of a module, not of a
program that uses it. The report tells which algorithms a process uses, and
whether the mode and each algorithm are approved.
