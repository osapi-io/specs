# repo-standards Specification

## Purpose

Defines which files an osapi-io repository carries and how its README is
structured, so that repositories of the same kind read alike and a new
repository can be created without imitating an arbitrary existing one.

## Requirements

### Requirement: Repository types

Every repository SHALL be one of five types, and its type SHALL determine its
README structure.

- **Go library** — a package other repositories import. A library MAY ship a CLI
  that wraps it; the library is the product and the CLI is a convenience, so it
  remains this type.
- **Main product** — the deployable service the organization exists to build.
- **Utility** — shared assets consumed by other repositories rather than
  imported as code.
- **Documentation** — specifications and design records.
- **UI** — a user interface, run or embedded rather than imported.

#### Scenario: Classifying a new repository

- **WHEN** a repository is created to hold a Go package other repositories
  import
- **THEN** it is a Go library and follows the Go library README structure

#### Scenario: Types with different audiences

- **WHEN** a reader opens a utility repository's README
- **THEN** it explains how to consume the assets, not how to import a package

### Requirement: Repository classification

Every repository SHALL have a recorded type. The classification is:

| Repository           | Type          |
| -------------------- | ------------- |
| `gohai`              | Go library    |
| `nats-client`        | Go library    |
| `nats-server`        | Go library    |
| `osapi-orchestrator` | Go library    |
| `osapi`              | Main product  |
| `osapi-justfiles`    | Utility       |
| `specs`              | Documentation |

`osapi-sdk`, `osapi-ui`, and `osapi-io-taskfiles` are outside this capability.
`osapi-sdk` and `osapi-ui` state their deprecation at the top of their README
and record that their contents moved into `osapi`. `osapi-io-taskfiles` states
nothing: no repository consumes it, and its README still presents it as current.

The **UI** type currently has no members. It is retained because a standalone
user interface repository may exist again, and a type with no members is cheaper
than reconstructing one later.

Adding a repository, or changing one's type, is a change to this capability.

#### Scenario: Determining which structure applies

- **WHEN** a contributor needs to know which README structure `gohai` must
  follow
- **THEN** the classification records it as a Go library, without inferring it
  from the repository's contents

#### Scenario: A repository is deprecated

- **WHEN** a repository's README states it is deprecated and its contents have
  moved elsewhere
- **THEN** it is recorded as deprecated and this capability stops binding it,
  regardless of whether it has been archived

#### Scenario: A repository is added

- **WHEN** a new repository is created
- **THEN** it is added to the classification, rather than left to be classified
  by whoever next edits it

### Requirement: Each fact is stated once

A fact SHALL be stated in exactly one file — the one that owns it — and every
other file that needs it SHALL point there rather than restating it.

Ownership follows audience: anything that applies to any contributor belongs in
`CONTRIBUTING.md`; anything specific to agents belongs in `AGENTS.md`; the
README orients a reader and links onward.

A file SHALL NOT summarize another file's content beyond what is needed to say
where to look.

#### Scenario: A convention applies to everyone

- **WHEN** a convention applies to both people and agents, such as the command
  to run before opening a pull request
- **THEN** it is stated in `CONTRIBUTING.md`, and `AGENTS.md` points there
  rather than repeating it

#### Scenario: The same instruction appears twice

- **WHEN** setup instructions appear in both the README and `CONTRIBUTING.md`
- **THEN** the README's copy is replaced by a pointer, because the two will
  otherwise drift and a reader cannot tell which is current

#### Scenario: A new file is added

- **WHEN** a repository adds a file that overlaps an existing one
- **THEN** the overlapping content moves to whichever file owns that audience,
  and the other points to it

### Requirement: Files every repository carries

