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
| a status                | `Badge`, `HealthDot` and `Text`, with `lib/status.ts`                |
| a page that loads       | `components/ui/spinner.tsx`                                          |
| a page without its perm | `components/layout/permission-denied.tsx`                            |
| an empty page           | `components/ui/empty-state.tsx`                                      |
| an error                | `components/ui/error-banner.tsx`                                     |
| key-value pairs         | `components/ui/kv-list.tsx`: the values line up, as `PrintKV`        |
| a count                 | `components/ui/count.tsx`, with `COUNT_TONES`                        |
| a result's summary line | `components/domain/result-summary.tsx`                               |
| a job                   | `JobView` in `components/domain/job-detail.tsx`, as `job get`        |
| a time, age or duration | `lib/format.ts`                                                      |
| a pick from a list      | `Picker` in `components/ui/popover.tsx`, with a hook for the list    |
| a choice in a row       | `components/ui/chip.tsx`                                             |
| a text field            | `Input`, with an `icon`, and `Textarea` in `components/ui/input.tsx` |
| a checkbox              | `components/ui/checkbox.tsx`                                         |
| a load for a form       | `hooks/use-load.ts`, under each resource hook such as `useObjects`   |

A table header is in capitals, in the tint of its section, as the CLI prints it.
A page uses these, not a raw `<button>`, `<input>` or `<textarea>`. A picker of
a resource gives `Picker` only its options; the trigger, the keyboard, the
loading state and the empty list, `None.`, are the same in each. A hook that
loads choices for a form builds on `useLoad`, which keeps the value as it was
when the load fails, so a picker stays empty and the form still works. A page
that must show a failure, such as Admission, keeps its own error state. A result
card counts its summary line from its per-host `results`, so a card never shows
a status that it did not count. A panel inside a card has the `surface` token,
not a hex value.

**A value has the format that the CLI gives it.** `lib/format.ts` has the
formatters of `internal/cli/ui.go` in TypeScript: `formatTime` prints
`2006-01-02 15:04:05` in local time, `formatAge` prints `3d 4h`,
`formatDurationMs` rounds as `FormatDuration` does and prints `3m4s`, and
`formatBytes` prints `5.2 KB`. A page does not call `toLocaleString` or write a
formatter of its own. A field has the name that the CLI gives it, such as
`Machine ID`, and a page lists the fields in the order of the CLI command for
the same resource. A result's summary line is `2 hosts: 1 ok, 1 skipped`, then
the whole job ID in gray, as the CLI prints it. A job ID is never cut.

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
`osapi token generate`. You paste it into the sign-in page, or you give it
through the environment. The UI sends it as a bearer header on each request.

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
refuses it, each page shows an error until the person signs out.

