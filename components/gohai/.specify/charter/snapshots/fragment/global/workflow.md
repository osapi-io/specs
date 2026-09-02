# Workflow

One workflow governs planning, design, and review, and it is Spec Kit. A second
workflow alongside it produces two answers to which artifact is authoritative,
and the answer that loses is the one nobody reads.

Design output is written where the workflow that reads it looks: a feature under
the project's `specs/`, consolidated into `.specify/memory/` when it merges. A
planning artifact written anywhere else is not durable knowledge, whatever it
contains, because nothing reaches it again.

The superpowers plugin is not used, and nothing it produces is committed. Its
workflows and its `docs/superpowers/` tree duplicate what Spec Kit already
provides, leaving a second planning record that drifts from the first.
