# Permissions

Each authenticated endpoint needs one named permission. A token has roles. The
roles resolve to a set of permissions. The handler checks the permission that it
needs.

## The shape is `resource:verb`

```
agent:read     sysctl:write    command:execute
job:read       network:write   command:shell
health:read    file:write      container:execute
audit:read     container:write container:exec ...
```

The resource is the domain of the endpoint. The verb is what the endpoint does
to it, and it is not always `read` or `write`. `command:execute`,
`command:shell`, `container:execute` and `container:exec` exist because to run
something is not the same as to change something. Thus a role can get one
without the other.

A [behavior](behaviors.md) does not declare permissions. osapi makes the
permission of each method from the definition:

- the resource is the top-level group, or the name of the behavior when it has
  no group
- the verb is `read` for a `Read` method, `write` for a `Write` method,
  `execute` for an `Action`, such as a service restart, and the verb of
  `.PermitAs(verb)` for an `Action` that has it: `exec` for docker exec, and
  `shell` for command shell, whose `.Shell()` is `.PermitAs(behavior.VerbShell)`

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

`client.Permission` and `client.Role` are named types, not aliases of `string`.
Thus a role does not compile where a permission goes, and a permission does not
compile where a role goes. The DSLs return a `client.Permission`. The check of
each request keeps the types too:

- `authtoken.ResolvePermissions` takes the roles as `[]Role`, the direct
  permissions as `[]Permission` and the custom roles as `authtoken.CustomRoles`,
  a `map[Role][]Permission`. It returns a `map[Permission]bool`.
- `authtoken.HasPermission` takes a `Permission`.
- The custom roles of the config are a `map[client.Role]CustomRole`, and each
  `CustomRole` has `[]client.Permission`. Each hand-written handler takes
  `authtoken.CustomRoles`.

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

A permission is admin only when its verb is `shell` or `exec`, when a method
that needs it is marked `AdminOnly()`, or when it is one of the hand-written
domains' admin permissions in `builtinAdminOnly`:

| Admin only                                     | Why                                                    |
| ---------------------------------------------- | ------------------------------------------------------ |
| `command:shell`                                | a shell                                                |
| `command:execute`                              | `AdminOnly()` on command exec: any command on the host |
| `container:exec`                               | its verb: docker exec runs any command in a container  |
| `user:write`                                   | an account or an SSH key reaches root                  |
| `schedule:write`                               | a cron entry runs a command as any user                |
| `admission:write`, `agent:write`, `audit:read` | `AdminOnly()` on the endpoint groups                   |

`schedule:write` is admin only from `AdminOnly()` on the create, update and
delete methods of the schedule behavior (osapi-io/osapi#1106), not from
`builtinAdminOnly`. The hand-written schedule domain is gone.

`command:execute` is admin only from `AdminOnly()` on the exec action of the
command behavior (osapi-io/osapi#1113). No hand-written domain is left, so
`builtinAdminOnly` is empty.

A behavior or a group that takes over a hand-written domain marks the same
methods `AdminOnly()`, and `authtoken.Check` fails until it does, because one
permission cannot be admin only on one method and not on another.

An action can have a verb of its own, with `.PermitAs(verb)`. The container
behaviors need it (osapi-io/osapi#1136). docker start and stop, and image pull,
are actions under the `container` group, so they share `container:execute`, and
the `operator` role gets it. docker exec runs any command in a container. With
`.PermitAs(behavior.VerbExec)`, its permission is `container:exec`, which only
the admin role gets. Without it, exec shares `container:execute`, and
`authtoken.Check` makes start, stop and pull admin only too, because one
permission cannot be admin only on one method and not on another. A permission
for each behavior in a group (osapi-io/osapi#1115) does not separate them:
`docker:execute` still has start, stop and exec.

`.PermitAs` takes only a verb that only the admin role gets: `VerbShell` or
`VerbExec`. A verb that a different role gets, such as `VerbWrite`, does not
need it, and `behavior validate` refuses it. Each verb is a `Verb` constant, so
the roles know each verb. `authtoken` keeps the same verbs in `adminVerbs`.

`file:write`, `package:write` and `sysctl:write` stay with `automation`. Each of
them can reach root: a file can be a unit or a sudoers entry, a package runs
install scripts, and a sysctl value can weaken the kernel. Thus give
`automation` only to a program that you trust as root, and say so where it is
configured. osapi does not hide this behind the role's name.

`read` keeps `log:read`, `file:read` and `process:read`, which can show a
secret: a log line, the content of a file, the arguments of a process. A
dashboard gets `observer`, which reads no log, file or command output.

`trace:read` is in `operator`, `automation`, `auditor` and `read`. A trace shows
the hosts, operations and errors of a request, the same as the job.

Not covered yet: a permission for each behavior in a group (`network:write`
covers dns, interface and route, osapi-io/osapi#1115), a token limited to some
hosts (osapi-io/osapi#1116), and a workflow that acts for a user
(osapi-io/osapi#1114).

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
- **A hand-written domain** under `internal/controller/api`: add each permission
  that it needs to `builtinPermissions` in `internal/authtoken/permissions.go`,
  as a string. The list goes as each domain becomes a behavior.

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
