# The parts that each DSL shares

osapi has three DSLs: the behavior DSL (`internal/behavior`), the endpoint DSL
(`internal/controller/endpoint`) and the command DSL (`internal/cli/command`).
The chain rules are a fourth set of terms in `internal/behavior`. Each DSL
defines a different thing, but each has the same parts. This page names the
parts, so that a new DSL gets each one and an old DSL keeps each one. The guide
for an author is the `build-a-dsl` dev skill in the binary
(`internal/skills/resources/dev-skills/build-a-dsl/`), with the procedure in
`SKILL.md` and each part in `references/parts.md`.
`osapi skill get --name build-a-dsl` prints it. The binary is its only source:
the docs page `development/dsl/new-dsl.md` points to the skill, and
[Agent skills](agent-skills.md) tells how the dev skills are kept.

## The parts

| Part         | Where it is                                    | What it holds                                                    |
| ------------ | ---------------------------------------------- | ---------------------------------------------------------------- |
| Spec         | `guide.Spec` in `internal/guide`               | a term for each exported part of the DSL: what it does, when     |
| Checks       | `guide.Checks` in `internal/guide`             | each rule of validate, what it requires, and its fix             |
| Registry     | `dsl.Register` in `internal/dsl`               | each DSL with its command, skill, page, permissions, operations  |
| Commands     | `dsl.Commands()`                               | the commands that each DSL has, listed below                     |
| Typed values | named types and constants in the DSL package   | each value from a fixed set, with a validate rule                |
| Tag keys     | `command.KnownTags`, `command.TagKeys`         | the struct tag keys that the three DSLs read                     |
| Secrets      | `secret.Value` in `internal/secret`            | the type of an input that holds a secret, with the rule `secret` |
| Permissions  | `Permissions` of each registered DSL           | the permission of each method that the API serves                |
| Generation   | `genfile.Writer` in `internal/cli/command/gen` | the files of a run, written only when the whole run succeeds     |
| Checks of CI | `go-generate-check`, `*-scaffold-check`        | generated files that match, and a scaffold that passes its test  |
| Docs page    | `dslPages` in `cmd/commands.go`                | the page under `development/dsl/` that the spec writes           |
| Skill        | `internal/skills/resources/dev-skills/`        | judgment only; it sends an agent to `spec get` and `validate`    |

## The shared commands

Each DSL registers once in `internal/dsl`, from a `dsl.go` in its package. The
registry holds the name of the DSL, the command of its group, its skill, its
docs page, and, for a DSL whose definitions serve the API, its permissions and
its operations. `Without` names a shared command that does not apply, with the
reason. `TestEveryDSLHasTheSharedParts` in `internal/cli/commands/all` fails
when a DSL does not have a shared command, its skill or its page, and when a
`Without` entry has no reason. Thus a command that one DSL gets, each DSL gets,
or the change says why not.

| Command       | behavior | chain                        | endpoint | command             |
| ------------- | -------- | ---------------------------- | -------- | ------------------- |
| `list`        | yes      | yes                          | yes      | yes                 |
| `get`         | yes      | yes                          | yes      | yes                 |
| `method get`  | yes      | no: a chain has no methods   | yes      | yes                 |
| `spec get`    | yes      | yes                          | yes      | yes                 |
| `validate`    | yes      | yes                          | yes      | yes                 |
| `create`      | yes      | no: `Requires` makes a chain | yes      | yes                 |
| `openapi get` | yes      | no: a chain serves no route  | yes      | no: it calls no API |

`method get` shows one method in full in each DSL: its fields with their
constraints, its output, its examples and what it refuses. An endpoint method
also shows where the request carries each field, and its errors. The chain uses
the skill of the behavior DSL.

## What keeps the parts complete

Tests hold each table to the code:

