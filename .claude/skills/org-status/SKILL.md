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

The output is read in a terminal. It must fit one screen. **Twenty lines is the
budget, and a sweep of a clean org should take five.** A reader who has to
scroll has been given a worse answer, not a more thorough one.

### Bare URLs, never markdown links

Ghostty and every other terminal linkify a bare URL and make it cmd-clickable.
`[text](url)` renders as literal punctuation with the address hidden, so the
reader cannot click it or copy it. Print the address.

### Shape

```
PRS  3 open, 8 repos

  FAIL  osapi #477  dependabot   9d  otelecho 0.69 -> 0.71, deprecated upstream
        https://github.com/osapi-io/osapi/pull/477
  ok    osapi #486  retr0h       4d  conform to the documented conventions
        https://github.com/osapi-io/osapi/pull/486

SECURITY  1 of 8 repos affected

  osapi   github.com/docker/docker v28.5.2   direct, runtime   117d
  NOT AFFECTED, daemon-side CVEs and osapi is a client
    HIGH    7.2  CVE-2026-42306  archive endpoint runs container binary on host
    HIGH    7.2  CVE-2026-41567  docker cp race redirects bind mount to host
    MEDIUM  6.1  CVE-2026-41568  docker cp symlink swap writes empty host files
    https://github.com/osapi-io/osapi/security/dependabot

  no other repo depends on docker/docker
  code scanning off everywhere, which is not the same as clean

CI  every default branch green
```

Rules for that shape:

- Lead each section with the count. A number first tells the reader whether to
  keep reading.
- **Name the repository where a reader cannot mistake it for something else.**
  A bare word in column one beside a package name reads as part of the
  dependency. Put the repository first on its own line with the package, and
  indent the findings under it.
- **Give each CVE its severity, its score, and what it does.** "2 HIGH" is a
  count. `HIGH 7.2 CVE-2026-42306 archive endpoint runs container binary on
  host` is a decision. One line each, and keep the effect under about seven
  words.
- Lead the block with the triage verdict, not the alert count. `NOT AFFECTED`,
  `EXPOSED`, `UPGRADE AVAILABLE`. See
  [references/triage.md](references/triage.md) for how each is established.
- One line per finding, then its URL indented beneath. Age in days, not dates:
  `9d` is a judgement, `2026-09-03` is arithmetic homework.
- Flag the exception in column one for pull requests: `FAIL`, `CONFLICT`.
  Everything healthy reads `ok` and needs no elaboration.
- Say in one line whether any other repository shares the dependency. The
  reader's next question is always whether this is one problem or eight.
- Name clean repositories in one line, or say "the other 7 are clean". Never one
  line each.
- No tables. They wrap at terminal width and turn one finding into four lines.

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
