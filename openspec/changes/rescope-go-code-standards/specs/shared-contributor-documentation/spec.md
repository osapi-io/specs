## Purpose

Defines how contributor guidance common to several repositories is distributed,
so that each repository holds a complete guide on disk while one source governs
the shared part of its content.

## ADDED Requirements

### Requirement: A shared convention has one source

A convention that binds more than one repository SHALL be written in one place
and distributed from there. It SHALL NOT be maintained as an independent copy in
each repository that follows it.

Independent copies diverge without anything reporting it, and each reader
believes the copy in front of them is current.

#### Scenario: A convention changes

- **WHEN** a convention that binds several repositories is amended
- **THEN** it is amended once and redistributed, rather than edited separately
  in each repository

#### Scenario: Copies have already diverged

- **WHEN** two repositories state the same convention differently
- **THEN** neither is authoritative, and the divergence is resolved by
  establishing the single source rather than by choosing the copy that looks
  more current

### Requirement: A repository holds the guidance it is bound by

A repository SHALL contain the full text of the conventions its contributors are
held to, readable without fetching another repository.

A pointer to guidance stored elsewhere SHALL NOT be the only statement of a
convention. A reader working offline, an agent with no second checkout, and a
reviewer reading a pull request in a browser each see only this repository.

#### Scenario: A contributor reads the guide

- **WHEN** a contributor opens a repository's contributing guide
- **THEN** the conventions they must follow are present in it, rather than named
  and left to be retrieved

#### Scenario: An agent works in a single checkout

- **WHEN** an agent works in one repository with no access to another
- **THEN** the conventions binding that repository are readable from within it

### Requirement: Distributed content is fetched, not committed

Shared contributor documentation SHALL reach a repository by the same mechanism
as its other shared assets, and the fetched copy SHALL NOT be committed.

A committed copy is indistinguishable from a local edit, so the next fetch
either overwrites deliberate changes or is not run at all.

#### Scenario: A repository is set up

- **WHEN** a contributor prepares a fresh checkout
- **THEN** the same command that retrieves the repository's other shared assets
  retrieves its shared documentation

#### Scenario: A fetched file is edited locally

- **WHEN** a repository needs shared guidance to differ
- **THEN** the difference is expressed where the source can produce it, rather
  than by editing the fetched copy

### Requirement: A rule a tool enforces is not also written as prose

Where a tool's configuration determines a convention, that configuration SHALL
be the statement of record, and the convention SHALL NOT be restated as prose
that can disagree with it.

Prose describing a tool's settings is maintained by hand and checked by nobody,
so it drifts from the configuration while continuing to read as authoritative.

#### Scenario: A linter set is documented

- **WHEN** contributor documentation lists which linters run
- **THEN** it names where the configuration lives rather than reproducing the
  list, because a reproduced list goes stale the first time the configuration
  changes

#### Scenario: Prose and configuration disagree

- **WHEN** documentation and a tool's configuration state different rules
- **THEN** the configuration is what runs, and the prose is removed rather than
  corrected
