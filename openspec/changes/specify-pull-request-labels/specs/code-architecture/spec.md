## ADDED Requirements

### Requirement: Labels match the kinds of file a repository holds

A repository SHALL define a pull request label for each kind of file it holds,
and SHALL NOT define a label for a kind it holds none of.

A label matching nothing is never applied, so a reader learns nothing from its
absence. A kind with no label is invisible on every pull request that changes
it.

Label names SHALL be shared across repositories: the same kind of file carries
the same label everywhere, so a label means one thing across the organization.

#### Scenario: A repository holds a kind nothing labels

- **WHEN** a repository contains a kind of file no label matches, such as its
  justfiles
- **THEN** a label for that kind is added, using the name other repositories use

#### Scenario: A kind leaves a repository

- **WHEN** the last file of a labelled kind is removed, such as deleting the
  module a label was written for
- **THEN** the label is removed in the same change

#### Scenario: A repository never had the kind

- **WHEN** a repository carries a label for a language or tool it does not use
- **THEN** the label is removed, because it can only ever mislead

### Requirement: A label names one kind, without overlap

Each label SHALL match a distinct set of files. Two labels SHALL NOT both match
the same file as a matter of course.

Where a broad label subsumes a narrow one, every change to the narrow kind
carries both, and neither tells a reader anything the other did not.

A label SHALL be prefixed by what it classifies, and the prefixes in use SHALL
be consistent across repositories.

#### Scenario: A broad label subsumes a narrow one

- **WHEN** one label matches every file of a format and another matches a subset
  of the same format in a particular directory
- **THEN** the narrower one excludes what the broader one already covers, or one
  of them is removed

#### Scenario: Prefixes disagree

- **WHEN** labels within a repository use different prefixes for the same sort
  of classification
- **THEN** they are brought onto one prefix, so a reader can predict the name

### Requirement: Labels classify by purpose, not only by format

Where files of one format serve different purposes, labels SHALL distinguish
those purposes.

A single label covering every file of a format tells a reader only what the
files are made of. Markdown in these repositories is a README, a contributing
guide, agent guidance, a policy, and reference documentation — five audiences,
one format. A label that cannot tell them apart is not worth applying.

Files that carry no extension SHALL still be labelled where they have a purpose,
so that a licence or an ignore file is not invisible because of its name.

#### Scenario: One format serves several audiences

- **WHEN** a repository holds markdown for readers, contributors, agents, and
  policy
- **THEN** each has its own label, so a pull request touching agent guidance is
  distinguishable from one touching reference documentation

#### Scenario: A file has no extension

- **WHEN** a repository holds a file with no extension, such as a licence
- **THEN** it is matched by name, rather than left unlabelled

#### Scenario: Configuration is labelled as its format

- **WHEN** a repository's linter, release, and coverage configuration are all
  matched only by their file format
- **THEN** a label for toolchain configuration is added, because a change to how
  the repository is built is not the same as a change to any other file in that
  format

#### Scenario: A purpose has one file today

- **WHEN** a purpose is served by a single file, such as agent guidance
- **THEN** it still gets a label, because the label describes the purpose and
  the number of files serving it will change
