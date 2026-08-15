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
| `osapi-ui`           | UI            |

`osapi-sdk` and `osapi-io-taskfiles` are deprecated and outside this capability.
Adding a repository, or changing one's type, is a change to this capability.

#### Scenario: Determining which structure applies

- **WHEN** a contributor needs to know which README structure `gohai` must
  follow
- **THEN** the classification records it as a Go library, without inferring it
  from the repository's contents

#### Scenario: A repository is added

- **WHEN** a new repository is created
- **THEN** it is added to the classification, rather than left to be classified
  by whoever next edits it

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

### Requirement: Boilerplate files are byte-identical

`LICENSE`, `AI_POLICY.md`, and `CODE_OF_CONDUCT.md` SHALL be byte-identical
across every repository. They state organization-wide policy, so a repository
holding a variant states policy that is not the organization's.

`LICENSE` SHALL read `Copyright (c) 2026 John Dewey`. `CODE_OF_CONDUCT.md` SHALL
name a working enforcement contact.

`AI_POLICY.md` SHALL refer to the organization as `osapi-io`. It SHALL NOT use
the name of any individual repository, and SHALL NOT use `OSAPI`, which is the
name of a repository and reads as that product rather than the organization.

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
