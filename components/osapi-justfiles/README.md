# osapi-justfiles

`osapi-justfiles` is a library of shared `just` recipes. It has no Go, no tool
and no service. It runs only recipes and the shell that they call. It exists so
that a convention for more than one repository is written one time, not eight
times.

It has six modules, 44 recipes and 22 override variables.

| Module       | What it is for                                                          |
| ------------ | ----------------------------------------------------------------------- |
| `ansible`    | Runs, lints and formats Ansible content through uv                      |
| `docusaurus` | Builds, serves, deploys and formats a Docusaurus documentation site     |
| `go`         | Builds, tests, formats, lints and measures coverage for a Go project    |
| `just`       | Formats and checks a repository's justfiles, using just's own formatter |
| `md`         | Formats every markdown file in a repository with mdformat               |
| `react`      | Builds, lints, formats and serves a React application                   |

## Where it sits

It depends on no other repository in the organization, and eight repositories
depend on it. It is the only node in the dependency graph with no outgoing
connection. Thus a change here has the widest effect in the organization. It
gets to the next continuous integration run of each consumer with no release, no
tag and no review in the consumer.

| Consumer             | Modules | Which                                  |
| -------------------- | ------: | -------------------------------------- |
| `osapi`              |       5 | all                                    |
| `gohai`              |       3 | `go`, `just`, `md`                     |
| `nats-client`        |       3 | `go`, `just`, `md`                     |
| `nats-server`        |       3 | `go`, `just`, `md`                     |
| `osapi-orchestrator` |       3 | `go`, `just`, `md`                     |
| `specs`              |       2 | `just`, `md`, having no Go and no site |
| `osapi-lab`          |       3 | `ansible`, `just`, `md`                |
| `osapi-justfiles`    |       1 | `md`, from itself                      |

Thus `md` goes to all eight, `just` to seven, `go` to five, and `react`,
`docusaurus` and `ansible` to one each. **A change to `md` has the widest
effect.** `specs` uses it, and the `just test` of `specs` checks each change to
these docs.

Get the consumer list from
`gh repo list osapi-io --no-archived --visibility public`, and read each `fetch`
recipe. Do not trust the table above. The table was incorrect one time. It said
six consumers, because the writer used the six *components*, and `specs` is not
a component.

## How a consumer gets a module

```
fetch:
    mkdir -p .just/remote
    curl -sSfL https://raw.githubusercontent.com/osapi-io/osapi-justfiles/refs/heads/main/go/go.just -o .just/remote/go.just
```

```
import? '.just/remote/go.just'
```

The consumer gets the module at build time. It does not keep a copy in git. Each
consumer ignores `.just/` in git. Thus nothing in a consumer records which
version of a module it used. The import is optional. Thus the justfile of a
consumer parses before `just fetch` ran, and a missing module shows as an
unknown recipe, not as a parse error.

Recipes come out and variables go in. Nothing else crosses the boundary: no
configuration file, no environment contract and no generated file. A consumer
sets the variables that it wants to change, then imports the module. The recipes
of the module read them.

## It is its own consumer, asymmetrically

The root justfile gets `md.just` from `main` and imports it. But it runs its own
`just` module directly from the working tree.

```
import? '.just/remote/md.just'

test:
    just --justfile just/just.just --working-directory . just-fmt-check
    just md-fmt-check
```

Thus one half of its own `test` recipe checks the local file. The other half
checks the file on `main`. The repository that owns `md.just` cannot test a
change to it until the change is on `main`. No other repository in the
organization has this shape.

## The recipes

The name of each recipe starts with its group, and its `[group(...)]` is that
prefix. Thus an import adds a predictable namespace, and `just --list` shows one
block for each tool. The prefix is the name of the module, except for
`docusaurus`, whose recipes are `docs-*`. The group tells what the recipes are
for, not which tool runs them.

