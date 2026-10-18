#!/usr/bin/env python3
"""Check every served STL for closed, consistently wound, outward bodies, from the files alone.

    python scripts/check_geometry.py [file.stl ...]    # no arguments: every served and cleaned geometry file

Standard library only; it does not import clean/geometry_checks.py or scripts/aijdata.py, so the module that
builds the geometry cannot vouch for itself. It parses the ASCII STL files, welds vertices at 1e-6, grows BODIES
over the edges that exactly two triangles use (an edge that four triangles use, where two separate bodies touch,
is a contact between bodies, not a defect) and verifies, per body:

  - no boundary edge (every edge of the body is used by two of its triangles),
  - every edge is traversed once in each direction (consistent winding; "misdir" counts the edges that are not),
  - positive signed volume (outward normals),
  - no degenerate triangle (a repeated vertex, or three vertices on one line) and no repeated triangle,
  - the stored facet normal equals the normal the winding gives.

Files checked: docs/api/cases/*/geometry*.stl (the latest alias), docs/api/<VERSION>/cases/*/geometry*.stl (this
release's frozen copy) and clean/cases/*/geometry*.stl. Older release trees are frozen as released and are skipped.
AS_PUBLISHED names the files that are the authors' own, kept as published: they are measured and listed, not failed.
Prints one row per file and exits 1 if any other file fails.
"""
from __future__ import annotations

import glob
import hashlib
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
WELD = 1e-6
DEGENERATE = 1e-6          # 2 * area / longest edge ** 2 below this: the vertices are on one line
NORMAL_TOLERANCE = 1e-4    # per component, stored (6 significant digits) against computed
AS_PUBLISHED = {
    "clean/cases/E/geometry_ac.stl": "the authors' BD_caseE.stl scaled x250, kept as published",
}


def parse(path):
    """[(stored normal, (v0, v1, v2))] of an ASCII STL with one solid; raises ValueError if it is anything else."""
    with open(path, encoding="ascii") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines or not lines[0].startswith("solid ") or not lines[-1].startswith("endsolid "):
        raise ValueError("not a single ASCII solid")
    out, i = [], 1
    while i < len(lines) - 1:
        a, b, c, d, e, f_, g = lines[i:i + 7]
        if not (a.startswith("facet normal ") and b == "outer loop" and c.startswith("vertex ") and d.startswith("vertex ")
                and e.startswith("vertex ") and f_ == "endloop" and g == "endfacet"):
            raise ValueError(f"malformed facet at line {i + 1}")
        nrm = tuple(float(t) for t in a.split()[2:5])
        vs = tuple(tuple(float(t) for t in x.split()[1:4]) for x in (c, d, e))
        out.append((nrm, vs))
        i += 7
    return out


def cross(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    return uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx


def check_file(path):
    facets = parse(path)
    ids, tri = {}, []
    for _, vs in facets:
        tri.append(tuple(ids.setdefault(tuple(round(c / WELD) for c in p), len(ids)) for p in vs))
    r = {"triangles": len(facets), "degenerate": 0, "repeated": 0, "normals": 0}
    seen = set()
    for (stored, vs), t in zip(facets, tri):
        n = cross(*vs)
        ln = math.sqrt(sum(x * x for x in n))
        longest = max(math.dist(vs[0], vs[1]), math.dist(vs[1], vs[2]), math.dist(vs[2], vs[0]))
        if len(set(t)) < 3 or longest == 0 or ln / longest ** 2 < DEGENERATE:
            r["degenerate"] += 1
        elif any(abs(s - x / ln) > NORMAL_TOLERANCE for s, x in zip(stored, n)):
            r["normals"] += 1
        key = tuple(sorted(t))
        r["repeated"] += key in seen
        seen.add(key)

    edges = {}   # (lo, hi) -> [(triangle, +1 if it runs lo -> hi else -1)]
    for k, (a, b, c) in enumerate(tri):
        for u, v in ((a, b), (b, c), (c, a)):
            edges.setdefault((u, v) if u < v else (v, u), []).append((k, 1 if u < v else -1))

    parent = list(range(len(tri)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for uses in edges.values():
        if len(uses) == 2:
            parent[find(uses[0][0])] = find(uses[1][0])
    body = [find(k) for k in range(len(tri))]

    boundary = inconsistent = non_manifold = contacts = 0
    for uses in edges.values():
        per = {}
        for k, d in uses:
            per.setdefault(body[k], []).append(d)
        if len(per) > 1 and len(uses) > 2:
            contacts += 1
        for dirs in per.values():
            if len(dirs) == 1:
                boundary += 1
            elif len(dirs) == 2:
                inconsistent += dirs[0] == dirs[1]
            else:
                non_manifold += 1
    volume = {}
    for k, (a, b, c) in enumerate(tri):
        p, q, s = (facets[k][1][i] for i in range(3))
        volume[body[k]] = volume.get(body[k], 0.0) + (p[0] * (q[1] * s[2] - q[2] * s[1]) - p[1] * (q[0] * s[2] - q[2] * s[0]) + p[2] * (q[0] * s[1] - q[1] * s[0])) / 6.0
    r.update(bodies=len(volume), boundary=boundary, inconsistent=inconsistent, non_manifold=non_manifold, contacts=contacts,
             min_volume=min(volume.values()) if volume else 0.0, nonpositive=sum(v <= 0 for v in volume.values()))
    why = [f"{r[k]} {w}" for k, w in (("boundary", "boundary edges"), ("inconsistent", "edges traversed twice the same way"), ("non_manifold", "non-manifold edges"),
                                      ("nonpositive", "bodies without positive volume"), ("degenerate", "degenerate triangles"),
                                      ("repeated", "repeated triangles"), ("normals", "stored normals against the winding")) if r[k]]
    r["why"] = why
    return r


def files():
    version = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
    pats = ["docs/api/cases/*/geometry*.stl", f"docs/api/{version}/cases/*/geometry*.stl", "clean/cases/*/geometry*.stl"]
    return [os.path.relpath(p, ROOT).replace(os.sep, "/") for pat in pats for p in sorted(glob.glob(os.path.join(ROOT, pat)))]


def main():
    cache, rows, failed = {}, [], 0
    for rel, path in [(a, a) for a in sys.argv[1:]] or [(r, os.path.join(ROOT, r)) for r in files()]:
        with open(path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        if digest not in cache:
            try:
                cache[digest] = check_file(path)
            except ValueError as e:
                cache[digest] = {"triangles": 0, "bodies": 0, "boundary": 0, "inconsistent": 0, "contacts": 0, "min_volume": 0.0, "why": [str(e)]}
        r = cache[digest]
        status = "as published" if rel in AS_PUBLISHED else ("OK" if not r["why"] else "FAIL")
        failed += status == "FAIL"
        rows.append((rel, r, status))
    w = max(len(rel) for rel, _, _ in rows)
    print(f"{'file'.ljust(w)}  {'triangles':>9} {'bodies':>6} {'boundary':>8} {'misdir':>7} {'contacts':>8} {'min volume':>14}  status")
    for rel, r, status in rows:
        print(f"{rel.ljust(w)}  {r['triangles']:>9} {r['bodies']:>6} {r['boundary']:>8} {r['inconsistent']:>7} {r['contacts']:>8} {r['min_volume']:>14.6g}  {status}")
        if status == "FAIL":
            print(f"{' ' * w}    {'; '.join(r['why'])}")
        elif status == "as published":
            print(f"{' ' * w}    {AS_PUBLISHED[rel]}; not checked ({'; '.join(r['why'])})")
    print(f"check_geometry: {len(rows)} files, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
