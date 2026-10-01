# osapi-justfiles

`osapi-justfiles` is a library of shared `just` recipes. No Go, no tool, no
service. Its only executable content is recipes and the shell they invoke, and
it exists so a convention binding several repositories is written once instead
of seven times.

Five modules, 38 recipes, 20 override variables.

| Module       | What it is for                                                          |
| ------------ | ----------------------------------------------------------------------- |
| `docusaurus` | Builds, serves, deploys and formats a Docusaurus documentation site     |
| `go`         | Builds, tests, formats, lints and measures coverage for a Go project    |
| `just`       | Formats and checks a repository's justfiles, using just's own formatter |
| `md`         | Formats every markdown file in a repository with mdformat               |
| `react`      | Builds, lints, formats and serves a React application                   |

## Where it sits

It depends on no other repository in the organization, and seven depend on it.
It is the only node in the dependency graph with no outgoing edge, which makes a
change here the widest change available in the organization: it reaches every
consumer's next continuous integration run with no release, no tag and no review
in the consuming repository.

| Consumer             | Modules | Which                                  |
| -------------------- | ------: | -------------------------------------- |
| `osapi`              |       5 | all                                    |
| `gohai`              |       3 | `go`, `just`, `md`                     |
| `nats-client`        |       3 | `go`, `just`, `md`                     |
| `nats-server`        |       3 | `go`, `just`, `md`                     |
| `osapi-orchestrator` |       3 | `go`, `just`, `md`                     |
| `specs`              |       2 | `just`, `md`, having no Go and no site |
| `osapi-justfiles`    |       1 | `md`, from itself                      |

So `md` reaches all seven, `just` six, `go` five, and `react` and `docusaurus`
one each. **`md` is the widest change available**, and `specs`, whose
`just test` gates every corpus change in the organization, is downstream of it.

Take the consumer list from
`gh repo list osapi-io --no-archived --visibility public` and read each `fetch`
recipe rather than trusting the table above. The table was wrong once: it said
six consumers, because it was written from the six *components* and `specs` is
not a component.

## How a consumer gets a module

```
fetch:
    mkdir -p .just/remote
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/go/go.just -o .just/remote/go.just
```

```
import? '.just/remote/go.just'
```

Fetched, not vendored. `.just/` is gitignored in every consumer, so nothing in a
consumer records which version of a module it built with. The import is
optional, so a consumer's justfile parses before `just fetch` has ever run and a
missing module surfaces as an unknown recipe rather than a parse error.

Recipes come out, variables go in. Nothing else crosses the boundary: no
configuration file, no environment contract, no generated artifact. A consumer
assigns the variables it wants to override, then imports the module, and the
module's recipes read them.

## It is its own consumer, asymmetrically

The root justfile fetches `md.just` from `main` and imports it, while invoking
its own `just` module straight from the working tree.

```
import? '.just/remote/md.just'

test:
    just --justfile just/just.just --working-directory . just-fmt-check
    just md-fmt-check
```

So one half of its own `test` recipe checks the file in front of you and the
other half checks whatever `main` holds. A change to `md.just` cannot be tested
by the repository that owns it until it is already on `main`. No other
repository in the organization has this shape.

## The recipes

37 of the 38 carry their module's name as a prefix, so an import adds a
predictable namespace. One does not: `run`, in `go`, which is the most widely
imported module. A consumer with its own `run` recipe collides with it.

| Module       | Recipes |                                                                                                                                                                                                                              |
| ------------ | ------: | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `docusaurus` |      10 | `docusaurus-build`, `-bump`, `-clean`, `-deploy`, `-deps`, `-fmt`, `-fmt-check`, `-generate`, `-serve`, `-start`                                                                                                             |
| `go`         |      16 | `go-deps`, `go-fmt`, `go-fmt-check`, `go-generate`, `go-mod`, `go-mod-bump`, `go-mod-check`, `go-test`, `go-unit`, `go-unit-cov`, `go-unit-cov-check`, `go-unit-cov-gaps`, `go-unit-cov-map`, `go-unit-int`, `go-vet`, `run` |
| `just`       |       2 | `just-fmt`, `just-fmt-check`                                                                                                                                                                                                 |
| `md`         |       2 | `md-fmt`, `md-fmt-check`                                                                                                                                                                                                     |
| `react`      |       8 | `react-build`, `react-deps`, `react-dev`, `react-fmt`, `react-fmt-check`, `react-generate`, `react-lint`, `react-test`                                                                                                       |

