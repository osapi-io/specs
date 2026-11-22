# Permissions

Each authenticated endpoint needs one named permission. A token has roles. The
roles resolve to a set of permissions. The handler checks the permission that it
needs.

## The shape is `resource:verb`

```
agent:read     sysctl:write    command:execute
job:read       network:write   command:shell
health:read    file:write      docker:execute
audit:read     docker:write    ...
```

The resource is the domain of the endpoint. The verb is what the endpoint does
to it, and it is not always `read` or `write`. `command:execute`,
`command:shell` and `docker:execute` exist because to run something is not the
same as to change something. Thus a role can get one without the other.

A [behavior](behaviors.md) does not declare permissions. osapi makes the
permission of each method from the definition:

- the resource is the top-level group, or the name of the behavior when it has
  no group
- the verb is `read` for a `Read` method and `write` for a `Write` method

The `get` of sysctl needs `sysctl:read`. dns under `network` needs
`network:read`, the same as now. `osapi behavior get --name <name>` lists them.

Thus a domain that moves to a behavior can change its permission. The node reads
were all `node:read`. As behaviors, each has its own: `uptime:read`, `os:read`,
`disk:read`, `memory:read`, `load:read`, and `hostname:read` with
`hostname:write`. `node:read` now covers only the status summary, and
`node:write` is gone, because hostname update was its only endpoint. The
built-in roles get each behavior permission, so a token with a built-in role
keeps its access. A custom role that named `node:read` or `node:write` for these
domains must name the new permissions.

`client.Permission` in the SDK is the type. Thus the permission set is part of
the public API of osapi, not an internal detail. A consumer can name the
permission that it needs.

## The three built-in roles

A rule in `RolePermissions` makes each role from the permissions that osapi
knows. No list of roles is written by hand.

| Role    | Gets                                                      |
| ------- | --------------------------------------------------------- |
| `admin` | each permission                                           |
| `write` | each `read` and `write` permission that is not admin only |
| `read`  | each `read` permission that is not admin only             |

A permission is admin only when its verb is `execute` or `shell`, or when a
method that needs it is marked `AdminOnly()`.

`trace:read` is in each role, `read` included. A trace shows the hosts,
operations and errors of a request, the same as the job that the role can
already read. It is a separate permission so that a custom role can read jobs
without traces.

`write` is not `admin` minus one thing. It does not have these:

```
admission:write   agent:write       audit:read        power:execute
process:execute   command:execute   command:shell     docker:execute
```

The verb makes the four `execute` permissions and `command:shell` admin only.
`AdminOnly()` on the methods of the admission, agent and audit endpoint groups
makes `admission:write`, `agent:write` and `audit:read` admin only.

The list is the fastest way to understand the role. `write` cannot run a
command, reboot, signal a process, admit a machine, or read who did something.

It can still make things occur. Service start, stop, restart, enable and disable
check `service:write`, which `write` has. This page said until 21 November 2026
that `write` "restarts nothing"; the service routes check `service:write`, and
they did when the page was written. `write` can also reach root without the
permissions that it does not have: a cron entry runs as the user that it names,
`user:write` adds SSH keys, and `file:write` and `package:write` change what
runs. osapi-io/osapi#999 audits the roles against the people who use osapi, and
decides these.

`read` has the reads of each domain. It does not have the writes, or the
permissions in the list above.

## How a token resolves to a permission set

`ResolvePermissions` takes the roles, the direct permissions, and the custom
roles that a deployment configured. Two facts about the order are more important
than the mechanism.

**Direct permissions replace the roles completely.** If a token has an explicit
permission, `ResolvePermissions` returns that set. It **never examines the
roles**:

```go
if len(directPermissions) > 0 {
    // roles are not consulted
    return set
}
```

Thus a token with `permissions: ["health:read"]` and `roles: ["admin"]` has
exactly one permission. This is correct for a token with a small scope. But a
person who expects a union of the two gets an unexpected result.

**A custom role replaces a built-in role with the same name.** osapi tries the
custom roles first. Thus a deployment that defines its own `admin` replaces the
built-in `admin`. It does not add to it. A custom role without `audit:read`
removes that permission.

