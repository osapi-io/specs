# nats client Constitution

<!-- [F] global/documentation SECTION -->

## Documentation

A repository states in full the conventions binding it. A reference to guidance
held elsewhere does not stand in place of stating them: a reviewer reading a
pull request in a browser, a contributor working offline, and an agent with a
single checkout each see only that repository.

Where a convention binds several repositories, each states it in the same words,
so a difference in wording means a difference in rule.

A rule a tool already enforces is never restated as prose. The configuration is
the statement of record; documentation names where it lives. Prose describing a
tool's settings is maintained by hand and checked by nothing, so it drifts while
continuing to read as authoritative.

<!-- [F] global/verification SECTION -->

## Verification

A claim about the codebase is measured, not inspected. Reading code and
concluding is a hypothesis; running something that would fail if the claim were
false is a result.

Completion is reported with the output that demonstrates it. "Tests pass" is a
claim; the command and its output are evidence.

Where a check can be automated it is automated. A rule enforced only by review
is a rule that holds until someone is busy.

<!-- [F] global/tooling SECTION -->

## Tooling

A tool a repository invokes is declared where the repository declares its tools.
A tool resolved from whatever the developer happens to have installed is not the
same tool across machines, and is not what continuous integration runs.

Both provisioning paths resolve to the same version. Where nothing maintains a
version automatically, both track the latest release so they move together;
where something does, both pin it and that mechanism moves both. A version
pinned in one path and floating in the other guarantees divergence.

A tool whose output is committed is pinned, so the committed artifact does not
change under whoever runs the generator.

<!-- [F] global/correction SECTION -->

## Correction

When applying a rule shows the rule is wrong, work stops and the rule is
corrected first, in its own change. Correcting the rule and the code together
produces a rule written to describe what was already done, and buries the
correction where nobody reviews it as a change of rule.

Write a requirement from evidence the repository already carries: its
configuration, its history, a failure it has had. A standard invented to fill a
template creates noise rather than a constraint, and is non-conformant from the
day it is written.

---

**Version**: 1.0.1 | **Ratified**: 2026-09-02 | **Last Amended**: 2026-09-02
