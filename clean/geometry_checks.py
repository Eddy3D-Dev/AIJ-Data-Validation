"""Winding, bodies and watertightness of triangle soups, and the repairs the served geometry needs (standard library only).

One copy, imported by clean/build.py and scripts/aijdata.py; scripts/check_geometry.py re-derives the same facts from the
written STL files without importing this module. A triangle is ((x, y, z), (x, y, z), (x, y, z)).

A BODY is a set of triangles connected through edges that exactly two triangles use. An edge used by four triangles
where two separate bodies touch is a BODY CONTACT, not a defect: each body still sees it as an ordinary two-triangle
edge. A body is CLOSED when it has no boundary edge (an edge of one triangle), CONSISTENT when every edge is traversed
once in each direction, and OUTWARD when its signed volume is positive. A file is WATERTIGHT when every body is closed,
consistent and outward.
"""
from __future__ import annotations

import io
import math
from collections import defaultdict

WELD = 1e-6          # vertices that round to the same multiple of this are one vertex
DEGENERATE = 1e-6    # 2 * area / longest edge ** 2 below this: the three vertices are on one line
BASE_Z = -1.0        # height (full-scale metres) of the base slab that closes the terrain of Cases F and M: the ground there is z = 0


def _volume6(a, b, c):
    """Six times the signed volume of the tetrahedron (origin, a, b, c)."""
    return a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])


def _cross(a, b, c):
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    return uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx


def _is_degenerate(a, b, c):
    n = math.sqrt(sum(x * x for x in _cross(a, b, c)))
    longest = max(math.dist(a, b), math.dist(b, c), math.dist(c, a))
    return longest == 0 or n / longest ** 2 < DEGENERATE


def _face_edges(f):
    a, b, c = f
    return [(u, v) if u < v else (v, u) for u, v in ((a, b), (b, c), (c, a))]


class _Soup:
    """A triangle soup welded into vertices, faces, edges and bodies."""

    def __init__(self, tris, tol=WELD):
        ids, self.verts, self.faces = {}, [], []
        for t in tris:
            f = []
            for p in t:
                k = (round(p[0] / tol), round(p[1] / tol), round(p[2] / tol))
                i = ids.get(k)
                if i is None:
                    i = ids[k] = len(self.verts)
                    self.verts.append(tuple(p))
                f.append(i)
            self.faces.append(tuple(f))
        self.tris = [(self.verts[a], self.verts[b], self.verts[c]) for a, b, c in self.faces]   # every vertex at its welded position
        self.edges = defaultdict(list)   # (lo, hi) -> [(face, +1 if the face runs lo -> hi else -1)]
        for fi, (a, b, c) in enumerate(self.faces):
            for u, v in ((a, b), (b, c), (c, a)):
                self.edges[(u, v) if u < v else (v, u)].append((fi, 1 if u < v else -1))
        self._grow()

    def _grow(self):
        """body[f]: the body of face f. flip[f]: f must be reversed to agree with the first face of its body (faces that
        share an edge must run it in opposite directions). conflicts: edges where that cannot be satisfied."""
        n = len(self.faces)
        self.body, self.flip, self.conflicts = [-1] * n, [False] * n, []
        nb = 0
        for seed in range(n):
            if self.body[seed] >= 0:
                continue
            self.body[seed] = nb
            stack = [seed]
            while stack:
                f = stack.pop()
                for u, v in zip(self.faces[f], self.faces[f][1:] + self.faces[f][:1]):
                    uses = self.edges[(u, v) if u < v else (v, u)]
                    if len(uses) != 2:
                        continue
                    g, dg = uses[0] if uses[1][0] == f else uses[1]
                    want = (not self.flip[f]) if (1 if u < v else -1) == dg else self.flip[f]
                    if self.body[g] < 0:
                        self.body[g], self.flip[g] = nb, want
                        stack.append(g)
                    elif self.flip[g] != want:
                        self.conflicts.append((f, g))
            nb += 1
        self.members = defaultdict(list)
        for fi, b in enumerate(self.body):
            self.members[b].append(fi)

    def own_edges(self, faces):
        """edge -> number of triangles of THIS body that use it (an edge two bodies share counts per body)."""
        own = defaultdict(int)
        for f in faces:
            for k in _face_edges(self.faces[f]):
                own[k] += 1
        return own

    def is_closed(self, faces):
        return all(n != 1 for n in self.own_edges(faces).values())


