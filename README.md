# osapi-io

Design docs for [osapi-io](https://github.com/osapi-io). No product code here.

**The product makes a Linux host behave like an appliance.** One binary, one
config file, and you get a REST API and a CLI for reading and changing system
configuration across a fleet.

## Where things are

| Path                                | What                                           |
| ----------------------------------- | ---------------------------------------------- |
| [components/](components/README.md) | One page per repository, plus its subjects     |
| [ARCHITECTURE.md](ARCHITECTURE.md)  | How the six fit together                       |
| [CONSTITUTION.md](CONSTITUTION.md)  | Rules every repository follows                 |
| [history/](history/)                | Old specs, kept for the record, not maintained |

Start with [osapi](components/osapi/README.md). Twelve subject pages hang off
it, and four of the other five repositories either feed it or consume it.

## Doc-driven development

You design something by writing the page. Then you build it. Then you correct
the page where building proved it wrong.

The page is the design up front and the description afterwards, and it is the
same page both times. Nothing gets converted from one form into another, because
that conversion is where the design and the docs drift apart.

Two checks run on every `just test`:

- `just check-counts` runs every count in every page against the command written
  beside it, in the repository that page describes. A number that moved fails
  the build.
- `just check-docs` fails on a broken link, a page missing from its index, or a
  page that reads like a spec instead of documentation.

The third check is a person. Hand somebody the docs and nothing else, ask them
to trace a change end to end, and fix whatever they could not answer. That has
found more problems than both scripts together.
