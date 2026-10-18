"""Host a release that predates the versioned API layout under docs/api/<release>/.

    python scripts/host_release.py 2.0.0           # write docs/api/2.0.0/ from the git tag v2.0.0
    python scripts/host_release.py 2.0.0 --check   # compare docs/api/2.0.0/ with what the tag gives; write nothing

Release 2.0.0 was published before the API had release-numbered paths, so its files exist only in the tag
(docs/api/ at v2.0.0) and as raw files at that tag. This script puts them where a release's files belong now,
/api/2.0.0/ on the site, WITHOUT regenerating anything: the tree is the tag's docs/api/ byte for byte, except that

  1. in every JSON and text file the file's own addresses are rewritten, the site's /api to /api/2.0.0 and the
     repository's raw docs/api on main to .../docs/api/2.0.0 (both read from the tag's own index.json), so that a
     client that starts in the copy stays in it; and
  2. in index.json the size, SHA-256 and ?v= of the files that rewrite changed are recomputed, because they no
     longer match what the tag lists.

CSV, STL and ZIP files are the tag's bytes. The result is checked three ways: --check re-derives the tree from the tag
and compares every byte with the tree on disk; every rewrite is shown to be undone by the opposite replacement (so no
other character moved); and `python scripts/build_api.py --check` then verifies the tree like any release tree
(its own schemas, every link, every hash). scripts/release.py check runs the first two.

Standard library only; needs git and the tag.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = os.path.join(REPO, "docs", "api")
TEXT = (".json", ".txt")
# What may follow a rewritten address: a path, the end of a JSON string, a query, white space or the end of the text.
# (Not a letter or a hyphen: /api-reference/ is another page and stays as it is.)
AFTER = r"(?=[/\"?\s]|$)"


def _git(*args):
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True)
    if r.returncode:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.decode('utf-8', 'replace').strip()}")
    return r.stdout


def _dump(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False, allow_nan=False) + "\n"


def _addresses(tag):
    """(site API base, raw main base) as the tag's own index.json states them."""
    idx = json.loads(_git("show", f"{tag}:docs/api/index.json"))
    return idx["base_url"], idx["fallback_base_url"]


def _forward(text, bases, version):
    for base in bases:
        text = re.sub(re.escape(base) + AFTER, f"{base}/{version}", text)
    return text


def _backward(text, bases, version):
    for base in bases:
        text = text.replace(f"{base}/{version}", base)
    return text


def derive(version):
    """{relative path: bytes} of the hosted tree, derived from the tag alone."""
    tag = f"v{version}"
    bases = _addresses(tag)
    names = [n[len("docs/api/"):] for n in _git("ls-tree", "-r", "--name-only", tag, "docs/api").decode().split("\n") if n]
    out, rewritten = {}, set()
    for name in sorted(names):
        data = _git("show", f"{tag}:docs/api/{name}")
        if name.endswith(TEXT):
            text = data.decode("utf-8")
            new = _forward(text, bases, version)
            if _backward(new, bases, version) != text:
                raise SystemExit(f"{name}: the address rewrite is not undone by the opposite replacement; refusing to host")
            if new != text:
                rewritten.add(name)
            data = new.encode("utf-8")
        out[name] = data
    # index.json lists the size and SHA-256 of every file: refresh the entries of the files the rewrite changed
    idx = json.loads(out["index.json"].decode("utf-8"))
    if _dump(json.loads(_git("show", f"{tag}:docs/api/index.json"))) != _git("show", f"{tag}:docs/api/index.json").decode("utf-8"):
        raise SystemExit("index.json does not survive a parse and dump unchanged; cannot rewrite it faithfully")
    for entry in idx["files"]:
        if entry["path"] in rewritten:
            body = out[entry["path"]]
            sha = hashlib.sha256(body).hexdigest()
            entry["bytes"], entry["sha256"] = len(body), sha
            entry["url"] = re.sub(r"\?v=[0-9a-f]{12}$", f"?v={sha[:12]}", entry["url"])
    out["index.json"] = _dump(idx).encode("utf-8")
    return out


def check(version):
    """Problems (empty if the tree on disk is exactly what the tag gives)."""
    root = os.path.join(API, version)
    if not os.path.isdir(root):
        return [f"docs/api/{version}/ does not exist; run scripts/host_release.py {version}"]
    want = derive(version)
    have = {}
    for dirpath, _, names in os.walk(root):
        for n in names:
            with io.open(os.path.join(dirpath, n), "rb") as f:
                have[os.path.relpath(os.path.join(dirpath, n), root).replace(os.sep, "/")] = f.read()
    problems = [f"docs/api/{version}/{p} is not in v{version}" for p in sorted(set(have) - set(want))]
    problems += [f"docs/api/{version}/{p} is missing" for p in sorted(set(want) - set(have))]
    problems += [f"docs/api/{version}/{p} differs from v{version} beyond its rewritten addresses"
                 for p in sorted(set(want) & set(have)) if want[p] != have[p]]
    return problems


def host(version):
    root = os.path.join(API, version)
    files = derive(version)
    if os.path.isdir(root):
        for dirpath, _, names in os.walk(root):
            for n in names:
                os.remove(os.path.join(dirpath, n))
    for name, data in files.items():
        path = os.path.join(root, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with io.open(path, "wb") as f:
            f.write(data)
    print(f"docs/api/{version}/: {len(files)} files from v{version}")


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and sys.argv[2] != "--check"):
        raise SystemExit(__doc__)
    v = sys.argv[1]
    if len(sys.argv) == 3:
        problems = check(v)
        for p in problems:
            print("PROBLEM:", p)
        print(f"host_release {v}:", "OK" if not problems else f"{len(problems)} problem(s)")
        sys.exit(1 if problems else 0)
    host(v)