def _up_down(tris):
    """Horizontal facets (normal within 0.6 degrees of vertical) facing up and down."""
    up = down = 0
    for t in tris:
        nx, ny, nz = _cross(*t)
        n = math.sqrt(nx * nx + ny * ny + nz * nz)
        if n > 0 and abs(nz) > 0.99995 * n:
            up += nz > 0
            down += nz < 0
    return up, down


def orient_consistent(tris, tol=WELD):
    """(triangles, info): every body wound consistently, closed bodies outward (positive signed volume) and open bodies
    (a terrain sheet) with the majority of their horizontal facets facing up. Order and positions are kept; welded
    vertices share one position. info: bodies, triangles_reversed, bodies_reversed, conflicting_edges."""
    s = _Soup(tris, tol)
    reverse = list(s.flip)
    reversed_bodies = 0
    for fs in s.members.values():
        cur = [(a, c, b) if s.flip[f] else (a, b, c) for f in fs for a, b, c in [s.tris[f]]]
        if s.is_closed(fs):
            wrong = sum(_volume6(*t) for t in cur) < 0
        else:
            up, down = _up_down(cur)
            wrong = down > up if up + down else sum(_volume6(*t) for t in cur) < 0
        if wrong:
            reversed_bodies += 1
            for f in fs:
                reverse[f] = not reverse[f]
    out = [(a, c, b) if r else (a, b, c) for (a, b, c), r in zip(s.tris, reverse)]
    return out, {"bodies": len(s.members), "triangles_reversed": sum(reverse), "bodies_reversed": reversed_bodies,
                 "conflicting_edges": len(s.conflicts)}


def _report(s):
    bad = defaultdict(set)
    for f, g in s.conflicts:
        bad[s.body[f]].update((f, g))
    out = []
    for b, fs in s.members.items():
        own = s.own_edges(fs)
        vs = {v for f in fs for v in s.faces[f]}
        nflip = sum(s.flip[f] for f in fs)
        minority = {f for f in fs if s.flip[f] == (nflip <= len(fs) - nflip)} if 0 < nflip < len(fs) else set()
        pts = [p for f in fs for p in s.tris[f]]
        out.append({
            "triangles": len(fs), "vertices": len(vs), "edges": len(own),
            "boundary_edges": sum(1 for n in own.values() if n == 1),
            "non_manifold_edges": sum(1 for n in own.values() if n > 2),
            "inconsistent_triangles": len(minority | bad[b]),
            "signed_volume": sum(_volume6(*s.tris[f]) for f in fs) / 6.0,
            "euler_characteristic": len(vs) - len(own) + len(fs),
            "closed": all(n != 1 for n in own.values()),
            "bbox_min": [min(p[i] for p in pts) for i in range(3)], "bbox_max": [max(p[i] for p in pts) for i in range(3)],
        })
    out.sort(key=lambda r: -r["triangles"])
    return out


def body_report(tris, tol=WELD):
    """One dict per body, largest first: triangles, vertices, edges, boundary_edges, non_manifold_edges,
    inconsistent_triangles (the fewest triangles to reverse), signed_volume, euler_characteristic, closed, bbox."""
    return _report(_Soup(tris, tol))


