## ADDED Requirements

### Requirement: Runnable examples

A Go library SHALL ship examples under `examples/`, each a standalone program
that compiles and runs against the library's public API.

The README's `Examples` section SHALL link them.

An example SHALL demonstrate a distinct usage shape rather than restating the
same call with different values.

#### Scenario: Reader wants to see the library used

- **WHEN** a developer opens a Go library repository
- **THEN** `examples/` contains programs they can run, and the README's
  `Examples` section links to them

#### Scenario: Library exposes several usage shapes

- **WHEN** a library supports more than one authentication mode or storage
  backend
- **THEN** each has its own example, rather than one example with commented-out
  alternatives

#### Scenario: Example stops compiling

- **WHEN** a change to the public API breaks an example
- **THEN** the example is updated in the same change, because it is part of the
  library's surface