Every repository SHALL contain `README.md`, `LICENSE`, `AI_POLICY.md`,
`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `AGENTS.md`, `CLAUDE.md`, and
`.mise.toml`.

`.mise.toml` SHALL be committed, never ignored. Its contents vary — a repository
pins the tools it actually uses — but every repository has one, so that
`mise install` provisions a working environment.

A tool a repository invokes SHALL be declared there, including the task runner
itself. A tool that is not declared is supplied by whatever the developer
happens to have installed, which is not the same thing across machines and is
not what continuous integration installs.

#### Scenario: Auditing a repository

- **WHEN** a repository is checked against the standard
- **THEN** the absence of any of those files is a defect

#### Scenario: The task runner is not declared

- **WHEN** a repository runs every check through a task runner but does not
  declare it
- **THEN** that is a defect: the version comes from the developer's system, and
  a formatter check can pass locally and fail in continuous integration on the
  same file

#### Scenario: Repository no longer needs a tool

- **WHEN** a repository stops using a tool, such as dropping bun after moving
  its markdown formatting to mdformat
- **THEN** that tool is removed from `.mise.toml`, which still exists and still
  pins what remains

### Requirement: Every path provisions the same tool version

A repository provisions its tools twice — `.mise.toml` for local work, and setup
actions in its workflows. Both SHALL resolve to the same version.

Where something maintains the version automatically, both paths SHALL pin it and
that mechanism SHALL move both. Where nothing does, both paths SHALL track the
latest release, so they move together.

A version pinned in one path and floating in the other SHALL NOT be used. It
guarantees divergence at the next release, and the divergence surfaces as a
check failing on a file nobody edited.

#### Scenario: Nothing automates the version

- **WHEN** a tool's version is not maintained by any update mechanism, as
  `.mise.toml` is not watched by Dependabot
- **THEN** both paths track the latest release, because a pin nothing bumps is a
  pin that only one side keeps

#### Scenario: An update mechanism covers the tool

- **WHEN** a tool's version is maintained automatically, as action and module
  versions are
- **THEN** both paths pin it, and that mechanism raises both

#### Scenario: A release changes the tool's output

- **WHEN** a formatter release reformats files a check compares against
  committed bytes
- **THEN** the check fails in continuous integration and locally alike, and the
  committed files are reformatted once — rather than one side passing and the
  other failing

#### Scenario: A tool is invoked but not declared

- **WHEN** a repository runs its checks through a tool it does not declare in
  `.mise.toml`
- **THEN** that is a defect: the version comes from whatever the developer has
  installed, and no path can be said to match

### Requirement: A repository no longer in use is archived

A repository that is no longer developed or consumed SHALL state that at the top
of its README and SHALL be archived on GitHub.

Stating deprecation without archiving leaves the repository accepting issues,
pull requests, and pushes, and listed alongside maintained ones. A reader
choosing between repositories sees no difference until they open the README.

#### Scenario: A repository's contents move elsewhere

- **WHEN** a repository's contents are absorbed into another
- **THEN** its README records where they went, and the repository is archived

#### Scenario: Nothing consumes a repository any more

- **WHEN** no repository declares a dependency on it and nothing references its
  files
- **THEN** it is deprecated explicitly, rather than left presenting itself as
  current

#### Scenario: A repository is superseded by a replacement

- **WHEN** an approach is replaced by another, such as task runner definitions
  replaced by a different task runner
- **THEN** the superseded repository names its replacement, so a reader who
  finds it is sent to the current one

### Requirement: Boilerplate files are standardized

`AI_POLICY.md` and `CODE_OF_CONDUCT.md` SHALL be byte-identical across every
repository. They state organization-wide policy, so a repository holding a
variant states policy that is not the organization's.

`CODE_OF_CONDUCT.md` SHALL name a working enforcement contact.

`LICENSE` SHALL be identical across every repository **except** its copyright
year, which SHALL be the year that repository was created. The copyright holder
SHALL be `John Dewey` in every repository.

A repository SHALL NOT express the year as a range.

`AI_POLICY.md` SHALL refer to the organization as `osapi-io`. It SHALL NOT use
the name of any individual repository, and SHALL NOT use `OSAPI`, which is the
name of a repository and reads as that product rather than the organization.

#### Scenario: Repositories created in different years

- **WHEN** one repository was created in 2024 and another in 2026
- **THEN** their `LICENSE` files differ only on the copyright year, and each
  states the year that repository was created

#### Scenario: A repository is modified years later

- **WHEN** a repository created in 2024 is still being changed in 2026
- **THEN** its copyright year remains 2024, and is not updated or expressed as a
  range

#### Scenario: Policy changes

- **WHEN** the AI usage policy is amended
- **THEN** the same file content lands in every repository, with no repository
  carrying a reworded version

#### Scenario: Policy is read in a repository that is not the product

- **WHEN** a contributor reads the AI policy in `gohai` or `nats-client`
- **THEN** it names `osapi-io`, so it is clear the policy is the organization's
  and not one repository's

#### Scenario: Reader checks the code of conduct

- **WHEN** a contributor wants to report a violation
- **THEN** the document names a contact they can actually reach

### Requirement: Only source is tracked

A repository SHALL track only its source, its configuration, and its
documentation. It SHALL NOT track command output, generated artifacts fetched at
build time, or data describing a particular machine.

Where such a file has already been committed, adding it to `.gitignore` is not
sufficient — `.gitignore` suppresses only untracked files, so the file SHALL be
removed from tracking as well.

#### Scenario: Command output is redirected to a file

- **WHEN** a contributor redirects a command's output to a file inside the
  repository
- **THEN** it is not committed, because it describes the machine it ran on
  rather than the project

#### Scenario: Fetched build-time file

- **WHEN** a repository fetches shared configuration at build time
- **THEN** the fetched copy is ignored rather than committed, so it cannot drift
  from its source

#### Scenario: A fetched file is committed because it was modified

- **WHEN** a file that looks fetched is tracked, and its content differs from
  what the fetch retrieves
- **THEN** it is a deliberate override, not a stray, and removing it breaks the
  build. The shared module is changed to take the differing value as
  configuration, and only then is the local copy removed

#### Scenario: Deciding whether a tracked file is stray

- **WHEN** a file is proposed for removal from tracking
- **THEN** its content is read first. A path that matches a generated or fetched
  location is not sufficient evidence that nothing depends on the committed copy

#### Scenario: The file is already tracked

- **WHEN** an ignore rule is added for a file that is already committed
- **THEN** the file is also removed from tracking, because the rule alone has no
  effect on it

### Requirement: Contributing documentation location

Contributing documentation SHALL live in a single `CONTRIBUTING.md` at the
repository root. Prerequisites, setup, conventions, and the pull request
workflow SHALL all be found there.

A repository SHALL NOT split this content across separate contributing and
development documents.

#### Scenario: Contributor looks for setup instructions

- **WHEN** a contributor wants to know how to build and test a repository
- **THEN** the instructions are in `CONTRIBUTING.md` at the root

#### Scenario: Repository publishes a documentation site

- **WHEN** a repository publishes a documentation site that already contains
  contributing or development pages
- **THEN** the root `CONTRIBUTING.md` becomes the single source, and the site's
  page is reduced to a pointer to it rather than being deleted or kept as a
  second copy

#### Scenario: GitHub surfaces the guide

- **WHEN** a contributor opens a new issue or pull request
- **THEN** GitHub links the repository's contributing guide, because it is at
  the location GitHub recognizes

### Requirement: CONTRIBUTING structure

`CONTRIBUTING.md` SHALL open and close with a fixed set of sections, in this
order, with repository-specific sections placed between them:

| Section                 | Position | Content                                 |
| ----------------------- | -------- | --------------------------------------- |
| `## Before you start`   | opening  | Code of Conduct, checking existing work |
| `## Prerequisites`      | opening  | Tools a contributor installs            |
| `## Setup`              | middle   | Fetching shared assets, installing deps |
| `## Project structure`  | middle   | What lives where                        |
| `## Code style`         | middle   | Formatters, linters, and their commands |
| `## Code standards`     | middle   | Conventions a reviewer holds code to    |
| `## Testing`            | middle   | Running tests, and test conventions     |
| *(repository-specific)* | middle   | Anything else, placed after `Testing`   |
| `## Before committing`  | closing  | The command that runs what CI runs      |
| `## Branching`          | closing  | Branch naming                           |
| `## Commit messages`    | closing  | Commit conventions                      |
| `## Submitting a PR`    | closing  | Pull request expectations               |
| `## AI usage`           | closing  | Pointer to `AI_POLICY.md`               |
| `## FAQ`                | closing  | Where to get help                       |

