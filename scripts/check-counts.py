#!/usr/bin/env python3
"""Run every count in every component's memory against the command beside it.

`global/baseline` says a count is written with the command that produces it,
because a number alone is a claim that was true when somebody typed it. This
turns that from a convention into a check: it finds the measurement tables in
`components/*/`, runs each command in the repository the
memory describes, and fails when a value has moved.

A memory table row looks like this:

    | Go files | 12 | `find . -name '*.go' -not -path './.git/*' \\| wc -l` |

Three columns, the middle one an integer, the third a command in backticks.
Rows whose command is prose ("the same, plus ...") inherit the previous row's
command and append their own difference, so they are resolved against the row
above.

Exit codes: 0 all counts current, 1 a count has moved, 2 a command could not
run. A missing target repository is skipped with a note rather than failed,
because a contributor without every clone is not a broken corpus.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_PARENT = Path.home() / "git" / "osapi-io"
SPECS = Path(__file__).resolve().parent.parent

ROW = re.compile(r"^\|\s*(?P<label>[^|]+?)\s*\|\s*(?P<value>[\d,]+)\s*\|\s*(?P<cmd>.+?)\s*\|\s*$")
BACKTICKED = re.compile(r"`([^`]+)`")

# A count inside a shell block, written as the command and its expected value:
#
#     grep -c foo bar.go   # 8
#
# Memory uses this form wherever a measurement does not belong in a table, so it
# has to be checked the same way. Only an integer comment opts a line in; a
# comment in words ("the same version twice") is prose and is left alone.
# Every fence, with whatever language it declares. Matching only shell fences
# desynchronizes the toggle: a ```go block's opening line would not match while
# its closing ``` would, so everything after it reads as inside a shell block.
FENCE = re.compile(r"^\s*```\s*(?P<lang>[A-Za-z0-9_+-]*)\s*$")
SHELL_LANGS = {"", "sh", "bash", "shell", "console", "zsh"}
# The comment may name what the number counts ("# 8 guards"), which reads better
# than a bare figure. What it may not do is start with something that only looks
# like a count: a version ("# 1.0.0"), a date, or a path are excluded by refusing
# a digit run followed by . - / or :.
ANNOTATED = re.compile(
    r"^(?P<cmd>[^#]+?)\s+#\s*(?P<value>\d[\d,]*)(?![\d.\-/:])[ ,]*(?P<note>[A-Za-z][^#]*)?$"
)


def command_in(cell: str) -> str | None:
    """The runnable command a table cell holds, or None.

    A cell must hold one complete command. "the same, plus X" is a shortcut for
    whoever wrote the table and cannot be run by anything, so it is reported as
    a defect rather than reconstructed: a count whose command needs the row above
    it to be understood is a count nobody can check in isolation.
    """
    if "the same" in cell.lower():
        return None
    parts = BACKTICKED.findall(cell)
    if not parts:
        return None
    # Markdown escapes a pipe inside a table cell. Undo that before running.
    return max(parts, key=len).replace(r"\|", "|")


def annotated_counts(text: str) -> list[tuple[str, int, str]]:
    """Every `command  # N` line inside a fenced shell block.

    A command that changes directory or reaches outside the repository is left
    alone: it cannot be run in the repository the memory describes, which is the
    only place a count means anything.
    """
    out = []
    in_block = False   # inside any fenced block
    is_shell = False   # and that block declared a shell language
    for line in text.splitlines():
        fence = FENCE.match(line)
        if fence:
            if in_block:
                in_block = is_shell = False
            else:
                in_block = True
                is_shell = fence.group("lang").lower() in SHELL_LANGS
            continue
        if not (in_block and is_shell):
            continue
        m = ANNOTATED.match(line)
        if not m:
            continue
        cmd = m.group("cmd").strip()
        if cmd.startswith("cd ") or cmd.startswith("for ") or "~/" in cmd:
            continue
        out.append((cmd[:60], int(m.group("value").replace(",", "")), cmd))
    return out


def run(cmd: str, cwd: Path) -> tuple[int | None, str]:
    try:
        out = subprocess.run(
            cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=120
        )
    except subprocess.TimeoutExpired:
        return None, "timed out"
    if out.returncode != 0:
        return None, (out.stderr or out.stdout).strip().splitlines()[:1][0] if (out.stderr or out.stdout).strip() else f"exit {out.returncode}"
    text = out.stdout.strip()
    if not text:
        return None, "no output"
    try:
        return int(text.split()[0]), ""
    except ValueError:
        return None, f"not a number: {text[:40]}"


def main() -> int:
    checked = moved = broken = skipped = 0
    partial: list[tuple[str, str]] = []
    for memory in sorted(SPECS.glob("components/*/*.md")):
        component = memory.relative_to(SPECS / "components").parts[0]
        target = REPO_PARENT / component
        rows = []
        in_table = False
        for line in memory.read_text().splitlines():
            # Only measurement tables are checked, and a measurement table
            # declares a Command column in its header. Without that opt-in a
            # table of recipe names reads as a table of commands, because both
            # hold backticks and an integer.
            if line.startswith("|") and "Command" in line and "Value" in line:
                in_table = True
                continue
            if in_table and not line.startswith("|"):
                in_table = False
            if not in_table:
                continue
            m = ROW.match(line)
            if not m:
                continue
            label = m.group("label").strip()
            if label.lower() in {"measurement", "count", "module", "consumer"} or set(label) <= set("-: "):
                continue
            try:
                expected = int(m.group("value").replace(",", ""))
            except ValueError:
                continue
            cell = m.group("cmd")
            cmd = command_in(cell)
            if cmd is None:
                if "the same" in cell.lower():
                    partial.append((component, label))
                continue
            rows.append((label, expected, cmd))
        rows.extend(annotated_counts(memory.read_text()))
        if not rows:
            continue
        if not target.is_dir():
            print(f"  {component}: {len(rows)} counts skipped, no clone at {target}")
            skipped += len(rows)
            continue
        for label, expected, cmd in rows:
            actual, err = run(cmd, target)
            checked += 1
            if actual is None:
                print(f"  {component} / {label}: command failed ({err})")
                print(f"      {cmd}")
                broken += 1
            elif actual != expected:
                print(f"  {component} / {label}: memory says {expected}, command returns {actual}")
                print(f"      {cmd}")
                moved += 1

    if partial:
        print()
        for component, label in partial:
            print(f"  {component} / {label}: command reads 'the same, plus ...' and cannot be run")
        print("  A count whose command needs the row above it cannot be checked alone.")

    print()
    print(
        f"{checked} counts checked, {moved} moved, {broken} commands failed, "
        f"{len(partial)} not runnable, {skipped} skipped"
    )
    if moved:
        print("A count has moved. Update memory and say when it was re-measured.")
        return 1
    if broken or partial:
        print("A command in memory does not run. A count nobody can reproduce is a claim.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
