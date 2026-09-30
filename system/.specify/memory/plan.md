# How these agreements were reached

Each one started as something going wrong in a repository, which is why they are
worth keeping rather than being the rules anybody would have guessed.

## The list rule came from a deletion

`dependencies.md` held a hand-maintained dependency graph. It was accurate when
written. The question that killed it was not whether it was wrong but what would
tell anybody when it became wrong, and the answer was nothing.

The graph was already derivable from `go.mod` files and justfiles, so the document
was a cache that nothing refreshed and nothing checked. Deleting it and stating the
command was the whole change.

## The shape came from a baseline that was already wrong for the goal

gohai's was written first and deliberately excluded architecture, on the reasoning
that the contract was what mattered. That is defensible for one repository and
fatal for a set: the goal is that somebody reads all six and understands how the
organisation fits together, and an inventory that states a contract and omits the
architecture cannot do that.

Five more in that shape would have made the inconsistency permanent. So the shape
was fixed before the second baseline rather than after the sixth, and gohai's
amendment is still owed.

## The riskiest case was taken sixth on purpose

`osapi-justfiles` has no Go at all. If the seven-section shape could not be filled
there, the shape was wrong, and finding that out after four conforming baselines is
the expensive order.

It fits. What it cost was one interpretation, recorded with the two readings
rejected: "the contract" had to mean what a consumer may depend on rather than
exported symbols.

## The documentation contract came from three readings saying the same thing

Each baseline gets a reading by somebody who has seen nothing else. Three of them
reported that memory read as a checklist with footnotes, and each time it was
recorded as a finding for this feature to decide rather than fixed.

That was wrong. It was a visible, actionable form problem filed as somebody else's
decision, and the rule that forbade it already existed: FR-017 said a baseline must
not use "checklist scaffolding, or any other testing formalism as its body". Five
archivals read that as binding the feature specification rather than what archival
writes into memory.

## Every reading has found something

Nine of them now, and none has come back clean on the first attempt.

A promised answer that did not exist. Five modules named in three places and
explained in none. An overclaim about what five documentation pages omitted. A
count hedged as "about twenty" beside a table enumerating exactly 20. A consumer
list that was wrong when written.

The most recent read all thirteen documents and answered all five of its questions,
and still found six defects: a six-versus-seven count that reads as a
contradiction, an undefined term, a result status nobody had stated, no document
tracing one request end to end, and the same rhetorical device in two unrelated
documents. That last one is the machine tell that survives every other pass.

**The reading is the only check on the prose.** `memory-check` catches a count that
moved and `check-memory-docs.py` catches specification form creeping back, and
neither can tell whether a paragraph is true or readable.

## What is enforced, and what is not

| Check                     | Catches                                                    |
| ------------------------- | ---------------------------------------------------------- |
| `just memory-check`       | a count whose command no longer produces it                |
| `just memory-docs`        | `MUST`, `FR-` labels, user stories, em dashes, broken links, an unlinked subject |
| `just skill-lint`         | a citation into the corpus that stopped resolving          |
| a reading                 | everything else, and it has never come back clean          |

## What is still owed

gohai's amendment, which needs sections 2 and 3 and the classification of its 68
documentation pages. The orchestrator's 140 pages are unclassified too, so nobody
has checked whether either repository is sitting on contributor knowledge the way
osapi was.

`sdk/guidelines.md`'s remainder in osapi, the package structure and the response
pattern, has no corpus counterpart and no feature open for it.

Six of osapi's subsystems have no document: `audit`, `telemetry`, `exec`, `cli`,
`authtoken` and `config`. None has a feature behind it, so none was ever
backfilled. `exec` matters most, because the rule that a secret never reaches a
command through its arguments lives there and `providers.md` points at it without
explaining it.
