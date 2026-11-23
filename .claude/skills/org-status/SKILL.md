---
name: org-status
description: Report and act on outstanding work across the osapi-io GitHub organization. Covers open pull requests and vetting them for typosquats, hijacked releases and disguised changes, auditing the org for signs of compromise and for missing Dependabot cooldowns, Dependabot version bumps, open issues, Dependabot and code-scanning and secret-scanning alerts, and CI health on default branches. Also triages security alerts and fixes them on request. Use when asked whether there are any open PRs, whether a PR is safe to approve or could be malicious, whether anything has been hacked or exploited, whether any dependency is malicious, whether cooldowns are set, any Dependabot PRs, anything waiting on review, what issues are open or what is left to work, any security or vulnerability alerts, whether CI is green, whether the go directive is behind a new Go release, whether any remote branches are stale or deletable, whether the nested modules under examples are untidy or behind, or for a sweep of what needs attention. Also use when asked what to do about an alert, whether the org is actually exposed or affected, whether vulnerable code is reachable, or to fix, bump, triage, or dismiss alerts, and whenever a GitHub osapi-io repository security URL is pasted.
compatibility: Requires the gh CLI, authenticated with read access to the osapi-io organization. Security alert queries need the security_events scope.
allowed-tools:
  - Bash(gh pr merge:*)
  - Bash(gh pr comment:*)
  - Bash(gh issue close:*)
  - Bash(gh api -X PATCH:*)
  - Bash(gh api -X DELETE:*)
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

Do this on each run, before anything else. Never get the list from a file, and
never use a list from earlier in the conversation. A written list is correct
when you write it. It is incorrect after somebody adds the next repository, and
nothing shows that change ([why](../../../CONSTITUTION.md)). Query all of them,
with `.github`, unless the user names some.

`--no-archived` matters. Archived repositories hold Dependabot PRs that can
never merge, and `gh search prs --owner osapi-io` counts them.

## 2. Route

| The user asks                                                                                        | Read                                                                                               |
| ---------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Open PRs, what is waiting, whose they are, Dependabot bumps                                          | [pull-requests.md](references/pull-requests.md), then [vetting.md](references/vetting.md) for each |
| Is this PR safe, could it be a typosquat or a hijacked release, can I approve it                     | [vetting.md](references/vetting.md)                                                                |
| Merge them, land the bumps, rebase and merge                                                         | [merging.md](references/merging.md)                                                                |
| Have we been hacked, exploited or compromised, do we depend on anything malicious, are cooldowns set | [audit.md](references/audit.md)                                                                    |
| Open issues, what is left to work, what a tracker still lists                                        | [issues.md](references/issues.md)                                                                  |
| Any alerts, vulnerabilities, anything leaked                                                         | [security.md](references/security.md)                                                              |
| What to do about an alert, are we exposed, a pasted `/security` URL                                  | [triage.md](references/triage.md)                                                                  |
| Fix it, dismiss them, open the bump                                                                  | [triage.md](references/triage.md), then act                                                        |
| Is CI green, is anything failing or unreleased, are we on the right Go                               | [quality.md](references/quality.md)                                                                |
| Any stale branches, can we delete any, what is left over                                             | [branches.md](references/branches.md)                                                              |
| Are the examples out of date, do nested modules need tidying or bumping                              | [modules.md](references/modules.md)                                                                |
| A sweep, or no clear category                                                                        | [audit.md](references/audit.md) first, then the rest in this order, vetting every open PR          |

## 3. Report

Give a grid of each repository. Then give one detail block for each item that
needs the reader. The grid answers "which repo". The blocks answer "what do I
do". When nothing needs attention, give only the grid.

```
osapi-io · 12 Sep · 8 repos

  repo                 pr  iss   sec   ci
  osapi                 1   13     3   ✅
  gohai                 0    0     0   ✅
  nats-server           0    0     0   🟡
  .github               0    0     0   ⚪

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
```

- **Grid.** Fixed-width ASCII. Pad the repository column to the longest name.
  Never use pipe-delimited markdown, because it wraps and makes one row into
  four. Give one row for each repository, also the clean ones. The row count
  proves that the query covered them.
- **`ci` glyphs**, these four only: `✅` green, `🔴` failed, `🟡` running, `⚪` no
  checks. Pending is never `🔴`. Variation-selector emoji (`⚙️`, `🛡️`) break the
  column alignment. Keep them out of the grid.
- **Bare URLs, never `[text](url)`.** A terminal makes a bare address into a
  link. Markdown punctuation hides the address.
- **Blocks** only for what needs the reader: failures first, then the oldest
  first. Start each block with the triage verdict, not a count. A CVE line has
  the severity, the score, the CVE, and the effect in approximately seven words.
  If a different repository has the same flagged dependency, say so in one line.
- **Each block ends with the words that act on it**, as `→ say "..."`, in
  quotes, as the reader must type them. The reader cannot guess that phrase.
  When no command applies, say so:
  `→ your call: narrow, replace, or accept. No upgrade exists.` When there is
  nothing to do, give no action line.
- **Leave out** check counts for green branches, zeroes for each repository,
  endpoint names, and the commands that you ran. Offer detail in a sentence. Do
  not print it.

## Rules

1. **Zero is an answer, with its denominator.** "No open PRs in any of the 8
   repositories." The count proves the query ran.
2. **A failed query is not a clean result.** But say so one time, and not again.
   Code scanning returns nothing for a repository that never enabled it. By its
   length, that looks like zero findings. Report it the first time that somebody
   asks, or when it changes. If you say it again in each sweep, the reader
   learns to skip the last line. One day, a real finding will be on that line.
3. **A standing condition is not a finding.** If the reader already saw
   something and decided not to act, it is state, not news. Examples are
   branches whose pull request was closed, a protected `gh-pages`, and a feature
   that nobody enabled. Leave them out, unless the user asks for them, they
   changed, or the question was about them. A finding gets its line when it is
   new, when the reader can act on it, or both. An action line on something that
   the reader always declines only annoys the reader.
4. **No pull request is ready until it is vetted.** A green check says that the
   code builds. It does not say that the code is what it claims to be. Run
   [vetting.md](references/vetting.md) before you call a pull request ready,
   before you approve or merge it, and before you check it out. Start its block
   with the verdict.
5. **Read by default. Write only when the user tells you to.** For fix, dismiss
   or bump, [triage.md](references/triage.md) has the write for each verdict.
   Each write needs the verdict first. Never dismiss an alert to make a list
   shorter.
