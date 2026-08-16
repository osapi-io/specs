## Purpose

Records what a repository documents locally and what the specification corpus
holds instead, so that a document has one home and a reader knows which place to
look.

## ADDED Requirements

### Requirement: What a repository documents

A repository's `docs/` SHALL hold documentation describing that repository:
reference material for what it contains, how-to guides for working in it, and
user-facing documentation for what it does.

It SHALL NOT hold requirements binding other repositories. Those are
capabilities in the corpus.

The test SHALL be applied to each document, not to the directory holding it. A
directory may contain documents of both kinds.

#### Scenario: Reference material for a component

- **WHEN** a repository contains many components of the same kind, each with its
  own fields, options, or behavior
- **THEN** each is documented in that repository, next to the code that
  implements it

#### Scenario: A guide for working in the repository

- **WHEN** a repository has a procedure for adding a component or validating
  output
- **THEN** it is documented in that repository, and `CONTRIBUTING.md` points to
  it rather than restating it

#### Scenario: A rule binds more than one repository

- **WHEN** a rule applies to repositories beyond the one documenting it
- **THEN** it becomes a capability in the corpus, and the repositories point at
  it

#### Scenario: One directory holds documents of both kinds

- **WHEN** a directory contains both a document stating cross-repository
  constraints and a document describing local packages
- **THEN** each is placed by what it says, and the directory is not moved whole

### Requirement: Requirements live in the corpus, descriptions in the repository

Documentation SHALL be placed by what it does. Text that constrains a future
decision — a rule work is held to, a principle that must be followed, a
condition for accepting a change — is a requirement and SHALL be a capability in
the corpus. Text that reports what the code currently is SHALL stay in the
repository that holds the code.

The number of repositories a requirement binds SHALL NOT determine where it
lives. A rule binding one repository is still a rule, and the corpus is where
rules are kept.

#### Scenario: A rule decides whether work is accepted

- **WHEN** a document lists conditions that must hold before a contribution is
  complete, and work not meeting them is sent back
- **THEN** those conditions are a capability in the corpus, because they are
  requirements regardless of how many repositories they bind

#### Scenario: A design principle produced code elsewhere

- **WHEN** a principle recorded in one repository is the reason a second
  repository's client is generated rather than hand-written
- **THEN** the principle is a capability in the corpus, because a change to it
  is a change to both repositories

#### Scenario: An interface contract has consumers

- **WHEN** a repository documents the rules its API surface follows, and other
  repositories are built against that surface
- **THEN** those rules are a capability in the corpus, so a consumer can be held
  to them

#### Scenario: A document mixes requirements with description

- **WHEN** a document opens with the principles a subsystem follows and then
  describes how that subsystem is currently built
- **THEN** the principles move to the corpus and the description stays in the
  repository

#### Scenario: Describing what the code currently does

- **WHEN** a document maps packages, layers, or request paths inside one
  repository
- **THEN** it stays in that repository, because rewriting it as requirements
  produces a corpus that goes stale on every refactor

#### Scenario: A walkthrough implements a rule held in the corpus

- **WHEN** a repository documents the steps for doing work the corpus has
  requirements about
- **THEN** the walkthrough stays in the repository and points at the capability,
  rather than restating the rules where they can drift

### Requirement: Design records live in the corpus

A design record — what is being built, why, what alternatives were rejected —
SHALL be a change in the specification corpus, not a document in a repository's
`docs/`.

A repository SHALL NOT contain planning documents. Keeping them in a repository
was a mistake: they duplicate what the corpus archive holds, they are never
updated once the work lands, and a reader cannot tell which of the two places is
current. Existing ones are removed; git history retains them.

#### Scenario: New work is designed

- **WHEN** work is proposed that changes how something behaves
- **THEN** the proposal, design, and tasks are a change in the corpus, and are
  archived there when the work completes

#### Scenario: A repository holds planning documents

- **WHEN** a repository contains planning documents
- **THEN** they are removed, because the corpus archive is where design records
  live and two homes for the same document means neither is authoritative

#### Scenario: Someone looks for why a decision was made

- **WHEN** a reader wants to know why something is the way it is
- **THEN** the corpus archive holds the reasoning, in the change that made it

### Requirement: Documentation is indexed

A repository's `docs/` SHALL contain a `README.md` listing what is there and
what each part covers.

#### Scenario: A reader opens the documentation directory

- **WHEN** a reader opens `docs/`
- **THEN** an index tells them what each directory and document covers, rather
  than requiring them to open each one

#### Scenario: Documentation is published as a site

- **WHEN** a repository publishes its documentation as a site with its own
  navigation
- **THEN** that navigation is the index, and no second one is maintained

### Requirement: The corpus has an entry point

The corpus SHALL contain a document naming every capability and what each one
covers, so a reader arriving without knowing which capability holds what can
find their way in.

That document SHALL state what the corpus is: the rules the organization's
software is held to, and where the reasoning behind each rule is kept. It SHALL
NOT describe the corpus as a description of how the software behaves, because
descriptions of current behavior stay in the repositories that hold the code.

#### Scenario: A reader arrives at the corpus

- **WHEN** someone opens the corpus without knowing which capability governs the
  work they are doing
- **THEN** an entry point names each capability and what it covers, rather than
  requiring every capability to be opened

#### Scenario: A capability is added

- **WHEN** a change adds a capability to the corpus
- **THEN** the entry point names it, so the map does not fall behind what it
  maps

#### Scenario: A reader wants to know why a rule exists

- **WHEN** a requirement's reasoning matters more than its wording
- **THEN** the entry point says the reasoning is in the archived change that
  introduced it, rather than leaving the archive to be discovered

### Requirement: A capability says what it is for before it constrains

A capability SHALL open by stating what it governs and why that ground needs
governing.

A reader who does not already know the domain SHALL be able to learn what the
capability is about from that opening, without reconstructing it from the
requirements below.

#### Scenario: A capability is read by someone new to the domain

- **WHEN** a contributor opens a capability governing a subsystem they have not
  worked in
- **THEN** its opening explains what the subsystem is for, so the requirements
  that follow are read with the reason for them in view

### Requirement: Documentation organisation is the repository's own

The names and shape of directories inside `docs/` SHALL be chosen by the
repository, according to what it documents.

A repository SHALL NOT be required to adopt another repository's structure for
subject matter it does not have.

#### Scenario: Two repositories document different subjects

- **WHEN** one repository documents collectors and another documents operations
- **THEN** each names its directory for what it holds, and neither is
  restructured to match the other

#### Scenario: A repository has little to document

- **WHEN** a repository has few documents
- **THEN** it keeps them at the top of `docs/` rather than creating directories
  to mirror a larger repository
