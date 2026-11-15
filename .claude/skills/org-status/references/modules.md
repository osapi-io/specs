# Nested modules

Resolve the repository set first, per [SKILL.md](../SKILL.md).

Every `examples/` directory in this organization holds its own `go.mod`, 19 of
them across five repositories. Dependabot watches the directory its config
names, which is the root, so the nested ones drift untouched.

The justfile knows how to do all of this. Do not hand-roll a `find` loop.

## Report

```bash
cd ~/git/osapi-io/$r && just go-mod-check
```

Non-zero when a committed module is untidy, naming each one:

```
untidy: examples/timings
run 'just go-mod' and commit the result
```

It no-ops in a repository with no `examples/`, so it is safe to run across all
of
them.

A committed module can be untidy while CI is green. The reason: `just test`
calls `go-mod`, which tidies, but CI does that in a temporary checkout. CI
discards the tidy, and nothing compares it with what is committed.

## Fix

```bash
cd ~/git/osapi-io/$r && just go-mod-bump && just test
```

`go-mod-bump` runs `go get -u ./...` then `go mod tidy` in each module under
`examples/`, and says so and exits 0 where there is no `examples/`. Run the
repository's own gate afterwards: several of these examples are referenced from
the README, and a broken example is broken documentation.

It does not touch the root module, on purpose. Dependabot owns that. A bump of
it also moves the tool versions that `go get -tool` writes again on each run.
That is noise, not a change.

## The go directive

A nested module declares its own, and nothing keeps it in step with the root.
Six
gohai examples sat at `go 1.25.7` against a root of `1.26.0`. The rule in
[the charter](../../../../CONSTITUTION.md) applies to these
files too.

```bash
find ~/git/osapi-io/$r -name go.mod -not -path '*/.worktrees/*' \
  -exec sh -c 'printf "%s\t%s\n" "$1" "$(grep -m1 "^go " "$1" | cut -d" " -f2)"' _ {} \;
```

`just go-mod-bump` moves it as a side effect, when it tidies against the current
toolchain. Thus this is a check, not a separate fix.

Exclude `.worktrees/`. Another agent may have a branch checked out there, and
its
modules are not this repository's to tidy.

## Do not compile the examples to check them

`go build ./...` writes a binary into each directory. One time, that put 52
stray binaries next to committed files in three repositories. `-o /dev/null`
fails when a directory has more than one `main` package, and some of these do.
`just test` is the check. If you need more, `go vet` compiles and writes
nothing.

## The durable fix, which is not this

Dependabot v2 takes `directories` with globs. With this, the drift stops:

```yaml
- package-ecosystem: "gomod"
  directories:
    - "/"
    - "/examples/*"
```

Also, `go-mod-check` in the `test` recipe of a repository fails the build, so
that nobody needs to find the drift. Both changes add noise, and both remove a
thing to remember. Both change how a repository operates. Thus propose them. Do
not make them.
