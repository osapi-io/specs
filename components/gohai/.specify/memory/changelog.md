# Changelog

## Merged Features Log

### A baseline for gohai — archived 2026-09-29

**Branch:** `001-gohai-baseline`

**Spec:** [specs/001-gohai-baseline/spec.md](../../specs/001-gohai-baseline/spec.md)

**What was added:** gohai's first memory. It was empty before this, so the file a
skill reads first said nothing about the repository it describes.

- The collector contract: a five-method interface, ten categories closed by
  constants, `DefaultEnabled` as the opt-out for heavy or privileged collectors, and
  `Dependencies` with `PriorResults` and `GetDep[T]` for reading what ran before.
- The registry's exported surface, and that it runs collectors in topological levels
  derived from their declared dependencies rather than in registration order.
- The OCSF conversion and the generated JSON schema.
- Four counts, each with the command that reproduces it: 314 Go files, 205 not
  tests, 62 collectors, 10 categories.

**The decision most worth preserving:** the 62 collectors are stated **by the
contract they share, not one requirement each** (FR-004). Sixty-two requirements
would rot on every addition, would state nothing `ls` does not, and would bury the
four rules that actually bind. gohai's own catalogue is the maintained enumeration,
so the corpus cites it. A later reader who does not find this reasoning will be
tempted to expand it into 62 entries.

**New Components:** none. Nothing landed in the gohai repository — the deliverable
is the inventory, which is what CONTRIBUTING requires of a baseline.

**Gaps found, and since corrected by gohai:**

- gohai's prose said **65 collectors** where 62 packages exist. A definition rather
  than an error: the catalogue carries an `Implemented` column and three entries —
  `rackspace`, `softlayer`, `eucalyptus` — are deprecated with no package.
- It said **9 categories** in two places where ten are declared and all ten are in
  use. Simply wrong.

Both were corrected by gohai in its own change, `gohai#201`, which is where a
correction to that repository belongs. That change also found a **third** defect
neither requirement had: the catalogue's legend defined `✅` twice, once as
"implemented and tested" and once as "planned", making the column unreadable given
that 62 of its 65 rows are ticks. It surfaced only because reconciling 65 against 62
meant reading the legend — the argument for pairing a count with its command rather
than stating the count alone.

No `tasks.md`: a baseline has no ordered work to break down, the same shape osapi's
provider contract had.
