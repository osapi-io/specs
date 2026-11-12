#!/usr/bin/env python3
"""Vet one pull request and print a verdict, the steps of vetting.md as code.

    vet-pr.py <owner/repo> <number>

Prints one line per finding, "LOOK <reason>" or "STOP <reason>", then
"VERDICT CLEAN|LOOK|STOP <owner/repo>#<number>". Exits 0 for CLEAN, 1 for LOOK
and 2 for STOP, so a caller can test the status alone.

Works for any owner. It fetches the base commit and the pull request's head
into a temporary bare clone and reads lockfiles from those commits with
deps.sh, so nothing on this machine is checked out and nothing in the pull
request runs. A lookup that fails is a LOOK, never a pass: a check that could
not be made is not a clean result.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
MIN_RELEASE_AGE_H = 72  # vetting.md step 5
MIN_PACKAGE_AGE_D = 90  # vetting.md step 4
NOW = datetime.now(timezone.utc)

findings = []


def look(msg):
    findings.append(("LOOK", msg))


def stop(msg):
    findings.append(("STOP", msg))


def run(*cmd, cwd=None, input=None, check=True):
    p = subprocess.run(cmd, cwd=cwd, input=input, capture_output=True, text=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:3])}: {p.stderr.strip()[:200]}")
    return p


def gh_json(*args):
    return json.loads(run("gh", *args).stdout or "null")


def http_json(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "org-status-vet"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if attempt == 2:
                raise
        except Exception:
            if attempt == 2:
                raise
        time.sleep(2)


def when(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def hours_old(ts):
    return (NOW - when(ts)).total_seconds() / 3600


# --- resemblance, as resembles.py ------------------------------------------


def dist(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def resembles(new, known, eco):
    """Return the known name a new one imitates, or None."""
    strip = lambda p: re.sub(r"/v[0-9]+$", "", p)
    n = strip(new)
    for k in known:
        if k == new:
            return None
    for k in known:
        kk = strip(k)
        if kk == n:
            continue  # same module, another major version
        # Short npm names sit within two edits of each other by chance
        # (ms, mz, qs), so require some length before calling it imitation.
        if dist(kk, n) <= 2 and (eco == "Go" or min(len(kk), len(n)) >= 5):
            return k
        if eco == "Go":
            ko, kn = kk.rsplit("/", 1) if "/" in kk else ("", kk)
            no, nn = n.rsplit("/", 1) if "/" in n else ("", n)
            if kn == nn and ko != no:
                return k
    return None


# --- lookups -----------------------------------------------------------------


def go_escape(path):
    return re.sub(r"[A-Z]", lambda m: "!" + m.group(0).lower(), path)


def published(eco, name, version):
    """When this exact version was published, as an ISO time, or None."""
    if eco == "Go":
        v = version if version.startswith("v") else "v" + version
        d = http_json(f"https://proxy.golang.org/{go_escape(name)}/@v/{v}.info")
        return d and d.get("Time")
    d = http_json("https://registry.npmjs.org/" + urllib.parse.quote(name, safe="@"))
    return d and d.get("time", {}).get(version)


def first_published(eco, name):
    system = {"Go": "go", "npm": "npm"}[eco]
    d = http_json(f"https://api.deps.dev/v3/systems/{system}/packages/" + urllib.parse.quote(name, safe=""))
    times = [v["publishedAt"] for v in (d or {}).get("versions", []) if v.get("publishedAt")]
    return min(times) if times else None


def osv(lines):
    """Run osv-malicious.sh over "eco name version" lines; return (malicious, vulns)."""
    if not lines:
        return [], []
    p = subprocess.run([os.path.join(HERE, "osv-malicious.sh")], input="\n".join(lines) + "\n",
                       capture_output=True, text=True, env={**os.environ, "OSV_LIST": "1"})
    if p.returncode not in (0, 1) or "VULNS" not in p.stdout:
        raise RuntimeError("osv-malicious.sh failed: " + p.stderr.strip()[:200])
    bad = [l for l in p.stdout.splitlines() if l.startswith("MALICIOUS ")]
    vulns = [l for l in p.stdout.splitlines() if l.startswith("VULN ")]
    return bad, vulns


# --- the steps ---------------------------------------------------------------

BUMP_TITLE = re.compile(r"^(\w+(\([^)]*\))?!?: )?bump ", re.I)
ALLOWED = {
    "go_modules": re.compile(r"(^|/)go\.(mod|sum)$"),
    "github_actions": re.compile(r"^\.github/workflows/[^/]+\.ya?ml$"),
    "bun": re.compile(r"(^|/)(package\.json|bun\.lock)$"),
    "npm_and_yarn": re.compile(r"(^|/)(package\.json|package-lock\.json)$"),
    "docker": re.compile(r"(^|/)Dockerfile[^/]*$"),
}
RISKY = [
    (re.compile(r"^\.github/(workflows|actions)/"), "runs in CI with the repository's token"),
    (re.compile(r"(^|/)(justfile|\.mise\.toml)$|^\.just/"), "runs on every just test"),
    (re.compile(r"(^|/)Dockerfile|(^|/)scripts/|\.sh$"), "runs during a build"),
]
USES = re.compile(r"^([-+])\s+(?:- )?uses:\s*([^@\s]+)@(\S+)(?:\s+#\s*(\S+))?")


def provenance(pr, repo, n):
    author = pr["author"]["login"]
    dependabot = author == "app/dependabot"
    if not dependabot and BUMP_TITLE.search(pr["title"]):
        stop(f"title reads like a bump but the author is {author}, not Dependabot")
    if pr["headRefName"].startswith("dependabot/") and pr["isCrossRepository"]:
        stop("a dependabot/ branch from a fork")
    commits = gh_json("api", f"/repos/{repo}/pulls/{n}/commits", "--paginate")
    if dependabot:
        for c in commits:
            a = (c.get("author") or {}).get("login", "none")
            m = (c.get("committer") or {}).get("login", "none")
            v = c["commit"]["verification"]["verified"]
            if (a, m, v) != ("dependabot[bot]", "web-flow", True):
                look(f"commit {c['sha'][:8]} is by {a} (committer {m}, signed={v}), not Dependabot's signed commit: read it")
    else:
        look(f"written by {author}, not Dependabot: a person has to read it")
    return dependabot


def files(pr, dependabot, diff):
    paths = [f["path"] for f in pr["files"]]
    if dependabot:
        eco = pr["headRefName"].split("/")[1] if pr["headRefName"].count("/") >= 2 else ""
        allowed = ALLOWED.get(eco)
        if allowed is None:
            look(f"Dependabot ecosystem '{eco}' has no file rule here: check the paths by hand")
        else:
            for p in paths:
                if not allowed.search(p):
                    stop(f"{p} is outside what a {eco} bump changes")
        if eco == "github_actions":
            for line in diff:
                if re.match(r"^[-+](?![-+])", line) and not USES.match(line) and line[1:].strip():
                    stop(f"workflow line other than uses: changed: {line[:100]}")
    else:
        for p in paths:
            for rx, why in RISKY:
                if rx.search(p):
                    look(f"{p} {why}")
                    break
        wf = False
        for line in diff:
            if line.startswith("+++ "):
                wf = ".github/workflows/" in line
            elif wf and line.startswith("+") and not line.startswith("+++"):
                body = line[1:]
                if "pull_request_target" in body:
                    stop("adds pull_request_target to a workflow")
                if re.search(r":\s*write\b", body):
                    stop(f"grants a write permission in a workflow: {body.strip()[:80]}")
                if "secrets." in body:
                    stop(f"references a secret in a workflow: {body.strip()[:80]}")
                if re.search(r"(curl|wget)[^|]*\|\s*(ba|z)?sh\b", body):
                    stop(f"runs a download in a workflow: {body.strip()[:80]}")
    return paths


PSEUDO = re.compile(r"v\d+\.\d+\.\d+-(\d+\.)?\d{14}-[0-9a-f]{12}")


def gomod(diff):
    in_mod = False
    removed, added = {}, []
    for line in diff:
        if line.startswith("+++ "):
            in_mod = line.endswith("go.mod")
            continue
        if not in_mod or line.startswith(("---", "+++")) or not line.startswith(("+", "-")):
            continue
        body = line[1:].strip()
        parts = body.removeprefix("require ").split()
        if line.startswith("-"):
            if len(parts) >= 2:
                removed[parts[0]] = parts[1]
            continue
        if body.startswith("replace") or "=>" in body:
            stop(f"adds or changes a replace directive: {body[:100]}")
        if re.match(r"^(go|toolchain|tool)\s", body):
            look(f"changes the go.mod line '{body}'")
        if len(parts) >= 2:
            added.append((parts[0], parts[1]))
    for mod, version in added:
        # Dependabot proposes tags, so an untagged commit replacing a tag is
        # somebody's choice. One pseudo-version replacing another is not.
        if PSEUDO.search(version) and not PSEUDO.search(removed.get(mod, "")):
            was = removed.get(mod)
            look(f"{mod} moves to untagged {version}" + (f" from tag {was}" if was else ""))


def dependencies(clone, base, head):
    def deps(ref):
        p = run(os.path.join(HERE, "deps.sh"), clone, ref)
        for l in p.stderr.splitlines():
            if l.startswith("unparsed "):
                look(f"lockfile not scanned: {l.split(' ', 1)[1]}")
        return set(l for l in p.stdout.splitlines() if l.strip())

    b, h = deps(base), deps(head)
    changed = sorted(h - b)
    known = {}
    for l in b:
        eco, name, _ = l.split(" ", 2)
        known.setdefault(eco, set()).add(name)
    new_names = sorted({(l.split(" ")[0], l.split(" ")[1]) for l in changed} -
                       {(e, n) for e, ns in known.items() for n in ns})

    for eco, name in new_names:
        k = resembles(name, known.get(eco, set()), eco)
        if k:
            stop(f"new {eco} package {name} resembles {k}, already depended on")
        try:
            first = first_published(eco, name)
        except Exception as e:
            look(f"could not tell how old new package {name} is: {e}")
            continue
        if first is None:
            look(f"new {eco} package {name}: deps.dev does not know it")
        elif hours_old(first) < MIN_PACKAGE_AGE_D * 24:
            look(f"new {eco} package {name} was first published {first[:10]}, under {MIN_PACKAGE_AGE_D} days ago")

    for l in changed:
        eco, name, version = l.split(" ", 2)
        try:
            t = published(eco, name, version)
        except Exception as e:
            look(f"could not tell when {name}@{version} was published: {e}")
            continue
        if t is None:
            look(f"no publish time for {name}@{version}")
        elif hours_old(t) < MIN_RELEASE_AGE_H:
            look(f"{name}@{version} was published {t[:16]}, under {MIN_RELEASE_AGE_H} hours ago")

    try:
        bad, vulns = osv(changed)
    except Exception as e:
        look(f"OSV could not be asked: {e}")
        return changed
    for l in bad:
        stop(l)
    for l in vulns:
        _, eco, name, version, ids = l.split(" ", 4)
        look(f"{name}@{version} has known advisories {ids}: triage.md decides whether they matter")
    return changed


def in_range(version, rng):
    """True, False, or None when the range cannot be read."""
    def key(v):
        m = re.match(r"v?(\d+)(?:\.(\d+))?(?:\.(\d+))?$", v.strip())
        return tuple(int(x or 0) for x in m.groups()) if m else None
    v = key(version)
    if v is None:
        return None
    for part in rng.split(","):
        m = re.match(r"\s*(<=|>=|<|>|=)\s*(\S+)\s*$", part)
        if not m or key(m.group(2)) is None:
            return None
        op, bound = m.group(1), key(m.group(2))
        ok = {"<": v < bound, "<=": v <= bound, ">": v > bound, ">=": v >= bound, "=": v == bound}[op]
        if not ok:
            return False
    return True


def actions(diff):
    minus, plus = [], []
    for line in diff:
        m = USES.match(line)
        if m:
            (minus if m.group(1) == "-" else plus).append(m.groups()[1:])
    old = {a for a, _, _ in minus}
    for action, ref, comment in plus:
        if action.startswith("./") or action.startswith("docker://"):
            continue
        if action not in old:
            stop(f"uses {action}, which the old line did not: owner or repository changed")
        owner_repo = "/".join(action.split("/")[:2])
        tag = comment if re.fullmatch(r"[0-9a-f]{40}", ref) else ref
        if not tag:
            look(f"{action}@{ref[:12]} names no version")
            continue
        try:
            r = gh_json("api", f"/repos/{owner_repo}/git/ref/tags/{tag}")
        except Exception:
            stop(f"{owner_repo} has no tag {tag}")
            continue
        sha = r["object"]["sha"]
        if r["object"]["type"] == "tag":
            sha = gh_json("api", f"/repos/{owner_repo}/git/tags/{sha}")["object"]["sha"]
        if re.fullmatch(r"[0-9a-f]{40}", ref) and sha != ref:
            stop(f"{action}@{ref[:12]} is not what tag {tag} points at ({sha[:12]})")
        try:
            rel = gh_json("api", f"/repos/{owner_repo}/releases/tags/{tag}")
            if rel and hours_old(rel["published_at"]) < MIN_RELEASE_AGE_H:
                look(f"{owner_repo} {tag} was released {rel['published_at'][:16]}, under {MIN_RELEASE_AGE_H} hours ago")
        except Exception:
            pass  # a tag with no release page is common for actions
        for adv in gh_json("api", f"/advisories?ecosystem=actions&affects={owner_repo}&per_page=100") or []:
            for vuln in adv.get("vulnerabilities", []):
                rng = vuln.get("vulnerable_version_range") or ""
                hit = in_range(tag, rng)
                if hit:
                    stop(f"{owner_repo} {tag} is inside {adv['ghsa_id']} ({rng})")
                elif hit is None:
                    look(f"{owner_repo} {tag}: cannot read the range of {adv['ghsa_id']} ({rng}), check by hand")


def main():
    if len(sys.argv) != 3 or "/" not in sys.argv[1]:
        sys.exit(__doc__)
    repo, n = sys.argv[1], sys.argv[2]
    pr = gh_json("pr", "view", n, "--repo", repo, "--json",
                 "author,isCrossRepository,headRefName,title,baseRefOid,headRefOid,files,state")
    try:
        dependabot = provenance(pr, repo, n)
        with tempfile.TemporaryDirectory() as tmp:
            run("git", "init", "-q", "--bare", tmp)
            run("git", "-C", tmp, "config", "credential.helper", "!gh auth git-credential")
            run("git", "-C", tmp, "remote", "add", "origin", f"https://github.com/{repo}.git")
            run("git", "-C", tmp, "fetch", "-q", "--filter=blob:none", "origin",
                pr["baseRefOid"], f"+refs/pull/{n}/head:refs/vet/head")
            head = run("git", "-C", tmp, "rev-parse", "refs/vet/head").stdout.strip()
            if head != pr["headRefOid"]:
                look("the branch moved while it was being fetched: vet it again")
            diff = run("git", "-C", tmp, "diff", pr["baseRefOid"], head).stdout.splitlines()
            files(pr, dependabot, diff)
            gomod(diff)
            dependencies(tmp, pr["baseRefOid"], head)
            actions(diff)
    except Exception as e:
        look(f"vetting did not finish: {e}")

    for level, msg in sorted(findings, key=lambda f: f[0] != "STOP"):
        print(level, msg)
    verdict = "STOP" if any(l == "STOP" for l, _ in findings) else "LOOK" if findings else "CLEAN"
    print(f"VERDICT {verdict} {repo}#{n} {pr['title']}")
    sys.exit({"CLEAN": 0, "LOOK": 1, "STOP": 2}[verdict])


if __name__ == "__main__":
    main()
