# pr-review-model

The review model of each osapi-io pull request. Two agents that did not write
the change review it: one for the standards of the project and one for the code.
The pull request merges only when both pass and its checks are green.

## Install

You install nothing. The skill is in this repository. Each agent that reads
skills finds it when it works from the repository root. It needs the [gh] CLI
authenticated against [osapi-io].

## Usage

Ask in plain language, or invoke it directly with `/pr-review-model`.

| Ask | You get |
| --- | --- |
| "open the pull request" | The title rule, the specs pull request first, and both queue labels |
| "review osapi#1800 for the standards" | The checklist, with the source of each rule, and how to post the result |
| "review osapi#1800 for the code" | The code checklist, and where an exploitable finding goes |
| "who merges this?" | The conditions of the merge loop |

## What it is for

On 27 November 2026 fixes merged with one-off test functions and with changes
that broke the standards. Their authors labelled them as checked. Thus an
author never certifies its own pull request now, and a different agent reads
each change.

[gh]: https://cli.github.com
[osapi-io]: https://github.com/osapi-io