- `TestEveryDSLHasTheSharedParts`, above.
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
such as `KnownPlatforms()` and `KnownParents()`. The sweeps of
osapi-io/osapi#1062 and osapi-io/osapi#1072 gave the DSLs these types.
`internal/dslcheck` has two guards (osapi-io/osapi#1078): a test that fails on a
new bare `string` in the exported API of a DSL that its allowlist does not give
a reason for, and a test that fails on a string literal where a typed value
goes.

Go reads a struct tag only by its exact key. Thus a misspelled key does nothing,
and no compiler reports it. The three DSLs use one list, `command.KnownTags`.
The command DSL refuses an unknown key of an output field, and the behavior DSL
refuses one of an input field.

## Secrets

A secret is a type, not a tag. `internal/secret` has `secret.Value`. An input
field of this type is a secret in each of the three DSLs. A map of secrets is
`map[string]secret.Value`, such as the environment of a container. Before
osapi-io/osapi#1240, the tag `secret:"true"` marked a secret. A tag with a typo
made the field an ordinary field, and nothing reported it (osapi-io/osapi#1062).
A type cannot have a typo. The key `secret` is not in `command.KnownTags`. Thus
a field that still has the tag fails the rule `tag`.

A `secret.Value` holds a reference, `secret://<vault>/<key>`, or a literal
value. `IsReference` tells which. `String`, `Format`, `MarshalJSON` and
`LogValue` give the reference, or `[redacted]` for a literal. Only `Reveal`
gives the value. A provider calls it only where it gives the value to a
command's standard input, an environment or a file. [Vaults](vaults.md) has the
vaults that a reference names.

What each part of a DSL does with a `secret.Value` field:

| Part                  | What it does                                                                                                                                                                                            |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spec of the API       | `type: string`, `format: password`, `writeOnly: true` and `x-osapi-secret: true`. The description says that it takes `secret://<vault>/<key>`. A map has this schema for each value.                    |
| `validate`            | refuses a secret field with `telemetry:"attr"`, and a secret field in the path or the query of a route, because a URL goes in logs. One rule, `secret`, in each DSL.                                    |
| `dslcheck`            | `TestSecretsAreTyped` fails on a `string` input field whose JSON name is on the audit denylist, unless `testdata/secrets.txt` gives a reason. This finds a missing type.                                |
| CLI                   | the flag takes a reference, or `-` to read the value from standard input. It refuses a literal value, because the shell history keeps it. A map flag takes `NAME=secret://...`.                         |
| SDK                   | a field of type `string`, from the spec. The SDK sends a literal or a reference as it gets it.                                                                                                          |
| `method get` and docs | the description of the field, from the spec.                                                                                                                                                            |
| Audit                 | the summary redacts each field name that has the type in a behavior or an endpoint group, with the fixed denylist of `internal/audit`. It keeps a reference, such as `secret://default/registry-token`. |
| Spans                 | never record the field.                                                                                                                                                                                 |
| Chain records         | `MarshalJSON` gives the reference, or `[redacted]`, at each depth of the input.                                                                                                                         |
| UI                    | the catalog marks the field as a secret. The form shows a password input, and a plan shows `<secret>`. A picker of references is not built ([Secrets](secrets.md#the-parts), part 9).                   |

The CLI sends the request, and the job client queues the job, with
`secret.Plain`. It gives a copy of the input in which each `secret.Value`
marshals its value. Each other marshal of the input gives the reference or
`[redacted]`.

The route of each method resolves a reference from its vault before the handler
gets the input ([Vaults](vaults.md#how-a-route-resolves-a-reference)). The job
client seals each value with `secret.PlainFunc`, and the dispatch of the agent
opens it with `secret.Map`
([Job system](job-system.md#a-secret-in-the-definition-is-sealed)). A `.Before`
step that changes the value, such as to the hash of a password, keeps it out of
the job in each case ([Behaviors](behaviors.md#a-step-on-the-controller)).

## Permissions

`declarations()` reads the permissions from `dsl.All()`: the `Permissions` of
each DSL that serves the API. A rule gives the built-in roles their permissions,
and `AdminOnly()` keeps a permission from `operator`, `automation` and `read`.
[Permissions](permissions.md) has the rule. The generator of the SDK constants
in `internal/authtoken/gen` and `authtoken.Operations`, which gives the
permission of each operation, read `dsl.All()` too. The catalog endpoint serves
the result of `Operations` to the UI ([the UI](ui.md#the-catalog)). Thus a new
DSL with API routes changes none of the three: it gives `Permissions` and
`Operations` when it registers. A DSL with no API route, as the command DSL,
gives neither. `dsl.All()` is in the order of the names, so the permissions of
the behaviors come before those of the endpoint groups.

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
