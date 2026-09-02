# Workflow

One workflow governs specification, planning, and implementation, and it is Spec
Kit: `speckit-specify` and `speckit-clarify` settle what a change must do,
`speckit-plan` and `speckit-tasks` settle how, `speckit-implement` carries it
out, and `speckit-archive-run` consolidates the result. A second workflow over
that same ground gives two answers to which artifact is authoritative, and the
answer that loses is the one nobody reads.

Design output is written where the workflow that reads it looks: a feature under
the project's `specs/`, consolidated into `.specify/memory/` when it merges. A
planning artifact written anywhere else is not durable knowledge, whatever it
contains, because nothing reaches it again.

The superpowers plugin is not used, and nothing it produces is committed. Its
planning skills cover ground Spec Kit already owns, and its `docs/superpowers/`
tree is a second planning record that drifts from the first.