def stl_stats(tris, tol=WELD):
    """Triangle count, bounding box, signed volume, the edge census and the body census of a soup.

    watertight: every body is closed (no boundary edge, no edge of its own that three triangles share), consistently
    wound and has a positive volume. body_contacts counts the edges
    that separate bodies share (they do not open a body); edges_non_manifold counts every edge used by more than two
    triangles, contacts included."""
    s = _Soup(tris, tol)
    counts = defaultdict(int)
    contacts = 0
    for uses in s.edges.values():
        counts[len(uses)] += 1
        if len(uses) > 2 and len({s.body[f] for f, _ in uses}) > 1:
            contacts += 1
    reps = _report(s)
    pts = [p for t in s.tris for p in t]
    lo = [min(p[i] for p in pts) for i in range(3)] if pts else [0.0] * 3
    hi = [max(p[i] for p in pts) for i in range(3)] if pts else [0.0] * 3
    return {"triangles": len(tris), "bbox_min": [round(v, 6) for v in lo], "bbox_max": [round(v, 6) for v in hi],
            "signed_volume": round(sum(r["signed_volume"] for r in reps), 9), "edges": len(s.edges),
            "edges_shared_by_two_faces": counts.get(2, 0), "edges_boundary": counts.get(1, 0),
            "edges_non_manifold": sum(v for k, v in counts.items() if k > 2),
            "bodies": len(reps), "body_contacts": contacts,
            "inconsistent_triangles": sum(r["inconsistent_triangles"] for r in reps),
            "min_body_volume": round(min((r["signed_volume"] for r in reps), default=0.0), 9),
            "watertight": bool(reps) and all(r["closed"] and r["non_manifold_edges"] == 0 and r["inconsistent_triangles"] == 0 and r["signed_volume"] > 0 for r in reps)}


# ------------------------------------------------------------------------------------------------ repairs

def drop_party_walls(tris, tol=WELD):
    """(triangles, walls): remove the wall that two buildings share face to face.

    Each building then has its own copy of the wall, and the four triangles that meet on every edge of the wall never
    join up: each copy is a planar open body of its own, two copies on the same vertices. Dropping both copies joins the
    two buildings into one closed body; the solid they enclose is unchanged. walls is a list of (vertices, triangles
    dropped, area)."""
    s = _Soup(tris, tol)
    patches = defaultdict(list)
    for b, fs in s.members.items():
        if s.is_closed(fs):
            continue
        t0 = s.tris[fs[0]]
        n = _cross(*t0)
        ln = math.sqrt(sum(x * x for x in n))
        if ln == 0 or any(abs(sum((p[i] - t0[0][i]) * n[i] for i in range(3))) / ln > tol for f in fs for p in s.tris[f]):
            continue   # not one plane
        patches[frozenset(v for f in fs for v in s.faces[f])].append(b)
    drop, walls = set(), []
    for vs, bodies in patches.items():
        if len(bodies) == 2:
            fs = [f for b in bodies for f in s.members[b]]
            drop.update(fs)
            area = sum(math.sqrt(sum(x * x for x in _cross(*s.tris[f]))) / 2 for f in s.members[bodies[0]])
            walls.append(([s.verts[v] for v in sorted(vs)], len(fs), area))
    return [t for f, t in enumerate(s.tris) if f not in drop], walls


def strip_flaps(tris, tol=WELD):
    """(triangles, flaps): remove slivers that hang on one edge of a surface: a triangle with two boundary edges whose
    third edge three or more triangles share. Nothing else touches them, so the surface keeps its shape."""
    s = _Soup(tris, tol)
    drop = {f for f, face in enumerate(s.faces)
            if sorted(len(s.edges[k]) for k in _face_edges(face)) in ([1, 1, 3], [1, 1, 4])}
    return [t for f, t in enumerate(s.tris) if f not in drop], [s.tris[f] for f in sorted(drop)]


def split_degenerate(tris, tol=WELD):
    """(triangles, dropped): remove triangles whose three vertices lie on one line (a vertex in the middle of a long
    edge, left by a mesher at a T-junction) and split the triangle across the long edge at that vertex, so the surface
    stays closed. Raises if the long edge has no neighbour to split."""
    tris, dropped = list(tris), 0
    for _ in range(len(tris) + 1):
        s = _Soup(tris, tol)
        bad = [f for f, t in enumerate(s.tris) if _is_degenerate(*t)]
        if not bad:
            return s.tris, dropped
        f = bad[0]
        a, b, c = s.faces[f]
        p, q = max(((a, b), (b, c), (c, a)), key=lambda e: math.dist(s.verts[e[0]], s.verts[e[1]]))   # the long edge
        mid = ({a, b, c} - {p, q}).pop()
        nb = [g for g, _ in s.edges[(p, q) if p < q else (q, p)] if g != f]
        if len(nb) != 1:
            raise ValueError(f"degenerate triangle {f} has {len(nb)} neighbours across its long edge")
        g = nb[0]
        i = next(i for i in range(3) if {s.faces[g][i], s.faces[g][(i + 1) % 3]} == {p, q})
        u, v, x = s.faces[g][i], s.faces[g][(i + 1) % 3], s.faces[g][(i + 2) % 3]
        tris = [t for h, t in enumerate(s.tris) if h not in (f, g)] + [(s.verts[u], s.verts[mid], s.verts[x]), (s.verts[mid], s.verts[v], s.verts[x])]
        dropped += 1
    raise ValueError("degenerate triangles do not run out")


