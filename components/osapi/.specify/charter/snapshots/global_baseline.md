# Baseline

A repository's memory states what the repository is before it states what was
decided about it. What it is, where it sits among the others, how it is built,
what a consumer may depend on, what was measured and the command that measures
it again, where its own prose and its code disagree, and what the inventory
leaves out.

Memory filled only by archived features records a sequence of changes. It
answers what was decided and never what the thing is, so a reader arriving at it
learns how one mechanism works before learning what the repository is for. That
is the state osapi's memory was in after five features: 1,840 lines, no
statement of purpose, no dependency, no architecture.

A count is written with the command that produces it. A number alone is a claim
that was true when somebody typed it, and nothing marks the moment it stops
being true.

Memory is documentation, written in the voice of somebody explaining a system to
somebody who has to work on it. Not a specification: no requirement identifiers
in the body, no "MUST", no user stories, no acceptance scenarios, no success
criteria. Those belong to the feature that produced the knowledge, where a
reviewer reads them once. Memory is read repeatedly by somebody learning the
system, and the formalism that serves the first reader obstructs the second.

A heading names the thing, with its path where a path helps. A statement is made
in the present tense and stated once. A design decision carries its reason, in a
sentence, the first time it appears — why the liveness probe checks nothing
belongs beside the liveness probe. What never appears is commentary about the
document: how a fact was found, that a fact is important, which requirement
obliged it, or what an earlier version said. A reader who wants that reads the
feature it came from.

Show the thing where showing it is shorter than describing it. A configuration
block, a directory tree, a response shape and a command are documentation; a
paragraph about the shape of a configuration block is not.

Memory is written in a human voice and checked for the tells that mark machine
prose. Em dashes, bold labels that restate the line after them, title case
headings, "serves as" where "is" would do, rule-of-three lists that were not
three things to begin with. A document a reader cannot finish is not
documentation, whatever it contains.
