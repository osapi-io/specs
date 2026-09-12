---
name: org-status
description: Report and act on outstanding work across the osapi-io GitHub organization. Covers open pull requests, Dependabot version bumps, Dependabot and code-scanning and secret-scanning alerts, and CI health on default branches. Also triages security alerts and fixes them on request. Use when asked whether there are any open PRs, any Dependabot PRs, anything waiting on review, any security or vulnerability alerts, whether CI is green, or for a sweep of what needs attention. Also use when asked what to do about an alert, whether the org is actually exposed or affected, whether vulnerable code is reachable, or to fix, bump, triage, or dismiss alerts, and whenever a GitHub osapi-io repository security URL is pasted.
compatibility: Requires the gh CLI, authenticated with read access to the osapi-io organization. Security alert queries need the security_events scope.
license: MIT
metadata:
  author: osapi-io
  source: https://github.com/osapi-io/specs
---

# Org status

## Step 1: resolve the repository set

Every question here spans repositories, so start by asking GitHub which ones
exist:

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' | sort
```

Run this first, every time. Do not read a repository list out of a file, and do
not reuse one from earlier in the conversation. The rule and the reason are in
[.charter/fragments/global/repositories.md](../../../.charter/fragments/global/repositories.md):
a written list is correct when written and wrong after the next repository is
added, with nothing to mark the moment it turns.

Narrow the set at the point of use. If the user names repositories, query only
those. Otherwise query all of them, `.github` included, since it carries
workflow dependencies of its own.

`--no-archived` is doing real work. `osapi-sdk` and `osapi-ui` are archived and
hold eleven open Dependabot pull requests between them, none of which can ever
merge. `gh search prs --owner osapi-io` returns all eleven and makes the org
look four times busier than it is. Mention that they exist only if the user
asks why a count looks low.

## Step 2: route to the question

| The user asks | Read |
| --- | --- |
| Any open PRs? Anything waiting on me? Whose PRs are these? | [references/pull-requests.md](references/pull-requests.md) |
| Any Dependabot PRs? What version bumps are pending? | [references/pull-requests.md](references/pull-requests.md) |
| Any security alerts? Any vulnerabilities? Anything leaked? | [references/security.md](references/security.md) |
| What do I do about this alert? Are we actually exposed? A pasted `/security` URL | [references/triage.md](references/triage.md) |
| Fix it. Fix these alerts. Dismiss them. Open the bump. | [references/triage.md](references/triage.md), then act |
| Is CI green? Is anything failing or unreleased? | [references/quality.md](references/quality.md) |
| A general sweep, or no clear category | All three, in the order above |

## Step 3: report

The output is read in a terminal. It must fit one screen. **The grid plus one
detail block per item needing attention, and nothing else.** A clean sweep is
the grid alone. A reader who has to scroll has been given a worse answer, not a
more thorough one.

### Bare URLs, never markdown links

Ghostty and every other terminal linkify a bare URL and make it cmd-clickable.
`[text](url)` renders as literal punctuation with the address hidden, so the
reader cannot click it or copy it. Print the address.

### Shape

A grid of every repository, then a detail block for anything that needs the
reader. The grid answers "which repo" at a glance; the blocks answer "what do I
do".

```
osapi-io · 12 Sep · 8 repos

  repo                 pr   sec   ci
  osapi                 1     3   ✅
  gohai                 0     0   ✅
  nats-client           0     0   ✅
  nats-server           0     0   🟡
  osapi-orchestrator    0     0   ✅
  osapi-justfiles       0     0   ✅
  specs                 0     0   ✅
  .github               0     0   ⚪

🔴 osapi #477 · dependabot · 9d · build failing
   otelecho 0.69 -> 0.71, deprecated upstream
   https://github.com/osapi-io/osapi/pull/477
   → say "fix 477" to migrate off the deprecated package