def boundary_loops(tris, tol=WELD):
    """The boundary of an open surface as closed loops of vertices, each in the direction its triangles run it (the
    surface is on the left). Raises if a vertex has two outgoing boundary edges."""
    s = _Soup(tris, tol)
    nxt = {}
    for (lo, hi), uses in s.edges.items():
        if len(uses) == 1:
            u, v = (lo, hi) if uses[0][1] == 1 else (hi, lo)
            if u in nxt:
                raise ValueError("the boundary touches itself at a vertex")
            nxt[u] = v
    loops = []
    while nxt:
        start = next(iter(nxt))
        loop, v = [start], nxt.pop(start)
        while v != start:
            loop.append(v)
            v = nxt.pop(v)
        loops.append([s.verts[i] for i in loop])
    return loops


def close_base(tris, z, tol=WELD):
    """(triangles, added): close an outward-wound surface that is open along convex rims by a base slab: a skirt of
    vertical walls from every rim edge down to height z and a bottom cap at z, fanned from the mean of the rim's
    vertices. The base faces outward (down); a rim that is not convex raises."""
    added = []
    for loop in boundary_loops(tris, tol):
        low = [(p[0], p[1], z) for p in loop]
        for i in range(len(loop)):
            a, b, a2, b2 = loop[i], loop[(i + 1) % len(loop)], low[i], low[(i + 1) % len(loop)]
            added += [(b, a, a2), (b, a2, b2)]
        c = (sum(p[0] for p in low) / len(low), sum(p[1] for p in low) / len(low), z)
        cap = [(c, low[(i + 1) % len(low)], low[i]) for i in range(len(low))]
        if any(_cross(*t)[2] >= 0 for t in cap):
            raise ValueError("the rim is not convex: the bottom cap would fold")
        added += cap
    return list(tris) + added, added


def quantize(tris, digits):
    """Every coordinate rounded to `digits` significant digits, as the STL writer will print it: what is checked here
    is then what a reader of the file sees."""
    return [tuple(tuple(float(f"{v:.{digits}g}") for v in p) for p in t) for t in tris]


def close_terrain(tris, z=BASE_Z, digits=6):
    """A terrain sheet with buildings, from a model scanner, as one closed outward body: coordinates rounded as the
    writer prints them, flaps and degenerate triangles removed, wound consistently with the ground facing up, then
    closed with a base slab down to height z. Returns (triangles, info)."""
    tris, flaps = strip_flaps(quantize(tris, digits))
    tris, collinear = split_degenerate(tris)
    tris, o = orient_consistent(tris)
    before = len(tris)
    tris, added = close_base(tris, z)
    tris = quantize(tris, digits)
    return tris, {"flaps_removed": len(flaps), "flap_area": sum(math.sqrt(sum(x * x for x in _cross(*t))) / 2 for t in flaps),
                  "degenerate_removed": collinear, "triangles_reversed": o["triangles_reversed"], "base_triangles": len(added),
                  "triangles_before_base": before}


def clean_buildings(tris, digits=6):
    """Separate buildings from a model scanner as closed outward bodies: coordinates rounded as the writer prints them,
    shared party walls dropped, every body wound consistently and outward. Returns (triangles, info)."""
    tris, walls = drop_party_walls(quantize(tris, digits))
    tris, o = orient_consistent(tris)
    return tris, {**o, "party_walls": walls}


