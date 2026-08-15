## Purpose

Defines which files an osapi-io repository carries and how its README is
structured, so that repositories of the same kind read alike and a new
repository can be created without imitating an arbitrary existing one.

## ADDED Requirements

### Requirement: Repository types

Every repository SHALL be one of four types, and its type SHALL determine its
README structure.

- **Go library** — a package other repositories import, optionally with a CLI
  wrapping it.
- **Main product** — the deployable service the organization exists to build.
- **Utility** — shared assets consumed by other repositories rather than
  imported as code.
- **Documentation** — specifications and design records.

#### Scenario: Classifying a new repository

- **WHEN** a repository is created to hold a Go package other repositories
  import
- **THEN** it is a Go library and follows the Go library README structure

#### Scenario: Types with different audiences

- **WHEN** a reader opens a utility repository's README
- **THEN** it explains how to consume the assets, not how to import a package

### Requirement: Files every repository carries

Every repository SHALL contain `README.md`, `LICENSE`, `AI_POLICY.md`,
`CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `AGENTS.md`, and `CLAUDE.md`.

#### Scenario: Auditing a repository

- **WHEN** a repository is checked against the standard
- **THEN** the absence of any of those files is a defect

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
