## MODIFIED Requirements

### Requirement: CONTRIBUTING structure

`CONTRIBUTING.md` SHALL open and close with a fixed set of sections, in this
order, with repository-specific sections placed between them:

| Section                 | Position | Content                                 |
| ----------------------- | -------- | --------------------------------------- |
| `## Before you start`   | opening  | Code of Conduct, checking existing work |
| `## Prerequisites`      | opening  | Tools a contributor installs            |
| `## Setup`              | middle   | Fetching shared assets, installing deps |
| `## Project structure`  | middle   | What lives where                        |
| `## Code style`         | middle   | Formatters, linters, and their commands |
| `## Code standards`     | middle   | Conventions a reviewer holds code to    |
| `## Testing`            | middle   | Running tests, and test conventions     |
| *(repository-specific)* | middle   | Anything else, placed after `Testing`   |
| `## Before committing`  | closing  | The command that runs what CI runs      |
| `## Branching`          | closing  | Branch naming                           |
| `## Commit messages`    | closing  | Commit conventions                      |
| `## Submitting a PR`    | closing  | Pull request expectations               |
| `## AI usage`           | closing  | Pointer to `AI_POLICY.md`               |
| `## FAQ`                | closing  | Where to get help                       |

Section names SHALL be taken from this table rather than reworded. A repository
that has nothing to say under a middle section SHALL omit it rather than rename
it or fold its content into a neighbour.

Sections a repository invents for its own subject SHALL follow `Testing`, so
that everything common to repositories of the same type appears in the same
order before anything that is not.

#### Scenario: Two repositories describe the pre-commit check

- **WHEN** two repositories document the command a contributor runs before
  committing
- **THEN** both name that section `## Before committing`, not one using
  `Before committing` and the other `Finishing a change`

#### Scenario: A repository has domain-specific conventions

- **WHEN** a repository has conventions that apply only to it, such as how its
  recipes are written
- **THEN** those appear as a middle section after `Testing`, leaving the common
  sections in place and in order

#### Scenario: The same convention sits under different headings

- **WHEN** one repository documents its function signature rule under
  `Code style` and another documents it under `Code standards`
- **THEN** both move it to `Code standards`, because a reader comparing two
  repositories should not have to discover where each chose to put it

#### Scenario: A repository has no structure worth describing

- **WHEN** a repository is small enough that its layout needs no explanation
- **THEN** it omits `Project structure` rather than inventing a heading or
  padding the section

## ADDED Requirements

### Requirement: Headings are sentence case

Every heading in a repository's contributor documentation SHALL be sentence case
— the first word capitalized, the rest lowercase except proper nouns and
identifiers.

Mixed casing makes two files stating the same thing look like they state
different things, and it is the difference a reader notices first when comparing
them.

#### Scenario: The same section is capitalized two ways

- **WHEN** one repository writes `### Function Signatures` and another writes
  `### Function signatures`
- **THEN** both write `### Function signatures`

#### Scenario: A heading contains an identifier

- **WHEN** a heading names a tool or a type, such as the CLI or a Go package
- **THEN** that word keeps its own capitalization, and the rest of the heading
  is lowercase

### Requirement: A repository states in full the conventions it is held to

A repository's `CONTRIBUTING.md` SHALL contain the conventions its contributors
are held to, in full. A reference to guidance held in another repository SHALL
NOT stand in place of stating them.

A contributor reading a pull request in a browser, a contributor working
offline, and an agent with a single checkout each see only this repository. A
convention they cannot read is one they cannot follow.

Where a convention is common to several repositories, the repositories SHALL
state it identically, so that a difference in wording means a difference in
rule.

#### Scenario: An agent works in one checkout

- **WHEN** an agent is asked to write code in a repository, with no access to
  any other
- **THEN** the conventions binding that code are readable from within that
  repository

#### Scenario: A convention is common to several repositories

- **WHEN** the same convention binds four repositories
- **THEN** each states it, in the same words, rather than one stating it and the
  others naming where to find it

#### Scenario: A shared convention changes

- **WHEN** a convention common to several repositories is amended
- **THEN** every repository that states it is updated in the same change, so
  none is left stating the superseded rule

### Requirement: A rule a tool enforces is not restated as prose

Where a tool's configuration determines a rule, that configuration SHALL be the
statement of record, and contributor documentation SHALL name where it lives
rather than reproducing what it says.

Prose describing a tool's settings is maintained by hand and checked by nothing,
so it drifts from the configuration while continuing to read as authoritative.

#### Scenario: The linter set is documented

- **WHEN** contributor documentation describes which linters run
- **THEN** it names the configuration file rather than listing them, because a
  copied list goes stale the first time the configuration changes

#### Scenario: Prose and configuration disagree

- **WHEN** documentation and a tool's configuration state different rules
- **THEN** the configuration is what runs, and the prose is removed rather than
  corrected
