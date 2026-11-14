# Checking text against STE

1. Classify each paragraph: procedure, description, or safety instruction.
2. List the terms. Mark each thing with two names and each name used for two
   things. See [words.md](words.md).
3. Read each sentence against [sentences.md](sentences.md) and the reference
   for its kind of text.
4. Count the words in every sentence that looks long. A command or an
   identifier counts as one word.
5. Report each sentence that breaks a rule, the rule, and its rewrite, in page
   order.

A sentence that breaks a rule is rewritten, not excused. If the rewrite would
lose technical meaning, split the sentence instead of cutting the meaning.

Then run the repository's format and test recipes through `mise exec -- just`.
