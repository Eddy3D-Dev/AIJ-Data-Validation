"""Sample Eddy3D's solved velocity fields on the measurement planes, for the field maps (plot_field_maps.py draws them).

  validation/results/planes/case{X}-{plane}.json
      The velocity on a regular grid over one plane of one case, in the case's own frame (the pairs' coordinates, the
      tunnel's metres or the field's), over the speed that normalises the served pairs: u along x, and the second in-plane
      component (v on a horizontal plane, w on a vertical one), rounded to 1e-3, null inside buildings. Beside them the
      buildings' outline on the plane (the building patch cut by it), the speed the field was divided by, how well the
      sampled field reproduces the served pairs on that plane (the check that the frame and the scale are right), and the
      SHA-256 of every file it was read from.

Only this script reads the solves, and only where they exist: the first of EDDY3D_VAL, C:/Eddy3DVal, ~/Eddy3DVal holding
the study. It needs pyvista (VTK's OpenFOAM readers), which the pinned build does not install: the build draws the maps from
the committed snapshots and never runs this. Run it by hand after a solve changes:

    pip install pyvista==0.49.1 && python validation/extract_planes.py [A B ...]

The frame: every Eddy3D fixture here solves the tunnel scaled by `scale` with the wind along +y, so a case point (x, y, z)
sits at (-y, x, z) * scale in the solve ("quarter"), except the urbanMicroclimateFoam scenes (J, L), solved in the case's own
axes ("same"), and Case F, whose probes are written in the case's frame at full scale. The speed: the field's component along
x at the plane's served points against the pairs' U_model (|U| against the scalar for Case F), the least-squares slope through
the origin; the check requires the two to correlate at r > 0.98 (a wrong frame or scale does not) and fails otherwise. The
residual is the difference between sampling a field interpolated to the mesh points and the solver's own probes.
"""
from __future__ import annotations

import csv
import glob
import hashlib
import io
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RESULTS = os.path.join(HERE, "results")
OUT = os.path.join(RESULTS, "planes")
NX = 320          # grid points along x; the other axis keeps the cells square

# case: study folder, pairs stem, scale (solve units per case unit), frame, normalising length and its name, rows kept,
# the component the speed is fitted on, and the planes: (name, axis, value, (x0, x1, a0, a1), tolerance for "on the plane")
CASES = {
    "A": dict(study="aij_A_realizableKE_L3", stem="caseA_openfoam12_realizableKE", scale=100.0, frame="quarter", L=0.16, Lname="H",
              planes=[("z0p01", "z", 0.01, (-0.24, 0.80, -0.24, 0.24), 1e-6), ("y0", "y", 0.0, (-0.24, 0.80, 0.0, 0.40), 1e-6)]),
    "F": dict(study="aij_F_realizableKE_L3", stem="caseF_openfoam12_realizableKE", scale=1.0, frame="same", L=1.0, Lname="1 m",
              keep=lambda r: r["frame"] == "agl" and r["source"] == "tunnel", zcol="z_probe", scalar="Umag_model",
              planes=[("z14", "z", 14.0, (-450.0, 450.0, -350.0, 450.0), 1e-6)]),
    "G": dict(study="aij_G_2d_conifer", stem="caseG_openfoam12_realizableKE", scale=1.0, frame="quarter", L=7.0, Lname="H",
              keep=lambda r: r["arm"] == "conifer",
              planes=[("y0", "y", 0.0, (-20.0, 50.0, 0.0, 20.0), 1e-6)]),
    "H": dict(study="aij_H_realizableKE_L3", stem="caseH_openfoam12_realizableKE", scale=100.0, frame="quarter", L=0.2, Lname="H",
              planes=[("z0p0125", "z", 0.0125, (-0.25, 0.45, -0.25, 0.25), 1e-6), ("y0", "y", 0.0, (-0.25, 0.45, 0.0, 0.40), 1e-6)]),
    "I": dict(study="aij_I_realizableKE_L3", stem="caseI_openfoam12_realizableKE", scale=60.0, frame="quarter", L=0.1, Lname="H",
              keep=lambda r: r["instrument"] == "ldv",
              planes=[("y0", "y", 0.0, (-0.20, 0.50, 0.0, 0.25), 1e-6)]),
    "J": dict(study="aij_J_umf/aijJ_umf_realizableKE", stem="caseJ_umf_realizableKE", scale=62.5, frame="same", L=0.16, Lname="H",
              planes=[("z0p04", "z", 0.04, (-0.20, 0.40, -0.20, 0.20), 1e-6), ("y0", "y", 0.0, (-0.20, 0.40, 0.0, 0.30), 1e-6)]),
    "K": dict(study="aij_K_realizableKE_L3", stem="caseK_openfoam12_realizableKE", scale=100.0, frame="quarter", L=0.06, Lname="H",
              planes=[("z0p01", "z", 0.01, (-0.18, 0.36, -0.21, 0.21), 1e-6), ("y0", "y", 0.0, (-0.18, 0.36, 0.0, 0.15), 1e-6)]),
    "L": dict(study="aij_L_umf/aijL_umf_cell3", stem="caseL_umf_realizableKE", scale=100.0, frame="same", L=0.06, Lname="H",
              planes=[("z0p01", "z", 0.01, (-0.24, 0.42, -0.24, 0.24), 1e-6), ("y0", "y", 0.0, (-0.24, 0.42, 0.0, 0.18), 1e-6)]),
    "M": dict(study="aij_M_realizableKE_L3_s3", stem="caseM_openfoam12_realizableKE", scale=1.0, frame="quarter", L=1.0, Lname="1 m",
              planes=[("z35p5", "z", 35.5, (-150.0, 150.0, -140.0, 140.0), 0.5)]),
}


