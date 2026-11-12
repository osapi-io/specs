#!/usr/bin/env python3
"""Merge a repository's pull requests in the order merging.md describes.

    merge-queue.py [--dry-run] <owner/repo> <number> [<number> ...]

Every pull request is vetted with vet-pr.py first and only a CLEAN one is
merged; LOOK and STOP are reported and left alone, so a human pull request is
never merged from here. Then:

- A pull request that touches no file another queued one touches merges as
  soon as its checks pass.
- Pull requests that share a file are serialized: merge one, ask Dependabot to
  rebase the next, vet it again (a rebase can move it to a newer release), wait
  for its checks and merge it. A bump of the root go.mod in a repository with
  nested modules goes last.
- A red check stops that pull request with the failing check named. A rebase
  does not fix it.

Waiting for checks requires at least one check to exist before trusting "none
pending": straight after a push GitHub has registered none, and "all of none
are done" is true.
"""

import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
POLL = 20
CHECKS_TIMEOUT = 45 * 60
REBASE_TIMEOUT = 15 * 60
MODULE_FILE = re.compile(r"(^|/)(go\.mod|go\.sum|package\.json|bun\.lock|package-lock\.json)$")


def gh(*args, check=True):
    p = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args[:3])}: {p.stderr.strip()[:200]}")
    return p.stdout


def view(repo, n, fields):
    return json.loads(gh("pr", "view", str(n), "--repo", repo, "--json", fields))


def say(n, msg):
    print(f"#{n} {msg}", flush=True)


def vet(repo, n):
    p = subprocess.run([os.path.join(HERE, "vet-pr.py"), repo, str(n)], capture_output=True, text=True)
    lines = p.stdout.strip().splitlines()
    if p.returncode != 0:
        for l in lines:
            say(n, l)
    return p.returncode == 0


def has_workflows(repo):
    out = gh("api", f"/repos/{repo}/actions/workflows", "-q", ".total_count", check=False).strip()
    return out not in ("", "0")


def wait_checks(repo, n):
    """True when every check passed, False when one failed or it timed out."""
    start = time.time()
    while time.time() - start < CHECKS_TIMEOUT:
        out = gh("pr", "checks", str(n), "--repo", repo, "--json", "name,bucket,link", check=False)
        checks = json.loads(out) if out.strip().startswith("[") else []
        if not checks and time.time() - start > 180 and not has_workflows(repo):
            say(n, "no CI in this repository")
            return True
        if checks and all(c["bucket"] != "pending" for c in checks):
            failed = [c for c in checks if c["bucket"] not in ("pass", "skipping")]
            for c in failed:
                say(n, f"check {c['name']} is {c['bucket']}: {c['link']}")
            return not failed
        time.sleep(POLL)
    say(n, "checks did not finish in time")
    return False


def wait_new_head(repo, n, old):
    start = time.time()
    while time.time() - start < REBASE_TIMEOUT:
        pr = view(repo, n, "headRefOid,mergeable,title")
        if pr["headRefOid"] != old:
            # mergeable is UNKNOWN until GitHub has recomputed it
            for _ in range(30):
                if pr["mergeable"] != "UNKNOWN":
                    break
                time.sleep(5)
                pr = view(repo, n, "headRefOid,mergeable,title")
            return pr
        time.sleep(POLL)
    return None


def rebase(repo, n):
    """Ask Dependabot to rebase, then to recreate. Returns success.

    Recreate follows when the rebase leaves a conflict, and also when
    Dependabot ignores the rebase request altogether, which it sometimes does
    without a reply or a reaction.
    """
    for command in ("rebase", "recreate"):
        before = view(repo, n, "headRefOid,title")
        gh("pr", "comment", str(n), "--repo", repo, "--body", f"@dependabot {command}")
        say(n, f"asked Dependabot to {command}")
        pr = wait_new_head(repo, n, before["headRefOid"])
        if pr is None:
            say(n, f"Dependabot did not {command} within {REBASE_TIMEOUT // 60} minutes")
            continue
        if pr["title"] != before["title"]:
            say(n, f"now reads: {pr['title']}")
        if pr["mergeable"] != "CONFLICTING":
            return True
        say(n, f"still conflicting after {command}")
    return False


def merge(repo, n, dry):
    if dry:
        say(n, "would merge")
        return True
    try:
        gh("pr", "merge", str(n), "--repo", repo, "--squash", "--delete-branch")
    except RuntimeError as e:
        say(n, f"merge refused: {e}")
        return False
    state = view(repo, n, "state")["state"]
    say(n, state)
    return state == "MERGED"


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]
    if len(args) < 2 or "/" not in args[0]:
        sys.exit(__doc__)
    repo, numbers = args[0], [int(a) for a in args[1:]]

    queue = []
    for n in numbers:
        pr = view(repo, n, "state,author,files")
        if pr["state"] != "OPEN":
            say(n, f"is {pr['state']}, skipped")
            continue
        if not vet(repo, n):
            say(n, "not CLEAN, left for a person")
            continue
        files = {f["path"] for f in pr["files"]}
        queue.append({"n": n, "files": files, "dependabot": pr["author"]["login"] == "app/dependabot"})

    # A root go.mod bump in a repository with nested modules touches every
    # example once tidied, so it goes last, alone.
    nested = any(re.search(r".+/go\.mod$", f) for q in queue for f in q["files"])
    queue.sort(key=lambda q: nested and "go.mod" in q["files"])

    merged_files = set()
    for q in queue:
        n, files = q["n"], q["files"]
        shared = files & merged_files
        if not shared:
            # The base branch may have moved before this run: a merge by hand,
            # or one from an earlier queue. Compare against what landed since
            # the pull request was built.
            pr = view(repo, n, "headRefOid,baseRefName")
            moved = gh("api", f"/repos/{repo}/compare/{pr['headRefOid']}...{pr['baseRefName']}",
                       "-q", "[.files[]?.filename]", check=False)
            landed = set(json.loads(moved)) if moved.strip().startswith("[") else set()
            shared = {f for f in files if MODULE_FILE.search(f)} & landed
        if shared:
            if not q["dependabot"]:
                say(n, "shares files with a pull request merged just now and is not Dependabot's to rebase: rebase it by hand")
                continue
            if dry:
                say(n, f"would rebase (shares {', '.join(sorted(shared))}), vet again, wait for checks, merge")
                merged_files |= files
                continue
            if not rebase(repo, n):
                continue
            if not vet(repo, n):
                say(n, "not CLEAN after the rebase, left for a person")
                continue
        if not dry and not wait_checks(repo, n):
            say(n, "not merged: read the failure first, a rebase does not fix it")
            continue
        if merge(repo, n, dry):
            merged_files |= {f for f in files if MODULE_FILE.search(f)}


if __name__ == "__main__":
    main()
