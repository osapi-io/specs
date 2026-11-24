# Words

## One word, one meaning

Use a word in one sense only, and use one word for one thing.

| Not STE | STE |
| --- | --- |
| The agent picks up the job. Then it picks the provider. | The agent receives the job. Then it selects the provider. |
| Restart the daemon. The service then reads the config. | Restart the agent. The agent then reads its configuration. |

Decide the terms before you write. On a long page, list them.

## The simplest common word

Use the most common word with its first dictionary meaning.

| Not STE | STE |
| --- | --- |
| utilize | use |
| initiate | start |
| ensure | make sure |
| prior to | before |
| in order to | to |

## Technical names and technical verbs

A technical name is allowed as it is: a command, a flag, a file, a field, a
product. Write it in code format: `osapi skill install`, `--target`, `osapi.yaml`.

A technical verb is allowed only where no common verb says it: deploy, compile,
mount. Do not use one where a common verb works.

## No phrasal verbs

| Not STE | STE |
| --- | --- |
| set up the token | make the token |
| look into the failure | examine the failure |
| carry out the cutover | do the cutover |

## Noun clusters

No more than three words in a noun cluster. Break a longer one with "of" or a
clause.

| Not STE | STE |
| --- | --- |
| the agent behavior settings file path | the path of the file that holds the behavior settings |
