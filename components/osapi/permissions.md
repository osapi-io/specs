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

- the resource is the name of the behavior, or of its parent for a child
- the verb is `read` for a `Read` method, `write` for a `Write` method,
  `execute` for an `Action`, such as a service restart, and the verb of
  `.PermitAs(verb)` for an `Action` that has it: `exec` for docker exec, and
  `shell` for command shell, whose `.Shell()` is `.PermitAs(behavior.VerbShell)`

The `get` of sysctl needs `sysctl:read`, and the `get` of dns needs `dns:read`.
`osapi dsl behavior get --name <name>` lists them.

A role can get `dns:write` and not `interface:write`. A behavior name is unique
in the registry, so two behaviors cannot make the same permission. A child, such
as route under interface, has the permission of its parent: a route needs
`interface:write`, and the sources of the log need `log:read`.

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

The groups went in osapi-io/osapi#1258, and three behaviors became children of a
different behavior. Their permissions changed to the parent's:

| Was                                           | Is                                       |
| --------------------------------------------- | ---------------------------------------- |
| `entry:read`, `source:read`                   | `log:read`                               |
| `updatepackages:read`, `updatepackages:write` | `package:read`, `package:write`          |
| `user:execute`                                | `user:write`, for `user password update` |

The roles do not change. `updatepackages:write` was in `admin` and `automation`,
as `package:write` is. `user:execute` and `user:write` were both admin only.

