## ADDED Requirements

### Requirement: A workflow is named for what it checks

A workflow's file name and its `name` SHALL state what it checks, and SHALL be
the same across repositories checking the same thing.

A workflow that outlives the tool it was written for keeps a name describing
work it no longer does, and a reader scanning a list of failed checks cannot
tell which one failed.

A workflow SHALL NOT bundle checks of unrelated subjects under one name. Where a
repository checks two subjects, it runs two workflows, so a failure names the
subject that failed.

#### Scenario: The tool a workflow runs is replaced

- **WHEN** a workflow's check changes from one tool to another, such as markdown
  formatting moving between formatters
- **THEN** the workflow is renamed in the same change, rather than keeping the
  name of the tool it no longer runs

#### Scenario: A repository checks two subjects

- **WHEN** a repository formats both a documentation site and markdown outside
  it
- **THEN** each has its own workflow, so a failed check names which

#### Scenario: Several workflows cover one subject

- **WHEN** a repository has more than one workflow for the same subject, such as
  building, deploying, and linting a documentation site
- **THEN** all of them name that subject the same way, so they read as a set
  rather than as unrelated jobs

#### Scenario: Two repositories check the same thing

- **WHEN** two repositories run the same check
- **THEN** the workflow has the same file name and the same `name` in both

### Requirement: Workflow names follow one form

A workflow file SHALL be named in kebab case, stating its subject and, where the
subject has more than one workflow, the action: `markdown-lint.yml`,
`docusaurus-build.yml`.

Its `name` SHALL be title case and SHALL name the same subject and action as the
file. It SHALL NOT be a sentence, and SHALL NOT name a destination, a vendor, or
a standard in place of the subject.

An organization whose boilerplate is identical everywhere should not have
workflow names that differ in form from repository to repository, or from each
other within a repository.

#### Scenario: A name is written as a sentence

- **WHEN** a workflow is named `Mark stale issues and pull requests`
- **THEN** it is shortened to the subject in title case, matching its file name

#### Scenario: A name describes where rather than what

- **WHEN** a workflow that builds and publishes a site is named for the hosting
  service it publishes to
- **THEN** it is named for the subject it acts on, because the hosting service
  can change without the workflow's purpose changing

#### Scenario: File and name disagree

- **WHEN** a file and its `name` describe the work differently
- **THEN** both are brought onto the same subject, with the `name` free to spell
  out what the file abbreviates
