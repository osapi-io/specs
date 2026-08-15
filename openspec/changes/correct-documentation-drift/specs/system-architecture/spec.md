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
