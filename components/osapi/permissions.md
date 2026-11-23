# Permissions

Each authenticated endpoint needs one named permission. A token has roles. The
roles resolve to a set of permissions. The handler checks the permission that it
needs.

## The shape is `resource:verb`

```
agent:read     sysctl:write    command:execute
job:read       dns:write       command:shell
health:read    file:write      docker:execute
audit:read     docker:write    docker:exec ...
```

The resource is the domain of the endpoint. The verb is what the endpoint does
to it, and it is not always `read` or `write`. `command:execute`,
`command:shell`, `docker:execute` and `docker:exec` exist because to run
something is not the same as to change something. Thus a role can get one
without the other.

A [behavior](behaviors.md) does not declare permissions. osapi makes the
permission of each method from the definition:

- the resource is the name of the behavior, also when the behavior is in a group
- the verb is `read` for a `Read` method, `write` for a `Write` method,
  `execute` for an `Action`, such as a service restart, and the verb of
  `.PermitAs(verb)` for an `Action` that has it: `exec` for docker exec, and
  `shell` for command shell, whose `.Shell()` is `.PermitAs(behavior.VerbShell)`

The `get` of sysctl needs `sysctl:read`. dns under `network` needs `dns:read`.
`osapi behavior get --name <name>` lists them.

A group puts a behavior in the route and the command tree. It does not put it in
a permission. Thus a role can get `dns:write` and not `interface:write`. A
behavior name is unique in the registry, so two behaviors cannot make the same
permission. A child, such as route under interface, has the permission of its
parent: a route needs `interface:write`.

The behaviors in a group had the permission of the group before this rule. The
permissions of the groups changed to these:

| Was                 | Is                                |
| ------------------- | --------------------------------- |
| `network:read`      | `dns:read`, `interface:read`      |
| `network:write`     | `dns:write`, `interface:write`    |
| `network:execute`   | `connectivity:execute`            |
| `container:read`    | `docker:read`, `image:read`       |
| `container:write`   | `docker:write`, `image:write`     |
| `container:execute` | `docker:execute`, `image:execute` |
| `container:exec`    | `docker:exec`                     |
| `log:read`          | `entry:read`, `source:read`       |

A custom role that named a permission of a group must name the new permissions.

