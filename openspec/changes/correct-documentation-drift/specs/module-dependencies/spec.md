## MODIFIED Requirements

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

## ADDED Requirements

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
