# Docs and tables

The Docusaurus site is user-facing: what a feature does, how to call it, what
the SDK exposes. Development guidance is not there, it is in this skill.

A domain that works but appears in none of these is invisible to everyone who
did not write it.

## Pages to add

```
docs/docs/sidebar/features/{domain}-management.md
docs/docs/sidebar/usage/cli/client/node/{domain}/{domain}.md   landing, <DocCardList />
docs/docs/sidebar/usage/cli/client/node/{domain}/{verb}.md     one per subcommand
docs/docs/sidebar/sdk/client/{category}/{domain}.md            SDK service page
```

CLI pages are hand-written, not generated. Each shows a real invocation and its
output, including the broadcast form. Copy the reference domain's page shape.

The SDK page's title is the `Client` field name, for example `# Power`, not the
Go struct name. Place it in the category directory its concern belongs to.

## Tables and navigation to update

| File | What to add |
| --- | --- |
| `docs/docusaurus.config.ts` | the feature in the Features dropdown, the service in the SDK dropdown |
| `features/features.md` | a row for the domain |
| `sdk/client/client.md` | the service in its category table |
| `features/authentication.md` | any new permission, in the roles and permissions tables |
| `usage/configuration.md` | the same permission, in the roles table and the YAML reference comments |
| `architecture/api-guidelines.md` | a new path pattern, if the domain introduces one |
| `architecture/system-architecture.md` | endpoints, if they belong in the health or endpoint tables |

A new permission appears in four places: the spec, the role expansion in code,
`authentication.md`, and `configuration.md`. Missing the last two means
operators cannot discover it.

## Writing

- Wrap at 80 characters. `mise exec -- just docusaurus-fmt` is prettier, and
  `just md-fmt` covers markdown outside the site.
- Say what the operation does, then show it. A command with its real output
  answers more questions than a paragraph.
- Document the idempotent outcome: what a second run reports.
- Note where an operation is unsupported, and what the caller sees then.
- No development instructions. If it tells a contributor how to build
  something, it belongs in a skill.

## Check

```bash
mise exec -- just docusaurus-build     # broken internal links fail the build
mise exec -- just docusaurus-fmt-check
mise exec -- just md-fmt-check
```

`onBrokenLinks: 'throw'` means a link to a page you have not created yet fails
the build rather than shipping a dead link.
