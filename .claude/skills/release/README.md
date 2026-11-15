# release

Answers "does this repository need a tag, which number, and will the tag really
make a release?". Thus a release needs one prompt, not a guess that publishes
something that you cannot remove.

A release here is one thing: a git tag. GoReleaser watches for `v*`. It builds
what the repository builds, writes the changelog, and makes the GitHub release.
The skill covers the decisions and the checks. It does not run anything by hand.

## Install

You install nothing. The skill is in this repository. Each agent that reads
skills finds it when it works from the repository root. It needs the [gh] CLI,
authenticated against [osapi-io], and a checkout of the repository to release.

## Usage

Ask in plain language, or invoke it directly with `/release`.

| Ask                                           | You get                                                           |
| --------------------------------------------- | ----------------------------------------------------------------- |
| "release gohai"                                | Whether it needs one, the number with the reasoning, and the tag   |
| "why does the badge say no releases?"          | Usually a tag that landed while the workflow failed to publish     |
| "why does go get give me a pseudo-version?"    | Usually a tag the module proxy rejects, like `v1.0`                |
| "can we re-tag that, it was the wrong number?" | No, and what the checksum database does to anyone who tries        |

## What it does

There are five steps:

1. Find if a tag is necessary.
1. Select the number. Read what merged to decide.
1. Check that the workflow can authenticate.
1. Push the tag.
1. Confirm that the version got to the Go module proxy.

## What it is for

Four traps, three of which this organization hit in one afternoon.

A valid tag is not always current. gohai had a good `v1.0.0`, and eighty-one
commits after it. In that case, the tag list looks correct.

Go requires versions with three parts. `v1.0` is not one. Thus nats-client and
nats-server served pseudo-versions, but looked released.

If a tag starts a workflow that cannot authenticate, the result is a tag with no
release. Nobody can take back the tag.

A version that the module proxy got is in `sum.golang.org` permanently. If you
move that tag, `go get` reports a checksum mismatch. Go treats that as
tampering, not as an error.

The version rule is to read what landed rather than count it. Seven `feat:`
commits that add exported functions are a minor release; two that add a justfile
recipe are a patch. Counting gets this backwards, and did.

## License

The [MIT](../../../LICENSE) License.

[gh]: https://cli.github.com
[osapi-io]: https://github.com/osapi-io