Two take arguments, which a bare name does not tell you: `docusaurus-bump`
requires a `version`, and `run` is variadic and forwards what it is given to
`go run`. The other 36 take none.

## The variables

Twenty, all with defaults. A consumer assigns the ones it wants to change before
the import.

| Module       | Variable             | Default                                                   |
| ------------ | -------------------- | --------------------------------------------------------- |
| `docusaurus` | `docusaurus_dir`     | `docs`                                                    |
| `docusaurus` | `docusaurus_host`    | `localhost`                                               |
| `docusaurus` | `docusaurus_port`    | `3001`                                                    |
| `go`         | `go_git_root`        | computed, `git rev-parse --show-toplevel`                 |
| `go`         | `go_main_package`    | `main.go`                                                 |
| `go`         | `go_coverage_dir`    | `.coverage`                                               |
| `go`         | `go_coverage_target` | `100`                                                     |
| `go`         | `go_fmt_excludes`    | empty, a consumer adds `! -path` clauses                  |
| `go`         | `go_os_tags`         | computed, `-tags=ubuntu` on Ubuntu and empty elsewhere    |
| `go`         | `go_packages`        | computed, `go list ./...` less `node_modules`             |
| `md`         | `md_version`         | `1.0.0`                                                   |
| `md`         | `md_gfm_version`     | `1.0.0`                                                   |
| `md`         | `md_wrap`            | `80`                                                      |
| `md`         | `md_python`          | `3.13`                                                    |
| `md`         | `md_site_dir`        | `docs`                                                    |
| `md`         | `md_excludes`        | excludes `.claude`, `node_modules`, `.worktrees`, `.just` |
| `md`         | `md_site_exclude`    | derived from `md_site_dir`, empty when that is empty      |
| `md`         | `md_extra_excludes`  | empty                                                     |
| `react`      | `react_dir`          | `.`                                                       |
| `react`      | `react_fmt_pattern`  | `src/**/*.{ts,tsx,css}`                                   |

An empty default and a missing default look the same in a table that prints
neither, and they are opposite facts: one means a consumer need not act, the
other means they must. Nineteen are declared in their module's header block;
`go_packages` is declared at `go/go.just:147`, beside the recipe that uses it.

`just` takes no configuration at all.

## What a consumer may depend on

38 recipe names and 20 variable names. That is a contract by every test that
matters: a consumer depends on it, renaming part of it breaks them at their next
fetch, and nothing in the repository declares it.

**What it is worth, stated as what is true rather than as what would be
reasonable: the contract is whatever `main` holds.** No release, no tag, no
version number, no deprecation path. A recipe renamed on `main` is renamed for
every consumer at their next `just fetch`. A consumer may depend on the names
above being what `main` holds today and on nothing about tomorrow.

Each module pins the tools it invokes while nothing pins the module. `md` pins
mdformat 1.0.0, mdformat-gfm 1.0.0 and Python 3.13; `go` pins a coverage target
of 100. The inner versions are fixed and the outer one floats, which is the
reverse of what a reader would guess from either half alone.

## How big it is

Five modules, 38 recipes, 20 override variables.

```sh
for m in docusaurus go just md react; do just --justfile $m/$m.just --working-directory . --summary; done | wc -w   # 38
grep -hcE '^[a-z_][a-z0-9_]* *:?= ' */*.just | paste -sd+ - | bc                                                    # 20
```

## Known limitations

**Nothing pins the modules.** Every consumer fetches from `refs/heads/main`, so
nothing records which version a build used. The rule this strains is that both
provisioning paths resolve to the same version, and here there is no mechanism
at all rather than a divergent one. The committed-output clause does not bite,
because `.just/` is gitignored rather than committed.

**The self-consumption asymmetry** above. A change to `md.just` cannot be tested
here before it is on `main`.

**One recipe breaks the namespace.** `run` in `go`, the most widely imported
module.

## Not covered here

What each recipe does internally. The recipes are the statement of record and
prose about their shell would drift.

The contents of the five module READMEs, which document the interface of the
file beside them.

The repository's own contributor conventions, its `Dockerfile`, and its five
GitHub workflows.

Whether any recipe is correct. This describes what the contract is, not whether
a recipe does what its name suggests.

______________________________________________________________________

Written from the osapi-justfiles repository. History:
`../../history/osapi-justfiles-001-justfiles-baseline/`.
