# module-dependencies Specification

## Purpose

Records how osapi-io repositories depend on one another and how those
dependencies are declared, so that a description of the system can be checked
against what the code actually does.

## Requirements

### Requirement: Module path matches repository location

A Go module SHALL declare a path matching the repository that holds it.

#### Scenario: Consumer resolves a dependency

- **WHEN** a developer runs `go get` using the repository's location
- **THEN** the module resolves, because its declared path is that location

#### Scenario: Repository moves between owners

- **WHEN** a repository moves to a different organization
- **THEN** its module path is updated to match, and consumers are updated in the
  same change

### Requirement: A repository's declared home matches where it lives

A repository SHALL NOT name an owner, project, or location other than its own.
This covers every place the repository states where it lives — the module path,
site deployment configuration, and links to the project's own issue tracker,
discussions, or releases.

A module path is checked by the toolchain and fails loudly when wrong. These
other declarations fail quietly: the build passes, the site publishes, and the
link resolves to somebody else's project.

#### Scenario: A repository moves between owners

- **WHEN** a repository moves to a different organization
- **THEN** every declaration of where it lives is updated, not only the ones a
  compiler checks

#### Scenario: Site deployment names a different organization

- **WHEN** a documentation site declares the organization it deploys under
- **THEN** that organization is the one hosting it, rather than a former owner
  the published URL contradicts

#### Scenario: A link points at the author's other project

- **WHEN** documentation links to the project's issue tracker, discussions, or
  releases
- **THEN** the link names this repository, not one it was copied from

### Requirement: Dependencies are declared by version

A repository SHALL depend on another repository by a released or pinned version
in `go.mod`.

A `replace` directive pointing outside the repository that holds it MAY be used
locally while developing against an unreleased change in a sibling repository.
It SHALL NOT be merged.

A `replace` directive pointing within the repository that holds it is a
different thing and SHALL be merged. A nested module — an example or tool module
under a repository that already declares its own — resolves its parent through
`replace` so it compiles against the working tree rather than a published
version. Without it the example cannot demonstrate the code it ships beside.

The distinction is direction, not mechanism: a `replace` crossing a repository
boundary substitutes for a version that should be pinned; one staying inside it
is how a nested module refers to its own repository.

#### Scenario: Consumer builds without the sibling checked out

- **WHEN** a repository is built by someone who has not cloned its sibling
  repositories
- **THEN** the build resolves every dependency from the module proxy

#### Scenario: An example module ships beside the code it demonstrates

- **WHEN** a repository carries a nested example module
- **THEN** that module declares a `replace` pointing at its own repository root,
  and it is merged, because the example must build against the source it sits
  next to

#### Scenario: Developing against an unreleased sibling change

- **WHEN** a developer adds a `replace` directive to test against a sibling
  repository's unmerged branch
- **THEN** it is removed and the dependency repinned to the released version
  before the change is merged

#### Scenario: The sibling change merges first

- **WHEN** the sibling change is merged and published
- **THEN** the dependent repository pins the new version, and the `replace`
  directive that stood in for it is gone

### Requirement: Documented relationships match declared ones

Documentation describing a dependency between repositories SHALL match what
`go.mod` declares. A repository SHALL NOT describe itself as consumed by, or
consuming, a repository it has no declared dependency on.

Documentation describing tooling SHALL match what the repository installs and
declares. A repository SHALL NOT name a library, tool, or directory it does not
use.

A repository SHALL NOT describe another repository's choices. Those go stale
without anyone editing the file that states them.

#### Scenario: A relationship is planned but not built

- **WHEN** a repository is intended to be used by another but is not yet
- **THEN** its documentation says so, rather than describing the intended state
  as current

#### Scenario: A dependency is removed

- **WHEN** a repository stops depending on another
- **THEN** the documentation describing that relationship is removed in the same
  change

#### Scenario: A library is replaced

- **WHEN** a repository migrates from one library to another
- **THEN** its documentation and its dependency installation are updated in the
  same change, so neither names the library it left

#### Scenario: Documentation points at a directory

- **WHEN** documentation tells a reader where something lives
- **THEN** that path exists, or the documentation says it does not yet

#### Scenario: One repository describes another's tooling

- **WHEN** a repository's documentation states which library a different
  repository uses
- **THEN** the claim is removed, because nothing updates it when that repository
  changes

### Requirement: A cross-reference resolves to what it names

A reference naming where content lives SHALL resolve to that content. Moving
content SHALL include repointing every reference to it, in the same change.

A reference SHALL be checked against the content, not the path. A path that
still resolves does not establish that what it once held is still there.

#### Scenario: Content moves out of a file that remains

- **WHEN** a document's content is moved to another file, and the original file
  is kept as a pointer
- **THEN** references into the original are repointed, because the file still
  resolves while the section it named no longer exists

#### Scenario: A reference names a section anchor

- **WHEN** documentation links to a heading in another file
- **THEN** that heading exists in that file

#### Scenario: A symbol is cited by location

- **WHEN** documentation tells a reader which file defines a function
- **THEN** the function is defined there, and a refactor that moves it updates
  the citation

#### Scenario: A reference attributes a rule to a file

- **WHEN** documentation justifies a decision as following a rule "per" a named
  file
- **THEN** that file states the rule, rather than having handed it off to
  another file

### Requirement: A counted claim matches what it counts

Documentation stating how many of something exists SHALL match the code. A
document SHALL NOT state a count it does not derive, and a table enumerating
items SHALL contain only items of the kind it names.

#### Scenario: A count is stated in prose

- **WHEN** documentation says how many fields carry a particular tag
- **THEN** the number matches the code, or the prose describes the set without
  counting it

#### Scenario: A table mixes two kinds of row

- **WHEN** a table listing one kind of item contains rows pasted from a table
  above it
- **THEN** the foreign rows are removed, because a reader cannot tell which rows
  belong

#### Scenario: The set grows

- **WHEN** an item of the counted kind is added
- **THEN** the count is updated in the same change, or the prose is rewritten so
  no count needs maintaining
