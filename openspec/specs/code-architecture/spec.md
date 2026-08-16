# code-architecture Specification

## Purpose

Defines how Go code is arranged within an osapi-io repository, what test
coverage is expected, and which toolchain versions are supported, so that
consistency which currently exists by copying is held by a rule.

## Requirements

### Requirement: Package layout

A repository SHALL place code according to who may import it:

| Directory   | Contains                                                  |
| ----------- | --------------------------------------------------------- |
| `pkg/`      | The public API other repositories import                  |
| `internal/` | Code this repository alone uses, enforced by the compiler |
| `cmd/`      | Command-line entry points                                 |

A repository SHALL only carry the directories it needs. A library with no
command-line interface has no `cmd/`; a library with nothing private has no
`internal/`.

#### Scenario: Library gains a CLI

- **WHEN** a library adds a command-line wrapper over its public API
- **THEN** the commands go in `cmd/`, and the library remains the product in
  `pkg/`

#### Scenario: Helper is not part of the API

- **WHEN** code exists to support the public API but should not be imported by
  other repositories
- **THEN** it goes in `internal/`, where the compiler enforces the boundary

### Requirement: Coverage target

A repository containing Go code SHALL target 100% test coverage, and SHALL
declare that target both in its coverage service configuration and in the recipe
that checks coverage locally. The two declarations SHALL state the same number,
and each SHALL carry a comment naming the other.

What is excluded from coverage SHALL be defined in exactly one place. The
excluded files SHALL be removed from the coverage profile before it is uploaded,
so the local check and the coverage service measure the same set rather than
each applying their own exclusions.

Generated code SHALL be excluded rather than counted or waived.

A coverage check SHALL fail when coverage is below the target. Reporting the
number without failing does not satisfy this requirement.

The check MAY read a tool's rounded summary rather than computing from the
profile. Rounding to one decimal place admits about 0.05% of tolerance, which is
small enough that a regression worth catching is still caught, and a target
below 100% makes the tolerance explicit rather than hidden.

A repository MAY declare a target below the organization-wide one. That target
SHALL be the level the repository currently holds, so it cannot decay.

Where the shortfall is untested code, the target SHALL be raised as that code is
covered. Where it is code that cannot be reached — a guard kept against a future
change that would otherwise fail silently, or an error branch the underlying
library never returns — the lower target is the correct one and SHALL NOT be
treated as debt. Making such code reachable to satisfy a number defeats the
reason it exists.

#### Scenario: Coverage falls below target

- **WHEN** a change lowers coverage below the declared target
- **THEN** the check fails, rather than the target being adjusted to accommodate
  the change

#### Scenario: A shortfall smaller than the rounding

- **WHEN** coverage falls by less than the summary tool's rounding
- **THEN** the check does not fail, and that is accepted: the tolerance is
  bounded and known, and the alternative is arithmetic in a shared recipe every
  repository runs

#### Scenario: Coverage is short only by unreachable guards

- **WHEN** every uncovered statement is a deliberate guard that cannot currently
  execute, and each says so
- **THEN** the repository declares the level it holds rather than adding tests
  that force the guard to run, because a guard exercised by a seam built for it
  no longer guards anything

#### Scenario: The two declarations disagree

- **WHEN** one declaration is raised or lowered and the other is not
- **THEN** that is a defect, and the comment in each names the other so whoever
  edits one knows to edit both

#### Scenario: An exclusion is added

- **WHEN** a file is added to the exclusion list
- **THEN** it disappears from both the local number and the service's number,
  because both read a profile the exclusions were already applied to

#### Scenario: The uploaded profile is chosen automatically

- **WHEN** a coverage service discovers coverage files itself rather than being
  given one
- **THEN** the workflow names the filtered profile explicitly, because
  discovering an unfiltered profile reports a different number for the same
  commit

### Requirement: Supported Go versions

A repository SHALL support the two most recent major Go versions, and SHALL
declare a minimum in `go.mod` consistent with that.

#### Scenario: A new major Go version is released

- **WHEN** Go publishes a new major version
- **THEN** support for the oldest of the three may be dropped, and `go.mod`
  updated accordingly

### Requirement: Release tooling

A repository that publishes a binary SHALL use goreleaser, configured in
`.goreleaser.yaml`, so that releases are produced the same way everywhere.

#### Scenario: Repository publishes no binary

- **WHEN** a repository produces no distributable artifact
- **THEN** it carries no release configuration

### Requirement: The pre-commit recipe fixes everything CI checks

A repository's `ready` recipe SHALL address every check its continuous
integration runs. A contributor who runs it and commits SHALL NOT then fail on
something the recipe could have fixed.

#### Scenario: CI checks a format the recipe does not fix

- **WHEN** continuous integration verifies the formatting of a file type
- **THEN** `ready` formats that file type, so running it before committing is
  sufficient

#### Scenario: A new check is added to CI

- **WHEN** a check is added to continuous integration
- **THEN** `ready` is extended in the same change, or the check is one nothing
  local can fix

### Requirement: Continuous integration is consistent by type

Repositories of the same type SHALL run the same set of workflows, and those
workflows SHALL differ only where the repository's build genuinely requires it.

Action and dependency versions are maintained by Dependabot. This capability
SHALL NOT name a version, because the current one changes without anyone
deciding it. What a repository SHALL do is keep its update queue moving — a
backlog of unmerged bumps is how repositories that should match stop matching.

#### Scenario: Repositories differ only by dependency version

- **WHEN** one repository's workflows pin older versions than another's
- **THEN** the difference is an unmerged update queue rather than a deliberate
  choice, and the queue is worked rather than the difference documented

#### Scenario: A version is proposed as a requirement

- **WHEN** someone proposes recording a specific action or module version here
- **THEN** it is declined, because Dependabot moves it and the corpus would be
  wrong by the next bump

#### Scenario: A build genuinely requires different infrastructure

- **WHEN** a repository must build on a different runner, or needs different
  credentials, than its siblings
- **THEN** its workflow differs in those respects and matches in all others

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
