# ste-100

Answers "is this clear to a reader whose first language is not English?". It
writes and checks documentation in ASD-STE100 Simplified Technical English.

## Install

You install nothing. The skill is in this repository. Each agent that reads
skills finds it when it works from the repository root.

## Usage

Ask in plain language, or invoke it directly with `/ste-100`.

| Ask | You get |
| --- | --- |
| `rewrite this page in STE` | The page in STE, with the terms it settled on |
| `check this procedure against STE` | Each sentence that breaks a rule, the rule, and its rewrite |
| `write the install steps in STE` | A procedure: commands, one instruction a sentence |
| `is this warning STE?` | The warning rewritten: command first, then the risk |

## How it works

STE is a set of rules. The skill reads a rule only when the text needs it.
`SKILL.md` classifies each paragraph as a procedure, a description or a safety
instruction. Then it sends the agent to the reference for that kind of text, and
for its words and sentences. Nothing else goes into the context.

It decides sentences, not content. What a page says still comes from the house
[voice](../document/references/voice.md), and `unslop` still runs after.

The STE dictionary of approved words belongs to ASD, and is not included. The
skill applies the rules and the one-word, one-meaning principle without it.

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
router. A rule and its examples go in the reference for that kind of text, which
loads only when the text needs it.

Do not run mdformat on this directory. `just md-fmt` already excludes
`.claude/**`. mdformat reads the first `---` as a horizontal rule, and changes
the YAML frontmatter into a heading. Then agents cannot find the skill, and
nothing reports it.

## License

The [MIT] License.

[agent skills specification]: https://agentskills.io/specification
[mit]: ../../../LICENSE