Section names SHALL be taken from this table rather than reworded. A repository
that has nothing to say under a middle section SHALL omit it rather than rename
it or fold its content into a neighbour.

Sections a repository invents for its own subject SHALL follow `Testing`, so
that everything common to repositories of the same type appears in the same
order before anything that is not.

#### Scenario: Two repositories describe the pre-commit check

- **WHEN** two repositories document the command a contributor runs before
  committing
- **THEN** both name that section `## Before committing`, not one using
  `Before committing` and the other `Finishing a change`

#### Scenario: A repository has domain-specific conventions

- **WHEN** a repository has conventions that apply only to it, such as how its
  recipes are written
- **THEN** those appear as a middle section after `Testing`, leaving the common
  sections in place and in order

#### Scenario: The same convention sits under different headings

- **WHEN** one repository documents its function signature rule under
  `Code style` and another documents it under `Code standards`
- **THEN** both move it to `Code standards`, because a reader comparing two
  repositories should not have to discover where each chose to put it

#### Scenario: A repository has no structure worth describing

- **WHEN** a repository is small enough that its layout needs no explanation
- **THEN** it omits `Project structure` rather than inventing a heading or
  padding the section

### Requirement: Agent guidance has no prescribed structure

`AGENTS.md` SHALL NOT have a required section structure. Its content is whatever
is specific to that repository and to agents, and forcing a common skeleton
would produce empty sections.

