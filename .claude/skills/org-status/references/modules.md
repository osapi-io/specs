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

It no-ops in a repository with no `examples/`, so it is safe to run across all of
them.

Why a committed module can be untidy while CI is green: `just test` calls
`go-mod`, which tidies, but CI does that in a throwaway checkout. The tidying is
discarded and nothing compares it against what is committed.

## Fix

```bash
cd ~/git/osapi-io/$r && just go-mod-bump && just test
```

`go-mod-bump` runs `go get -u ./...` then `go mod tidy` in each module under
`examples/`, and says so and exits 0 where there is no `examples/`. Run the
repository's own gate afterwards: several of these examples are referenced from
the README, and a broken example is broken documentation.

It leaves the root module alone on purpose. Dependabot owns that, and bumping it
would drag along the tool versions `go get -tool` rewrites on every run, which is
churn rather than a change.

## The go directive

A nested module declares its own, and nothing keeps it in step with the root. Six
gohai examples sat at `go 1.25.7` against a root of `1.26.0`. The rule in
[the charter](../../../../.charter/fragments/global/tooling.md) applies to these
files too.

```bash
find ~/git/osapi-io/$r -name go.mod -not -path '*/.worktrees/*' \
  -exec sh -c 'printf "%s\t%s\n" "$1" "$(grep -m1 "^go " "$1" | cut -d" " -f2)"' _ {} \;
```

`just go-mod-bump` moves it as a side effect of tidying against the current
toolchain, so this is a check rather than a separate fix.

Exclude `.worktrees/`. Another agent may have a branch checked out there, and its
modules are not this repository's to tidy.

## Do not compile the examples to check them

`go build ./...` writes a binary into each directory, which is how 52 stray
binaries once ended up committed-adjacent across three repositories. `-o /dev/null`
fails outright when a directory holds several `main` packages, which several of
these do. `just test` is the check; if something beyond that is needed, `go vet`
compiles without emitting anything.

## The durable fix, which is not this

Dependabot v2 takes `directories` with globs, so the drift could stop happening:

```yaml
- package-ecosystem: "gomod"
  directories:
    - "/"
    - "/examples/*"
```

And adding `go-mod-check` to a repository's `test` recipe would fail the build
rather than leaving the drift to be noticed. Both trade noise for not having to
remember, and both change how a repository behaves, so propose them rather than
making them.
