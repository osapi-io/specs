## Purpose

Defines which files an osapi-io repository carries and how its README is
structured, so that repositories of the same kind read alike and a new
repository can be created without imitating an arbitrary existing one.

## ADDED Requirements

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

#### Scenario: Auditing a repository

- **WHEN** a repository is checked against the standard
- **THEN** the absence of any of those files is a defect

#### Scenario: Repository no longer needs a tool

- **WHEN** a repository stops using a tool, such as dropping bun after moving
  its markdown formatting to mdformat
- **THEN** that tool is removed from `.mise.toml`, which still exists and still
  pins what remains

### Requirement: Tools whose output is checked are pinned

`.mise.toml` SHALL pin a version for every tool whose output a check compares
against a committed file. `latest` SHALL NOT be used for such a tool.

A floating version makes the toolchain an untracked input to CI. The check
compares committed bytes against bytes the tool generates, so a release that
changes the tool's output turns CI red with no commit touching the repository,
across every branch and on the default branch at once.

Dependabot raises these pins, so the version is still maintained — as a change
with a pull request behind it, rather than silently at the next run.

#### Scenario: A formatter release changes its output

- **WHEN** a formatter that a check runs in check mode is released with altered
  formatting
- **THEN** the pin holds the old version until a pull request raises it, rather
  than every branch failing at once

#### Scenario: A tool's output is never compared

- **WHEN** a tool only provisions or runs things, and no check compares its
  output against a committed file
- **THEN** it may float, because a release cannot invalidate a committed file

#### Scenario: Pinning is inconsistent across repositories

- **WHEN** language runtimes are pinned but the tools that format and lint float
- **THEN** the tools are pinned too, because those are the ones whose output is
  compared

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
| *(repository-specific)* | middle   | Setup, conventions, workflow            |
| `## Before committing`  | closing  | The command that runs what CI runs      |
| `## Branching`          | closing  | Branch naming                           |
| `## Commit messages`    | closing  | Commit conventions                      |
| `## Submitting a PR`    | closing  | Pull request expectations               |
| `## AI usage`           | closing  | Pointer to `AI_POLICY.md`               |
| `## FAQ`                | closing  | Where to get help                       |

Section names SHALL be taken from this table rather than reworded. The middle
varies by repository, because what a contributor needs to know differs.

#### Scenario: Two repositories describe the pre-commit check

- **WHEN** two repositories document the command a contributor runs before
  committing
- **THEN** both name that section `## Before committing`, not one using
  `Before committing` and the other `Finishing a change`

#### Scenario: A repository has domain-specific conventions

- **WHEN** a repository has conventions that apply only to it, such as how its
  recipes are written
- **THEN** those appear as a middle section, leaving the opening and closing
  sections in place

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
