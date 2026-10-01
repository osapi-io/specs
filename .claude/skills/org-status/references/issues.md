# Issues

Resolve the repository set first, per [SKILL.md](../SKILL.md).

An issue is an intent nobody is working on yet: something that should change,
recorded so it survives being put down. Work under way is tracked by its Spec Kit
task list instead, so an issue with a pull request already open against it is not
waiting on anyone
([why](../../../../CONSTITUTION.md)).

## What is open

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  n=$(gh issue list --repo "osapi-io/$r" --state open --limit 100 --json number -q 'length')
  printf "%-22s %s\n" "$r" "$n"
done
```

`gh issue list` returns issues only. The search endpoint does not: `gh search
issues --owner osapi-io` reaches archived repositories, the same trap
`--no-archived` exists to avoid for pull requests.

Detail for a repository with a non-zero count:

```bash
gh issue list --repo "osapi-io/$r" --state open --limit 100 \
  --json number,title,labels,createdAt \
  -q '.[] | "\(.number)\t\([.labels[].name]|join(","))\t\(.createdAt[:10])\t\(.title)"'
```

Labels carry the kind (`bug`, `enhancement`) and the area (`kind/go`). Neither
says whether anyone has started.

## What is already in hand

An open pull request declares the issues it closes, so ask before reporting an
issue as untouched:

```bash
gh pr list --repo "osapi-io/$r" --state open \
  --json number,closingIssuesReferences \
  -q '.[] | "\(.number) closes \([.closingIssuesReferences[].number]|join(","))"'
```

An issue named there is in flight, and belongs in the pull request block rather
than in a block of its own. An issue whose fix has already merged is still open
only because nobody closed it — say so, because it reads as outstanding work.

## Trackers

A tracking issue here groups the others as a markdown checklist of links, not as
GitHub sub-issues, so `/repos/{owner}/{repo}/issues/{n}/sub_issues` returns
nothing and the boxes are ticked by hand. Read the tracker for the grouping and
read the state from the issues themselves; the two disagree the moment a fix
merges.

## Reporting

The `iss` column counts open issues, trackers included. A long-standing list of
review findings is a standing condition, not news: the count carries it, and a
block is earned by an issue that is new since the last sweep, one whose fix has
merged, or one the question was about.

```
🔴 osapi #494 · bug · 11d · fix merged, still open
   CLI exits 0 when a remote command fails
   https://github.com/osapi-io/osapi/issues/494
   → say "close 494" to close it against the merged PR
```

## Writing

Closing is a write, so it needs the words that ask for it, and no issue is ever
closed to shorten a list:

```bash
gh issue close "$n" --repo "osapi-io/$r" --comment "Fixed in #<pr>."
```

Something exploitable is never opened as an issue at all. It is a draft advisory,
per [triage.md](triage.md).