Thus a domain that moves to a behavior can change its permission. The node reads
were all `node:read`. As behaviors, each has its own: `uptime:read`, `os:read`,
`disk:read`, `memory:read`, `load:read`, and `hostname:read` with
`hostname:write`. The status summary needs `status:read`. `node:read` and
`node:write` are gone, because no endpoint needs them (osapi-io/osapi#1171). The
built-in roles get each behavior permission, so a token with a built-in role
keeps its access. A custom role that named `node:read` or `node:write` for these
domains must name the new permissions.

`types.Permission` in `pkg/sdk/types` is the type. Thus the permission set is
part of the public API of osapi, not an internal detail. A consumer can name the
permission that it needs.

`types.Permission` and `types.Role` are named types, not aliases of `string`.
Thus a role does not compile where a permission goes, and a permission does not
compile where a role goes. The DSLs return a `types.Permission`. The check of
each request keeps the types too:

- `authtoken.ResolvePermissions` takes the roles as `[]Role`, the direct
  permissions as `[]Permission` and the custom roles as `authtoken.CustomRoles`,
  a `map[Role][]Permission`. It returns a `map[Permission]bool`.
- `authtoken.HasPermission` takes a `Permission`.
- The custom roles of the config are a `map[types.Role]CustomRole`, and each
  `CustomRole` has `[]types.Permission`. The scope middleware and the endpoint
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

| Role         | Who                                  | Gets                                                                  |
| ------------ | ------------------------------------ | --------------------------------------------------------------------- |
| `admin`      | the owner of the fleet               | each permission                                                       |
| `operator`   | the person on call                   | each `read` and each `execute` permission that is not admin only      |
| `automation` | CI, or a workflow that changes hosts | each `read`, `write` and `use` permission that is not admin only      |
| `auditor`    | a person who audits                  | `audit:read`, `trace:read`, `job:read`, `health:read`, `catalog:read` |
| `read`       | a person who looks                   | each `read` permission that is not admin only                         |
| `observer`   | a dashboard or a monitor             | `health:read`, `status:read`, `agent:read`, `catalog:read`            |

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
| `secret:reveal`                                | `AdminOnly()` on secret reveal: the value of a secret  |

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

`read` keeps `log:read`, `file:read` and `process:read`, which can show a
secret: a log line, the content of a file, the arguments of a process. A
dashboard gets `observer`, which reads no log, file or command output.

`trace:read` is in `operator`, `automation`, `auditor` and `read`. A trace shows
the hosts, operations and errors of a request, the same as the job.

`secret:read` and `secret:write` follow the rule of their verbs. `secret:read`
gives the names and the metadata of the secrets, and no value, so `operator` and
`read` have it. `secret:use` is the one permission with the verb `use`: a
request needs it to give a reference to a secret. `authtoken` declares it,
because no method needs it. The rule gives `automation` each `use` permission,
because a secret goes into a write. `operator` does not get it, because no
action takes a secret ([Vaults](vaults.md#the-secret-endpoint-group)).
`secret:reveal` gives the value of a secret, so it is admin only, from
`AdminOnly()` on `secret reveal`.

`catalog:read` is in each built-in role. The UI loads the catalog after sign-in
and shows no page without it ([the UI](ui.md#the-catalog)). Thus each role that
uses the UI needs it, `observer` too. It is the default permission of the GET of
the `catalog` group, so the rule gives it to `operator`, `automation` and
`read`, and the lists of `auditor` and `observer` name it. Two other choices
were possible. `health:read` is in each built-in role too, but it names a
different resource, and a role that may read the health could then read the
catalog. An option of the endpoint DSL that lets each token call a method needs
no permission, but the DSL does not have it, and a custom role could then not
refuse the catalog. A custom role that uses the UI names `catalog:read`.

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
  verb `<group>:write`. `.Permission(types.PermAgentRead)` names a different
  one, which something else must declare. Use the `Perm` constant, not a string.
- **A permission that no method declares:** `builtinPermissions` in
  `internal/authtoken/permissions.go` has it. It has only `health:read` and
  `trace:read`, which endpoint groups name with `.Permission`.

To keep a permission from each role but `admin`, mark the method `.AdminOnly()`,
in the behavior DSL or the endpoint DSL. Each method that needs the permission
must agree. `osapi controller role get --name <role>` shows what a role gets.
`osapi dsl behavior spec get` and `osapi dsl endpoint spec get` teach the same
rule.

`AllPermissions()` and `RolePermissions(role)` make their result on each call,
not one time. A behavior or a group registers in the `init` of its own package,
and that `init` can run after the `init` of `authtoken`. Thus a test that checks
roles imports the groups and the behaviors, as the binary does.

`go generate ./internal/behaviors/all` writes the SDK's constants in
`pkg/sdk/types/permissions.gen.go`, one `Perm` constant for each permission and
one `Role` constant for each built-in role. A test fails when the file is stale.
A permission constant is `Perm`, then the resource and the verb with capitals,
such as `PermDiskRead` for `disk:read`. The UI reads the permissions and the
roles from the catalog endpoint, at run time ([the UI](ui.md#the-catalog)).
`just cli-docs-generate` writes the role table of the configuration page of the
docs site from `RolePermissions`.

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
a custom role is not one that osapi knows.
`osapi controller token generate --roles` accepts a built-in role or a custom
role of the config.

An operator who configures a custom role looks for the list of permissions. The
authentication page of the published site had that list as a table that people
updated by hand. It now points to `osapi controller role list`. That command
prints the list from the binary, so it cannot be out of date.

**Select by the possible damage, not by the endpoint group.** If two operations
can do different amounts of damage, they need two permissions, also if their
shape is the same. That is why `command:shell` is separate from
`command:execute`.

## A token's target scope

A role applies to each host. A token can also have a target scope, the `targets`
claim, so that a team can act only on its own hosts. The scope is a list of
hostnames and labels, such as `web-01` and `group:web`.
`osapi controller token generate -t` sets it. A token without targets acts on
each host. The `target_scope` rule refuses `_all`, `_any` and `_local` in a
scope, because they are not hosts.

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

The scope also limits what the token reads of the jobs, the traces and the audit
log (osapi-io/osapi#1188). `authtoken.Sees` has the rule. A token without a
scope sees each record. A scoped token sees a record only when the record has a
target and `authtoken.InScope` accepts that target:

- **A job** has the target that its definition stores.
- **An audit entry** has the `{hostname}` of a `/api/node/{hostname}/` path. The
  endpoint reads it from the path that the entry records, so an old entry needs
  no change. An entry of a request with no target, such as `GET /api/job`, has
  no target.
- **A trace** has each `osapi.target` that its spans record. The token sees the
  trace only when a span records a target and each target is in the scope.

**The rule fails closed.** A record with no target, or with the target `_all` or
`_any`, is hidden from a scoped token, because it can tell about hosts outside
the scope. A list leaves out each hidden record, and its totals and status
counts include only the records that the token sees. A get of a hidden record
gets 404, the same as a record that does not exist. A delete or a retry of a
hidden job also gets 404, because for the token the job does not exist. A retry
checks its new target first, so its 403 does not tell whether the old job
exists.

## The keys that sign a token

A token is a JWT with HS256. `controller.api.security.signing_keys` is a list of
keys, and each key has an `id` and a `key`:

```yaml
controller:
  api:
    security:
      signing_keys:
        - id: 2026-11
          key: <64 hex characters>
        - id: 2026-08
          key: <64 hex characters>
```

- **The first key signs.** `osapi controller token generate` signs with the
  first key of the list, and puts its `id` in the `kid` header of the token.
  Thus the newest key goes first.
- **Each key verifies.** The middleware reads the `kid` of the token and
  verifies the signature with the key that has that `id`. It does not try each
  key.
- **A token with no `kid`, or with a `kid` that the list does not have, gets
  401.** Thus a token stops when you remove its key. A token from before the
  list had no `kid`, and the controller refuses it too.

`osapi controller token validate` shows the `kid` with the claims, so you can
see which key signed a token before you remove the key. `internal/authtoken` has
the two sides: `Generate` takes one `authtoken.Key`, and `Validate` takes
`authtoken.Keys` and puts the `kid` in the claims as `KeyID`.

The config does not load when the list is empty, when two keys have the same
`id`, or when a key has fewer than 32 characters. The rules are `required`,
`unique=ID` and `signing_key`. A problem names the key by its index, such as
`controller.api.security.signing_keys[1].key`.

To change the key with no outage:

1. Put a new key at the start of the list, and restart the controller. New
   tokens get the new key. The tokens of the old key still work.
2. Sign a new token for each client.
3. Remove the old key when no client sends a token that it signed. A token
   expires after three months.

The environment variable `OSAPI_CONTROLLER_API_SECURITY_SIGNING_KEYS` takes the
list as `id=key` pairs with a comma between them, such as
`2026-11=<key>,2026-08=<key>`. A decode hook in `internal/config` makes each
pair a key, because a variable cannot hold a YAML list. Thus an `id` cannot have
`=`, and a `key` cannot have a comma. `openssl rand -hex 32` gives a key with
neither.

`osapi config list` prints the list as `********`, because the field has the tag
`mask:"password"`.

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
`internal/controller/api/middleware.go`, `internal/config/types.go` and
`pkg/sdk/types/permissions.gen.go`.
