# release

Answers "does this repository need a tag, which number, and will the tag actually
produce a release?" so cutting one is a prompt rather than a guess that publishes
something you cannot withdraw.

A release here is one thing: a git tag. GoReleaser watches for `v*`, builds
whatever the repository builds, writes the changelog, and creates the GitHub
release. The skill covers deciding and checking, not running anything by hand.

## Install

Nothing to install. The skill lives in this repository and any skills-aware agent
working from the repository root finds it. It needs the [gh] CLI authenticated
against [osapi-io] and a checkout of whatever is being released.

## Usage

Ask in plain language, or invoke it directly with `/release`.

| Ask                                           | You get                                                           |
| --------------------------------------------- | ----------------------------------------------------------------- |
| "release gohai"                                | Whether it needs one, the number with the reasoning, and the tag   |
| "why does the badge say no releases?"          | Usually a tag that landed while the workflow failed to publish     |
| "why does go get give me a pseudo-version?"    | Usually a tag the module proxy rejects, like `v1.0`                |
| "can we re-tag that, it was the wrong number?" | No, and what the checksum database does to anyone who tries        |

## What it does

Five steps: work out whether a tag is needed at all, pick the number by reading
what landed, check the workflow can authenticate, push the tag, and confirm the
version reached the Go module proxy.

## What it is for

Four traps, three of which this organization hit in one afternoon.

A valid tag is not a current one. gohai had a good `v1.0.0` and eighty-one
commits sitting behind it, and the tag list looks healthy in exactly that case.

Go requires three-part versions. `v1.0` is not one, so nats-client and
nats-server served pseudo-versions while appearing released.

A tag that fires a workflow which cannot authenticate leaves a tag with no
release, and the tag is the half that cannot be taken back.

A version the module proxy has fetched is in `sum.golang.org` permanently.
Moving that tag makes `go get` report a checksum mismatch, which Go treats as
tampering rather than as a mistake.

The version rule is to read what landed rather than count it. Seven `feat:`
commits that add exported functions are a minor release; two that add a justfile
recipe are a patch. Counting gets this backwards, and did.

## License

The [MIT](../../../LICENSE) License.

[gh]: https://cli.github.com
[osapi-io]: https://github.com/osapi-io