It SHALL, however, open by directing the reader to `CONTRIBUTING.md`.

#### Scenario: Two repositories need different agent guidance

- **WHEN** one repository needs a planning boundary documented and another needs
  a warning that its artifacts cannot be tested locally
- **THEN** each states only what applies to it, with no shared headings required

### Requirement: Agent guidance is tool-neutral

Agent guidance SHALL live in `AGENTS.md`. `CLAUDE.md` SHALL exist and SHALL
point to it rather than duplicating its content.

`AGENTS.md` SHALL carry only guidance specific to agents, and SHALL reference
`CONTRIBUTING.md` for anything that applies to people as well.

#### Scenario: Convention applies to both audiences

- **WHEN** a convention applies to any contributor, such as running the test
  suite before opening a pull request
- **THEN** it is stated in `CONTRIBUTING.md`, and `AGENTS.md` points there
  rather than restating it

#### Scenario: A different agent tool is adopted

- **WHEN** a tool other than Claude Code is used
- **THEN** the guidance is already tool-neutral and needs no rewrite

### Requirement: README section vocabulary

README sections SHALL be drawn from a fixed vocabulary, each with its emoji, and
SHALL appear in this order when present:

| Section               | Purpose                              |
| --------------------- | ------------------------------------ |
| `## 📦 Install`       | How to obtain the thing              |
| `## ✨ Features`      | What it does, as a table             |
| `## 🎯 Usage`         | How it is used, in prose or commands |
| `## 📋 Examples`      | Pointers to runnable examples        |
| `## 📖 Documentation` | Links to fuller documentation        |
| `## 🤝 Contributing`  | Pointer to `CONTRIBUTING.md`         |
| `## 📄 License`       | The license                          |

A repository SHALL NOT invent a section name for a purpose the vocabulary
already covers.

#### Scenario: Two repositories describe the same thing

- **WHEN** two repositories both document how they are used
- **THEN** both use `## 🎯 Usage`, not one using `Usage` and the other `Examples`

#### Scenario: A section does not apply

- **WHEN** a repository has no runnable examples
- **THEN** it omits `## 📋 Examples` rather than renaming another section

### Requirement: README structure by type

Each repository type SHALL use the section set defined for it.

A **Go library** README SHALL contain `Install`, `Features`, `Examples`,
`Documentation`, `Contributing`, and `License`. It MAY add sections for subject
matter the vocabulary does not cover, placed before `Contributing`.

A **utility** README SHALL contain `Usage`, `Documentation`, `Contributing`, and
`License`.

A **documentation** README SHALL contain `Usage`, `Documentation`,
`Contributing`, and `License`.

A **UI** README SHALL contain `Usage`, `Documentation`, `Contributing`, and
`License`. A UI is run or embedded rather than obtained as a package, so it has
no `Install` section.

The **main product** README is exempt from this requirement. It serves as the
organization's landing page rather than describing a consumable artifact.