def validation_root(study):
    for p in (os.environ.get("EDDY3D_VAL"), r"C:/Eddy3DVal", os.path.expanduser("~/Eddy3DVal")):
        if p and os.path.isdir(os.path.join(p, study)):
            return p
    return None


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def to_study(c, cfg):
    """Case-frame points (n, 3) to the solve's frame."""
    s = cfg["scale"]
    if cfg["frame"] == "quarter":
        return np.c_[-c[:, 1], c[:, 0], c[:, 2]] * s
    return c * s


def to_case_vec(u, cfg):
    """Velocities in the solve's frame to the case's (u along x)."""
    if cfg["frame"] == "quarter":
        return np.c_[u[:, 1], -u[:, 0], u[:, 2]]
    return u


def to_case_pts(p, cfg):
    s = cfg["scale"]
    if cfg["frame"] == "quarter":
        return np.c_[p[:, 1], -p[:, 0], p[:, 2]] / s
    return p / s


def read_solve(case_dir):
    """The last time of the solve: the air (or only) region's mesh with point data, the building walls, and the U files."""
    import pyvista as pv

    foam = sorted(glob.glob(os.path.join(case_dir, "*.foam")))[0]
    umf = os.path.isdir(os.path.join(case_dir, "processor0")) and os.path.isdir(os.path.join(case_dir, "constant", "air"))
    r = pv.POpenFOAMReader(foam) if umf else pv.OpenFOAMReader(foam)
    if umf:
        r.case_type = "decomposed"
    t = r.time_values[-1]
    r.set_active_time_value(t)
    r.disable_all_patch_arrays()
    names = r.patch_array_names
    mesh_name = "/air/internalMesh" if umf else "internalMesh"
    walls = [n for n in names if n.endswith("patch/building") or n.endswith("/air/patch/buildings")]
    for n in [mesh_name] + walls:
        r.enable_patch_array(n)
    mb = r.read()
    region = mb["air"] if umf else mb
    mesh = region["internalMesh"]
    if umf:                             # the processors' meshes share their boundary points twice: merge them, or the field has seams there
        mesh = mesh.clean(tolerance=1e-9, remove_unused_points=False, produce_merge_map=False)
    mesh = mesh.cell_data_to_point_data()
    bld = None
    if walls:
        b = region["boundary"]
        bld = b[b.keys()[0]]
    tdir = f"{t:g}"
    files = sorted(glob.glob(os.path.join(case_dir, "processor*", tdir, "air", "U")) if umf else glob.glob(os.path.join(case_dir, tdir, "U")))
    return mesh, bld, t, files


def pairs(cfg):
    with io.open(os.path.join(RESULTS, cfg["stem"] + "_pairs.csv"), encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if cfg.get("keep", lambda r: True)(r)]
    return rows


def fnum(v):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return math.nan
    return f


