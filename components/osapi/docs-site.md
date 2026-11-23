# The docs site

The docs site of osapi is in `docs/` of osapi-io/osapi, a Docusaurus site. Its
pages are of two kinds. A page that says what this build has is generated from
the binary. A page that explains or teaches is written by hand. Thus a page of
the first kind cannot be wrong about the build, and a person writes only what
the binary cannot say.

## The sections

| Section      | Has                                                                    | Written by                           |
| ------------ | ---------------------------------------------------------------------- | ------------------------------------ |
| Features     | what osapi does, by feature                                            | hand                                 |
| Usage        | how to run it, and the CLI reference: a page for each command          | hand; the CLI pages generated        |
| SDK          | the Go SDK                                                             | generated; the overviews by hand     |
| Reference    | what this build has: behaviors, chains, endpoints, CLI groups, the API | generated; the landing pages by hand |
| Architecture | how osapi is built                                                     | hand                                 |
| Development  | how to build with osapi, and the DSLs                                  | hand; the DSL pages generated        |

Reference answers "what does this build have". Development answers "how do I
build one". The DSL pages are under Development, because only a person who
builds osapi reads the grammar of a DSL.

## A reference page is the output of a command

Each page under Reference is the output of the `list` or `get` command that
shows the same thing, written as markdown:

| Page                         | Is the output of                                                              |
| ---------------------------- | ----------------------------------------------------------------------------- |
| Behaviors, and each behavior | `osapi behavior list`; `osapi behavior get`, and `method get` for each method |
| Chains, and each chain       | `osapi behavior chain list`; `osapi behavior chain get`                       |
| Endpoints, and each group    | `osapi controller endpoint list`; `osapi controller endpoint get`             |
| CLI, and each local group    | `osapi cli command list`; `osapi cli command get`                             |

`osapi cli docs reference generate` calls the handler of each command with the
same dependencies that the CLI gives it, then prints the output with
`command.Render` and a markdown printer, `cli.Markdown`. The terminal prints
through the same `Render` with its own printer. Thus a page and its command show
the same headings, key-value blocks and tables, and a field that a command adds
is on its page with no other change. The first version of the behavior pages was
a separate page builder. It showed less than `behavior get`, and nothing held
the two together.

A page links what it names. The rule of each page says which column or label is
a link: the name of a behavior to its page, the behaviors that it uses or that
use it, a behavior to its chain, and a command to its page in the CLI reference.

A landing page, such as `reference/behaviors/behaviors.mdx`, is written by hand.
It explains the section and imports the generated table, `_catalog.mdx`. The
generator removes a generated page that no command writes now, such as the page
of a behavior that was removed, and keeps a page that a person wrote.

## The DSL pages

`osapi cli docs dsl generate` writes a page for each DSL under
`development/dsl/`: the behavior DSL, chains, the endpoint DSL and the command
DSL. Each page is the spec that the `spec get` command of the DSL prints, in the
same order. `guide.Spec.Markdown` writes it.

## The look

The site has the look of the UI and the CLI. The palette is
`docs/src/css/palette.gen.css` and `docs/src/palette.gen.ts`, which
`go generate ./internal/behaviors/all` writes from `internal/cli/theme.go`, as
it writes the status colors of the UI. A test fails when a file is stale.
`docs/src/css/custom.css` uses the palette, and copies the parts of the UI that
it names.

- The type is the UI's: the system font, a page title of 1.75rem, and a section
  heading of 1.125rem. Each `h2` takes a logo color in page order, after the
  dark-blue bar, as a section of the UI does. Under a heading, the text is the
  text color and gray.
- A link is a word in the logo's cyan, underlined only under the pointer.
- A table, a code block, a note and a card are cards of the UI: black, a faint
  border and 8px corners. A table header is small gray capitals. A table with no
  header, such as the key-value table of a behavior page, has gray keys.
- Under the pointer, a card is as the UI's `Card`: only its border is brighter,
  `white/20` from `white/9`. A card has no colored bar.
