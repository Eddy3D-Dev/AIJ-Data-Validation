"""Snapshot the grid-convergence study of the OpenFOAM fixtures of Cases A and E into validation/results/grid/.

Eddy3D solved both fixtures on four meshes, every cell edge shrinking by sqrt(2) per step (cell scale 1.41, 1.00, 0.71,
0.50), and computed a per-point grid convergence index with foamgci (Eddy3D repository, testing/aij-openfoam-gci; its
docs/VALIDATION.md, section 22). The study ran Eddy3D's current set-up, the eddy-viscosity cap lifted: the configuration
of the community submission eddy3d-of12-nutcap-lifted, whose Case A scores its 1.00 mesh reproduces. The served runs of
validation/results/ keep OpenFOAM's cap, so the study is snapshotted beside them, never into them: its own model values,
measured values and bands, from one solve.

The GCI arithmetic is foamgci's; this script only picks, per point, the band of the 1.00 mesh, the medium mesh of the
triplet [1.41, 1.00, 0.71]:

  monotonic convergence   GCI_32 (Roache's index for the medium mesh, Celik et al. 2008 procedure, Fs = 1.25)
  oscillatory             half the spread of the three values (Celik et al. 2008)
  divergent, degenerate   no band (the change grows under refinement, or there is no change to measure)

It runs by hand, never in the build, like the other snapshots that read a solve:

  EDDY3D_GCI=<Eddy3D checkout>/testing/aij-openfoam-gci uv run python validation/snapshot_grid.py

Outputs, per case: grid/case{A,E}_openfoam12_realizableKE.csv (per point: the measured value, the 1.00 mesh's value and
its band, in the served pairs' units and keys) and .json (the meshes, the scores on each, the method and the source).
"""
from __future__ import annotations

import csv
import io
import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")
GCI = os.environ.get("EDDY3D_GCI", "")

FOAMGCI = "foamgci 3.5.0 (https://github.com/rithikrn/foamgci at 3b7274cb88421f90b3d783ad822f157d26849536)"
METHOD = ("Roache's grid convergence index by the procedure of Celik et al. (2008), safety factor 1.25, on three consecutive "
          f"meshes of a four-mesh ladder; computed by {FOAMGCI}; representative cell size h = N^(-1/3)")
BAND = ("per point, the uncertainty of the 1.00 mesh (the medium mesh of the triplet 1.41, 1.00, 0.71): GCI_32 where the three "
        "values converge monotonically, half the spread of the three values (Celik's oscillatory estimate) where they oscillate, "
        "and no band where the change grows under refinement (divergent) or vanishes (degenerate)")
CONFIGURATION = ("the served fixture with the eddy-viscosity cap lifted (nutMaxCoeff above any value the solve reaches), as Eddy3D "
                 "ships it: the configuration of the community submission eddy3d-of12-nutcap-lifted; the served run keeps OpenFOAM's cap")
COARSE, SERVED = "_cs1.4142", ""          # study-folder suffixes: the triplet's coarse mesh and the 1.00 mesh


def _rows(path):
    with io.open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _band(r):
    if r["regime"] == "monotonic":
        return float(r["gci_medium_abs"])
    if r["regime"] == "oscillatory":
        return float(r["u_osc_abs"])
    return None


def _per_point(evidence_csv, study, state=""):
    """{point (1-based row of the probe table): (x, y, z, value on the 1.00 mesh, band or None, regime)}."""
    tag = f":{state}" if state else ""
    served, coarse = study + SERVED + tag, study + COARSE + tag
    out = {}
    for r in _rows(evidence_csv):
        i = int(r["point"])
        at = next((k for k in ("coarse", "medium", "fine") if r[f"label_{k}"] == served), None)
        if at is None:
            continue
        band, regime = (_band(r), r["regime"]) if r["label_coarse"] == coarse else (None, "lost on the coarsest mesh")
        if i not in out or r["label_coarse"] == coarse:
            out[i] = (float(r["x"]), float(r["y"]), float(r["z"]), float(r[f"phi_{at}"]), band, regime)
    return out


