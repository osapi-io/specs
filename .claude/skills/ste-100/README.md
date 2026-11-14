# ste-100

Answers "is this clear to a reader whose first language is not English?" by
writing and checking documentation in ASD-STE100 Simplified Technical English.

## Install

Nothing to install. The skill lives in this repository and any skills-aware
agent working from the repository root finds it.

## Usage

Ask in plain language, or invoke it directly with `/ste-100`.

| Ask | You get |
| --- | --- |
| `rewrite this page in STE` | The page in STE, with the terms it settled on |
| `check this procedure against STE` | Each sentence that breaks a rule, the rule, and its rewrite |
| `write the install steps in STE` | A procedure: commands, one instruction a sentence |
| `is this warning STE?` | The warning rewritten: command first, then the risk |

## How it works

STE is a rule set looked up as the text needs it. `SKILL.md` classifies each
paragraph as a procedure, a description or a safety instruction, then routes to
the reference for that kind of text and for the words and sentences in it.
Nothing else enters context.

It decides sentences, not content. What a page says still comes from the house
[voice](../document/references/voice.md), and `unslop` still runs after.

The STE dictionary of approved words belongs to ASD and is not included. The
skill applies the writing rules and the one-word, one-meaning principle without
it.

## Documentation

| File | Covers |
| --- | --- |
| [SKILL.md](SKILL.md) | Classifying text, routing, the report shape |
| [references/words.md](references/words.md) | One word, one meaning; common words; technical names and verbs; phrasal verbs; noun clusters |
| [references/sentences.md](references/sentences.md) | Length, one topic, verb forms, -ing forms, voice, articles, lists |
| [references/procedures.md](references/procedures.md) | Commands, one instruction a sentence, conditions, notes, numbered steps |
| [references/descriptions.md](references/descriptions.md) | Main point first, one topic, six sentences, naming who acts |
| [references/safety.md](references/safety.md) | Warnings and cautions: command first, then the risk |
| [references/checking.md](references/checking.md) | Reviewing existing text and reporting what breaks a rule |

Format details are in the [Agent Skills specification].

## Contributing

See the [Contributing](../../../CONTRIBUTING.md) guide. Keep `SKILL.md` a
router: a rule and its examples belong in the reference for that kind of text,
which loads only when the text needs it.

Do not run mdformat over this directory. `just md-fmt` already excludes
`.claude/**`, because mdformat reads the opening `---` as a horizontal rule and
collapses YAML frontmatter into a heading, which makes a skill silently
undiscoverable.

## License

The [MIT] License.

[agent skills specification]: https://agentskills.io/specification
[mit]: ../../../LICENSE
