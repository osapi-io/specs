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