#### Scenario: Reading two Go libraries

- **WHEN** a developer reads the README of one Go library and then another
- **THEN** the same sections appear in the same order

#### Scenario: A library needs a subject-specific section

- **WHEN** a Go library documents a concept the vocabulary does not cover
- **THEN** it adds that section before `Contributing`, leaving the standard
  sections in place

### Requirement: Contributing section content

The `## 🤝 Contributing` section SHALL point to `CONTRIBUTING.md` rather than
restating its content.

#### Scenario: Reader follows the contributing section

- **WHEN** a reader reaches the contributing section of any README
- **THEN** it directs them to `CONTRIBUTING.md` for prerequisites, setup,
  conventions, and the pull request workflow

### Requirement: Agent guidance says how to invoke the repository's tools

`AGENTS.md` SHALL state that tools are invoked through the version manager the
repository declares, rather than from the shell's path.

A person working in a repository has that version manager active in their shell,
so the declared version is what they get. An agent runs commands in a shell
without it, and gets whatever happens to be installed — a different version,
silently.

The failure this produces is misleading rather than obvious: a check fails for
the agent and passes for everyone else, on a file nobody changed, and the
difference is invisible in the output.

#### Scenario: An agent runs a formatter

- **WHEN** an agent runs a repository's format check
- **THEN** it invokes it through the version manager, so the result matches what
  continuous integration reports

#### Scenario: An agent sees a failure nobody else sees

- **WHEN** a check fails for an agent and passes in continuous integration on
  the same commit
- **THEN** the version the agent invoked is the first thing to establish, before
  the failure is treated as real

#### Scenario: A repository declares no version manager

- **WHEN** a repository has no version manager configuration
- **THEN** that is a defect under the requirement that a tool a repository
  invokes is declared

### Requirement: Headings are sentence case

Every heading in a repository's contributor documentation SHALL be sentence case
— the first word capitalized, the rest lowercase except proper nouns and
identifiers.

Mixed casing makes two files stating the same thing look like they state
different things, and it is the difference a reader notices first when comparing
them.

#### Scenario: The same section is capitalized two ways

- **WHEN** one repository writes `### Function Signatures` and another writes
  `### Function signatures`
- **THEN** both write `### Function signatures`

#### Scenario: A heading contains an identifier

- **WHEN** a heading names a tool or a type, such as the CLI or a Go package
- **THEN** that word keeps its own capitalization, and the rest of the heading
  is lowercase

### Requirement: A repository states in full the conventions it is held to

A repository's `CONTRIBUTING.md` SHALL contain the conventions its contributors
are held to, in full. A reference to guidance held in another repository SHALL
NOT stand in place of stating them.

A contributor reading a pull request in a browser, a contributor working
offline, and an agent with a single checkout each see only this repository. A
convention they cannot read is one they cannot follow.

Where a convention is common to several repositories, the repositories SHALL
state it identically, so that a difference in wording means a difference in
rule.

#### Scenario: An agent works in one checkout

- **WHEN** an agent is asked to write code in a repository, with no access to
  any other
- **THEN** the conventions binding that code are readable from within that
  repository

#### Scenario: A convention is common to several repositories

- **WHEN** the same convention binds four repositories
- **THEN** each states it, in the same words, rather than one stating it and the
  others naming where to find it

#### Scenario: A shared convention changes

- **WHEN** a convention common to several repositories is amended
- **THEN** every repository that states it is updated in the same change, so
  none is left stating the superseded rule

### Requirement: A rule a tool enforces is not restated as prose

Where a tool's configuration determines a rule, that configuration SHALL be the
statement of record, and contributor documentation SHALL name where it lives
rather than reproducing what it says.

Prose describing a tool's settings is maintained by hand and checked by nothing,
so it drifts from the configuration while continuing to read as authoritative.

#### Scenario: The linter set is documented

- **WHEN** contributor documentation describes which linters run
- **THEN** it names the configuration file rather than listing them, because a
  copied list goes stale the first time the configuration changes

#### Scenario: Prose and configuration disagree

- **WHEN** documentation and a tool's configuration state different rules
- **THEN** the configuration is what runs, and the prose is removed rather than
  corrected
