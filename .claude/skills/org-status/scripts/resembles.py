"""Flag module paths that look like an existing dependency but are not it.

Reads candidate paths on stdin and the paths already depended on from the file
named as the first argument. A candidate resembles a known path when the two
are within two edits of each other, or share a final element under a different
owner, which is how typosquats of Go modules are usually named.
"""

import re, sys

def dist(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]

def split(path):
    path = re.sub(r"/v[0-9]+$", "", path)
    parts = path.split("/")
    return parts[:-1], parts[-1]

known = [l.strip() for l in open(sys.argv[1]) if l.strip()]
for new in sys.stdin.read().split():
    if new in known:
        continue
    nowner, nname = split(new)
    for k in known:
        kowner, kname = split(k)
        if dist(k, new) <= 2 or (nname == kname and nowner != kowner):
            print(f"{new}\tresembles {k}")
