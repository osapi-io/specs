"""Run each count a page states against the repository the page describes.

A count is a line in a sh or bash code block that ends with a comment that
starts with a number, such as `ls -d pkg/*/ | wc -l   # 62`. The page under
components/<repo>/ describes <repo>. The command runs in a checkout of that
repository, and its output must be the number in the comment.

A checkout comes from OSAPI_IO_ROOT (default: the parent of this repository),
or is cloned into .just/repos when it is not there.
"""

import os
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = pathlib.Path(os.environ.get("OSAPI_IO_ROOT", ROOT.parent))
CACHE = ROOT / ".just" / "repos"
FENCE = re.compile(r"^```(sh|bash)\s*$")
COUNT = re.compile(r"^(?P<cmd>.*\S)\s+#\s*(?P<want>[0-9][0-9,]*)\b")


def checkout(repo):
    local = BASE / repo
    if (local / ".git").exists():
        return local
    dest = CACHE / repo
    if not dest.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "-q", "--depth", "1",
             f"https://github.com/osapi-io/{repo}.git", str(dest)],
            check=True,
        )
    return dest


def counts(page):
    inside = False
    for n, line in enumerate(page.read_text().splitlines(), 1):
        if line.startswith("```"):
            inside = bool(FENCE.match(line)) if not inside else False
            continue
        if inside:
            m = COUNT.match(line)
            if m and not line.lstrip().startswith("#"):
                yield n, m["cmd"], m["want"].replace(",", "")


def main():
    failed = checked = 0
    for page in sorted((ROOT / "components").glob("*/*.md")):
        repo = page.parent.name
        for n, cmd, want in counts(page):
            where = checkout(repo)
            out = subprocess.run(
                ["bash", "-o", "pipefail", "-c", cmd],
                cwd=where, capture_output=True, text=True,
            )
            got = out.stdout.strip().split()[-1] if out.stdout.strip() else ""
            checked += 1
            if got != want:
                failed += 1
                rel = page.relative_to(ROOT)
                print(f"{rel}:{n}: want {want}, got {got or out.stderr.strip()[:120] or 'nothing'}")
                print(f"    {cmd}")
    print(f"{checked} counts checked, {failed} wrong")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
