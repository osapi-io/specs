# Permissions

Each authenticated endpoint needs one named permission. A token has roles. The
roles resolve to a set of permissions. The handler checks the permission that it
needs.

There are 37 permissions and three built-in roles.

```sh
grep -cE '^\tPerm[A-Za-z]+ +Permission = ' pkg/sdk/client/permissions.go  # 37
```

## The shape is `resource:verb`

```
agent:read     node:write      command:execute
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

`client.Permission` in the SDK is the type. Thus the permission set is part of
the public API of osapi, not an internal detail. A consumer can name the
permission that it needs.

## The three built-in roles

| Role    | Permissions | Is                                     |
| ------- | ----------: | -------------------------------------- |
| `admin` |          37 | everything, including `audit:read`     |
| `write` |          30 | read, write and execute, but not audit |
| `read`  |          17 | reads only                             |

```sh
awk '/client.RoleAdmin: {/,/^\t},/' internal/authtoken/permissions.go | grep -cE '^\t\tPerm'  # 37
awk '/client.RoleWrite: {/,/^\t},/' internal/authtoken/permissions.go | grep -cE '^\t\tPerm'  # 30
awk '/client.RoleRead: {/,/^\t},/' internal/authtoken/permissions.go | grep -cE '^\t\tPerm'   # 17
```

`write` is not `admin` minus one thing. It does not have these seven:

```
agent:write       audit:read        power:execute     process:execute
command:execute   command:shell     docker:execute
```

Seven is 37 minus 30. The commands above give the two numbers. The names come
from a comparison of the two blocks in `internal/authtoken/permissions.go`.

The list is the fastest way to understand the role. `write` can change the
configuration, but it cannot make anything *occur*. It restarts nothing, runs no
command, reboots nothing, and cannot read who did. Each of the seven runs
something, or shows who ran something.

`read` has 17 of 37. Thus it does not have the 20 writes and the seven above. A
domain usually has one read and one write. Thus the two sides are almost the
same size.

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
`init` of `authtoken`. `osapi token roles` prints the result, with the
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
updated by hand. It now points to `osapi token roles`. That command prints the
list from the binary, so it cannot be out of date.

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