| Module       | Group     | Recipes |                                                                                                                                                                                                                                 |
| ------------ | --------- | ------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ansible`    | `ansible` |       6 | `ansible-deps`, `ansible-fmt`, `ansible-fmt-check`, `ansible-lint`, `ansible-run`, `ansible-test`                                                                                                                               |
| `docusaurus` | `docs`    |      10 | `docs-build`, `-bump`, `-clean`, `-deploy`, `-deps`, `-fmt`, `-fmt-check`, `-generate`, `-serve`, `-start`                                                                                                                      |
| `go`         | `go`      |      16 | `go-deps`, `go-fmt`, `go-fmt-check`, `go-generate`, `go-mod`, `go-mod-bump`, `go-mod-check`, `go-run`, `go-test`, `go-unit`, `go-unit-cov`, `go-unit-cov-check`, `go-unit-cov-gaps`, `go-unit-cov-map`, `go-unit-int`, `go-vet` |
| `just`       | `just`    |       2 | `just-fmt`, `just-fmt-check`                                                                                                                                                                                                    |
| `md`         | `md`      |       2 | `md-fmt`, `md-fmt-check`                                                                                                                                                                                                        |
| `react`      | `react`   |       8 | `react-build`, `react-deps`, `react-dev`, `react-fmt`, `react-fmt-check`, `react-generate`, `react-lint`, `react-test`                                                                                                          |

Three recipes take arguments, and the name does not tell you. `docs-bump` needs
a `version`. `go-run` takes any number of arguments and gives them to `go run`.
`ansible-run` needs a `playbook`, and gives more arguments to
`ansible-playbook`. The other 41 take none.

Until all repositories change, the old names, `docusaurus-*` and `run`, still
work as hidden aliases. A consumer with its own `run` recipe, as voidspan and
psion have, does not conflict with `go` now.

## The variables

There are twenty-two, and all have defaults. A consumer sets
`allow-duplicate-variables` and sets the variables that it wants to change in
its own justfile. The value of the consumer applies, before or after the import.
A module reads no environment variable. A variable in the justfile is the only
way to change a value.

```sh
# just 1.45: prints "before", then "after"
printf 'x := "module"
show:
    @echo {{x}}
' > mod.just
printf 'set allow-duplicate-variables
x := "before"
import "mod.just"
' > b.just
printf 'set allow-duplicate-variables
import "mod.just"
x := "after"
' > a.just
just -f b.just show; just -f a.just show
```

| Module       | Variable             | Default                                                   |
| ------------ | -------------------- | --------------------------------------------------------- |
| `ansible`    | `ansible_dir`        | `ansible`                                                 |
| `ansible`    | `ansible_playbooks`  | `playbooks`                                               |
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
neither. But they are opposite facts. The first means that a consumer need not
act. The second means that the consumer must act. The header block of each
module declares twenty-one variables. `go_packages` is declared at
`go/go.just:147`, next to the recipe that uses it.

`just` takes no configuration.

## What a consumer may depend on

Consumers depend on 44 recipe names and 22 variable names, and nothing in the
repository declares them.

**The contract is the content of `main`.** There is no release, no tag, no
version number and no deprecation path. If somebody renames a recipe on `main`,
each consumer gets the new name at its next `just fetch`. Thus you can depend on
the names above as `main` has them today, and on nothing about tomorrow.

Each module pins the tools that it calls, but nothing pins the module. `md` pins
mdformat 1.0.0, mdformat-gfm 1.0.0 and Python 3.13. `go` pins a coverage target
of 100. The inner versions are fixed, and the outer version is not. A reader
expects the opposite from either half alone.

## How big it is

There are six modules, 44 recipes and 22 override variables.

```sh
for m in ansible docusaurus go just md react; do just --justfile $m/$m.just --working-directory . --summary; done | wc -w   # 44
grep -hcE '^[a-z_][a-z0-9_]* *:?= ' */*.just | paste -sd+ - | bc                                                    # 22
```

## Known limitations

**Nothing pins the modules.** Each consumer gets the modules from
`refs/heads/main`. Thus nothing records which version a build used. The rule is
that the two provisioning paths use the same version. Here there is no mechanism
at all, not two different mechanisms. The rule about committed output does not
apply, because each consumer ignores `.just/` in git and does not commit it.

**The asymmetric self-use** above. This repository cannot test a change to
`md.just` before the change is on `main`.

**One recipe breaks the namespace.** `run` in `go`, the module that most
repositories import.

## Not covered here

What each recipe does inside. The recipes are the statement of record, and prose
about their shell becomes incorrect.

The content of the six module READMEs. Each one documents the interface of the
file next to it.

The contributor conventions of the repository, its `Dockerfile` and its five
GitHub workflows.

If each recipe is correct. This page describes the contract, not if a recipe
does what its name says.

______________________________________________________________________

Written from the osapi-justfiles repository.
