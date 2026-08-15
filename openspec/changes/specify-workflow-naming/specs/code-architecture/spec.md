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

#### Scenario: Two repositories check the same thing

- **WHEN** two repositories run the same check
- **THEN** the workflow has the same file name and the same `name` in both