`HasPermission` is then a map lookup. There is no wildcard, no inheritance at
check time and no implicit grant.

## `RoleHierarchy` is a different thing

`internal/authtoken/token.go` has a second map:

```go
var RoleHierarchy = map[string][]string{
    "admin": {"read", "write", "admin"},
    "write": {"read", "write"},
    "read":  {"read"},
}
```

This map is about **scopes on the token**. `GenerateAllowedRoles` uses it when
it makes a token. It is not the permission resolution above. People confuse the
two, because both are maps with role names as keys. Permissions come from
`RolePermissions(role)`. This map decides what a token can claim.

## Adding a permission

Declare the method. The permission and its roles come from the definition:

- **A behavior:** register it. Its methods need `<name>:read` and
  `<name>:write`, or those of its group.
- **An endpoint group:** register it. A GET needs `<group>:read`, and each other
  verb `<group>:write`. `.Permission("agent:read")` names a different one, which
  something else must declare.
- **A hand-written domain** under `internal/controller/api`: add each permission
  that it needs to `builtinPermissions` in `internal/authtoken/permissions.go`,
  as a string. The list goes as each domain becomes a behavior.

To keep a permission from `write` and `read`, mark the method `.AdminOnly()`, in
the behavior DSL or the endpoint DSL. Each method that needs the permission must
agree. `osapi token roles get --name write` shows what a role gets.
`osapi behavior spec get` and `osapi endpoint spec get` teach the same rule.

`AllPermissions()` and `RolePermissions(role)` make their result on each call,
not one time. A behavior or a group registers in the `init` of its own package,
and that `init` can run after the `init` of `authtoken`. Thus a test that checks
roles imports the groups and the behaviors, as the binary does.

`go generate ./internal/behaviors/all` writes the SDK's constants in
`pkg/sdk/client/permissions.gen.go`, one `Perm` constant for each permission and
one `Role` constant for each built-in role, and the UI's list in
`ui/src/lib/permissions.gen.ts`. A test fails when either file is stale. A
permission constant is `Perm`, then the resource and the verb with capitals,
such as `PermDiskRead` for `disk:read`. `just cli-docs-generate` writes the role
table of the configuration page of the docs site from `RolePermissions`.

Before osapi-io/osapi#1059, an endpoint group's permission reached a role only
when a person added it to `builtinPermissions` and to `builtinRolePermissions`,
and the admin-only set was the difference between two hand lists.
`builtinRolePermissions` is gone. The roles that the rule makes are the same as
those lists made. A test compared all three before and after the change.

A permission that nothing declares gives no signal at runtime. A handler checks
it, no role has it, and each call gets 403. Thus `authtoken.Check` fails a test
when an endpoint method names a permission that nothing declares, or when one
method marks a permission `AdminOnly()` and another method does not.

A custom role in `controller.api.security.roles` is a name and a list of
permissions, for each deployment. The config does not load when a permission of
a custom role is not one that osapi knows. `osapi token generate --roles`
accepts a built-in role or a custom role of the config.

An operator who configures a custom role looks for the list of permissions. The
authentication page of the published site had that list as a table that people
updated by hand. It now points to `osapi token roles list`. That command prints
the list from the binary, so it cannot be out of date.

**Select by the possible damage, not by the endpoint group.** If two operations
can do different amounts of damage, they need two permissions, also if their
shape is the same. That is why `command:shell` is separate from
`command:execute`.

## What checks it

The handler checks it, through scope middleware that the domain package wraps
itself. Before the code runs, `TestPermissionsAreDeclared` in
`internal/behaviors/all` runs `authtoken.Check` with each group and behavior
registered. The UI also reads the roles claim to decide what to show. **That is
not a check.** [The embedded UI](ui.md) decodes the token, but it does not
verify it. When the UI hides something, that does not protect it.

## Where this connects

[Building a domain](domains.md) tells how to add a domain. It also tells where
to register a new permission, and why a handler wraps its own middleware.

[The embedded UI](ui.md) tells what the UI does with the roles claim, and why
its decode is not a verification.

______________________________________________________________________

Written from `internal/authtoken/` and `pkg/sdk/client/permissions.gen.go`.
