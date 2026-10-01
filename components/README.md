# The components

Six repositories, one product. Each has a page here saying what it is and
linking to its subjects.

| Component                                          | Is                                           | Read it to learn                                                  |
| -------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------- |
| [osapi](osapi/README.md)                           | The API and the agent that manage a host     | How work reaches a machine, and everything downstream of that     |
| [osapi-orchestrator](osapi-orchestrator/README.md) | A declarative layer over osapi's SDK         | How several operations are composed into one plan                 |
| [nats-client](nats-client/README.md)               | A wrapper over the NATS client               | What osapi's transport does and does not handle                   |
| [nats-server](nats-server/README.md)               | A NATS server embedded in its consumer       | What runs the message bus, and what it will not let you configure |
| [gohai](gohai/README.md)                           | A system fact collection library, standalone | How facts are gathered, if you need them                          |
| [osapi-justfiles](osapi-justfiles/README.md)       | Shared `just` recipes                        | What every repository's build resolves to                         |

**Start with osapi.** Four of the other five either feed it or consume it, so
its page makes the rest legible. [How they fit together](../ARCHITECTURE.md) has
the graph and the facts that belong to no single repository.

gohai is the exception and reads standalone, which makes it the right place to
see the shape of these documents without holding another repository in your
head.

## Adding a page

A new design is a page under the component whose behaviour it describes, named
for its subject, linked from that component's README. The test for which
component is in [the constitution](../CONSTITUTION.md) under Repositories: ask
whether the subject is how one repository behaves, or an agreement two of them
must both honour. The second belongs in [ARCHITECTURE.md](../ARCHITECTURE.md).

A subject that outgrows one page becomes a directory with its own README and
pages beside it. The pattern is the same one level down.