- The open page has the text color and the raised background in the sidebar, as
  a page under the pointer has. The open tab of a Tabs block or of an API page
  has the raised background and a border. Nothing that is open or selected has a
  blue line or bar under or beside it.
- Green, amber and red are a status only: on a success, warning or danger note.
  An HTTP method is a quiet chip in a logo color: GET cyan, POST yellow, PUT and
  PATCH blue, DELETE magenta. A required field is magenta.
- A code block uses the CLI's colors: keywords magenta, strings yellow, names
  cyan, numbers and flags blue, comments gray. In bash, a command name is the
  text color, because Prism colors only the commands that it knows.
- The dark page is the UI's: `#0a0a0a` under black cards. The light page uses
  the dark tints of the logo colors, which read on white, as the README's
  `logo-light.svg` does.

Before osapi-io/osapi#1037 the site had a theme of its own. Green was the color
of each link, of the navbar and of the cards, and a purple rule was under the
navbar. "Getting Started" and "Usage" in the navbar were active on each page,
because a doc item of the navbar is active on each page of its sidebar. The
languages in `additionalLanguages`, bash among them, were in a nested `prism`
key that Docusaurus does not read, so bash was not highlighted.

The dev server and the build do not apply the CSS in the same order. The build's
minifier merges rules that have the same declarations, and that can move a rule
of `custom.css` before a rule of Docusaurus or of the OpenAPI plugin that has
the same weight. Then the other rule wins in production only. After
osapi-io/osapi#1037, three rules lost this way: the underline of a link under
the pointer showed on a card, a link in an admonition had the text color and an
underline, and each language tab of an API page had the plugin's line, not the
dark-blue one. Docusaurus' `.cardContainer_*` is on the same element as `.card`,
so in the build it can also give a card a bright border, and the white of the
text under the pointer. Thus a rule of `custom.css` that must win over a rule of
the same weight is `!important`. Do not depend on its place in the file.

## The output of a command

Each command page of a behavior shows what its examples print, under Result.
`command.Output` gives three things for each example:

- the command for one host, `--target web-01`, and what the CLI prints;
- the same command for `--target _all`, where `web-01` and `web-02` answer and
  `mac-01` skips with `operation not supported on this OS family`;
- the API's response, which `--json` prints.

The two screens come from the CLI's own printer, with the colors forced on. The
generator writes each screen, the escape codes of the colors included, in a
fenced block of language `ansi`. The site's `CodeBlock` wrapper,
`docs/src/theme/CodeBlock`, shows such a block with `Ansi`, which turns each
code into a colored span. Thus the page shows what a terminal shows, and
`cli-docs-gen-check` fails when the printer changes and the page does not. The
page stays a `.md` file, because the build drops raw HTML in a `.md` page.

A page that a person wrote shows the same screens with a marker, which
`osapi cli docs reference generate` fills from the first example of a behavior's
method:

```markdown
<!-- osapi:output sysctl list web-01 mac-01:skipped web-02:failed -->
<!-- /osapi:output -->
```

The words after the method are the hosts: `host` answers the example,
`host:skipped` skips as a Mac does, and `host:failed` fails. One host is
`--target host`, and more hosts are `--target _all`. `--json` last gives the
response body, which the CLI prints with no table and no color. The output page,
`usage/cli/output.md`, is made of these screens. Before, it wrote them by hand
in `text` blocks, which have no colors. In a fleet screen, a value that is the
example's host becomes the host's own, so `hostname get` shows each host's own
name.

osapi-io/osapi#725 removed this output with the pages of each method. Before
then, the same three things were on each method's page, as raw HTML in an `.mdx`
page. osapi-io/osapi#1044 brought back only the screen for one host. The fleet
and the JSON came back after it.