def buildings_note(raw, info, out):
    """The sentence the geometry's source field carries after clean_buildings: what was wrong and what was done."""
    r = stl_stats(raw)
    walls = info["party_walls"]
    shells = shells_from_tris(raw, tol=1e-4)
    inward = sum(1 for sh in shells if sum(_volume6(*t) for t in sh) < 0)     # the count the earlier whole-shell flip acted on
    note = (f"{inward:,} of {len(shells):,} shells are wound inward in the 3dm and {r['inconsistent_triangles']:,} of {r['triangles']:,} triangles are wound "
            "against their neighbours; every body is re-wound here, outward")
    if walls:
        note += (f"; {len(walls)} wall shared by two buildings ({sum(w[1] for w in walls)} triangles) is removed, which joins them into one body" if len(walls) == 1
                 else f"; {len(walls)} walls shared by two buildings ({sum(w[1] for w in walls)} triangles) are removed, which joins each pair into one body")
    return note + f"; {out['bodies']:,} bodies, all closed, {out['body_contacts']} edges where two bodies touch"


# ------------------------------------------------------------------------------------------------ files

def shells_from_tris(tris, tol=1e-9):
    """Connected components of a triangle soup by shared (welded) vertices; not the same as a body (see the docstring)."""
    key = lambda p: tuple(round(c / tol) for c in p)
    parent = {}

    def find(a):
        while parent.setdefault(a, a) != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for t in tris:
        k0, k1, k2 = (key(p) for p in t)
        r0, r1, r2 = find(k0), find(k1), find(k2)
        if r0 != r1:
            parent[r0] = r1
        if find(k1) != r2:
            parent[find(k1)] = r2
    groups = defaultdict(list)
    for t in tris:
        groups[find(key(t[0]))].append(t)
    return list(groups.values())


def read_ascii_stl(path):
    tris, cur = [], []
    with io.open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if s.startswith("vertex"):
                cur.append(tuple(float(t) for t in s.split()[1:4]))
                if len(cur) == 3:
                    tris.append(tuple(cur))
                    cur = []
    return tris


def write_ascii_stl(path, tris, name, digits=7):
    """LF-only ASCII STL (CRLF makes OpenFOAM keep the \\r in the last token of a line). Vertices are rounded to `digits`
    significant digits first and the facet normal is taken from the rounded vertices, so what the file says about a
    facet is what its own numbers give."""
    fmt = lambda v: f"{v:.{digits}g}"
    with io.open(path, "w", encoding="ascii", newline="\n") as f:
        f.write(f"solid {name}\n")
        for t in tris:
            q = [tuple(float(fmt(v)) for v in p) for p in t]
            nx, ny, nz = _cross(*q)
            n = math.sqrt(nx * nx + ny * ny + nz * nz)
            nx, ny, nz = (nx / n, ny / n, nz / n) if n > 0 else (0.0, 0.0, 0.0)
            f.write(f"  facet normal {nx:.6g} {ny:.6g} {nz:.6g}\n    outer loop\n")
            for p in q:
                f.write(f"      vertex {fmt(p[0])} {fmt(p[1])} {fmt(p[2])}\n")
            f.write("    endloop\n  endfacet\n")
        f.write(f"endsolid {name}\n")


def mesh_3dm(path, state):
    """Triangles of the Niigata district from the 3dm: 'bc' = layer 'buildings', 'ac' = + 'buildings_new_construction'."""
    import rhino3dm
    f = rhino3dm.File3dm.Read(path)
    layers = {l.Index: l.Name for l in f.Layers}
    wanted = {"buildings"} if state == "bc" else {"buildings", "buildings_new_construction"}
    tris = []
    for o in f.Objects:
        if layers.get(o.Attributes.LayerIndex) not in wanted:
            continue
        m = o.Geometry
        if not isinstance(m, rhino3dm.Mesh):
            continue
        vs = [(m.Vertices[i].X, m.Vertices[i].Y, m.Vertices[i].Z) for i in range(len(m.Vertices))]
        for i in range(len(m.Faces)):
            face = m.Faces[i]
            a, b, c, d = face[0], face[1], face[2], face[3]
            tris.append((vs[a], vs[b], vs[c]))
            if d != c:
                tris.append((vs[a], vs[c], vs[d]))
    return tris
