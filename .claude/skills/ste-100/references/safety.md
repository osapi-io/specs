# Warnings and cautions

A warning is about a risk to a person or to data. A caution is about a risk to
equipment or to a system. Both use the same form.

1. Start with a clear command.
2. Then give the risk, in a short sentence.
3. Put the warning before the step it is about, never after.

| Not STE                                                                                              | STE                                                                                             |
| ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| It is important to be aware that a token with `command:shell` can be dangerous for an agent to hold. | Do not give an agent's token `command:shell`. With it, the agent can run any command on a host. |
