# The components

| Component                                          | Is                                           |
| -------------------------------------------------- | -------------------------------------------- |
| [osapi](osapi/README.md)                           | The API and the agent that manage a host     |
| [osapi-orchestrator](osapi-orchestrator/README.md) | A declarative layer over osapi's SDK         |
| [nats-client](nats-client/README.md)               | A wrapper over the NATS client               |
| [nats-server](nats-server/README.md)               | A NATS server embedded in its consumer       |
| [gohai](gohai/README.md)                           | A system fact collection library, standalone |
| [osapi-justfiles](osapi-justfiles/README.md)       | Shared `just` recipes                        |

Start with [osapi](osapi/README.md). [ARCHITECTURE.md](../ARCHITECTURE.md) has
the dependency graph and the facts that belong to no single repository.
