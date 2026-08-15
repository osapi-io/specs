# AGENTS.md

Test: `just test` | Format: `just md-fmt`

Read @CONTRIBUTING.md first. It covers the workflow, the operating model,
formatting, and every convention — all of which apply to agents exactly as they
apply to people. This file carries only what is specific to agents.

## Planning boundary

`/opsx:propose` produces planning artifacts and then stops. Do not edit code in
the same response, even when the request asks you to build or fix something.
Wait for an explicit instruction to apply.

## Writing artifacts

Read `openspec/config.yaml` before generating any artifact. Its `context` and
`rules` are injected into every generation — apply them as constraints, and do
not copy them into the output.

Follow the artifact build order from `openspec status`, not the order the
templates happen to appear in.