Thus a domain that moves to a behavior can change its permission. The node reads
were all `node:read`. As behaviors, each has its own: `uptime:read`, `os:read`,
`disk:read`, `memory:read`, `load:read`, and `hostname:read` with
`hostname:write`. The status summary needs `status:read`. `node:read` and
`node:write` are gone, because no endpoint needs them (osapi-io/osapi#1171). The
built-in roles get each behavior permission, so a token with a built-in role
keeps its access. A custom role that named `node:read` or `node:write` for these
domains must name the new permissions.

`client.Permission` in the SDK is the type. Thus the permission set is part of
the public API of osapi, not an internal detail. A consumer can name the
permission that it needs.

`client.Permission` and `client.Role` are named types, not aliases of `string`.
Thus a role does not compile where a permission goes, and a permission does not
compile where a role goes. The DSLs return a `client.Permission`. The check of
each request keeps the types too:

- `authtoken.ResolvePermissions` takes the roles as `[]Role`, the direct
  permissions as `[]Permission` and the custom roles as `authtoken.CustomRoles`,
  a `map[Role][]Permission`. It returns a `map[Permission]bool`.
- `authtoken.HasPermission` takes a `Permission`.
- The custom roles of the config are a `map[client.Role]CustomRole`, and each
  `CustomRole` has `[]client.Permission`. The scope middleware and the endpoint
  server take `authtoken.CustomRoles`.

A token's claims, a route's scope and the output of a command are text. The
conversion is at those boundaries: `authtoken.RolesOf` and
`authtoken.PermissionsOf` read the claims, and `string()` or `authtoken.Strings`
writes the text. Go converts an untyped string literal to a named type. Thus
`.Permission("helth:read")` compiles, and `authtoken.Check` is the guard for a
name that nothing declares.

## The built-in roles

osapi has one built-in role for each kind of person or program that uses it
(osapi-io/osapi#999). A rule in `RolePermissions` makes each role from the
permissions that osapi knows. No list of roles is written by hand, except the
two short lists of `auditor` and `observer`.

| Role         | Who                                  | Gets                                                             |
| ------------ | ------------------------------------ | ---------------------------------------------------------------- |
| `admin`      | the owner of the fleet               | each permission                                                  |
| `operator`   | the person on call                   | each `read` and each `execute` permission that is not admin only |
| `automation` | CI, or a workflow that changes hosts | each `read` and each `write` permission that is not admin only   |
| `auditor`    | a person who audits                  | `audit:read`, `trace:read`, `job:read`, `health:read`            |
| `read`       | a person who looks                   | each `read` permission that is not admin only                    |
| `observer`   | a dashboard or a monitor             | `health:read`, `status:read`, `agent:read`                       |

The verbs separate the two kinds of change. `write` changes what a host is
configured to be: a file, a package, a sysctl value. `execute` makes something
happen and changes no configuration: a restart, a signal, a reboot. An action of
a behavior has the permission `<name>:execute`, and is a write in each other
way: a modify job and an output that reports `changed`. Thus an operator
restarts a service and cannot change its unit file, and automation changes the
unit file and cannot restart it.

A permission is admin only when its verb is `shell` or `exec`, or when a method
that needs it is marked `AdminOnly()`:

| Admin only                                     | Why                                                    |
| ---------------------------------------------- | ------------------------------------------------------ |
| `command:shell`                                | a shell                                                |
| `command:execute`                              | `AdminOnly()` on command exec: any command on the host |
| `docker:exec`                                  | its verb: docker exec runs any command in a container  |
| `user:write`                                   | an account or an SSH key reaches root                  |
| `schedule:write`                               | a cron entry runs a command as any user                |
| `admission:write`, `agent:write`, `audit:read` | `AdminOnly()` on the endpoint groups                   |

`schedule:write` is admin only from `AdminOnly()` on the create, update and
delete methods of the schedule behavior (osapi-io/osapi#1106). `command:execute`
is admin only from `AdminOnly()` on the exec action of the command behavior
(osapi-io/osapi#1113). `builtinAdminOnly`, the list of the admin permissions of
the hand-written domains, is gone (osapi-io/osapi#1171).

Each method that needs a permission marks `AdminOnly()` the same.
`authtoken.Check` fails when they do not agree, because one permission cannot be
admin only on one method and not on another.

An action can have a verb of its own, with `.PermitAs(verb)`. The docker
behavior needs it (osapi-io/osapi#1136). docker start and stop are actions of
the `docker` behavior, so they share `docker:execute`, and the `operator` role
gets it. docker exec runs any command in a container. With
`.PermitAs(behavior.VerbExec)`, its permission is `docker:exec`, which only the
admin role gets. Without it, exec shares `docker:execute`, and `authtoken.Check`
makes start and stop admin only too, because one permission cannot be admin only
on one method and not on another.

`.PermitAs` takes only a verb that only the admin role gets: `VerbShell` or
`VerbExec`. A verb that a different role gets, such as `VerbWrite`, does not
need it, and `behavior validate` refuses it. Each verb is a `Verb` constant, so
the roles know each verb. `authtoken` keeps the same verbs in `adminVerbs`.

`file:write`, `package:write` and `sysctl:write` stay with `automation`. Each of
them can reach root: a file can be a unit or a sudoers entry, a package runs
install scripts, and a sysctl value can weaken the kernel. Thus give
`automation` only to a program that you trust as root, and say so where it is
configured. osapi does not hide this behind the role's name.

`read` keeps `entry:read`, `file:read` and `process:read`, which can show a
secret: a log line, the content of a file, the arguments of a process. A
dashboard gets `observer`, which reads no log, file or command output.

`trace:read` is in `operator`, `automation`, `auditor` and `read`. A trace shows
the hosts, operations and errors of a request, the same as the job.

Not covered yet: a token limited to some hosts (osapi-io/osapi#1116), and a
workflow that acts for a user (osapi-io/osapi#1114).

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

## Adding a permission

Declare the method. The permission and its roles come from the definition:

- **A behavior:** register it. Its methods need `<name>:read`, `<name>:write`
  and, for an action, `<name>:execute`, or those of its group.
- **An endpoint group:** register it. A GET needs `<group>:read`, and each other
  verb `<group>:write`. `.Permission(client.PermAgentRead)` names a different
  one, which something else must declare. Use the `Perm` constant, not a string.
- **A permission that no method declares:** `builtinPermissions` in
  `internal/authtoken/permissions.go` has it. It has only `health:read` and
  `trace:read`, which endpoint groups name with `.Permission`.

To keep a permission from each role but `admin`, mark the method `.AdminOnly()`,
in the behavior DSL or the endpoint DSL. Each method that needs the permission
must agree. `osapi token roles get --name <role>` shows what a role gets.
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

## A token's target scope

A role applies to each host. A token can also have a target scope, the `targets`
claim, so that a team can act only on its own hosts. The scope is a list of
hostnames and labels, such as `web-01` and `group:web`.
`osapi token generate -t` sets it. A token without targets acts on each host.
The `target_scope` rule refuses `_all`, `_any` and `_local` in a scope, because
they are not hosts.

`validation.InScope` compares a target with the scope:

- **A label target** is in the scope when a label of the scope has the same key,
  and its value is the same or above the value of the target. `group:web` covers
  `group:web.dev`. It does not cover `group:webapp`. This is the same prefix
  rule that routes a label target to the agents.
- **A host target** is in the scope when the scope names the host. It is also in
  the scope when the agent that the target resolves to has a label that a label
  of the scope covers. The resolution is `ResolveTarget`, so a machine ID and a
  hostname give the same result.
- **`_all` and `_any`** are never in a scope. They reach each agent, or an agent
  that NATS selects, and a scope cannot limit them.

The scope middleware checks the `hostname` path parameter of each route, after
the permission check. A target outside the scope gets 403, and no job goes to a
host. The job group checks the target of a retry, because it is in the body. A
retry without a target goes to `_any`, so a scoped token must name a target. The
middleware puts the scope in the context of the request, and `authtoken.InScope`
reads it there. The audit entry records the scope.

The scope limits where a token acts. It does not limit the reads of the
controller, such as the jobs, the traces and the audit log. osapi-io/osapi#1188
has that decision.

## What checks it

The handler checks it, through scope middleware that the domain package wraps
itself. Before the code runs, `TestPermissionsAreDeclared` in
`internal/behaviors/all` runs `authtoken.Check` with each group and behavior
registered. The UI also reads the roles claim to decide what to show. **That is
not a check.** [The embedded UI](ui.md) decodes the token, but it does not
verify it. When the UI hides something, that does not protect it.

## Where this connects

[Behaviors](behaviors.md#how-a-behavior-is-served) tells how the permissions of
a behavior come from its definition, and how the persona roles get them.

[The embedded UI](ui.md) tells what the UI does with the roles claim and the
targets claim, and why its decode is not a verification.

______________________________________________________________________

Written from `internal/authtoken/`, `internal/validation/target.go`,
`internal/controller/api/middleware.go` and `pkg/sdk/client/permissions.gen.go`.
