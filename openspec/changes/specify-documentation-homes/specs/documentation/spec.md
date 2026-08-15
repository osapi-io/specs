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

### Requirement: Design records live in the corpus

A design record — what is being built, why, what alternatives were rejected —
SHALL be a change in the specification corpus, not a document in a repository's
`docs/`.

Planning documents already committed to a repository are historical and SHALL be
left in place. A repository SHALL NOT add new ones.

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
