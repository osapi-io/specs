## Why

Labels were written once and not revisited as repositories changed. Three kinds
of file have no label, three labels match nothing, and two labels overlap.

**Kinds with no label:**

| Kind        | Files | Where            |
| ----------- | ----- | ---------------- |
| justfiles   | 20    | every repository |
| TypeScript  | 468   | `osapi`          |
| Dockerfiles | 3     | `osapi`          |

**Labels matching nothing:**

| Label       | Repository                 | Reality                                        |
| ----------- | -------------------------- | ---------------------------------------------- |
| `kind/bats` | `osapi-justfiles`          | no `.bats` file exists; the module was removed |
| `kind/go`   | `osapi-justfiles`, `specs` | neither holds Go                               |
| `test/unit` | `specs`                    | matches `**/*_test.go`                         |

**Overlap:** `github/action` matches `.github/**/*.yml`, which `kind/yaml`
already matches in full, so every workflow change carries both. It is also the
only label not prefixed `kind/`.

## What Changes

- A repository labels the kinds of file it holds, and nothing else
- The same kind carries the same label name everywhere
- Labels do not overlap, and prefixes are consistent

## Impact

- `code-architecture` — two added requirements
- Seven repositories' `.github/labeler.yml`
