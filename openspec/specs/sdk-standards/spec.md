# sdk-standards Specification

## Purpose

Records what the SDK at `pkg/sdk` guarantees the repositories built on it, so a
consumer can read the contract it depends on rather than infer it from another
repository's contributor documentation.

## Requirements

### Requirement: A method name does not repeat its service

A service method SHALL be named for the action alone. The service already
supplies the namespace, so repeating it in the method reads twice at every call
site.

Methods SHALL use `List`, `Get`, `Create`, `Update`, and `Delete` for operations
on a resource. An operation with no persistent resource — a one-shot action or a
command execution — MAY use a verb naming what it does.

#### Scenario: A service gains a read method

- **WHEN** a service is added for a domain
- **THEN** its read method is `Get`, not the domain name followed by `Get`

#### Scenario: An operation has no resource

- **WHEN** an operation performs an action rather than acting on a stored
  resource
- **THEN** it is named for the action, because none of the five resource verbs
  describes it

### Requirement: Generated types stay inside the SDK

A public method signature SHALL NOT contain a type from the generated OpenAPI
package. The SDK exists to hide that package; a signature naming one requires
every consumer to import it, and re-exports each regeneration as a breaking
change.

A consumer needing to import the generated package indicates the SDK is missing
a wrapper, rather than indicating the consumer should import it.

#### Scenario: A request needs a generated body type

- **WHEN** a method sends a request whose body is a generated type
- **THEN** the method accepts an SDK-defined type and builds the generated one
  internally

#### Scenario: A consumer reaches for the generated package

- **WHEN** a consumer cannot express a call without importing the generated
  package
- **THEN** the SDK adds the missing wrapper, rather than the consumer adding the
  import

### Requirement: Every exported result field carries a JSON tag

Every exported field on a result type SHALL carry a `json` tag naming the key in
`snake_case`.

The tags are load-bearing rather than decorative: results are converted to
generic maps by round-tripping through JSON, and an untagged field arrives under
its Go name, which does not match the key the API returned.

A field whose absence is meaningful SHALL use `omitempty`. A field a caller must
always be able to read SHALL NOT, so that a false or empty value is
distinguishable from a field that was never set.

#### Scenario: A result is converted to a map

- **WHEN** a result is converted to a generic map
- **THEN** its keys match the API's, because each field names its key

#### Scenario: A mutation reports whether it changed anything

- **WHEN** a mutation result reports that nothing changed
- **THEN** the field is present and false, rather than omitted

### Requirement: Errors reaching a consumer carry context

An error returned from an SDK method SHALL name the operation that produced it.

A response body SHALL be checked for nil after its status is checked, because a
status alone does not establish that a body was returned.

#### Scenario: A call fails inside a wrapped client

- **WHEN** an underlying call fails
- **THEN** the returned error names the SDK operation, so a consumer's log
  identifies the call without a stack trace

#### Scenario: A success status arrives with no body

- **WHEN** a response carries a success status and no body
- **THEN** the SDK returns an error rather than dereferencing it
