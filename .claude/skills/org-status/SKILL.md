---
name: org-status
description: Report outstanding work across the osapi-io GitHub organization. Covers open pull requests, Dependabot version bumps, Dependabot and code-scanning and secret-scanning alerts, and CI health on default branches. Use when asked whether there are any open PRs, any Dependabot PRs, anything waiting on review, any security or vulnerability alerts, whether CI is green, or for a general sweep of what needs attention across the org.
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

## Step 2: route to the question

| The user asks | Read |
| --- | --- |
| Any open PRs? Anything waiting on me? Whose PRs are these? | [references/pull-requests.md](references/pull-requests.md) |
| Any Dependabot PRs? What version bumps are pending? | [references/pull-requests.md](references/pull-requests.md) |
| Any security alerts? Any vulnerabilities? Anything leaked? | [references/security.md](references/security.md) |
| Is CI green? Is anything failing or unreleased? | [references/quality.md](references/quality.md) |
| A general sweep, or no clear category | All three, in the order above |

## Rules

1. **Report zero as zero.** "No open PRs in any of the 8 repositories" is a
   real answer. Say how many repositories you checked, so an empty result is
   distinguishable from a query that silently failed.
2. **A failed query is not a clean result.** Three of GitHub's security
   endpoints return a 404 body for a repository that never enabled the feature,
   which looks identical to zero alerts if you only count array length. Each
   reference file says which, and how to tell them apart. Report those
   separately from a genuine zero.
3. **Sort by what needs attention.** Severity first for alerts, age first for
   pull requests. A three-week-old PR matters more than yesterday's.
4. **Give the URL.** Every finding gets its full address, not link text that
   hides it.
5. **Read, do not write.** This skill answers questions. Merging a PR, closing
   an alert, or pushing a fix is a separate request the user makes explicitly.

## Do not format this file with mdformat

The repository's `just md-fmt` excludes `.claude/**` for a reason: mdformat
reads the opening `---` as a horizontal rule and collapses the YAML frontmatter
into a heading, which makes the skill undiscoverable. If you reformat markdown
here, exclude this directory.
