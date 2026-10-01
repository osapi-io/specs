# Contributing

This repo is the design record for [osapi-io]. It holds no product code. The
documents under `components/` describe how each repository behaves, and they are
the thing you change.

## How work happens here

Doc-driven: you design something by writing the page, build it in the repository
it belongs to, then correct the page where building proved it wrong.

The page is the design up front and the description afterwards. It is the same
page either way, which is the point. There is no separate spec that gets
converted into documentation later, because that conversion is where the two
drift apart.

So a change here is one of three things:

- A new subject: a new page under the component, linked from its README.
- A change to how something behaves: an edit to the page that already covers it.
- An agreement between repositories: an edit to `ARCHITECTURE.md`, or a rule in
  `CONSTITUTION.md` if every repository has to honour it.

Pick the component by asking whether the subject is how one repository behaves
or an agreement two of them must both keep. Job retry logic is osapi's
behaviour. The subject naming that osapi and osapi-orchestrator both depend on
belongs to neither, so it goes in `ARCHITECTURE.md`.

## Issues

The rule is [Tracking](CONSTITUTION.md#tracking). In practice:

An issue is opened in the repository the change lands in. A finding about
osapi's code is an osapi issue, not one here, because that is where the person
who fixes it is looking. An issue here is for the design record itself: a page
that is wrong, a subject with no page, a rule stated in two places.

Open one when the work is larger than the change in hand. A one-line fix found
while editing a page is part of that change. A provider that decides idempotency
the wrong way is not, and widening the change to cover it buries the fix in a
diff about something else.

Carry the evidence. The counts and commands that found it belong in the issue
for the same reason they belong in a page: a reader who cannot reproduce it has
to take your word for it, and in six months so do you.

Something exploitable is never an issue, because an issue is public the moment
it is opened. It is a draft advisory on the repository it affects.

## Prerequisites

```bash
brew install mise gh
mise trust && mise install
just fetch
just test
```

[mise] provisions `just` and `uv` from `.mise.toml`. `gh` is installed
separately because `mise` resolves it through `aqua`, whose attestation check
fails for that package.

## What a page looks like

Read [components/osapi/job-system.md](components/osapi/job-system.md) for the
shape. The rules are in [CONSTITUTION.md](CONSTITUTION.md); the ones you will
hit immediately:

- Explain the system to somebody who has to work on it. `/document` carries the
  voice and runs `unslop`; use it rather than writing a page by hand.
- Every count carries the command that produces it, and the command has to work
  on its own.
- State a fact once. Link to it from anywhere else that needs it.
- Say what the tradeoff was when there was one.

`just test` enforces the first three. The fourth is on you.

## Before committing

```bash
just test
```

That runs markdown formatting, justfile lint, skill validation, every count
against its command, and the documentation contract. `just md-fmt` fixes
formatting.

[mdformat] rewrites two things silently, so write them correctly the first time:
GitHub alert syntax (`> [!WARNING]`) becomes a plain blockquote and stops
rendering, and link definitions get lowercased and sorted.

## Branches and commits

Branch from `main` as `type/short-description`, matching the
[Conventional Commits] type: `docs/add-firewall-page`,
`fix/correct-retry-count`.

Commit subjects max 50 characters, imperative, capitalized, no period. Body
wraps at 72. Say what changed and why, not how.

Keep PRs to a single commit where you can. Describe what changed and why in the
description; a reviewer should not have to read the diff to find the reason.

## AI usage

This repo is written with AI assistance and the workflow assumes it. The
[AI Usage Policy](AI_POLICY.md) applies. Disclose the tool, and be able to
explain what your page says without it.

[conventional commits]: https://www.conventionalcommits.org
[mdformat]: https://pypi.org/project/mdformat/
[mise]: https://mise.jdx.dev
[osapi-io]: https://github.com/osapi-io