A command of an endpoint group shows its output too. `.Prints(out)` gives an
`.Example` the answer of the API, a value of the method's output type. The
command generator, `internal/cli/command/gen`, prints the value through
`command.Derive`, as the CLI prints the answer, and writes the screen and the
JSON in the Result section of the page. An endpoint method runs on the
controller, not on a host, so its page has no screen for the fleet. The
generator fixes the time that an age is from to 2026-01-15 10:00 UTC, and prints
each time in UTC. Thus a page is the same on each run and in each time zone, and
`cli-docs-gen-check` does not fail from the clock. A hand-written command of
`cmd/` has no example output yet. It gets one when it becomes a behavior
(osapi-io/osapi#1049).

## The navbar

The dropdowns of the navbar come from the docs tree, not from a list in the
config. `docs/src/navbar.ts` reads the pages of a folder when the site builds,
in the order of their `sidebar_position`, with the title of each page.

- **Features** has each page of `sidebar/features`, except its index.
- **SDK** has the overview of the client, then a section for each folder of
  `sidebar/sdk/client`, with the page of each service in it. The label and the
  order of a section come from the `_category_.json` of its folder, which
  `internal/sdk/gen` writes from the areas of the spec
  ([areas](endpoints.md#areas)). Then it has the platform pages and the link to
  the orchestrator.
- **Behaviors** has the page of each behavior under `reference/behaviors`, which
  the registry generates.

Thus a new page shows in the navbar with no edit, and a page that is gone leaves
it. Before osapi-io/osapi#1014 the config had 65 doc IDs written by hand. The
Features dropdown had 16 of the 29 feature pages, and no behavior page was in
the navbar.

## Checks

`just cli-docs-generate` writes the CLI pages, the DSL pages and the reference.
`just cli-docs-gen-check`, in `just test`, fails when one of them differs from
the binary. Each generated page has the title of the thing in its front matter,
with initialisms such as DNS in capitals. Docusaurus does not read the title
from a heading after the generated comment, and showed the file name in the
sidebar.

## The config tables

A feature page that has settings shows them in a table that `config.Keys`
writes: each key, its type, its default, the environment variable that sets it,
and its doc. The page marks where the table goes, with the key prefixes that it
shows:

```markdown
<!-- osapi:config agent.facts nats.facts -->
<!-- /osapi:config -->
```

`osapi cli docs reference generate` writes the table between the two markers,
and keeps the rest of the page. Thus `just cli-docs-generate` writes it, and
`cli-docs-gen-check` fails when a key changes and its table does not.

A key with no default in `config.Defaults` gets its value from
`configs/osapi.yaml`, the config that osapi ships. The table says so, as
`none; 9091 in configs/osapi.yaml`, and does not call that value a default.
Before osapi-io/osapi#1011 the tables were written by hand, and they gave 9091,
9092, `agent-facts` and `5m` as defaults. A config file without those keys does
not get those values.

## The metrics reference

`internal/telemetry/instruments` lists each metric that osapi records: its name
without the namespace, its kind, unit, labels, the component that records it,
and its doc. The code that makes an instrument takes its name and doc from that
list. `just cli-docs-generate` writes the table of `features/metrics.md` between
`<!-- osapi:metrics -->` markers from the same list. A test records a behavior
call and compares the labels of its values with the list.

Before osapi-io/osapi#1012 the table was written by hand, and it did not have
the three behavior metrics. A name must not have the `osapi_` prefix, because
the Prometheus exporter adds it: `osapi_behavior_calls_total` was exported as
`osapi_osapi_behavior_calls_total` until osapi-io/osapi#1056.
`osapi_nats_client_operation_duration_seconds` is in the prose of the page, not
the table, because nats-client records it.

## What is not generated yet

The overview of the client of the SDK and its guidelines are written by hand.
The page of each service of the SDK is generated, from the spec and the source
of the SDK: [the SDK](sdk.md#the-examples-and-the-pages-are-generated) tells
how. The role table of the configuration page is generated, as the config tables
are, between `<!-- osapi:roles -->` markers.

A feature page explains a feature, and links to the generated page of each
behavior that it uses for the permission, the platforms and the route of each
method. It does not copy them. Before osapi-io/osapi#1010, seven feature pages
had their own tables of operations, platforms and permissions, and four were
wrong: the update checks asked for `package:*`, the node status for `node:read`,
the timezone read was "skipped" on macOS and Linux where it runs, and the
network page listed a route get that no longer exists. A copy goes stale the
first time its behavior changes, and no check reads it.
