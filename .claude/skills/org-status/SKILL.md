---
name: org-status
description: Report and act on outstanding work across the osapi-io GitHub organization. Covers open pull requests, Dependabot version bumps, Dependabot and code-scanning and secret-scanning alerts, and CI health on default branches. Also triages security alerts and fixes them on request. Use when asked whether there are any open PRs, any Dependabot PRs, anything waiting on review, any security or vulnerability alerts, whether CI is green, whether the go directive is behind a new Go release, or for a sweep of what needs attention. Also use when asked what to do about an alert, whether the org is actually exposed or affected, whether vulnerable code is reachable, or to fix, bump, triage, or dismiss alerts, and whenever a GitHub osapi-io repository security URL is pasted.
compatibility: Requires the gh CLI, authenticated with read access to the osapi-io organization. Security alert queries need the security_events scope.
license: MIT
metadata:
  author: osapi-io
  source: https://github.com/osapi-io/specs
---

# Org status

## 1. Resolve the repository set

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' | sort
```

Every run, before anything else. Never from a file, never reused from earlier in
the conversation: a written list is right when written and wrong after the next
repository is added, with nothing marking the moment
([why](../../../.charter/fragments/global/repositories.md)). Query all of them,
`.github` included, unless the user names some.

`--no-archived` matters. Archived repositories hold Dependabot PRs that can
never merge, and `gh search prs --owner osapi-io` counts them.

## 2. Route

| The user asks | Read |
| --- | --- |
| Open PRs, what is waiting, whose they are, Dependabot bumps | [pull-requests.md](references/pull-requests.md) |
| Any alerts, vulnerabilities, anything leaked | [security.md](references/security.md) |
| What to do about an alert, are we exposed, a pasted `/security` URL | [triage.md](references/triage.md) |
| Fix it, dismiss them, open the bump | [triage.md](references/triage.md), then act |
| Is CI green, is anything failing or unreleased, are we on the right Go | [quality.md](references/quality.md) |
| A sweep, or no clear category | All four, in that order |

## 3. Report

A grid of every repository, then one detail block per item needing the reader.
The grid answers "which repo"; the blocks answer "what do I do". When nothing
needs attention the grid stands alone.

```
osapi-io · 12 Sep · 8 repos

  repo                 pr   sec   ci
  osapi                 1     3   ✅
  gohai                 0     0   ✅
  nats-server           0     0   🟡
  .github               0     0   ⚪

🔴 osapi #477 · dependabot · 9d · build failing
   otelecho 0.69 -> 0.71, deprecated upstream
   https://github.com/osapi-io/osapi/pull/477
   → say "fix 477" to migrate off the deprecated package

🔴 osapi · github.com/docker/docker v28.5.2 · direct, runtime · 117d
   NOT AFFECTED, daemon-side CVEs and osapi is a client
   HIGH    7.2  CVE-2026-42306  archive endpoint runs container binary on host
   MEDIUM  6.1  CVE-2026-41568  docker cp symlink swap writes empty host files
   https://github.com/osapi-io/osapi/security/dependabot
   → say "dismiss the docker alerts" to close all three as not_used

   no other repo depends on docker/docker

⚪ code scanning off everywhere, which is not the same as clean
```

- **Grid.** Fixed-width ASCII, repository column padded to the longest name.
  Never pipe-delimited markdown, which wraps and turns one row into four. One
  row per repository including clean ones, because the row count proves the
  query covered them.
- **`ci` glyphs**, these four only: `✅` green, `🔴` failed, `🟡` running, `⚪` no
  checks. Pending is never `🔴`. Variation-selector emoji (`⚙️`, `🛡️`) break
  column alignment, so keep them out of the grid.
- **Bare URLs, never `[text](url)`.** A terminal linkifies a bare address and
  hides one behind markdown punctuation.
- **Blocks** only for what needs the reader, failing first then oldest first,
  led by the triage verdict rather than a count. CVE lines are severity, score,
  CVE, effect in about seven words. Say in one line if another repository shares
  a flagged dependency.
- **Each block ends with the words that act on it**, as `→ say "..."`, quoted
  as it should be typed. That phrase is the one thing a reader cannot guess.
  Where no command applies, say so: `→ your call: narrow, replace, or accept.
  No upgrade exists.` Nothing to do means no action line.
- **Leave out** check counts for green branches, per-repository zeroes, endpoint
  names, and the commands you ran. Offer detail in a sentence instead of
  printing it.

## Rules

1. **Zero is an answer, with its denominator.** "No open PRs in any of the 8
   repositories." The count proves the query ran.
2. **A failed query is not a clean result.** Code scanning returns nothing for a
   repository that never enabled it, which by length alone looks like zero
   findings.
3. **Read by default. Write only when told to.** On fix, dismiss or bump,
   [triage.md](references/triage.md) has the write for each verdict and every
   one needs the verdict established first. Never dismiss an alert to shorten a
   list.