def _run_results(study):
    for root, dirs, _ in os.walk(os.path.join(GCI, "runs")):
        if study in dirs:
            with io.open(os.path.join(root, study, "results.json"), encoding="utf-8") as f:
                return json.load(f)
    raise SystemExit(f"no results.json for {study} under {GCI}/runs")


def _scores(res, key):
    m = res.get(key)
    return None if not isinstance(m, dict) else {k: m[k] for k in ("Fac2", "Fb", "HitRate", "R") if k in m}


def _fmt(v):
    return "" if v is None else repr(v)


def _source():
    commit = subprocess.run(["git", "-C", GCI, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return {"repository": "https://github.com/Eddy3D-Dev/Eddy3D", "folder": "testing/aij-openfoam-gci", "commit": commit,
            "documentation": "docs/VALIDATION.md, section 22"}


def _write(case, columns, rows, summary):
    os.makedirs(os.path.join(RESULTS, "grid"), exist_ok=True)
    base = os.path.join(RESULTS, "grid", f"case{case}_openfoam12_realizableKE")
    with io.open(base + ".csv", "w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(columns)
        w.writerows(rows)
    with io.open(base + ".json", "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {os.path.relpath(base, HERE)}.csv ({len(rows)} rows) and .json")


def _summary(case, grids, studies, headline, extra):
    scores = {label: [_scores(_run_results(s), key) for s in studies] for label, key in headline.items()}
    return {"case": case, "engine": "openfoam12-realizableKE", "configuration": CONFIGURATION, "method": METHOD,
            "band_meaning": BAND, "grids": grids, "scores_on_each_grid": scores, **extra, "source": _source()}


def _measured_k_a(uh):
    """k/U_H^2 of RS-caseA.csv as published (m^2/s^2, -999.9 = not measured), in its row order; the served pairs carry no k."""
    with io.open(os.path.join(os.path.dirname(HERE), "raw", "cases", "case-a", "RS-caseA.csv"), encoding="utf-8-sig") as f:
        rd = csv.reader(f)
        col = [h.split("(")[0].split("[")[0].strip() for h in next(rd)].index("k")
        out = []
        for r in rd:
            if any(c.strip() for c in r):
                v = float(r[col])
                out.append(None if abs(v + 999.9) < 1e-6 else v / uh ** 2)
    return out


def snapshot_a():
    summ = json.load(io.open(os.path.join(GCI, "evidence", "summary.json"), encoding="utf-8"))["cases"]["A"]
    study = "aij_A_realizableKE_L3"
    per = {q: _per_point(os.path.join(GCI, "evidence", f"A_{q}_points.csv"), study) for q in "UVWk"}
    pairs = _rows(os.path.join(RESULTS, "caseA_openfoam12_realizableKE_pairs.csv"))
    scale = _run_results(study)["scale"]
    k_meas = _measured_k_a(4.491)                  # U_H of Case A, as the served pairs are normalised
    if len(k_meas) != len(pairs):
        raise SystemExit(f"RS-caseA.csv has {len(k_meas)} rows, the pairs {len(pairs)}")
    rows = []
    for i, p in enumerate(pairs, start=1):        # the probe table's rows are the measured table's, in order
        row = [p["point_id"], p["x"], p["y"], p["z"]]
        for q in "UVWk":
            x, y, z, value, band, regime = per[q][i]
            # the solve's frame is full scale with the wind along +y: x = y_case/scale, y = -x_case/scale, z = z_case/scale
            if max(abs(y / scale - float(p["x"])), abs(-x / scale - float(p["y"])), abs(z / scale - float(p["z"]))) > 1e-6:
                raise SystemExit(f"Case A point {p['point_id']}: the GCI table's point {i} is at ({x}, {y}, {z}) in the solve's frame")
            meas = p[f"{q}_meas"] if q != "k" else _fmt(k_meas[i - 1])
            row += [meas, repr(value), _fmt(band), regime]
        rows.append(row)
    lr = summ["scalars"]["recirculation.LrOverH"]
    grids = [{"cell_scale": g["cellScale"], "cells": g["cells"], "iterations": g["iterations"]} for g in summ["grids"]]
    extra = {"refinement_ratios": summ["refinement_ratios"],
             "recirculation_Lr_over_H": [lr[0]["phi_coarse"], lr[0]["phi_medium"], lr[0]["phi_fine"], lr[1]["phi_fine"]],
             "recirculation_Lr_over_H_extrapolated": {"value": lr[1]["phi_exact"], "observed_order": lr[1]["p_apparent"],
                                                      "note": "from the three finest meshes, whose observed order sits at foamgci's clip of 6; "
                                                              "the triplet with the 1.00 mesh oscillates"}}
    cols = ["point_id", "x", "y", "z"] + [c for q in "UVWk" for c in (f"{q}_meas", f"{q}_model", f"{q}_band", f"{q}_regime")]
    _write("A", cols, rows, _summary("A", grids, [g["label"] for g in summ["grids"]],
                                     {"U": "velocity.U", "V": "velocity.V", "W": "velocity.W", "k": "k"}, extra))


def snapshot_e():
    summ = json.load(io.open(os.path.join(GCI, "evidence", "summary.json"), encoding="utf-8"))["cases"]
    study = "aij_E_realizableKE_L3"
    pairs = _rows(os.path.join(RESULTS, "caseE_openfoam12_realizableKE_pairs.csv"))
    rows = []
    for state in ("bc", "ac"):
        per = {name: _per_point(os.path.join(GCI, "evidence", f"E_{state}_{state}.{q}_points.csv"), study, state)
               for name, q in (("scalar", "rms"), ("vector", "Umag"))}
        at = {(round(v[0], 3), round(v[1], 3)): (v, per["vector"][i]) for i, v in per["scalar"].items()}
        for p in (r for r in pairs if r["config"] == state):
            s, v = at[(round(float(p["x"]), 3), round(float(p["y"]), 3))]
            rows.append([p["config"], p["wind_direction"], p["point_id"], p["x"], p["y"], p["z"], p["measured_ratio"],
                         repr(s[3]), _fmt(s[4]), s[5], repr(v[3]), _fmt(v[4]), v[5]])
    grids = [{"cell_scale": a["cellScale"], "iterations": a["iterations"], "cells": {"bc": b["cells"], "ac": a["cells"]}}
             for a, b in zip(summ["E_ac"]["grids"], summ["E_bc"]["grids"])]
    extra = {"refinement_ratios": {"bc": summ["E_bc"]["refinement_ratios"], "ac": summ["E_ac"]["refinement_ratios"]},
             "note": "the 1.41 mesh puts point 74 inside a building in both states, so that point has no band and that mesh no scores"}
    _write("E", ["config", "wind_direction", "point_id", "x", "y", "z", "measured_ratio", "scalar_ratio", "scalar_band", "scalar_regime",
                 "vector_ratio", "vector_band", "vector_regime"], rows,
           _summary("E", grids, [g["label"].split(":")[0] for g in summ["E_ac"]["grids"]],
                    {"before, √(|U|²+2k)": "vr.bc.SW.rms", "before, |U|": "vr.bc.SW.Umag",
                     "after, √(|U|²+2k)": "vr.ac.SW.rms", "after, |U|": "vr.ac.SW.Umag"}, extra))


if __name__ == "__main__":
    if not os.path.isdir(os.path.join(GCI, "evidence")):
        raise SystemExit("set EDDY3D_GCI to the Eddy3D checkout's testing/aij-openfoam-gci")
    snapshot_a()
    snapshot_e()
