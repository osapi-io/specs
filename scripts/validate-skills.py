#!/usr/bin/env python3
"""Validate every SKILL.md against the Agent Skills specification.

https://agentskills.io/specification

`just md-fmt` excludes `.claude/**` because mdformat reads the opening `---` as
a horizontal rule and collapses YAML frontmatter into a heading. That exclusion
is correct and it leaves the skills unchecked by anything, so a stray `: ` in a
description makes a skill silently undiscoverable: the file still looks fine and
the skill simply never loads.
"""

import re
import sys
from pathlib import Path

import yaml

NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.S)


def check(skill: Path) -> list[str]:
    """Return the reasons skill fails validation, empty when it passes."""
    bad = []
    text = skill.read_text()

    matched = FRONTMATTER.match(text)
    if not matched:
        return ["no YAML frontmatter, or it does not open on line 1"]

    try:
        meta = yaml.safe_load(matched.group(1))
    except yaml.YAMLError as err:
        line = getattr(getattr(err, "problem_mark", None), "line", None)
        where = f" at frontmatter line {line + 1}" if line is not None else ""
        return [f"frontmatter is not valid YAML{where}: {getattr(err, 'problem', err)}"]

    if not isinstance(meta, dict):
        return ["frontmatter is not a mapping"]

    name = meta.get("name")
    if not name:
        bad.append("name is missing")
    elif not isinstance(name, str):
        bad.append("name is not a string")
    else:
        if not 1 <= len(name) <= 64:
            bad.append(f"name is {len(name)} characters, must be 1 to 64")
        if not NAME.fullmatch(name):
            bad.append(
                f"name {name!r} must be lowercase a-z, 0-9 and single hyphens, "
                "and may not lead or trail with one"
            )
        if name != skill.parent.name:
            bad.append(f"name {name!r} does not match directory {skill.parent.name!r}")

    description = meta.get("description")
    if not description:
        bad.append("description is missing or empty")
    elif not isinstance(description, str):
        bad.append("description is not a string")
    elif len(description) > 1024:
        bad.append(f"description is {len(description)} characters, limit is 1024")

    compatibility = meta.get("compatibility")
    if compatibility is not None and len(str(compatibility)) > 500:
        bad.append(f"compatibility is {len(str(compatibility))} characters, limit is 500")

    metadata = meta.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            bad.append("metadata is not a mapping")
        else:
            bad += [
                f"metadata.{key} is {type(value).__name__}, must be a string"
                for key, value in metadata.items()
                if not isinstance(value, str)
            ]

    body = text[matched.end():]
    lines = len(text.splitlines())
    if lines > 500:
        bad.append(f"{lines} lines, specification recommends under 500")

    for target in re.findall(r"\]\(((?:\.\./|references/)[^)#:]+\.md)\)", body):
        if not (skill.parent / target).resolve().exists():
            bad.append(f"links {target}, which does not exist")

    for ref in sorted(skill.parent.glob("references/*.md")):
        for target in re.findall(r"\]\(((?:\.\./|[a-z])[^)#:]+\.md)\)", ref.read_text()):
            if not (ref.parent / target).resolve().exists():
                bad.append(f"{ref.name} links {target}, which does not exist")

    return bad


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    skills = sorted(root.glob(".claude/skills/*/SKILL.md"))
    if not skills:
        print("no skills found under .claude/skills/")
        return 0

    failed = 0
    for skill in skills:
        reasons = check(skill)
        shown = skill.relative_to(root)
        if reasons:
            failed += 1
            print(f"FAIL {shown}")
            for reason in reasons:
                print(f"       {reason}")
        else:
            print(f"ok   {shown}")

    print(f"\n{len(skills) - failed} of {len(skills)} valid")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
