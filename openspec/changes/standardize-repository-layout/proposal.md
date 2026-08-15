## Why

Nine repositories carry the same kinds of file and describe themselves in the
same kinds of section, but no two agree on where those files live or what the
sections are called. A survey of the organization found only five files present
in every repository, and only one README section (`📄 License`) common to all
nine.

The contributing documentation is split across `docs/contributing.md` and
`docs/development.md` in eight repositories and consolidated at the root in one,
with no record of which is intended. Agent guidance sits in `CLAUDE.md`
everywhere except `specs`, which uses the `AGENTS.md` split already adopted
outside this organization.

Every new repository, and every attempt to bring an existing one up to standard,
is currently a matter of picking a repository to imitate.

## What Changes

- Establish the `repo-standards` capability, covering which files every
  repository carries and how its README is structured.
- Classify repositories by type — Go library, main product, utility, and
  documentation — because a Go library's README and a documentation repository's
  README answer different questions and should not be forced into one shape.
- Require a uniform README section vocabulary and ordering **within** each type,
  so that all Go libraries read alike.
- Adopt root `CONTRIBUTING.md` as the single contributing document, replacing
  `docs/contributing.md` and `docs/development.md`.
- Adopt `AGENTS.md` for agent guidance with `CLAUDE.md` as a pointer to it,
  making the guidance tool-neutral.
- **BREAKING** Eight repositories must move and merge their contributing
  documentation, and every inbound link to the old paths must be updated.

CI workflows, coverage configuration, and justfile recipe surface are
deliberately out of scope. They drift too, but they are a separate subject and
would double the size of this change.

## Capabilities

### New Capabilities

- `repo-standards`: which files an osapi-io repository carries, how its README
  is structured, and how those differ by repository type.

### Modified Capabilities

None.

## Impact

- `osapi-justfiles`: first repository converted. Contributing documentation
  consolidated to the root; `AGENTS.md` added; `CLAUDE.md` reduced to a pointer.
- `gohai`, `nats-client`, `nats-server`, `osapi`, `osapi-orchestrator`,
  `osapi-ui`: same conversion, one repository at a time.
- `specs`: already conforms; it is the reference for the file layout.
- `osapi`: exempt from the README structure requirement. It is the
  organization's landing page rather than a library, and its README deliberately
  differs.
- `osapi-sdk`: out of scope. It is deprecated and its README says so.
