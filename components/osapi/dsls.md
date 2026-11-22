# The parts that each DSL shares

osapi has three DSLs: the behavior DSL (`internal/behavior`), the endpoint DSL
(`internal/controller/endpoint`) and the command DSL (`internal/cli/command`).
The chain rules are a fourth set of terms in `internal/behavior`. Each DSL
defines a different thing, but each has the same parts. This page names the
parts, so that a new DSL gets each one and an old DSL keeps each one. The osapi
page `development/dsl/new-dsl.md` tells an author the same parts, with the
steps.

## The parts

| Part         | Where it is                                    | What it holds                                                   |
| ------------ | ---------------------------------------------- | --------------------------------------------------------------- |
| Spec         | `guide.Spec` in `internal/guide`               | a term for each exported part of the DSL: what it does, when    |
| Checks       | `guide.Checks` in `internal/guide`             | each rule of validate, what it requires, and its fix            |
| Commands     | `<dsl> spec get`, `<dsl> validate`, `create`   | the spec, the problems with their fixes, and a new definition   |
| Typed values | named types and constants in the DSL package   | each value from a fixed set, with a validate rule               |
| Tag keys     | `command.KnownTags`, `command.TagKeys`         | the struct tag keys that the three DSLs read                    |
| Permissions  | `declarations()` in `internal/authtoken`       | the permission of each method that the API serves               |
| Generation   | `genfile.Writer` in `internal/cli/command/gen` | the files of a run, written only when the whole run succeeds    |
| Checks of CI | `go-generate-check`, `*-scaffold-check`        | generated files that match, and a scaffold that passes its test |
| Docs page    | `dslPages` in `cmd/commands.go`                | the page under `development/dsl/` that the spec writes          |
| Skill        | `internal/skills/resources/dev-skills/`        | judgment only; it sends an agent to `spec get` and `validate`   |

## What keeps the parts complete

Tests hold each table to the code:

- A spec test reads the exported functions of the DSL package and fails on one
  that has no term. The behavior DSL has `TestSpecHasEveryPartOfTheDSL`. The
  endpoint DSL and the command DSL have `TestSpecCoversTheDSL`.
- A checks test fails on a rule that has no check. The behavior DSL reads each
  `Rule` constant. The endpoint DSL and the command DSL also fail on a check
  that no test case triggers.
- A test of each registry runs validate on each registered definition.
- `cli-docs-gen-check` fails when a DSL page differs from the binary.

## Typed values

Go converts an untyped string literal to a named string type. Thus a type alone
does not refuse a misspelled value: `behavior.Platform("debain", ...)` compiles.
Each typed value also has a validate rule that refuses a value outside its set,
such as `KnownPlatforms()`, `KnownGroups()` and `KnownParents()`. The sweeps of
osapi-io/osapi#1062 and osapi-io/osapi#1072 gave the DSLs these types.
osapi-io/osapi#1078 plans two guards: a test that fails on a new bare `string`
in the exported API of a DSL, and a test that fails on a string literal where a
typed value goes.

Go reads a struct tag only by its exact key. Thus a misspelled key does nothing,
and no compiler reports it. The three DSLs use one list, `command.KnownTags`.
The command DSL refuses an unknown key of an output field, and the behavior DSL
refuses one of an input field.

## Permissions

`declarations()` reads the permissions from the registries of the endpoint DSL
and the behavior DSL. A rule gives the built-in roles their permissions, and
`AdminOnly()` keeps a permission from `write` and `read`.
[Permissions](permissions.md) has the rule. A new DSL with API routes adds its
registry to three places: `declarations()`, the generator of the SDK constants
in `internal/authtoken/gen`, and `RegistryOperations`, which gives the
permission of each operation of the UI. A DSL with no API route, as the command
DSL, declares no permission.

## Generation

`genfile.Writer` records each change, and `Flush` makes the changes at the end
of a run that succeeds. Thus a generator that fails or panics part way changes
nothing on disk. Before this, a generator that panicked left a `gen/` directory
empty, and a commit removed its files (osapi-io/osapi#1070). jennifer's `Lit`
panics on a named type, so a generator writes `jen.Lit(string(v))`.

## What this page does not cover

- How to use each DSL: the pages that `spec get` writes, and
  [Behaviors](behaviors.md), [Endpoints](endpoints.md) and
  [Commands](commands.md).
- Records at run time. The examples record each call of a behavior with
  `behavior.Record`. A real job that records its calls is planned in
  osapi-io/osapi#1076.
- Extensions. A DSL that extensions use must let a definition register without a
  recompile, and its registry must not depend on code that osapi generates.
  osapi-io/osapi#1064 has the design questions.
