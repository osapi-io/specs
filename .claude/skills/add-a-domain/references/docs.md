# Docs and tables

The Docusaurus site is user-facing: what a feature does, how to call it, what the
SDK exposes. Development guidance is not there — it is in the corpus, and this
skill cites it.

A domain that works but appears in none of these is invisible to everyone who did
not write it.

## The rule is in the corpus, not here

The obligation is stated in
[005-building-a-domain](../../../../components/osapi/specs/005-building-a-domain/spec.md).

| What you need to know | Where |
| --- | --- |
| A domain appears everywhere an existing domain appears, and the check is to pick one and search for it | FR-001 |
| What verifies a finished domain, and why the documentation gate is not in Step 8's commands | FR-024 |

FR-024 is the one to read before running anything: the documentation below is
checked by `docusaurus-fmt-check` and `docusaurus-build`, which run in
`just test` and **not** in `just ready`. Writing these pages and then running only
the build-and-unit commands hands in work that fails continuous integration on the
pages you just wrote.

## Pages to add

```
docs/docs/sidebar/features/{domain}-management.md
docs/docs/sidebar/usage/cli/client/node/{domain}/{domain}.md   landing, <DocCardList />
docs/docs/sidebar/usage/cli/client/node/{domain}/{verb}.md     one per subcommand
docs/docs/sidebar/sdk/client/{category}/{domain}.md            SDK service page
```

CLI pages are hand-written, not generated. Each shows a real invocation and its
output, including the broadcast form. Copy the reference domain's page shape.

The SDK page's title is the `Client` field name, for example `# Power`, not the Go
struct name. Place it in the category directory its concern belongs to.

## Tables and navigation to update

| File | What to add |
| --- | --- |
| `docs/docusaurus.config.ts` | the feature in the Features dropdown, the service in the SDK dropdown |
| `features/features.md` | a row for the domain |
| `sdk/client/client.md` | the service in its category table |
| `features/authentication.md` | any new permission, in the roles and permissions tables |
| `usage/configuration.md` | the same permission, in the roles table and the YAML reference comments |
| `architecture/system-architecture.md` | endpoints, if they belong in the health or endpoint tables |

A new permission appears in four places: the spec, the role expansion in code,
`authentication.md`, and `configuration.md`. Missing the last two means operators
cannot discover it.

**`architecture/api-guidelines.md` is not on this list any more.** It was, and the
row said to add a new path pattern to its table. The page no longer exists: its six
guidelines are FR-014 and FR-015, and its address redirects. A new path pattern is
now a question of whether it obeys FR-014, not of whether a table lists it.

## Writing

- Wrap at 80 characters. `mise exec -- just docusaurus-fmt` is prettier, and
  `just md-fmt` covers markdown outside the site.
- Say what the operation does, then show it. A command with its real output answers
  more questions than a paragraph.
- Document the idempotent outcome: what a second run reports.
- Note where an operation is unsupported, and what the caller sees then.
- No development instructions. If it tells a contributor how to build something,
  it belongs in the corpus with a citation from this skill.

## Check

```bash
mise exec -- just docusaurus-build     # broken internal links fail the build
mise exec -- just docusaurus-fmt-check
mise exec -- just md-fmt-check
```

`onBrokenLinks: 'throw'` means a link to a page you have not created yet fails the
build rather than shipping a dead link.
