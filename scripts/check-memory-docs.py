#!/usr/bin/env python3
"""Hold the documentation contract that `global/baseline` states.

Memory is documentation. The fragment says what that means and archival reads it,
but an instruction is obeyed by whoever remembers it. These checks fail instead.

What is enforced:

  1. No specification scaffolding. A `MUST`, an `FR-` label, a user story, a
     success criterion or an acceptance scenario in memory means an archival
     copied the feature's form instead of converting it.
  2. No em dashes, which is the machine tell that survives every other pass.
  3. Every link resolves, so the tree is navigable rather than nominally linked.
  4. Every subject document is reachable from its component's entry point. An
     unlinked document is one nobody will find.
  5. Every component has an entry point at all.

What is not enforced, and cannot be: whether the prose is any good. A count that
moves fails `memory-check`; a paragraph that drifts from the code does not. Only a
reader catches that, and every reading so far has caught something.

Exit 0 when the contract holds, 1 when it does not.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SPECS = Path(__file__).resolve().parent.parent
COMPONENTS = SPECS / "components"

# A changelog is an audit trail of what each archival did, so it keeps the
# feature identifiers it is recording. Everything else is documentation.
EXEMPT = {"changelog.md", "constitution.md"}

SCAFFOLDING = [
    (re.compile(r"\bMUST\b"), "normative MUST; memory states what is, not what is required"),
    (re.compile(r"^\s*-?\s*\*\*FR-\d"), "an FR- label; memory carries no requirement identifiers"),
    (re.compile(r"^#+\s*User Stor", re.I), "a user story; that belongs to the feature that was reviewed"),
    (re.compile(r"^\s*-?\s*\*\*SC-\d"), "an SC- label; success criteria belong to the feature"),
    (re.compile(r"^\s*-?\s*\*\*(Given|When|Then)\*\*"), "an acceptance scenario"),
    (re.compile(r"^#+\s*(Success Criteria|Measurable Outcomes|Acceptance)", re.I), "a feature-review heading"),
    (re.compile(r"\[Source: specs/"), "a per-paragraph source footer; memory names its feature once, at the end"),
]

LINK = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#[^)]*)?\)")
INLINE_CODE = re.compile(r"`[^`]*`")


def prose(line: str) -> str:
    """The line with inline code removed.

    A backticked `MUST` is being named, not used. The rule that forbids the word
    has to be able to say the word, and so does a table describing these checks.
    """
    return INLINE_CODE.sub("", line)


def memory_docs() -> list[Path]:
    out = []
    for root in list(COMPONENTS.glob("*/.specify/memory")) + [SPECS / "system/.specify/memory"]:
        for f in sorted(root.rglob("*.md")):
            if f.name not in EXEMPT:
                out.append(f)
    return out


def rel(f: Path) -> str:
    return str(f.relative_to(SPECS))


def main() -> int:
    problems: list[str] = []
    docs = memory_docs()

    for f in docs:
        text = f.read_text()
        lines = text.splitlines()

        for pattern, why in SCAFFOLDING:
            for n, line in enumerate(lines, 1):
                if pattern.search(prose(line)):
                    problems.append(f"{rel(f)}:{n} holds {why}\n      {line.strip()[:96]}")
                    break  # one report per pattern per file is enough to act on

        for n, line in enumerate(lines, 1):
            if "—" in line:
                problems.append(f"{rel(f)}:{n} holds an em dash\n      {line.strip()[:96]}")
                break

        for m in LINK.finditer(text):
            target = (f.parent / m.group(1)).resolve()
            if not target.exists():
                problems.append(f"{rel(f)} links to {m.group(1)}, which does not exist")

    # Every subject document reachable from its component's entry point.
    for entry in sorted(COMPONENTS.glob("*/.specify/memory/spec.md")):
        subjects = sorted((entry.parent / "architecture").glob("*.md")) if (entry.parent / "architecture").is_dir() else []
        if not subjects:
            continue
        linked = {m.group(1) for m in LINK.finditer(entry.read_text())}
        for s in subjects:
            want = f"architecture/{s.name}"
            if want not in linked:
                problems.append(f"{rel(s)} is not linked from {rel(entry)}; nobody will find it")

    # Every component has an entry point.
    for comp in sorted(COMPONENTS.iterdir()):
        if not comp.is_dir():
            continue
        if not (comp / ".specify/memory/spec.md").exists():
            problems.append(f"{comp.name} has no memory/spec.md; it has no documentation")

    for p in problems:
        print(f"  {p}")

    print()
    print(f"{len(docs)} documents checked, {len(problems)} problems")
    if problems:
        print("Memory is documentation. See global/baseline in the constitution.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
