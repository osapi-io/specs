"""Check the pages of this repository against the documentation contract.

- Each relative link points to a file that exists, and each #anchor to a
  heading in that file.
- Each skill's SKILL.md starts with YAML frontmatter that has a name and a
  description. Without it, an agent does not find the skill.
- No page has an em dash, a requirement identifier (FR-001, SC-002, NFR-003),
  a user story, an acceptance scenario, or "MUST" outside quotes and code.

templates/ holds files for other repositories, so their links are not checked.
"""

import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = ("node_modules", ".just", ".git", ".specify")
CODE = re.compile(r"```.*?```", re.S)
INLINE = re.compile(r"`[^`\n]*`")
RULES = [
    (re.compile("—"), "em dash"),
    (re.compile(r"\b(?:FR|SC|NFR)-\d{3}\b"), "requirement identifier"),
    (re.compile(r"\bUser Stor(?:y|ies)\b"), "user story"),
    (re.compile(r"\bAcceptance Scenarios?\b"), "acceptance scenario"),
    (re.compile(r'(?<!")\bMUST\b(?!")'), "MUST"),
]
EXEMPT = {"CODE_OF_CONDUCT.md", "AI_POLICY.md", "LICENSE"}


def pages():
    # The pages are what git has or would add: tracked files and new ones,
    # without what .gitignore leaves out. A walk of the tree also read the
    # pages of a local worktree in .worktrees/, on another branch.
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    for p in sorted(ROOT / f for f in listed):
        if not p.exists():
            continue
        rel = p.relative_to(ROOT)
        if any(part in SKIP for part in rel.parts) or rel.name in EXEMPT:
            continue
        if ".agents" in rel.parts:
            continue
        yield p


def slug(heading):
    h = INLINE.sub(lambda m: m.group(0)[1:-1], heading.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def anchors(path, cache={}):
    if path not in cache:
        text = CODE.sub("", path.read_text())
        cache[path] = {slug(h) for h in re.findall(r"^#+ (.*)$", text, re.M)}
    return cache[path]


def prose(text):
    return INLINE.sub("", CODE.sub("", text))


def main():
    problems = []
    for p in pages():
        rel = p.relative_to(ROOT)
        raw = p.read_text()
        text = prose(raw)
        lines = text.splitlines()
        for n, line in enumerate(lines, 1):
            for rx, what in RULES:
                if rx.search(line):
                    problems.append(f"{rel}: {what}: {line.strip()[:100]}")
        if rel.parts[0] == "templates":
            continue
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            file, _, anchor = target.partition("#")
            dest = (p.parent / file).resolve() if file else p
            if not dest.exists():
                problems.append(f"{rel}: missing link target: {target}")
            elif anchor and dest.suffix == ".md" and anchor not in anchors(dest):
                problems.append(f"{rel}: missing anchor: {target}")
    for skill in sorted((ROOT / ".claude" / "skills").glob("*/SKILL.md")):
        head = skill.read_text().split("\n---", 1)[0]
        rel = skill.relative_to(ROOT)
        if not head.startswith("---\n"):
            problems.append(f"{rel}: no YAML frontmatter")
        for key in ("name", "description"):
            if not re.search(rf"^{key}:", head, re.M):
                problems.append(f"{rel}: frontmatter has no {key}")
    for line in problems:
        print(line)
    print(f"{len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
