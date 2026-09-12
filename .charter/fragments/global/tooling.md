# Tooling

A tool a repository invokes is declared where the repository declares its tools.
A tool resolved from whatever the developer happens to have installed is not the
same tool across machines, and is not what continuous integration runs.

Both provisioning paths resolve to the same version. Where nothing maintains a
version automatically, both track the latest release so they move together;
where something does, both pin it and that mechanism moves both. A version
pinned in one path and floating in the other guarantees divergence.

A tool whose output is committed is pinned, so the committed artifact does not
change under whoever runs the generator.

## The language version

A tool version and a language version are different promises. The tool version
is what this repository builds with. The language version in `go.mod` is a
floor: the oldest release a consumer may build with, and the only one of the two
that binds somebody else.

A repository supports the two most recent Go minor releases, so the directive
names the older of them. Naming the newest drops support for the one before it,
which is the opposite of the rule. Tool provisioning still tracks the latest
release, because building with a newer toolchain than the floor is always
allowed and surfaces new vet findings early.

The floor is built in continuous integration, not only declared. A repository
testing one version while promising two has not tested the promise, and the day
a newer standard library call compiles locally is the day the floor breaks for
every consumer with nothing reporting it. The job building the floor reads the
version from `go.mod` rather than repeating it, so moving the directive moves
the build with it.

Which release is current is not recorded here. It is what the toolchain list
returns, for the same reason the repository list is not recorded either.
