# Permissions

Every authenticated endpoint requires one named permission. A token carries roles,
roles resolve to a set of permissions, and the handler checks the one it needs.

37 permissions, three built-in roles.

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

The resource is the domain the endpoint belongs to. The verb is what the endpoint
does to it, and it is not always `read` or `write`: `command:execute`,
`command:shell` and `docker:execute` exist because running something is not the
same as changing something, and a role can be given one without the other.

`client.Permission` in the SDK is the type, so the permission set is part of
osapi's public API rather than an internal detail. A consumer can name the
permission it needs.

## The three built-in roles

| Role    | Permissions | Is                                                   |
| ------- | ----------: | ---------------------------------------------------- |
| `admin` |          37 | everything, including `audit:read`                   |
| `write` |          30 | read, write and execute, but not audit               |
| `read`  |          17 | reads only                                           |

```sh
awk '/client.RoleAdmin: {/,/^\t},/' internal/authtoken/permissions.go | grep -cE '^\t\tPerm'  # 37
awk '/client.RoleWrite: {/,/^\t},/' internal/authtoken/permissions.go | grep -cE '^\t\tPerm'  # 30
awk '/client.RoleRead: {/,/^\t},/' internal/authtoken/permissions.go | grep -cE '^\t\tPerm'   # 17
```

`write` is not `admin` minus one thing. The seven it lacks:

```
agent:write       audit:read        power:execute     process:execute
command:execute   command:shell     docker:execute
```

Seven is 37 minus 30, both of which carry their command above. The names come
from reading the two blocks in `internal/authtoken/permissions.go` side by side.

Reading the list is the fastest way to understand the role: `write` can change
configuration and cannot make anything *happen*. It restarts nothing, runs no
command, reboots nothing, and cannot read who did. Every one of the seven is
either executing something or seeing who executed something.

`read` holds 17 of 37, so the 20 it lacks are the writes and the seven above. A
domain typically exposes one read and one write, which is why the two sides are
close in size rather than one dominating.

## How a token resolves to a permission set

`ResolvePermissions` takes roles, direct permissions, and the custom roles a
deployment configured. Two things about the order matter more than the mechanism.

**Direct permissions override roles completely.** If a token carries any explicit
permission, `ResolvePermissions` returns that set and **never looks at the roles at
all**:

```go
if len(directPermissions) > 0 {
    // roles are not consulted
    return set
}
```

So a token with `permissions: ["health:read"]` and `roles: ["admin"]` has exactly
one permission. That is the intended behaviour for a narrowly scoped token, and it
is a trap for anybody who expects the two to union.

**A custom role shadows a built-in one of the same name.** Custom roles are tried
first, so a deployment defining its own `admin` replaces the built-in `admin`
rather than extending it. A custom role that omits `audit:read` takes it away.

`HasPermission` is then a map lookup. There is no wildcard, no inheritance at
check time, and no implicit grant.

## `RoleHierarchy` is a different thing

`internal/authtoken/token.go` holds a second map:

```go
var RoleHierarchy = map[string][]string{
    "admin": {"read", "write", "admin"},
    "write": {"read", "write"},
    "read":  {"read"},
}
```

This is about **scopes on the token**, used by `GenerateAllowedRoles` when issuing
one. It is not the permission resolution above, and the two are easy to confuse
because both are maps keyed by role name. Permissions come from
`DefaultRolePermissions`; this decides what a token may claim.

## Adding a permission

Four places, and missing any one of them is a different failure.

| Add it to                          | Or else                                              |
| ---------------------------------- | ---------------------------------------------------- |
| the permission constants           | it does not exist                                    |
| `AllPermissions`                   | it is not a known permission                         |
| `DefaultRolePermissions`           | **it reaches nobody**                                |
| the SDK's `client.Permission` set  | a consumer cannot name it                            |

The third is the silent one. A permission that exists in the OpenAPI
specification, is checked by a handler, and appears in no role is a permission no
token can ever have, so the endpoint is unreachable and nothing reports it.

The roles tables on the published site need it too, because that is where an
operator configuring a custom role will look.

**Choose by blast radius, not by endpoint group.** Two operations that differ in
how much damage they can do want two permissions however similar their shape.
That is why `command:shell` is separate from `command:execute`.

## What checks it

The handler, through scope middleware that a domain package wraps itself. The UI
also reads the roles claim to decide what to show, and **that is not a check**:
[the embedded UI](ui.md) decodes the token without verifying it, so nothing the UI
hides is protected by the UI hiding it.

## Where this connects

Adding a domain, including where a new permission has to be registered and why a
handler wraps its own middleware, is [building a domain](domains.md).

What the UI does with the roles claim, and why its decode is not verification, is
[the embedded UI](ui.md).

______________________________________________________________________

Written from `internal/authtoken/` rather than from a feature. No feature covers
this package, which is why the embedded UI's specification could state that the
permission model "is osapi's" and cite nothing: the corpus had no statement of it
to cite.
