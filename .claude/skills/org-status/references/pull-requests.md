# Pull requests

Resolve the repository set first, per [SKILL.md](../SKILL.md).

## Every open PR, with its author

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  gh pr list --repo "osapi-io/$r" --state open --limit 100 \
    --json number,title,author,isDraft,createdAt,mergeable,reviewDecision \
    -q ".[] | \"$r\t#\(.number)\t\(.author.login)\t\(.isDraft)\t\(.createdAt[:10])\t\(.mergeable)\t\(.title)\"" 2>/dev/null
done
```

The author login of Dependabot is `app/dependabot`. With it, you tell a version
bump from a human PR. It is the split between "any of my PRs" and "any
Dependabot PRs". If Renovate runs here, it is `app/renovate`.

## Filtering

Human PRs only:

```bash
gh pr list --repo "osapi-io/$r" --state open \
  --json number,title,author -q '.[] | select(.author.login | startswith("app/") | not)'
```

Dependabot only:

```bash
gh pr list --repo "osapi-io/$r" --state open \
  --json number,title,author -q '.[] | select(.author.login=="app/dependabot")'
```

## Fields worth reporting

- `isDraft`: a draft does not wait for review. Say so. Do not count it as
  pending.
- `mergeable`: `CONFLICTING` means it needs a rebase before anything else.
  `UNKNOWN` means that GitHub still calculates it. Query again. Do not report it
  as a problem.
- `reviewDecision`: an empty string means that nobody asked for or gave a
  review.
  `APPROVED` means it is ready to merge.
- `createdAt`: sort the oldest first. Age is the signal.

## Checks on a PR

```bash
gh pr checks <number> --repo "osapi-io/$r"
```

The exit status is not zero when any check fails. This is useful in a loop.
Report a PR as failed only when a check really completed. A pending check is not
a failure.

## Before calling one ready

A green PR is not always safe. Vet each one with [vetting.md](vetting.md), and
report its verdict, also for Dependabot PRs.

## What not to do

`gh search prs --owner osapi-io` answers in one call, not one call for each
repository. That is attractive. But it reads the search index of GitHub, not the
repositories. That index updates on its own schedule. Thus a PR that somebody
opened a short time ago may not show. Use it only when the user wants an
approximate count for the org, and says that the time is not important.
Otherwise, run `gh pr list` in a loop. It reads the live state.

## Held on purpose

Leave these out of each sweep, each report and each merge run:

- osapi-io/osapi#661, the TypeScript 7 bump in `ui/`, and each later TypeScript
  7 bump there. typescript-eslint does not support TypeScript 7 yet. The owner
  holds it. Check the peer range of typescript-eslint again only when the owner
  asks about it.
- The Dependabot pull requests of osapi-ui and osapi-sdk. Both repositories are
  archived, so nobody can close them. `--no-archived` keeps them out of a sweep.
  `gh search prs --owner osapi-io` includes them.