def extract(case, cfg, root):
    case_dir = os.path.join(root, cfg["study"])
    sub = sorted(glob.glob(os.path.join(case_dir, "study", "case_*")))
    case_dir = sub[0] if sub else case_dir
    mesh, bld, t, files = read_solve(case_dir)
    rows = pairs(cfg)
    zcol = cfg.get("zcol", "z")
    import pyvista as pv

    coord = lambda r, k: fnum(r[zcol] if k == "z" else r.get(k, 0.0) or 0.0)  # noqa: E731

    def fit(on, uref=None):
        """The field against the pairs at their points: the speed (least squares through the origin), r and the rms residual."""
        P = np.array([[coord(r, "x"), coord(r, "y"), coord(r, "z")] for r in on])
        S = pv.PolyData(to_study(P, cfg)).sample(mesh)
        Uc = to_case_vec(np.asarray(S["U"]), cfg)
        if "scalar" in cfg:
            ref, got = np.array([fnum(r[cfg["scalar"]]) for r in on]), np.linalg.norm(Uc, axis=1)
        else:
            ref, got = np.array([fnum(r["U_model"]) for r in on]), Uc[:, 0]
        good = (np.asarray(S["vtkValidPointMask"]) > 0) & np.isfinite(ref)
        got, ref = got[good], ref[good]
        uref = uref or float(got @ ref / (ref @ ref))
        return uref, float(np.corrcoef(got, ref)[0, 1]), float(np.sqrt(np.mean((got / uref - ref) ** 2))), int(good.sum())

    uref, r_all, rms_all, n_all = fit(rows)          # one speed per case, as the pairs have one
    print(f"{case}: U_ref {uref:.4f} from {n_all} points, r {r_all:.4f}, rms {rms_all:.4f}")
    for name, axis, value, (x0, x1, a0, a1), tol in cfg["planes"]:
        on = [r for r in rows if abs(coord(r, axis) - value) <= tol]
        _, r_corr, rms, n = fit(on, uref)
        print(f"  {name}: {n} of {len(on)} points, r {r_corr:.4f}, rms {rms:.4f}")
        assert r_corr > 0.98, f"{case} {name}: the sampled field does not reproduce the pairs (frame or scale wrong)"

        ny = max(2, int(round(NX * (a1 - a0) / (x1 - x0))))
        gx, ga = np.linspace(x0, x1, NX), np.linspace(a0, a1, ny)
        g1, g2 = np.meshgrid(gx, ga)
        G = np.c_[g1.ravel(), g2.ravel(), np.full(g1.size, value)] if axis == "z" else np.c_[g1.ravel(), np.full(g1.size, value), g2.ravel()]
        Sg = pv.PolyData(to_study(G, cfg)).sample(mesh)
        Ug = to_case_vec(np.asarray(Sg["U"]), cfg) / uref
        Ug[np.asarray(Sg["vtkValidPointMask"]) == 0] = np.nan
        second = 1 if axis == "z" else 2

        outline = []
        if bld is not None:
            normal = to_study(np.array([[0, 0, 1.0]]) if axis == "z" else np.array([[0, 1.0, 0]]), {**cfg, "scale": 1.0})[0]
            origin = to_study(np.array([[0, 0, value]]) if axis == "z" else np.array([[0, value, 0]]), cfg)[0]
            cut = bld.slice(normal=normal, origin=origin)
            if cut.n_points:
                pts = to_case_pts(np.asarray(cut.points), cfg)[:, [0, second]]
                for a, b in np.asarray(cut.lines).reshape(-1, 3)[:, 1:]:
                    outline.append([round(float(v), 5) for v in (*pts[a], *pts[b])])
        outline.sort()

        q = lambda A: [[None if not math.isfinite(v) else round(float(v), 3) for v in row] for row in A]  # noqa: E731
        doc = {
            "case": case, "plane": {"name": name, "axis": axis, "value": value}, "study": cfg["study"], "time": t,
            "pairs": cfg["stem"] + "_pairs.csv", "L": cfg["L"], "Lname": cfg["Lname"],
            "U_ref": round(uref, 6), "check": {"points": n, "r": round(r_corr, 5), "rms": round(rms, 5)},
            "x": [round(float(v), 6) for v in gx], "a": [round(float(v), 6) for v in ga],
            "u": q(Ug[:, 0].reshape(ny, NX)), "second": "v" if axis == "z" else "w", "s": q(Ug[:, second].reshape(ny, NX)),
            "outline": outline,
            "sources": {os.path.relpath(f, root).replace(os.sep, "/"): sha256(f) for f in files},
        }
        os.makedirs(OUT, exist_ok=True)
        dest = os.path.join(OUT, f"case{case}-{name}.json")
        with io.open(dest, "w", encoding="utf-8", newline="\n") as f:
            json.dump(doc, f, separators=(",", ":"))
            f.write("\n")
        print(f"  wrote {os.path.relpath(dest, REPO)} ({os.path.getsize(dest) // 1024} KB, {len(outline)} outline segments)")


if __name__ == "__main__":
    wanted = sys.argv[1:] or list(CASES)
    for case in wanted:
        cfg = CASES[case]
        root = validation_root(cfg["study"])
        if root is None:
            print(f"{case}: {cfg['study']} not found under EDDY3D_VAL, C:/Eddy3DVal or ~/Eddy3DVal; kept the committed planes")
            continue
        extract(case, cfg, root)
