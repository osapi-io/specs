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

| Role    | Is                                     |
| ------- | -------------------------------------- |
| `admin` | everything, including `audit:read`     |
| `write` | read, write and execute, but not audit |
| `read`  | reads only                             |

`trace:read` is in each role, `read` included. A trace shows the hosts,
operations and errors of a request, the same as the job that the role can
already read. It is a separate permission so that a custom role can read jobs
without traces.

`write` is not `admin` minus one thing. It does not have these:

```
admission:write   agent:write       audit:read        power:execute
process:execute   command:execute   command:shell     docker:execute
```

The names come from a comparison of the two blocks in
`internal/authtoken/permissions.go`.

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

To add the permissions of a behavior, register the behavior. Nothing else is
necessary. `AllPermissions()` and `RolePermissions(role)` in
`internal/authtoken/permissions.go` make their result on each call. They use the
hand-written lists and the methods of each registered behavior: `<name>:read`
and `<name>:write`, or those of the group. `admin` and `write` get both. `read`
gets the read.

They make the result on each call, not one time. The reason: a behavior
registers in the `init` of its own package, and that `init` can run after the
`init` of `authtoken`. `osapi token roles list` prints the result, with the
behaviors.

The permission of a hand-written domain still goes in four places. If you forget
one, a different failure occurs.

| Add it to                         | Or else                      |
| --------------------------------- | ---------------------------- |
| the permission constants          | it does not exist            |
| `builtinPermissions`              | it is not a known permission |
| `builtinRolePermissions`          | **it reaches nobody**        |
| the SDK's `client.Permission` set | a consumer cannot name it    |

The third failure gives no signal. A permission can be in the OpenAPI
specification, and a handler can check it. If no role has it, no token can ever
have it. Thus nobody can use the endpoint, and nothing reports it.

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
itself. The UI also reads the roles claim to decide what to show. **That is not
a check.** [The embedded UI](ui.md) decodes the token, but it does not verify
it. When the UI hides something, that does not protect it.

## Where this connects

[Building a domain](domains.md) tells how to add a domain. It also tells where
to register a new permission, and why a handler wraps its own middleware.

[The embedded UI](ui.md) tells what the UI does with the roles claim, and why
its decode is not a verification.

______________________________________________________________________

Written from `internal/authtoken/` and `pkg/sdk/client/permissions.go`.
