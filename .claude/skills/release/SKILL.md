---
name: release
description: Cut a release for an osapi-io Go repository. Works out whether a tag is needed and which number it should be, checks the release workflow will actually publish, pushes the tag, and confirms the result reached the Go module proxy. Use when asked to release, tag, cut a version, bump a version, or publish a repository, and when asked why a release failed, why a badge shows no release, or why `go get` resolves a pseudo-version.
compatibility: Requires the gh CLI authenticated against osapi-io, and a checkout of the repository being released.
license: MIT
metadata:
  author: osapi-io
  source: https://github.com/osapi-io/specs
---

# Release

A release here is one thing: a git tag. GoReleaser watches for `v*`, builds
whatever the repository builds, writes the changelog, and creates the GitHub
release. Nothing else is run by hand.

Two facts decide everything in this skill. Go resolves versions from tags and
has never heard of GitHub releases. And a version, once the module proxy has
fetched it, can never be changed.

## 1. Decide whether a tag is needed at all

A valid tag is not the same as a current one.

```bash
r=<repo>
gh api "repos/osapi-io/$r/tags" --jq '[.[].name] | join(", ")'
gh api "repos/osapi-io/$r/compare/<latest-tag>...main" --jq '.ahead_by'
curl -s "https://proxy.golang.org/github.com/osapi-io/$r/@v/list"
```

The three answers disagree more often than not. gohai had a perfectly valid
`v1.0.0` and eighty-one commits sitting behind it. nats-client and nats-server
were tagged `v1.0`, which the proxy ignores, so both served pseudo-versions
while looking released.

An empty proxy list on a repository that has tags means the tags are not valid
Go versions. Go requires three parts: `v1.0` is not a version, `v1.0.0` is.

Not every repository takes a tag. osapi-justfiles is consumed by curling from
`refs/heads/main` and specs is documentation. Neither has release machinery and
neither should get a tag.

## 2. Pick the number

Read what landed. Do not count it, and do not guess from the diff size.

```bash
gh api "repos/osapi-io/$r/compare/<latest-tag>...main" \
  --jq '.commits[].commit.message | split("\n")[0]' | grep '^feat'
```

Then read the list and ask which of those changed what a consumer can call.
A `feat:` that adds a justfile recipe or a coverage gate is a patch. A `feat:`
that adds an exported function is a minor bump.

Counting gets this backwards, and did. nats-client had seven `feat:` commits
and nats-server two, which looked like the larger release was nats-client's by
a wide margin and the smaller one nearly nothing. In fact nats-client's seven
were Object Store support, core Subscribe and PublishCore, KV CreateOrUpdate
and OTel trace propagation, all API, while nats-server's two were a justfile
recipe and a coverage gate and touched no consumer at all. The recommendation
that came out of counting was `v1.0.1` for the one with seven API additions
and `v1.1.0` for the one with none.

A repository that has never been tagged starts at `v0.1.0`, because `v1.0.0` is
a promise about API stability, and a library makes that promise once.

The first release of an application is a product decision rather than a
mechanical one. Ask instead of picking.

## 3. Check the workflow will publish

A tag that fires a workflow that cannot authenticate leaves a tag with no
release, and the tag is the half that cannot be taken back.

```bash
gh api "repos/osapi-io/$r/contents/.github/workflows/release.yml" --jq .content \
  | base64 -d | grep -n 'GITHUB_TOKEN:'
```

It must read `${{ secrets.GITHUB_TOKEN }}`. A `secrets.GH_PAT` here is a bug.
No repository in this organization publishes outside itself, so none of them
needs a personal token:

```bash
gh api "repos/osapi-io/$r/contents/.goreleaser.yaml" --jq .content | base64 -d \
  | grep -E '^(brews|dockers|nfpms|aurs|scoops|publishers|winget):'
```

If that prints nothing, the built-in token is sufficient and the workflow
already grants `contents: write`. A PAT expires; the built-in token cannot.

## 4. Tag it

```bash
cd ~/git/osapi-io/$r
git checkout main && git pull
git tag vX.Y.Z && git push origin vX.Y.Z
```

The push is the release. Watch it land:

```bash
gh run watch -R "osapi-io/$r" "$(gh run list -R "osapi-io/$r" \
  --workflow=release.yml --limit 1 --json databaseId --jq '.[0].databaseId')"
```

## 5. Confirm it reached the proxy

The GitHub release is for people. This is the one consumers use.

```bash
curl -s "https://proxy.golang.org/github.com/osapi-io/$r/@v/vX.Y.Z.info"
```

The `@v/list` endpoint lags by minutes, so a specific `.info` is the real
answer.

## When a release fails after the tag landed

Do not delete the tag. If the proxy fetched the version, it is in
`sum.golang.org` permanently, and that database is append-only:

```bash
curl -s "https://sum.golang.org/lookup/github.com/osapi-io/$r@vX.Y.Z"
```

Anything there is published forever. Re-pointing the tag at a different commit
makes `go get` report a checksum mismatch, which Go treats as tampering rather
than as a mistake, and every consumer sees it.

Fix the cause, then create the missing release against the tag that already
exists:

```bash
gh release create vX.Y.Z -R "osapi-io/$r" --generate-notes
```

Re-running the failed workflow does not work. A re-run uses the workflow file
as it was at that tag's commit, so a token fix merged afterwards is not in it,
and it fails again identically.