🔴 osapi · github.com/docker/docker v28.5.2 · direct, runtime · 117d
   NOT AFFECTED, daemon-side CVEs and osapi is a client
   HIGH    7.2  CVE-2026-42306  archive endpoint runs container binary on host
   HIGH    7.2  CVE-2026-41567  docker cp race redirects bind mount to host
   MEDIUM  6.1  CVE-2026-41568  docker cp symlink swap writes empty host files
   https://github.com/osapi-io/osapi/security/dependabot
   → say "dismiss the docker alerts" to close all three as not_used

   no other repo depends on docker/docker

⚪ code scanning off everywhere, which is not the same as clean
```

When nothing needs attention the grid stands alone, which is the five-line
clean sweep:

```
osapi-io · 12 Sep · 8 repos

  repo                 pr   sec   ci
  osapi                 0     0   ✅
  ...

✅ nothing open. ⚪ code scanning off everywhere, not the same as clean.
```

Rules for that shape:

- **The grid is fixed-width ASCII, not a markdown table.** Pad the repository
  column to the longest name and keep `pr`, `sec` and `ci` to three characters.
  A markdown table wraps at terminal width and turns one row into four lines; a
  padded grid of short columns does not. Never emit pipe-delimited markdown.
- One row per repository, always, including the clean ones. Seeing every
  repository is how a reader knows the query covered them, and the row count is
  bounded by the number of repositories.
- `ci` glyphs, and only these four: `✅` green, `🔴` something failed, `🟡` still
  running, `⚪` no checks configured. Pending is never `🔴`; a check that has not
  concluded has not failed.
- `pr` and `sec` are counts. A zero is a zero, not a blank or a dash.
- A detail block per item needing the reader, led by `🔴`, ordered failing
  before green and oldest before newest. Anything the grid already says
  needs no block.
- Keep the CVE lines as severity, score, CVE, then effect in about seven words.
  Lead the block with the triage verdict rather than the alert count. See
  [references/triage.md](references/triage.md).
- Say in one line whether any other repository shares a flagged dependency.
- **End every actionable block with the words that act on it**, as a
  `→ say "..."` line. A reader who has to ask what to type has been handed a
  status board instead of an answer, and the phrase is the one thing they
  cannot guess. Quote it exactly as it should be typed:
  - `→ say "dismiss the docker alerts" to close all three as not_used`
  - `→ say "bump golang.org/x/sys" to open the PR`
  - `→ say "fix 477" to migrate off the deprecated package`
  - For EXPOSED with no patch there is no command, so say that:
    `→ your call: narrow, replace, or accept. No upgrade exists.`
  A finding with nothing to do gets no action line. Do not invent one.
- Stick to the glyphs named here. Emoji carrying a variation selector (`⚙️`,
  `🛡️`) render at inconsistent widths and break the grid alignment, so keep them
  out of any padded column.

### What to leave out

Detail the reader did not ask for costs them the finding they did. Omit check
counts for green branches, per-repository zeroes, endpoint names, and the
commands you ran. A failing check gets its log URL; a passing one gets nothing.

Offer the detail instead of printing it: "say the word and I will dig into
why #477 fails". One line, and the reader chooses.

### Rules that hold regardless of length

1. **Report zero as zero, with the denominator.** "No open PRs in any of the 8
   repositories." The count proves the query ran.
2. **A failed query is not a clean result.** Code scanning returns nothing for a
   repository that never enabled it, which is indistinguishable from zero
   findings by length alone. One line: "code scanning: off everywhere, which is
   not the same as clean."
3. **Sort by what needs attention.** Failing before green, severity before
   count, oldest before newest.
4. **Read by default. Write only when told to.** A question is answered, never
   acted on. When the user does say fix, dismiss, or open the bump,
   [references/triage.md](references/triage.md) has the write for each triage
   verdict, and every one of them needs the verdict established first. Never
   dismiss an alert to make a list shorter.

## Do not format this file with mdformat

The repository's `just md-fmt` excludes `.claude/**` for a reason: mdformat
reads the opening `---` as a horizontal rule and collapses the YAML frontmatter
into a heading, which makes the skill undiscoverable. If you reformat markdown
here, exclude this directory.
