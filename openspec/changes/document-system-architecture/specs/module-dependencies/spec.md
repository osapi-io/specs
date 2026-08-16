## Purpose

Records how osapi-io repositories depend on one another and how those
dependencies are declared, so that a description of the system can be checked
against what the code actually does.

## ADDED Requirements

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

#### Scenario: A relationship is planned but not built

- **WHEN** a repository is intended to be used by another but is not yet
- **THEN** its documentation says so, rather than describing the intended state
  as current

#### Scenario: A dependency is removed

- **WHEN** a repository stops depending on another
- **THEN** the documentation describing that relationship is removed in the same
  change
