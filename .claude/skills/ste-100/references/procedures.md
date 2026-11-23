# Procedures

A procedure tells the reader what to do. Read [sentences.md](sentences.md) too:
a procedure sentence has 20 words or fewer.

## Write a command

Write each instruction in the imperative.

| Not STE                       | STE            |
| ----------------------------- | -------------- |
| You should now run the tests. | Run the tests. |

## One instruction in each sentence

Unless the reader must do two actions at the same time.

| Not STE                                  | STE                                           |
| ---------------------------------------- | --------------------------------------------- |
| Build the binary and copy it to the hub. | Build the binary. Copy the binary to the hub. |

## Condition first

| Not STE                                   | STE                                        |
| ----------------------------------------- | ------------------------------------------ |
| Read the log if the agent does not start. | If the agent does not start, read the log. |

## Notes are not steps

Information that is not an instruction goes in a note after the step.

| Not STE                                        | STE                                                        |
| ---------------------------------------------- | ---------------------------------------------------------- |
| Run `just test`, which also checks the format. | Run `just test`. Note: `just test` also checks the format. |

## Number the steps

Steps in order are a numbered list. One step, one number.
