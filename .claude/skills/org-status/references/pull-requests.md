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

Dependabot's author login is `app/dependabot`. That is how you tell a version
bump from a human PR, and it is the split behind "any of my PRs" versus "any
Dependabot PRs". Renovate, if it ever runs here, is `app/renovate`.

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

- `isDraft` — a draft is not waiting on review. Say so rather than counting it
  as pending.
- `mergeable` — `CONFLICTING` means it needs a rebase before anything else.
  `UNKNOWN` means GitHub is still computing it, so re-query rather than
  reporting it as a problem.
- `reviewDecision` — empty string means no review has been requested or given.
  `APPROVED` means it is ready to merge.
- `createdAt` — sort oldest first. Age is the signal.

## Checks on a PR

```bash
gh pr checks <number> --repo "osapi-io/$r"
```

Exit status is non-zero when any check fails, which is useful in a loop. Only
report a PR as failing when a check has actually concluded; a pending check is
not a failure.

## What not to do

`gh search prs --owner osapi-io` answers in one call instead of one per
repository, which is tempting. It reads GitHub's search index rather than the
repositories, and that index updates on its own schedule, so a PR opened a
moment ago may not appear. Use it only when the user wants a rough cross-org
count and says timeliness does not matter. Otherwise loop `gh pr list`, which
reads live state.
