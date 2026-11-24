# The embedded UI

osapi ships a React single-page application inside the controller binary. There
is no separate deployment, no second process and no additional port. The build
puts the assets into the Go binary through `//go:embed`. The controller serves
them from the same host and port as the REST API.

```yaml
controller:
  ui:
    enabled: true # default
```

If you set it to false, the controller does not register the SPA handler. It
serves only the REST API. This is the only UI setting that an operator changes.

## Its API client is generated from the same specification as the Go SDK

Nobody writes the client by hand, and there is no second specification. `orval`
generates it from the combined OpenAPI file. The Go SDK comes from the same
file. Thus **an endpoint that you add to a domain goes to the two clients**, and
nobody writes TypeScript for it.

A fetch mutator changes the generated client for the browser. It attaches the
bearer token.

`orval` reads the combined file where `just generate` writes it, in
`internal/controller/api/gen/`. It empties `ui/src/sdk/gen/` before it writes.
Thus the client of an endpoint or a tag that the spec no longer has is deleted,
and a page that still imports it fails the type check. Before this, `orval` left
the old files. The configure page imported three clients whose tags had changed
names, and it used code from an older `orval` (osapi#784).

`just react-generate-check` writes the client again and compares it with the
committed files. If a file is different, the check fails and tells you to run
`just react-generate`. `just test` and CI run it with the quick checks.
`go generate` does not run `orval`. Thus, before this check, a bump of `orval`
that changes its output went to main with the old client two times (osapi#686,
osapi#1150). Now the pull request of the bump fails until somebody regenerates
the client.

## The four kinds of component

Two answers separate the kinds: **what each one knows, and if it renders**. The
name does not separate them. Put a new file where those two answers put it.

| Kind             | Knows                           | Lives in                    |
| ---------------- | ------------------------------- | --------------------------- |
| primitive        | no osapi resource               | `ui/src/components/ui/`     |
| domain component | exactly one osapi resource      | `ui/src/components/domain/` |
| layout           | none; it holds page chrome      | `ui/src/components/layout/` |
| hook             | a resource, and renders nothing | `ui/src/hooks/`             |

The shared components that each page uses for the same thing:

| Thing                   | Component                                                            |
| ----------------------- | -------------------------------------------------------------------- |
| a card                  | `components/ui/card.tsx`                                             |
| a table                 | `components/ui/data-table.tsx`: CLI headers, and "None." if empty    |
| a status                | `Badge`, `HealthDot` and `Text`, with `useStatus`                    |
| a page that loads       | `components/ui/spinner.tsx`                                          |
| a page without its perm | `components/layout/permission-denied.tsx`                            |
| an empty page           | `components/ui/empty-state.tsx`                                      |
| an error                | `components/ui/error-banner.tsx`                                     |
| key-value pairs         | `components/ui/kv-list.tsx`: the values line up, as `PrintKV`        |
| a count                 | `components/ui/count.tsx`, with the count tones of the catalog       |
| a result's summary line | `components/domain/result-summary.tsx`                               |
| a job                   | `JobView` in `components/domain/job-detail.tsx`, as `job get`        |
| a time, age or duration | `lib/format.ts`                                                      |
| a pick from a list      | `Picker` in `components/ui/popover.tsx`, with a hook for the list    |
| a list of words         | `components/ui/tag-input.tsx`                                        |
| a read, write or action | `KindMark` in `components/domain/method-kind.tsx`                    |
| a text field            | `Input`, with an `icon`, and `Textarea` in `components/ui/input.tsx` |
| a checkbox              | `components/ui/checkbox.tsx`                                         |
| a load for a form       | `hooks/use-load.ts`, under each resource hook such as `useObjects`   |

A table header is in capitals and gray. A page uses these, not a raw `<button>`,
`<input>` or `<textarea>`. A picker of a resource gives `Picker` only its
options; the trigger, the keyboard, the loading state and the empty list,
`None.`, are the same in each. A hook that loads choices for a form builds on
`useLoad`, which keeps the value as it was when the load fails, so a picker
stays empty and the form still works. A page that must show a failure, such as
Admission, keeps its own error state. A result card counts its summary line from
its per-host `results`, so a card never shows a status that it did not count. A
panel inside a card has the `surface` token, not a hex value.

**A value has the format that the CLI gives it.** `lib/format.ts` has the
formatters of `internal/cli/ui.go` in TypeScript: `formatTime` prints
`2006-01-02 15:04:05` in local time, `formatAge` prints `3d 4h`,
`formatDurationMs` rounds as `FormatDuration` does and prints `3m4s`, and
`formatBytes` prints `5.2 KB`. A page does not call `toLocaleString` or write a
formatter of its own. A field has the name that the CLI gives it, such as
`Machine ID`, and a page lists the fields in the order of the CLI command for
the same resource. A result's summary line is `2 hosts: 1 ok, 1 skipped`, then
the whole job ID in gray, as the CLI prints it. A job ID is never cut.

**A result links its job and its trace.** On the Plans page, each step that ran
shows a line under its card with the job and the trace of its call, whole, each
with a copy button (`RunLinks` in `components/domain/run-links.tsx`). A click on
the job opens `/admin/jobs/<id>`, which shows the detail of that job above the
list. A click on the trace opens `/admin/traces/<id>`. The trace comes from the
`traceresponse` header of the answer, which the controller sets on each answer
and the CLI reads for its trace line (`lib/trace.ts`). A step that failed keeps
its trace too. The links are `IdBadge`s, with no underline.

**The Audit page shows the changes first.** The list hides the reads at first,
because the UI's own polling reads fill the log, and an operator looks for a
change. A box shows the reads. The filters are the user, text of the operation
or the path, and the status, and the controller applies them to the whole log.
The columns are the time, the user, the method, the operation (or the path, when
the entry has no operation ID), the status and the duration. A click on an entry
opens it in full: the user, the roles, the source IP, the operation, the path,
the status, the duration, the request with each secret replaced, and the links
to its job and its trace (`RunLinks`).

**The Secrets page writes a value and never shows one.** It is at
`/admin/secrets`, and its link in the Admin menu shows under
`canCall("GetSecretVaults")`. A picker selects a vault, and a table lists its
keys with the columns of `osapi client secret list`: the key, the version, when
it changed and who changed it. A form writes a value to a new key or to a key of
the table, under `canCall("PutSecret")`. Its value field is a password field,
and it is empty again after each write. Each row has a delete button under
`canCall("DeleteSecret")`. No API answer has a value, so the page has no value
to show.

Thus:

- Markup with one resource is a domain component.
- A resource with no markup is a hook.
- Markup with no resource is a primitive. If it is page chrome, it is a layout.

The knowledge column cannot separate a primitive from a layout, because neither
knows a resource. A primitive can be used again in any location. A layout exists
to put pages in position.

The file extension enforces the hook rule. Each file in `ui/src/hooks/` is
`.ts`, not `.tsx`. Thus a hook **cannot** contain markup.

## Authentication, and the difference to know

The UI uses the same JWT as the rest of osapi. A token comes from
`osapi controller token generate`. You paste it into the sign-in page, or you
give it through the environment. The UI sends it as a bearer header on each
request.

**The UI decodes that token, but it does not verify it.** It reads the roles
claim to decide what to show. The server verifies the token on each request.

A contributor who reads only the client can think that the decode is a check. It
is not a check. When the UI hides something, that does not protect it.

The sign-in page refuses two kinds of token before it keeps one.
`checkTokenFormat` in `ui/src/lib/token-format.ts` refuses a token that has
whitespace, a character outside base64url, or a number of parts that is not
three. The page does not remove the bad character. A token that the terminal
wrapped gets a space at the line break, and `atob` ignores that space. The
server does not ignore it, and it returns 401 to each request. Thus the page
tells the person to copy the token again.

Then the page sends one request, `GET /api/health/status`, with the new token. A
401 means that the server refused the token, for example because a different
signing key made it. The page shows the reason from the server and does not keep
the token. Any other status means that the server accepted the token, and the
page keeps it. This is the verification of the server, not of the UI. The server
still checks each request after sign-in.

A token in `localStorage` from an earlier session gets no check. If the server
refuses it, the catalog does not load, and the UI shows the reason with a sign
out.

The sign-in page needs no catalog. `SessionProvider` (`ui/src/lib/session.tsx`)
keeps the token, and `useSession()` reads it. After sign-in, the UI loads the
catalog, and only then shows a page ([the catalog](#the-catalog)).

The permission model of the UI is the model of osapi. The roles claim uses the
permissions and the six built-in roles that the API checks.
[Permissions](permissions.md) describes them. The UI does not keep its own list.
The catalog has each permission, and each built-in role in order with its
description and its permissions, from `AllPermissions`, `Roles`,
`RoleDescription` and `RolePermissions` in `internal/authtoken`. `AuthProvider`
(`ui/src/lib/auth.tsx`) is inside the catalog. It finds the role of the token,
or of the role switch, in the roles of the catalog. A role that the catalog does
not have gets the last role, which has the least. The role switch and the Roles
page show the roles of the catalog. The `Permission` type of the UI is the
`Permission` enum of the spec, so TypeScript fails the build on a permission
that the controller does not have. A hand copy came before the generated list,
and it was out of date: it had `cron:*`, `hostname:*` and `group:*`, which no
token has, and did not have `schedule:*` (osapi-io/osapi#749). The published
site also tells what each role permits for an *operator*, because a person who
configures a role looks there.

A page, its link in the Admin menu and each control that writes check the API
operation that they call, not a permission. `useAuth().canCall("GetAdmissions")`
reads the permission of the operation from the operations of the catalog. The
type of the argument is the `OperationID` enum of the spec, so TypeScript fails
the build on an operation that the API does not have. An operation that the
catalog does not have is refused. Thus a link and its page cannot disagree.
Before, the Admin menu showed each link to a role with `audit:read`, and each
page typed its own permission: an auditor saw Admission, and the page refused it
(osapi-io/osapi#1232). `ui/src/lib/can-call.test.ts` fails on a permission typed
into `can("...")`. Roles calls no API, so each role sees it.

The UI also reads the targets claim, the target scope of the token.
`jwtClaimStrings` in `ui/src/lib/jwt.ts` reads the roles and the targets. The
Roles page shows the targets, or "each host" for a token without a scope. The
detail of an audit entry shows the scope that the entry records. The UI does not
hide a host outside the scope. The controller refuses a request to it with 403.
[Permissions](permissions.md#a-tokens-target-scope) tells the rule.

## The catalog

The UI gets its metadata from one operation of the controller,
`GET /api/catalog` (`osapi client catalog get`), through the generated client.
The `catalog` endpoint group builds it on each request from the registries of
the controller ([Endpoints](endpoints.md#the-inventory)). The catalog has:

- each behavior that the API serves, and each internal behavior.
- each area of `area.All`, in order, with its label.
- each permission, and each built-in role in order, with its description and its
  permissions.
- the permission of each operation that needs one, by its operationId, from
  `authtoken.Operations`.
- the tones of the status words and of the counts, from `StatusTones` and
  `CountTones` of the CLI ([color](#color-one-palette-with-the-cli)).
- the host families, the platforms that gohai names.

Each behavior has:

- its name, its title from its definition, such as "Package updates", its area,
  its doc and its parent, such as `user` for `sshkey`.
- the platforms of its providers, such as `debian` and `darwin`.
- the behaviors that it calls, `uses`, and the behaviors that call it,
  `used_by`, and its chain, as `osapi dsl chain list` prints it.
- its methods.

Each method has:

- its kind: `read`, `write` or `action`. The kind is the verb of the permission
  of the method: `read`, `write`, or a verb of an action (`execute`, `shell` or
  `exec`).
- its doc and its long doc.
- the HTTP method and the path of its route, `http_method` and `path`, and its
  permission. An internal behavior has no route and no permission.
- the platforms that it runs on: the platforms that its `On` limits it to, else
  each platform of the behavior.
- its input and output types, with their fields, as `osapi dsl behavior get`
  shows them: `UpdateInput { interface_name*, servers }`.
- the fields of its input. Each field has its place in the request (the path,
  the query or the body), its kind, its doc, whether it is required, the values
  of its enum, from a closed set or a `oneof` rule, and whether it is a secret.
- the fields of the rows that it answers, as the CLI's output reads them: the
  label, the `render` tag, and the fields of an object or of a list of objects.
- its calls: the calls that its examples make to other behaviors, under the call
  that made them, each one time. `behaviortest.Chains` runs each example on a
  fake host and records the calls, as `osapi dsl chain get` does. It takes
  approximately 20 ms for each request.
- its examples, with their input and output. A secret of an input is
  `[redacted]`.

The spec has the types of the catalog, so `orval` generates them, and
`ui/src/lib/catalog.ts` uses them. The `Permission` and the `OperationID` types
are enums of the spec, which `endpoint.Enum` makes from the registries
([Endpoints](endpoints.md#the-definition)).

`CatalogProvider` (`ui/src/lib/catalog-provider.tsx`) loads the catalog one time
after sign-in. Until it has the catalog, it shows a spinner, and no page. When
the load fails, it shows the reason, with Retry and Sign out. Each page reads
the catalog only through `useCatalog()` in `ui/src/hooks/use-catalog.ts`, and
`useStatus()` gives the colors of a status word from its tones.
`ui/src/lib/catalog-index.ts` indexes the catalog: the behaviors by name, the
sections of the Behaviors page by area, the definition of each step that a plan
can run, the roles, and the permission of each operation.

The controller builds the catalog on each request. Thus a behavior that an
extension adds at run time (osapi-io/osapi#1064) is in the next catalog. No file
of the UI holds a copy, so no test checks that a file is current. Until
osapi-io/osapi#1256 Go wrote four TypeScript files beside the spec, and a Go
test failed on each when it was stale:

| File                            | Generator                           |
| ------------------------------- | ----------------------------------- |
| `ui/src/lib/catalog.gen.ts`     | `internal/behavior/uicatalog/gen`   |
| `ui/src/lib/permissions.gen.ts` | `internal/authtoken/gen`            |
| `ui/src/lib/operations.gen.ts`  | `internal/authtoken/gen/operations` |
| `ui/src/lib/status.gen.ts`      | `internal/cli/gen`                  |

Each was a second channel beside the spec, which the build fixed. The catalog
was also most of the size of the UI, so the pages that read it loaded it on the
first visit.

Each test of the UI that needs a catalog uses `ui/src/test/catalog.ts`, a small
catalog in the shape that the controller answers.

Before osapi-io/osapi#1197 the generator was `internal/behavior/uiblocks`. It
wrote `blocks.gen.ts`, with a block of the Configure page for each method: the
form, the route, the permission and the columns. It did not write the kind, the
platforms, the chain or the examples. Thus the page showed a method as a verb
only, such as "Update". It did not show what the method changes, the permission
that it needs, the platforms that it runs on, or the behaviors that it calls.

## The Behaviors page

`/behaviors` lists the behaviors by area, in the order of the areas of the
catalog. An area with no behavior, such as `fleet`, has no section. The three
levels look different:

- An area is a section heading.
- A behavior is a row: its title, its name, its doc, the behaviors that it
  calls, and a mark for each method. The mark is `R` for a read, `W` for a write
  and `A` for an action. A behavior with a parent is after its parent, with an
  arrow, so "User SSH key" is after "User".
- A method is on the page of its behavior only.

The marks use colors of the logo, not the status colors: gray for a read, the
blue of the logo for a write, and magenta for an action. A write is not a
warning. A mark is faint when the role of the viewer does not have the
permission of the method. A behavior whose methods the role cannot run has a
lock. The filter matches each word of the query in the title, the name, the doc
or a method of a behavior, so `dns update` and `dns.update` both find DNS. The
internal behaviors are last, in their own section, because a plan cannot run
them.

`/behaviors/<name>` is the page of a behavior, as `osapi dsl behavior get` and
`osapi dsl chain get` print it. It shows the area, the parent, the platforms,
the behaviors that the behavior calls and that call it, and each method in a
card. The card of a method has its kind, its doc, its input and output types and
its route, its permission with whether the role of the viewer has it, its
platforms, a disruption when the method has one, its chain as a tree, and its
examples. **Add to plan** adds the method to the plan as a step. It is disabled
when the role does not have the permission. A link such as
`/behaviors/dns#update` opens the page at the card of the method. Each call of a
chain links to the page of its behavior.

## Plans

`/plans/new` is the composer. A plan is a list of steps that run in order. A
step has the shape of a step of a workflow file ([Workflows](workflows.md)):
`run`, the method as `behavior.method`, such as `dns.update`; `target`; and
`with`, the input of the method. `ui/src/lib/plan.ts` has the model, as pure
functions that `bun test` checks. `PlanProvider` keeps the plan while the person
moves between pages. Thus a method that a person adds from the page of its
behavior is a step on the Plans page.

The list at the left has each area, then each behavior of the area, then the
methods of the behavior. A click on a behavior opens it; a click on a method
adds a step. A filter opens each behavior that matches. A method that the role
cannot run is disabled and has a lock. The list stays in view as the plan grows,
and scrolls on its own when it is taller than the window.

The card of a step has its place in the plan, and the title of its behavior and
its method, such as "DNS · Update". It also has the input and output types of
the method, the behaviors that the method calls, its kind and its status. A step
can move up and down. The form of a step comes from the input of its method:

- A field with the values of an enum is a select.
- A list is a field of tags. Enter, a comma or a space adds a tag.
- A flag is a checkbox, and an object is JSON.
- A secret field takes a reference, `secret://<vault>/<key>`, from a picker
  beside it, as a text field takes a `@fact.` reference. The picker lists each
  key of each vault, grouped by vault, from `GET /api/secret` and
  `GET /api/secret/{vault}`. It shows only when the role may call both. A value
  that is not a reference is a password field. A reference shows as text,
  because it is not a secret. A map of secrets, such as the `env` of
  `docker.create`, is JSON, as each object is.
- Another field takes text or a `@fact.` reference.
- The doc of each field stays under the field, so it does not go when a person
  types.

A new read starts with the target `_all`. A new write or action has no target.
The card asks for the hosts, and the step is pending, until it has a target. Run
does not run a pending step. Before osapi-io/osapi#1166 each new block of the
Configure page started with `_all`, also a reboot or a delete. Thus a person who
applied with no look changed each host.

Above the steps, a preflight shows what the plan needs:

- each permission of its steps, and whether the role of the viewer has it. The
  controller makes the same check on each call.
- each host of a target where a method does not run. The preflight reads the
  platform of a host from `os_info.family` of the agent list. The agent reports
  there the family that it picks providers by, from gohai's `family.Detect`
  (osapi#1224). The catalog gives each method `runs_on`: the host platforms that
  it runs on, from `Behavior.RunsOnHost`, the rule that the agent itself calls,
  and `*` for a Linux host whose platform gohai has no family for. A platform
  that is not one of the host families of the catalog is such a host. The UI
  does not copy the rule (osapi#1235).
- the count of steps that wait for input or a target.

The preflight refuses nothing. **Run** runs each step that can run, in order,
and continues after a step fails. Each step that ran shows its job and its
trace, its result, and the chain of calls of its job on each host. The bar with
Run is pinned to the bottom of the window. After a run, the bar says what the
run did, such as `3 ran: 3 ok`, and has Clear, to start over, and Run again.

**Export YAML** shows the plan as a workflow file, read only, with a button that
copies it. A step with no target has a comment in place of its target. A plan
holds only references: a secret field keeps its reference, and a value is
`<secret>`, also each value of a map of secrets. The UI does not save a plan.
Save comes with workflow files. Before osapi-io/osapi#1197 the Configure page
had saved stacks, which were mock data behind a flag, and a Save that wrote to
the console.

The Object Store area of the list has four steps that run on the controller:
`objectstore.list`, `objectstore.upload`, `objectstore.delete` and
`objectstore.stale`. They are not behaviors, so they are not on the Behaviors
page. They take no target. Each names the operation that it calls in
`catalog-index.ts`, and its permission comes from the operations of the catalog.
TypeScript fails the build on an operation that the spec does not have. A step
whose operation the catalog does not have is not in the list. A workflow cannot
run them yet, so the YAML has them as a comment. The audit log is not in the
list. The Audit page, at `/admin/audit`, lists, opens and exports the entries.

A step is refused when it has no permission. `permitted` in
`ui/src/lib/permissions.ts` allows a permission only when the role has it, and a
role has only the permissions of the catalog. Before osapi-io/osapi#1161 the
panel of the Configure page enabled a block that had no permission. Command exec
and ping had no entry, so a role that cannot run a command saw both enabled.

The result of a method groups its rows by host and shows each field of the
output by its label (`GenericRowsResult` in `result-card.tsx`). It formats a
value by its `render` tag, as the CLI does: bytes as a size, such as 1.9 GB, a
time in the one format, and a flag as yes or no. An object is one line, such as
`total 1.9 GB, free 843.7 MB, used 253.2 MB`. A list of objects, such as the
disks of a host, is one line for each item under the row. A host whose one row
is only a list counts the items: `4 disks`. No behavior has a card of its own.
Thus a new method gets its step, and a changed input or output changes its step,
with no change to the UI. Before osapi-io/osapi#1027 the blocks of disk, memory
and status had hand-written cards. Before osapi-io/osapi#1007 each behavior
block had a hand-written form, call and card. The cards of packages and services
read the nested lists of the hand-written domains after those became behaviors,
and showed "0 packages" on each row (osapi-io/osapi#972, #1018). A click-through
in the lab found them, which a type check of the UI does not
([AGENTS.md](../../AGENTS.md#use-the-lab)).

Some behavior of a request is not clear from the code:

- The request keeps `@` and `:` in a path key. The controller reads a path key
  as the client sends it. Thus an escaped `@fact.` reference does not resolve,
  and the controller refuses it.
- A flag goes in the request only after a person sets it. Thus a flag that
  nobody touched keeps the default of the API.
- A refusal (a status of 400 or more) puts the step in its error state, with the
  `error` and the `reason` of the answer.

`JobView` shows the chain of calls of a job, as `osapi client job get` does. For
each host that answered with steps, its Chain section shows each call as
`behavior.method`, under the call that made it. Each call has `changed`, the
error of a call that failed, and its duration. A job that has `chain` lines and
no steps shows the lines. The Jobs page and the job panel of a step's result
both use `JobView`. Under the result of a step, `JobChain` shows the same tree
with no click. Before osapi-io/osapi#1162 the UI did not show the steps that the
job API returns.

## Color: one palette with the CLI

The UI and the CLI use one palette. The palette is the six colors of the logo,
`asset/logo-dark.svg`, and the status colors in `internal/cli/theme.go`.
`ui/src/index.css` holds the colors as tokens, and each token names the CLI
color that it copies. Thus a page and a terminal show the same color for the
same thing. [The output style of the CLI](cli.md#color) has the rules for the
terminal. A change to a color changes both.

| Color               | Means                                       | Tokens                                      |
| ------------------- | ------------------------------------------- | ------------------------------------------- |
| green `#67ea94`     | ok: ready, completed, applied               | `primary`, `status-ready`, `status-applied` |
| amber `#ffd787`     | needs attention: pending, retried           | `status-pending`                            |
| red `#ef4444`       | wrong: failed, error                        | `status-error`                              |
| gray `#8a8a8a`      | secondary text, labels, and a count of zero | `text-muted`                                |
| the logo colors     | section headings                            | `heading-1` to `heading-5`                  |
| dark blue `#2300fd` | the logo accent: the heading bar            | `accent`                                    |

**Green, amber and red mean status, and nothing else.** The chrome is neutral:
borders, the navigation, the stat numbers and URLs. A count of zero is gray,
because `failed: 0` is not a failure. The `admin` role chip is gray, because a
role is not a problem. A URL is a link in the logo's cyan that underlines on
hover, as a link of the docs site is. A component row shows its status word only
when the status is not ok. The green dot says ok, so a card of healthy rows has
one mark on each row, not two.

**Section headings take the logo colors in page order:** cyan, magenta, yellow,
green, blue. These are the five heading colors of the CLI. The CLI mixes their
order for each run; the UI keeps one order, so a page looks the same on each
load. `PageLayout` sets `data-heading-color` on each `SectionLabel` when the
page changes. Thus two headings next to each other never have the same color.
Each heading has a short bar in the dark blue of the logo at its left.

**A label is gray, under each heading.** A label is a `CopyField` label, such as
`ID:`, a key of a `KVList`, a table header, the icon of a `MetricValue`, or the
icon of a card. A value has the text color. An ID, a unit and a missing value
are gray too. Only the heading takes the color of its section. Before 21
November 2026 a label took a dark tint of its heading, as the CLI's labels do.
Under the green Agents heading, the dark green labels mixed with the status
green of the Ready badges and the health dots, and the cards had too much color.
The CLI keeps its tints.

The logo has two colors that a heading cannot use as they are:

- The dark blue `#2300fd` has a contrast of 2.3:1 on the page. That is too low
  for text. Thus a heading uses `#6b5cff`, the `LogoBlueText` of the CLI, and
  the dark blue is only a shape: the heading bar and the background network.
- The logo green `#45ae17` is darker than the ok green `#67ea94`. Thus a green
  heading does not look like a status.

**The background network is part of the design.** `network-map-background.tsx`
draws it in the dark blue. A flood that moves through it sparkles white. Do not
remove it to make a page quieter. osapi-io/osapi#1031 removed it, and
osapi-io/osapi#1052 put it back.

The loading spinner takes one heading color, which `spinner-color.ts` selects
one time for each page load.

**A status word has the color that the CLI gives it.** `StatusTones` in
`internal/cli/theme.go` gives each status word a tone: ok, warn or err. The
catalog serves the map as `status_tones`. `statusVariant()` in
`ui/src/lib/status.ts` reads the first word of a status, lowercased, as the CLI
does. It gives the `Badge` variant. `statusDot()` and `statusText()` give the
`HealthDot` and `Text` colors of the same word. `useStatus()` gives the three
with the tones of the catalog, and each badge, dot and status text uses it. A
page does not map a status to a color of its own. A word that the CLI does not
color, such as `processing`, is gray. Thus `skipped`, `submitted`, `draining`
and a condition are amber on each page and in the terminal.

A count has a tone too. `CountTones` in the same file gives the tone of a count
above zero by what it counts: `failed` and `dlq` are red, `unprocessed` and
`skipped` are amber, `completed` is green. A zero is gray. The catalog serves
`CountTones` as `count_tones`, and `Count` reads it.

An HTTP method, an HTTP code, a role and a target group are not statuses, so
they never take green, amber or red. The audit log shows a method in bold, as
the CLI does, and a code in the text color. A permission that writes is in bold.
Blue `#3b82f6`, `status-running`, is not a status color: it is the color of
command output in a code block.

`--font-mono` starts with the mono font of the system. JetBrains Mono is not in
the bundle. When it was first in the list, a browser without it showed a serif
Courier.

## The dashboard

The dashboard shows what needs attention first. Its four tiles are the agents
that are ready, the failed jobs, the dead letters (the jobs that used up their
retries), and the uptime and version of the controller. A count of zero is gray
and a count of failures is red. The NATS version and its URL are a line of the
NATS card. The consumer count is on the line of the stream in Storage.

The controller card is at the left. The NATS card and Storage are at the right,
one above the other, so the short NATS card does not leave a gap. A component
shows its version only when the version is not the version of the controller,
and then in amber. A mismatch is the case that a person looks for. An age is
`up 2m`, not `2m`, so that the number has a meaning.

## The agent cards

The dashboard shows a card for each agent. The registry of agents gives the
agents in no fixed order. Thus `use-agents.ts` sorts them by hostname. Without
the sort, two cards changed places on each poll (osapi-io/osapi#823).

A card lists its fields in the order of `osapi client agent list`: the
conditions, the labels, the age, the load and the OS. The machine ID and the
fingerprint are in an `Identity` disclosure below the health checks, because
nobody scans them. The card shows the version of the agent only when it is not
the version of the controller, in amber. The metrics row always has two columns,
the age and the load. A value that the agent does not report is `-`. Thus the
cards align when a host, such as Fedora, does not report the load. The age is
`up` and the time from `started_at`, as `FormatAge` of the CLI prints it, and
the uptime of the system is in the tooltip. The memory line is
`7.7 GB total, 3.4 GB used, 4.3 GB free`, as `osapi client agent get` prints it.
A drain or an undrain applies at the agent's next heartbeat, up to 20s after the
controller accepts it. The card shows the request at once: the badge reads
`Draining` or `Undraining` in amber, the button has a spinner, and a line says
that the request was accepted and when it applies. The card then polls the
agents every 2s, not each 10s, until the state the agent reports matches. After
60s it says that the agent has not acted on it yet. A request that fails shows
its error on the card. Before, the card showed nothing until the next heartbeat
and poll, and a failure was silent.

## Coverage says nothing about it

`/ui/` is in `.coverignore`. Thus the coverage figure of osapi does not include
the UI. The gate does not cover the UI, and nothing in the output of the gate
says so.

The UI has its own checks: `just react-lint`, `just react-test`,
`just react-unit` and the Docusaurus build for its documentation.
`just react-unit` runs `bun test` on the `src/**/*.test.ts` and
`src/**/*.test.tsx` files of the UI, and `tsconfig.test.json` checks their
types. It is one of the quick checks of `just test`, so CI runs it. bun preloads
happy-dom (`src/test/dom.ts`), so a test renders a component or a hook with
React Testing Library, and `src/test/cleanup.ts` unmounts it after each test.
The tests cover the logic of the pages, the shared hooks and the shared
components. They do not render a whole page against the API. Thus a
click-through in the lab is still necessary
([AGENTS.md](../../AGENTS.md#use-the-lab)).

A page reads the API through `usePolling` (`ui/src/hooks/use-polling.ts`): it
calls at once and then at each interval, while `enabled`, and it drops an answer
that comes after the page left or after its inputs changed. A page passes
`enabled: canCall(operation)`, so a role that the API refuses sends no request.
Before, the Jobs, Audit and Admission pages polled each 10 seconds and got a 403
for a refused role (osapi-io/osapi#1236). `useJob` reads one job. A value that
the API gives as an enum, such as a job status or an agent state, comes from the
orval client's constants, such as `GetJobsStatus`, not a typed string
(osapi-io/osapi#1234).

## Where this connects

[Behaviors](behaviors.md#generated-and-committed) tells what the client comes
*from*, and the checks that hold the full specification to the server.

______________________________________________________________________

Written from `ui/`, `internal/controller/api/ui/` and
`internal/controller/endpoints/catalog/`.
