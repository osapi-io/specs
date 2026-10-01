#!/usr/bin/env python3
"""Three things a script can check about the docs, so a reader does not have to.

  1. Every relative link resolves. Moving a page breaks links silently, and the
     reorganization that flattened this repository broke ten of them.
  2. Every page is linked from its component's README. An unlinked page is one
     nobody finds.
  3. No em dashes. The one rule in VOICE.md a script can enforce, and 32 of them
     had accumulated in two skills nobody was checking.

Everything else about the writing needs a reader. Exit 0 when these hold, 1 when
they do not.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SPECS = Path(__file__).resolve().parent.parent
COMPONENTS = SPECS / "components"

LINK = re.compile(r"\[[^\]]+\]\(([^)#]+\.md)(?:#[^)]*)?\)")


def docs() -> list[Path]:
    """Every markdown file somebody wrote: the pages, the skills, the root."""
    out = list(COMPONENTS.rglob("*.md"))
    out += (SPECS / ".claude").rglob("*.md")
    out += SPECS.glob("*.md")
    return sorted(set(out))


def rel(f: Path) -> str:
    return str(f.relative_to(SPECS))


def main() -> int:
    problems: list[str] = []
    files = docs()

    for f in files:
        text = f.read_text()

        for n, line in enumerate(text.splitlines(), 1):
            if "—" in line:
                problems.append(f"{rel(f)}:{n} has an em dash\n      {line.strip()[:96]}")
                break

        for m in LINK.finditer(text):
            if not (f.parent / m.group(1)).resolve().exists():
                problems.append(f"{rel(f)} links {m.group(1)}, which does not exist")

    for readme in sorted(COMPONENTS.glob("*/README.md")):
        pages = [p for p in sorted(readme.parent.glob("*.md")) if p.name != "README.md"]
        linked = {m.group(1) for m in LINK.finditer(readme.read_text())}
        for p in pages:
            if p.name not in linked:
                problems.append(f"{rel(p)} is not linked from {rel(readme)}")

    for comp in sorted(d for d in COMPONENTS.iterdir() if d.is_dir()):
        if not (comp / "README.md").exists():
            problems.append(f"{comp.name} has no README.md")

    for p in problems:
        print(f"  {p}")

    print()
    print(f"{len(files)} files checked, {len(problems)} problems")
    if problems:
        print("See VOICE.md.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
