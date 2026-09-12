# Nested modules

Resolve the repository set first, per [SKILL.md](../SKILL.md).

Every `examples/` directory in this organization holds its own `go.mod`, 19 of
them across five repositories. Dependabot does not see any of them: each
`dependabot.yml` declares `gomod` at `directory: "/"` only, so the root module is
watched and the nested ones drift untouched.

## Find them

```bash
gh api "/repos/osapi-io/$r/git/trees/HEAD?recursive=1" \
  --jq '.tree[] | select(.path | endswith("go.mod")) | select(.path != "go.mod") | .path'
```

Locally, which is what the fix needs anyway:

```bash
find ~/git/osapi-io/$r -name go.mod -not -path '*/.worktrees/*' -not -path "*/$r/go.mod"
```

Exclude `.worktrees/`. Another agent may have a branch checked out there, and its
modules are not this repository's to tidy.

## What drifts

**Tidiness.** `go mod tidy -diff` exits non-zero when the module is untidy and
prints what would change. It writes nothing, so it is safe to run across every
module before deciding anything.

```bash
(cd "$d" && go mod tidy -diff)
```

**The `go` directive.** A nested module declares its own, and nothing keeps it in
step with the root. All six gohai examples sat at `go 1.25.7` while the root was
at `1.26.0`. The rule in
[the charter](../../../../.charter/fragments/global/tooling.md) applies to these
files too: the floor is the older of the two newest minor releases, and a nested
module has no reason to differ from its parent.

```bash
find ~/git/osapi-io/$r -name go.mod -not -path '*/.worktrees/*' \
  -exec sh -c 'printf "%s\t%s\n" "$1" "$(grep -m1 "^go " "$1" | cut -d" " -f2)"' _ {} \;
```

**Dependency versions.** A nested module resolves its own requirements, so it can
pin an older version of something the root has already moved past.

## Fixing

```bash
cd ~/git/osapi-io/$r
for d in $(find . -name go.mod -not -path './.worktrees/*' -not -path './go.mod' -exec dirname {} \;); do
  (cd "$d" && go get -u ./... && go mod tidy)
done
just ready && just test
```

`go get -u ./...` is what actually bumps; `go mod tidy` alone only reconciles
what is already required. Run the repository's own gate afterwards: an example
that no longer compiles is a broken example, and several of these are referenced
from the README.

A module using `replace ... => ../../` to point at its parent needs no version
bump for the parent, and `go get -u` will not invent one.

## The better fix, which is not this

Dependabot v2 takes `directories` with globs, so the drift could stop happening
rather than be swept up:

```yaml
- package-ecosystem: "gomod"
  directories:
    - "/"
    - "/examples/*"
```

Worth proposing when reporting this. The cost is more Dependabot pull requests;
the benefit is that nobody has to remember. Do not change `dependabot.yml`
without asking: it decides how much noise the repository generates.