The permission model of the UI is the model of osapi. The roles claim uses the
permissions and the three roles that the API checks.
[Permissions](permissions.md) describes them. The UI does not keep its own list.
`go generate ./internal/behaviors/all` writes `ui/src/lib/permissions.gen.ts`
from `AllPermissions` and `RolePermissions` in `internal/authtoken`, with every
behavior registered. A Go test fails when the file is stale, and TypeScript
fails the build on a permission that Go does not have. A hand copy came before
it, and it was out of date: it had `cron:*`, `hostname:*` and `group:*`, which
no token has, and did not have `schedule:*` (osapi-io/osapi#749). The published
site also tells what each role permits for an *operator*, because a person who
configures a role looks there.

## Color: one palette with the CLI

The UI and the CLI use one palette. The palette is the six colors of the logo,
`asset/logo-dark.svg`, and the status colors in `internal/cli/theme.go`.
`ui/src/index.css` holds the colors as tokens, and each token names the CLI
color that it copies. Thus a page and a terminal show the same color for the
same thing. [The output style of the CLI](cli.md#color) has the rules for the
terminal. A change to a color changes both.

| Color               | Means                                    | Tokens                                      |
| ------------------- | ---------------------------------------- | ------------------------------------------- |
| green `#67ea94`     | ok: ready, completed, applied            | `primary`, `status-ready`, `status-applied` |
| amber `#ffd787`     | needs attention: pending, retried        | `status-pending`                            |
| red `#ef4444`       | wrong: failed, error                     | `status-error`                              |
| gray `#8a8a8a`      | secondary text, and a count of zero      | `text-muted`                                |
| the logo colors     | section headings                         | `heading-1` to `heading-5`                  |
| a dark tint of each | the labels and icons under that heading  | `tint-1` to `tint-5`                        |
| dark blue `#2300fd` | the logo accent: heading bar, background | `accent`                                    |

**Green, amber and red mean status, and nothing else.** The chrome is neutral:
borders, the navigation, the stat numbers and URLs. A count of zero is gray,
because `failed: 0` is not a failure. The `admin` role chip is gray, because a
role is not a problem. A URL has the text color and is a link that underlines on
hover.

**Section headings take the logo colors in page order:** cyan, magenta, yellow,
green, blue. These are the five heading colors of the CLI. The CLI mixes their
order for each run; the UI keeps one order, so a page looks the same on each
load. `PageLayout` sets `data-heading-color` on each `SectionLabel` when the
page changes. Thus two headings next to each other never have the same color.
Each heading has a short bar in the dark blue of the logo at its left.

**A label takes the tint of its section heading.** This is the tint tier of the
CLI, and the tints are the `tints` of `internal/cli/theme.go`. A label is a
`CopyField` label, such as `ID:`, an icon of a `MetricValue`, or the icon of a
card. A value has the text color. An ID, a unit and a missing value are gray.
`index.css` gives each element after a heading the `--section-tint` of that
heading, with the selector `[data-heading-color="N"] ~ *`. The `text-tint`
utility reads it. Thus a label must be in the same parent element as the
heading, below it. A label outside a section is gray.

The logo has two colors that a heading cannot use as they are:

- The dark blue `#2300fd` has a contrast of 2.3:1 on the page. That is too low
  for text. Thus a heading uses `#6b5cff`, the `LogoBlueText` of the CLI, and
  the dark blue is only a shape: the heading bar and the background network.
- The logo green `#45ae17` is darker than the ok green `#67ea94`. Thus a green
  heading does not look like a status.

**The background network is part of the design.** `network-map-background.tsx`
draws it in the dark blue. A flood that moves through it sparkles white. Do not
remove it to make a page quieter.

The loading spinner takes one heading color, which `spinner-color.ts` selects
one time for each page load.

**A status word has the color that the CLI gives it.** `StatusTones` in
`internal/cli/theme.go` gives each status word a tone: ok, warn or err. Go
generate writes the map to `ui/src/lib/status.gen.ts`, and a test in
`internal/behaviors/all` fails when that file is stale. `statusVariant()` in
`ui/src/lib/status.ts` reads the first word of a status, lowercased, as the CLI
does. It gives the `Badge` variant. `statusDot()` and `statusText()` give the
`HealthDot` and `Text` colors of the same word. Each badge, dot and status text
uses them. A page does not map a status to a color of its own. A word that the
CLI does not color, such as `processing`, is gray. Thus `skipped`, `submitted`,
`draining` and a condition are amber on each page and in the terminal.

A count has a tone too. `CountTones` in the same file gives the tone of a count
above zero by what it counts: `failed` and `dlq` are red, `unprocessed` and
`skipped` are amber, `completed` is green. A zero is gray. Go generate writes
`CountTones` to the same file as `COUNT_TONES`, and `Count` reads it.

An HTTP method, an HTTP code, a role and a target group are not statuses, so
they never take green, amber or red. The audit log shows a method in bold, as
the CLI does, and a code in the text color. A permission that writes is in bold.
Blue `#3b82f6`, `status-running`, is not a status color: it is the color of
command output in a code block.

`--font-mono` starts with the mono font of the system. JetBrains Mono is not in
the bundle. When it was first in the list, a browser without it showed a serif
Courier.

## The agent cards

The dashboard shows a card for each agent. The registry of agents gives the
agents in no fixed order. Thus `use-agents.ts` sorts them by hostname. Without
the sort, two cards changed places on each poll (osapi-io/osapi#823).

A card lists its fields in the order of `osapi client agent list`: the machine
ID, the conditions, the labels, the age, the load, the OS and the version. The
metrics row always has two columns, the age and the load. A value that the agent
does not report is `-`. Thus the cards align when a host, such as Fedora, does
not report the load. The age is from `started_at`, as `FormatAge` of the CLI
prints it, and the uptime of the API is in the tooltip. The memory line is
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

The UI has its own checks: `just react-lint`, `just react-test` and the
Docusaurus build for its documentation.

## Where this connects

[Building a domain](domains.md) tells what the client comes *from*. It also
tells why the client cannot see a domain that is not in the combined
specification.

______________________________________________________________________

Written from `ui/` and `internal/controller/api/ui/`.
