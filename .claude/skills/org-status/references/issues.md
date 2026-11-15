# Issues

Resolve the repository set first, per [SKILL.md](../SKILL.md).

An issue is an intent that nobody works on yet. It records something that must
change, so that the intent stays when nobody works on it. The Spec Kit task list
tracks work in progress. Thus an issue with an open pull request does not wait
for anybody ([why](../../../../CONSTITUTION.md)).

## What is open

```bash
gh repo list osapi-io --no-archived --visibility public --limit 200 --json name -q '.[].name' |
while read -r r; do
  n=$(gh issue list --repo "osapi-io/$r" --state open --limit 100 --json number -q 'length')
  printf "%-22s %s\n" "$r" "$n"
done
```

`gh issue list` returns issues only. The search endpoint does not:
`gh search issues --owner osapi-io` reaches archived repositories, the same trap
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

An open pull request declares the issues that it closes. Thus ask before you
report that nobody touched an issue:

```bash
gh pr list --repo "osapi-io/$r" --state open \
  --json number,closingIssuesReferences \
  -q '.[] | "\(.number) closes \([.closingIssuesReferences[].number]|join(","))"'
```

Somebody works on an issue that is named there. It goes in the block of the pull
request, not in its own block. If the fix of an issue already merged, the issue
is open only because nobody closed it. Say so, because it looks like work that
remains.

## Trackers

A tracking issue here puts the others in a group as a markdown checklist of
links, not as GitHub sub-issues. Thus
`/repos/{owner}/{repo}/issues/{n}/sub_issues` returns nothing, and people mark
the boxes by hand. Read the tracker for the group. Read the state from the
issues themselves. The two disagree when a fix merges.

## Reporting

The `iss` column counts open issues, with the trackers. An old list of review
findings is a standing condition, not news. The count shows it. An issue gets a
block only when it is new since the last sweep, when its fix merged, or when the
question was about it.

```
🔴 osapi #494 · bug · 11d · fix merged, still open
   CLI exits 0 when a remote command fails
   https://github.com/osapi-io/osapi/issues/494
   → say "close 494" to close it against the merged PR
```

## Working one

An action line that offers a fix sends the reader to
[work-an-issue](../../work-an-issue/SKILL.md). That skill makes the issue occur
again before it changes anything. It decides if the issue is a direct fix or a
Spec Kit feature. It closes the issue through the pull request.

Reporting stops here. This skill reads by default, so an issue is worked only
when the words that ask for it arrive:

```
   → say "fix 179" to reproduce it, fix it, and close it through a PR
```

An action line has the same rule as a block. If the reader did not act on an
issue before, it does not get an action line again. An offer that comes again in
each sweep annoys the reader, and does not help.

## Writing

Closing is a write, so it needs the words that ask for it, and no issue is ever
closed to shorten a list:

```bash
gh issue close "$n" --repo "osapi-io/$r" --comment "Fixed in #<pr>."
```

Something exploitable is never opened as an issue at all. It is a draft
advisory,
which only maintainers can read. [audit.md](audit.md#reporting) has the command.
