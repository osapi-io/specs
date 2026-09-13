# Stale branches

Resolve the repository set first, per [SKILL.md](../SKILL.md).

## Classify, do not just list

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  def=$(gh api "/repos/osapi-io/$r" --jq '.default_branch')
  gh api "/repos/osapi-io/$r/branches?per_page=100" --jq ".[] | select(.name != \"$def\") | .name" |
  while read -r b; do
    # Guard the assignment, not its result. A compare with no common
    # ancestor answers 404 with a JSON body on stdout, so ${ahead:-orphan}
    # sees that body and never falls back. The exit status is the signal.
    if ! ahead=$(gh api "/repos/osapi-io/$r/compare/$def...$b" --jq '.ahead_by' 2>/dev/null); then
      ahead=orphan
    fi
    pr=$(gh pr list --repo "osapi-io/$r" --head "$b" --state all \
      --json number,state -q '.[0] | "#\(.number) \(.state)"' 2>/dev/null)
    printf "%s\t%s\t%s\t%s\n" "$r" "$b" "$ahead" "${pr:-no PR}"
  done
done
```

Four outcomes, and only the first is safe without asking:

| Signal | Meaning | Action |
| --- | --- | --- |
| PR `MERGED` | the work is in | safe to delete |
| `ahead_by` 0, no PR | nothing the default branch lacks | safe to delete |
| PR `CLOSED` | abandoned, and deleting discards it | report, ask first |
| PR `OPEN` | active | leave alone |

## Two traps

**`ahead_by` is not a merge test.** A squash merge rewrites history, so the
branch stays ahead of the default branch while its work is fully landed.
`ahead:4` alongside a `MERGED` pull request is safe to delete. Judging by
`ahead_by` alone keeps every squash-merged branch forever.

**An orphan branch is not stale.** `gh-pages` shares no history with `main`, so
the compare call returns 404 with "No common ancestor". Treat a 404 there as
protected, never as deletable. It is the published documentation site.

## Protected, never deleted

- the default branch
- `gh-pages`, and any branch whose compare has no common ancestor
- anything with an open pull request

## Reporting

Group by outcome, not by repository. The reader decides once per category, and a
merged branch in one repository is the same decision as a merged branch in
another.

```
🔴 18 merged branches safe to delete · 7 repos
   osapi 6 · gohai 4 · specs 5 · osapi-orchestrator 1 · nats-client 2
   → say "delete the merged branches" to remove them
```

Report the merged ones, because they are work with nothing left to decide.

**Do not report the abandoned ones in a sweep.** A branch whose pull request was
closed is a decision the reader already made, and repeating it every run with an
action line attached is nagging rather than reporting. Name them when asked about
branches directly, and leave them out otherwise. The same holds for a protected
branch: nobody needs telling that `gh-pages` is still `gh-pages`.

## Deleting

```bash
gh api -X DELETE "/repos/osapi-io/$r/git/refs/heads/$b"
```

One at a time, and echo each deletion. `gh` has no bulk branch delete, and a
loop that fails halfway should leave a record of how far it got.

Never delete a local branch as part of this: the user may have work checked out
against it. This deletes remote refs only, and `git fetch --prune` is how their
clone catches up.
