"""Validation figures for AIJ UWE Cases K (9 x 9 cube array, floor point source) and G (tree belt) solved with Eddy3D / OpenFOAM 12.

Three figures, each answering one question:

  case-k-openfoam-agreement.png   Does the model agree with the tunnel?  Case K: measured against modelled U, W and k, and the
                      dimensionless concentration c* at all three turbulent Schmidt numbers (0.3, 0.5, 0.7), with the 1:1 line and the
                      factor-of-two band. The four points within one cube height of the source are drawn open.
  case-g-openfoam-sweep.png       Does it agree with the field, and what does the unknown drag do?  Case G: measured against modelled
                      |U| and k at the 28 points behind the belt, one column per arm of Eddy3D's drag sweep (no belt, three crowns of
                      rising leaf area density x drag coefficient, and the real 74 m belt as a half domain).
  case-g-openfoam-stations.png    The same arms by distance behind the belt: the mean speed and the mean k at the seven stations.

Inputs, all in this repository: the cleaned measurement tables clean/cases/{K,G}/points.csv, and the per-point pairs
validation/results/case{K,G}_openfoam12_realizableKE*_pairs.csv built from them and from the probes the Eddy3D fixtures
TestAijCaseKContainerE2E and TestAijCaseGContainerE2E wrote (validation/results/*_probes.csv, snapshots of the probe files under
~/Eddy3DVal/aij_K_realizableKE_L3 and ~/Eddy3DVal/aij_G_*; refreshed from there when that folder exists, set EDDY3D_VAL for another
location). The scores in validation/results/case{K,G}_openfoam12_*.json are computed FROM THE PAIRS by validation/dispersion_metrics.py;
this script recomputes them on every run and fails if a file disagrees. When the Eddy3D results are present it also scores the
published CSVs the way the fixtures do and requires the fixtures' own numbers to 1e-9 (the control that these metrics are theirs), and prints
the recomputed scores next to the fixtures' (they differ in the measured side: the cleaned workbooks against the rounded CSVs).

Case K. The model velocity is divided by the stated U_H = 2.33 m/s, as the measurement is: the dataset's U_H is only the common divisor,
the solve is driven by the measured approach profile (3.23 m/s at 0.2 m), which gives 1.97 m/s at z = H. c* = C/c0 for the measurement
(c0 = q/(U_H H^2) = 429.2 ppm, the cleaned table's concentration_ratio), c* = c U_H H^2/Q (full scale, Q = 1 kg/s) for the model.
Probe frame: the fixture solves the case turned so that the wind blows along world +y, at 1:100; X = y/100, Y = -x/100, Z = z/100,
U = U_y, V = -U_x, W = U_z.

Case G. Field data, full scale. The measurement is U/U_H and k/U_H^2 with U_H the wind at the tree height (7 m) during each period. The model
is divided by its OWN U(7 m) at x = -35 m (the tabulated inlet has a smooth floor, so the approach speeds up along the fetch) in the headline, and by
the imposed U_H = 5.6 (7/9)^0.22 m/s in the second set of scores. Eddy3D's trees are a momentum sink only: k is not modelled by the canopy.

Colours follow plotstyle.py: the OpenFOAM model is its engine colour (OPENFOAM); the arms of the drag sweep take viridis, which is for magnitudes;
reference geometry (1:1 line, factor-of-two band) is recessive grey.
"""
from __future__ import annotations

import csv
import io
import math
import os
import re

import numpy as np
import ultraplot as uplt

import dispersion_metrics as DM
import plotstyle as style
from snapshot_common import (RESULTS, SPECIES, check_snapshot, clean_table, column, fnum, is_score as is_metric, non_scores, panel, raw_table, read_json, read_lf, read_pairs,
                             sha256, stats_text, validation_root, write_json, write_lf, write_pairs, mirror_mean)

# ----------------------------------------------------------------------------- Case K

K_STUDY = "aij_K_realizableKE_L3"
K_UH, K_SCALE, K_HFULL, K_H, K_Q = 2.33, 100.0, 6.0, 0.06, 3.6e-6      # stated U_H [m/s], model scale, full-scale H [m], cube [m], tracer flow [m3/s]
K_PITCH, K_X0, K_SOURCE = 0.12, -0.36, (-0.15, 0.0)                    # model frame, m
K_STEM = "caseK_openfoam12_realizableKE"
K_PAIR_FIELDS = ["point_id", "x", "y", "z", "region", "near_source", "U_meas", "V_meas", "W_meas", "U_model", "V_model", "W_model", "k_meas", "k_model",
                 "cstar_meas", "cstar_sct03", "cstar_sct05", "cstar_sct07"]
K_REGIONS = ("aboveRoof", "lateralStreet", "crossStreet")
# what the fixture records that is not recomputed here (the structure it asserted, the sampling and symmetry notes, the inflow), and what is recomputed from the pairs
K_RECORDED = ("note.", "sampling.", "symmetry.", "structure.", "inflow.U.", "plume.")
K_RECOMPUTED = ("velocity.", "k.", "cstar.", "region.", "shift.", "scalarSpeed.")


def k_region(x, z):
    """CubeArrayCase.Region: above the roofs, in a street along the wind (x inside a row's extent) or across it (x in a gap between rows)."""
    if z > K_H + 1e-9:
        return "aboveRoof"
    return "lateralStreet" if any(K_X0 + i * K_PITCH - 1e-9 <= x <= K_X0 + i * K_PITCH + K_H + 1e-9 for i in range(9)) else "crossStreet"


def k_near(x, y, z):
    """CubeArrayCase.NearSource: within one cube height of the floor outlet, where a source sized to a cell cannot be scored."""
    return math.sqrt((x - K_SOURCE[0]) ** 2 + (y - K_SOURCE[1]) ** 2 + z * z) <= K_H + 1e-9


def read_probe(src, scale, species=True):
    """Rows of a fixture probe file (the case frame, full scale) in the MODEL frame: X = y/scale, Y = -x/scale, Z = z/scale, U = U_y, V = -U_x, W = U_z."""
    out = []
    with io.open(src, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            g = lambda k: float(r[k]) if k in r and r[k] != "" else math.nan  # noqa: E731
            row = {"X": g("y") / scale, "Y": -g("x") / scale, "Z": g("z") / scale, "U": g("U_y"), "V": -g("U_x"), "W": g("U_z"), "mag": g("U_mag"), "k": g("k")}
            if species:
                row.update({sp: g(f"c_{sp}") for sp, _ in SPECIES})
            out.append(row)
    return out


def k_cstar_model(c):
    """c* = c U_H H^2 / Q, full scale (H = 6 m, Q = 1 kg/s), the fixture's CubeArrayCase.CaseCStar."""
    return c * K_UH * K_HFULL ** 2


def k_rows(measured, probes):
    """The pairs of Case K: the cleaned table's rows against the probes at the same points (one probe per published point, in the table's order)."""
    rows = []
    for m, p in zip(measured, probes):
        x, y, z = float(m["x"]), float(m["y"]), float(m["z"])
        assert abs(p["X"] - x) < 1e-6 and abs(p["Y"] - y) < 1e-6 and abs(p["Z"] - z) < 1e-6, (m["point_id"], (x, y, z), (p["X"], p["Y"], p["Z"]))
        r = {"point_id": int(m["point_id"]), "x": x, "y": y, "z": z, "region": k_region(x, z), "near_source": int(k_near(x, y, z))}
        for q in "UVW":
            r[f"{q}_meas"] = fnum(m[q]) / K_UH
            r[f"{q}_model"] = p[q] / K_UH
        r["k_meas"] = fnum(m["k"]) / K_UH ** 2
        r["k_model"] = p["k"] / K_UH ** 2
        r["cstar_meas"] = fnum(m["concentration_ratio"])
        for sp, _ in SPECIES:
            r[f"cstar_{sp}"] = k_cstar_model(p[sp])
        rows.append(r)
    return rows


def k_scores(rows):
    """Every score of Case K from its pairs. Keys follow the fixture's results.json."""
    c = lambda key: column(rows, key)  # noqa: E731
    out = {f"velocity.{q}": DM.velocity(c(f"{q}_meas"), c(f"{q}_model")) for q in "UVW"}
    out["k"] = DM.turbulence(c("k_meas"), c("k_model"))
    # V has a constant offset and no antisymmetric part, and a model with V = 0 everywhere hits 0.05 U_H almost everywhere: V's hit rate scores nothing
    out["velocity.V.zeroModelHitRate"] = float(np.mean(np.abs(c("V_meas")) <= 0.05))
    out["velocity.V.measuredMeanOverUh"] = float(np.mean(c("V_meas")))
    cm, near = c("cstar_meas"), c("near_source") == 1
    pts = np.c_[c("x"), c("y"), c("z")]
    out["cstar.peakMeasured"] = float(np.nanmax(cm))
    out["cstar.nearSource.points"] = int(near.sum())
    # the ceiling of a y-symmetric model on a file whose plume is displaced toward -y: no symmetric prediction fits a mirror pair better than its mean
    out["velocity.U.symmetryCeiling"] = DM.velocity(c("U_meas"), mirror_mean(pts, c("U_meas")))
    ceiling = mirror_mean(pts, cm)
    out["cstar.symmetryCeiling"] = DM.concentration(cm, ceiling)
    out["cstar.symmetryCeiling.excludingNearSource"] = DM.concentration(cm[~near], ceiling[~near])
    region = np.array([r["region"] for r in rows])
    for sp, _ in SPECIES:
        cp = c(f"cstar_{sp}")
        out[f"cstar.c_{sp}"] = DM.concentration(cm, cp)
        out[f"cstar.c_{sp}.excludingNearSource"] = DM.concentration(cm[~near], cp[~near])
        out[f"cstar.c_{sp}.peakAtReferencePoints"] = float(np.nanmax(cp))
        out[f"cstar.c_{sp}.nearSourceModelOverMeasured"] = float(np.nanmean(cp[near] / cm[near]))
    for name in K_REGIONS:
        sel = region == name
        out[f"region.{name}.points"] = int(sel.sum())
        out[f"region.{name}.U"] = DM.velocity(c("U_meas")[sel], c("U_model")[sel])
        out[f"region.{name}.k"] = DM.turbulence(c("k_meas")[sel], c("k_model")[sel])
        far = sel & ~near
        for sp, _ in SPECIES:
            cp = c(f"cstar_{sp}")
            out[f"region.{name}.cstar.c_{sp}"] = DM.concentration(cm[sel], cp[sel])
            if far.sum() != sel.sum() and far.sum() > 1:
                out[f"region.{name}.cstar.c_{sp}.excludingNearSource"] = DM.concentration(cm[far], cp[far])
    return out


K_QUANTITY = ("U, V, W over the stated U_H = 2.33 m/s and k over U_H^2 (split fibre, 203 points); c* = C/c0 (c0 = q/(U_H H^2) = 429.2 ppm) against the "
              "model's c U_H H^2/Q for turbulent Schmidt numbers 0.3, 0.5 and 0.7; the four points within one cube height of the source are scored with "
              "and without")


def k_snapshot(root):
    src = os.path.join(root, K_STUDY)
    probe = os.path.join(src, "reference.probe.csv")
    write_lf(os.path.join(RESULTS, f"{K_STEM}_probes.csv"), read_lf(probe))
    rows = k_rows(clean_table("K"), read_probe(probe, K_SCALE))
    write_pairs(os.path.join(RESULTS, f"{K_STEM}_pairs.csv"), K_PAIR_FIELDS, rows)
    fx = read_json(os.path.join(src, "results.json"))
    keep = non_scores(fx, drop=K_RECORDED + K_RECOMPUTED + ("quantity", "reference."))
    sources = {f"{K_STUDY}/{n}": sha256(os.path.join(src, n)) for n in ("reference.probe.csv", "results.json", "study/case_180/run_01_foamRun.txt", "config.json")}
    res = {**keep, "quantity": K_QUANTITY, "uhStated": K_UH, "pairs": f"{K_STEM}_pairs.csv", "probes": f"{K_STEM}_probes.csv",
           "solveLog": {"iterationsRun": 3000, "stoppedBy": "the iteration limit: the log has no 'solution converged' line (residualControl not met)",
                        "finalInitialResiduals": final_residuals(os.path.join(src, "study", "case_180", "run_01_foamRun.txt"))},
           "fixtureRecorded": {k: v for k, v in fx.items() if k.startswith(K_RECORDED) and not is_metric(v)},
           "scoresFrom": "the pairs file (validation/dispersion_metrics.py); the fixture's own scores, computed against RS_caseK.csv, are in Eddy3D's results.json",
           "sources": sources, **k_scores(rows)}
    write_json(os.path.join(RESULTS, f"{K_STEM}.json"), res)
    print(f"snapshot {K_STEM}: {len(rows)} pairs")


def final_residuals(log, tail_bytes=600000):
    """The initial residuals of every field in the last time step of a simpleFoam/foamRun log (tail read; the logs are 6 MB)."""
    size = os.path.getsize(log)
    with open(log, "rb") as f:
        f.seek(max(0, size - tail_bytes))
        text = f.read().decode("utf-8", "ignore")
    block = text.split("\nTime = ")[-1]
    return {m.group(1): float(m.group(2)) for m in re.finditer(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)", block)}


def k_control(root, fx):
    """Case K's published CSV scored the way the fixture scores it, with its own probes: its results.json to 1e-9."""
    rs = raw_table("case-k/RS_caseK.csv")
    probes = read_probe(os.path.join(root, K_STUDY, "reference.probe.csv"), K_SCALE)
    rows = []
    for i, p in enumerate(probes):
        x, y, z = rs["x"][i], rs["y"][i], rs["z"][i]
        r = {"point_id": i + 1, "x": x, "y": y, "z": z, "region": k_region(x, z), "near_source": int(k_near(x, y, z))}
        for q in "UVW":
            r[f"{q}_meas"], r[f"{q}_model"] = rs[q][i] / K_UH, p[q] / K_UH
        r["k_meas"], r["k_model"] = rs["k"][i] / K_UH ** 2, p["k"] / K_UH ** 2
        r["cstar_meas"] = rs["C"][i] * 1e-6 * K_UH * K_H ** 2 / K_Q
        for sp, _ in SPECIES:
            r[f"cstar_{sp}"] = k_cstar_model(p[sp])
        rows.append(r)
    got = k_scores(rows)
    checked = 0
    for key, mine in got.items():
        if key not in fx:
            continue
        if isinstance(mine, dict):
            assert DM.same(mine, fx[key], fixture=True), (K_STEM, key, mine, fx[key])
        else:
            assert abs(mine - fx[key]) <= 1e-9 * max(1.0, abs(fx[key])), (K_STEM, key, mine, fx[key])
        checked += 1
    print(f"fixture control {K_STEM}: {checked} scores reproduced from RS_caseK.csv and the fixture's probes")


def k_parity(fx):
    mine = read_json(os.path.join(RESULTS, f"{K_STEM}.json"))
    for key in ("velocity.U", "velocity.V", "velocity.W", "k", "cstar.c_sct03", "cstar.c_sct05", "cstar.c_sct07"):
        a, b = fx[key], mine[key]
        fb = "n/a" if b["Fb"] is None else format(b["Fb"], "+.4f")
        print(f"{K_STEM} {key}: R {a['R']:+.4f} -> {b['R']:+.4f}  FAC2 {a['Fac2']:.4f} -> {b['Fac2']:.4f}  FB {a['Fb']:+.4f} -> {fb}  n {a['Count']} -> {b['Count']}")


# ----------------------------------------------------------------------------- Case G

G_UB, G_HB, G_H, G_EXP, G_CENTRE_Y = 5.6, 9.0, 7.0, 0.22, 0.2
G_UH_IMPOSED = G_UB * (G_H / G_HB) ** G_EXP                                   # 5.2988 m/s: the imposed wind at the tree height
G_POINTS, G_FAR_AT, G_FAR_SEVEN = 28, 28, 3                                   # measured points; row of the far approach column in a probe file; its z = 7 m entry
# (arm id = the configuration, study folder, layout, LAD [1/m], Cd [-], the fixture's provenance sentence)
G_ARMS = [
    ("open-field", "aij_G_2d_open", "slab", 0.0, 0.0, "no trees: the open-field control on the identical mesh, inflow and numerics"),
    ("pine", "aij_G_2d_pine", "slab", 1.5, 0.20, "the vegetation library's 'Scots pine' (LAD 1.5, Cd 0.20): the lightest crown of the sweep"),
    ("conifer", "aij_G_2d_conifer", "slab", 2.5, 0.25, "the library's 'Conifer' (LAD 2.5, Cd 0.25): the middle of the sweep"),
    ("screen", "aij_G_2d_screen", "slab", 3.5, 0.25, "the library's 'Cypress screen' (LAD 3.5, Cd 0.25): the densest crown, the upper bracket of the sweep"),
    ("half-belt-conifer", "aij_G_3d_conifer", "half belt", 2.5, 0.25, "the 'Conifer' crown on the real 74 m belt: a half domain with the measured plane on the symmetry plane"),
]
G_STEM = "caseG_openfoam12_realizableKE"
G_PAIR_FIELDS = ["arm", "point_id", "x", "z", "U_meas", "U_model", "Urms_model", "U_model_imposed", "Urms_model_imposed", "k_meas", "k_model", "u7_mps"]
G_QUANTITY = ("U/U_H and k/U_H^2 at the 28 points, U_H the wind at the tree height (7 m): the measured mean scalar speed against the modelled |U| and "
              "sqrt(|U|^2 + 2k), both over the model's own U(7 m) at x = -35 m, and over the imposed U_H = 5.299 m/s; LAD and Cd are not in the dataset")


def g_name(arm):
    return f"{G_STEM}_{arm}"


def g_rows(arm, measured, probes):
    """The pairs of one arm: the 28 published points against the probes at x = 1.75 ... 35 m behind the belt (the table's order)."""
    u7 = probes[G_FAR_AT + G_FAR_SEVEN]["mag"]
    rows = []
    for m, p in zip(measured, probes[:G_POINTS]):
        assert abs(p["X"] - float(m["x"])) < 1e-9 and abs(p["Z"] - float(m["z"])) < 1e-9, (arm, m["point_id"], m["x"], m["z"], p["X"], p["Z"])
        rms = math.sqrt(p["mag"] ** 2 + 2 * p["k"])
        rows.append({"arm": arm, "point_id": int(m["point_id"]), "x": float(m["x"]), "z": float(m["z"]), "U_meas": fnum(m["velocity_ratio"]), "U_model": p["mag"] / u7,
                     "Urms_model": rms / u7, "U_model_imposed": p["mag"] / G_UH_IMPOSED, "Urms_model_imposed": rms / G_UH_IMPOSED,
                     "k_meas": fnum(m["k_ratio"]), "k_model": p["k"] / u7 ** 2, "u7_mps": u7})
    return rows


def g_scores(rows):
    c = lambda key: column(rows, key)  # noqa: E731
    return {"score.U.ownApproach": DM.velocity(c("U_meas"), c("U_model")), "score.U.imposedUH": DM.velocity(c("U_meas"), c("U_model_imposed")),
            "score.rms.ownApproach": DM.velocity(c("U_meas"), c("Urms_model")), "score.rms.imposedUH": DM.velocity(c("U_meas"), c("Urms_model_imposed")),
            "score.k.ownApproach": DM.turbulence(c("k_meas"), c("k_model"))}


def g_stations(rows):
    """Mean over the four heights at each of the seven stations: measured and modelled."""
    out = []
    for x in sorted({r["x"] for r in rows}):
        sel = [r for r in rows if r["x"] == x]
        mean = lambda key: float(np.mean([r[key] for r in sel]))  # noqa: E731
        out.append({"x": x, "xOverH": x / G_H, "observedU": mean("U_meas"), "modelU": mean("U_model"), "modelRms": mean("Urms_model"),
                    "observedK": mean("k_meas"), "modelK": mean("k_model")})
    return out


def g_extras(arm_rows):
    """What the sweep as a whole says, from the pairs: the root-mean-square error of U per arm (the calibration) and the half belt against the slab."""
    rmse = {a: float(np.sqrt(np.mean((column(r, "U_model") - column(r, "U_meas")) ** 2))) for a, r in arm_rows.items()}
    d = column(arm_rows["half-belt-conifer"], "U_model") - column(arm_rows["conifer"], "U_model")
    return rmse, {"maxAbs": float(np.abs(d).max()), "meanSigned": float(d.mean()), "meanAbs": float(np.abs(d).mean()),
                  "r": float(np.corrcoef(column(arm_rows["half-belt-conifer"], "U_model"), column(arm_rows["conifer"], "U_model"))[0, 1])}


def g_snapshot(root):
    measured = clean_table("G")
    fixture = read_json(os.path.join(root, "aij_G", "results.json"))
    arm_rows, pair_rows = {}, []
    for arm, folder, layout, lad, cd, why in G_ARMS:
        src = os.path.join(root, folder)
        probe = os.path.join(src, "belt.probe.csv")
        write_lf(os.path.join(RESULTS, f"{g_name(arm)}_probes.csv"), read_lf(probe))
        arm_rows[arm] = g_rows(arm, measured, read_probe(probe, 1.0, species=False))
        pair_rows += arm_rows[arm]
    write_pairs(os.path.join(RESULTS, f"{G_STEM}_pairs.csv"), G_PAIR_FIELDS, pair_rows)
    rmse, end_effect = g_extras(arm_rows)
    shared = {k: fixture[k] for k in ("turbulenceModel", "numericsLevel", "iterations", "cpus", "idealisation", "inflow", "k.assertion", "lad.provenance")}
    for arm, folder, layout, lad, cd, why in G_ARMS:
        src = os.path.join(root, folder)
        pre = folder + "."
        own = {k[len(pre):]: v for k, v in fixture.items() if k.startswith(pre) and not is_metric(v) and not k.startswith(pre + "byStation")}
        log = os.path.join(src, "study", "case_180", "run_01_foamRun.txt")
        res = {"case": fixture["case"], "reference": fixture["reference"], **shared, "quantity": G_QUANTITY, "arm": arm, "layout": layout,
               "Lad": lad, "Cd": cd, "dragPerMetre": lad * cd, "armProvenance": why, **own,
               "solveLog": {"iterationsRun": 3000, "stoppedBy": "the iteration limit: the log has no 'solution converged' line (residualControl not met)",
                         "finalInitialResiduals": final_residuals(log)},
               "pairs": f"{G_STEM}_pairs.csv", "probes": f"{g_name(arm)}_probes.csv", "UhImposed": G_UH_IMPOSED,
               "scoresFrom": "the pairs file (validation/dispersion_metrics.py); the fixture's own scores, computed against RS_caseG.csv, are in Eddy3D's results.json",
               "sources": {f"{folder}/belt.probe.csv": sha256(os.path.join(src, "belt.probe.csv")), f"{folder}/study/case_180/run_01_foamRun.txt": sha256(log),
                           f"{folder}/config.json": sha256(os.path.join(src, "config.json")), "aij_G/results.json": sha256(os.path.join(root, "aij_G", "results.json"))},
               "byStation": g_stations(arm_rows[arm]), "calibration.rmseU": rmse[arm], **g_scores(arm_rows[arm])}
        if arm == "half-belt-conifer":
            res["endEffect.halfBeltMinusSlab"] = end_effect
        write_json(os.path.join(RESULTS, f"{g_name(arm)}.json"), res)
    print(f"snapshot {G_STEM}: {len(pair_rows)} pairs in {len(G_ARMS)} arms")


def g_control(root, fixture):
    """Case G's published CSV scored the way the fixture scores it, with its own probes: its results.json to 1e-9."""
    rs = raw_table("case-g/RS_caseG.csv")
    for arm, folder, *_ in G_ARMS:
        probes = read_probe(os.path.join(root, folder, "belt.probe.csv"), 1.0, species=False)
        u7 = probes[G_FAR_AT + G_FAR_SEVEN]["mag"]
        rows = []
        for i, p in enumerate(probes[:G_POINTS]):
            assert abs(p["X"] - rs["X"][i]) < 1e-9 and abs(p["Z"] - rs["Z"][i]) < 1e-9
            rms = math.sqrt(p["mag"] ** 2 + 2 * p["k"])
            rows.append({"U_meas": rs["U/UH"][i], "U_model": p["mag"] / u7, "Urms_model": rms / u7, "U_model_imposed": p["mag"] / G_UH_IMPOSED,
                         "Urms_model_imposed": rms / G_UH_IMPOSED, "k_meas": rs["k/UH^2"][i], "k_model": p["k"] / u7 ** 2})
        for key, mine in g_scores(rows).items():
            want = fixture[f"{folder}.{key}"]
            assert DM.same(mine, want, fixture=True), (folder, key, mine, want)
        print(f"fixture control {g_name(arm)}: 5 scores reproduced from RS_caseG.csv and the fixture's probes")


def g_parity(fixture):
    for arm, folder, *_ in G_ARMS:
        mine = read_json(os.path.join(RESULTS, f"{g_name(arm)}.json"))
        for key in ("score.U.ownApproach", "score.rms.ownApproach", "score.k.ownApproach"):
            a, b = fixture[f"{folder}.{key}"], mine[key]
            print(f"{g_name(arm)} {key}: R {a['R']:+.4f} -> {b['R']:+.4f}  FAC2 {a['Fac2']:.4f} -> {b['Fac2']:.4f}  FB {a['Fb']:+.4f} -> {b['Fb']:+.4f}  n {a['Count']} -> {b['Count']}")
    eff = read_json(os.path.join(RESULTS, f"{g_name('half-belt-conifer')}.json"))["endEffect.halfBeltMinusSlab"]
    fx = fixture["endEffect.conifer"]
    print("endEffect half belt minus slab: " + ", ".join(f"{k} {fx[k]:+.4f} -> {eff[k]:+.4f}" for k in ("maxAbs", "meanSigned", "meanAbs", "r")))
    for arm, folder, *_ in G_ARMS:
        print(f"{g_name(arm)} RMSE(U) {fixture['calibration']['rmseByArm'][folder]:.4f} -> {read_json(os.path.join(RESULTS, f'{g_name(arm)}.json'))['calibration.rmseU']:.4f}")


# ----------------------------------------------------------------------------- snapshots, checks

root = validation_root(K_STUDY, "aij_G")
if root:
    k_fx = read_json(os.path.join(root, K_STUDY, "results.json"))
    g_fx = read_json(os.path.join(root, "aij_G", "results.json"))
    k_control(root, k_fx)
    g_control(root, g_fx)
    k_snapshot(root)
    g_snapshot(root)
    k_parity(k_fx)
    g_parity(g_fx)

k_pairs = read_pairs(os.path.join(RESULTS, f"{K_STEM}_pairs.csv"))
check_snapshot(os.path.join(RESULTS, f"{K_STEM}.json"), k_scores(k_pairs))
g_pairs = read_pairs(os.path.join(RESULTS, f"{G_STEM}_pairs.csv"))
g_by_arm = {arm: [p for p in g_pairs if p["arm"] == arm] for arm, *_ in G_ARMS}
for arm, *_ in G_ARMS:
    assert len(g_by_arm[arm]) == G_POINTS, arm
    check_snapshot(os.path.join(RESULTS, f"{g_name(arm)}.json"), g_scores(g_by_arm[arm]))
    check_snapshot(os.path.join(RESULTS, f"{g_name(arm)}.json"), {"calibration.rmseU": g_extras(g_by_arm)[0][arm]})

# ----------------------------------------------------------------------------- figure: Case K
style.apply()
k_res = read_json(os.path.join(RESULTS, f"{K_STEM}.json"))
near = column(k_pairs, "near_source") == 1
K_PANELS = [("U", "U_meas", "U_model", "velocity.U", "U/U$_H$", False), ("W", "W_meas", "W_model", "velocity.W", "W/U$_H$", False),
            ("k", "k_meas", "k_model", "k", "k/U$_H^2$", False)] + \
           [(f"c{sp}", "cstar_meas", f"cstar_{sp}", f"cstar.c_{sp}", f"c* = C/c$_0$, {lab}", True) for sp, lab in SPECIES]
fig, axs = uplt.subplots(nrows=2, ncols=3, refwidth=2.1, refaspect=1, share=False, wspace=4.2, hspace=3.4)
for i, (tag, mk, pk, key, label, log) in enumerate(K_PANELS):
    ax = axs[i // 3, i % 3]
    shown = panel(ax, column(k_pairs, mk), column(k_pairs, pk), style.OPENFOAM, log=log, xlab="Tunnel [–]" if i // 3 == 1 else None,
                  ylab="Eddy3D [–]" if i % 3 == 0 else None, hollow=near if log else None)
    ax.format(title=label)
    style.stats(ax, stats_text(k_res[key], shown if log else None), loc=(0.40, 0.36) if log else (0.05, 0.80))
style.finish(fig, "AIJ UWE Case K — Eddy3D (OpenFOAM 12, realizable k-ε) vs wind tunnel, 9 × 9 cube array with a floor source",
             handles=[style.marker(style.OPENFOAM, "Eddy3D at the measured points"), style.marker(style.OPENFOAM, "within one cube height of the source", filled=False),
                      style.line(style.REFERENCE, "1:1", lw=1.0), style.line(style.REFERENCE, "factor of two", lw=0.8, ls=":")])
style.save(fig, "case-k-openfoam-agreement.png")

# ----------------------------------------------------------------------------- figures: Case G
g_res = {arm: read_json(os.path.join(RESULTS, f"{g_name(arm)}.json")) for arm, *_ in G_ARMS}
G_LABEL = {"open-field": "no belt (control)", "pine": "pine · Cd·LAD 0.30", "conifer": "conifer · 0.625", "screen": "screen · 0.875",
           "half-belt-conifer": "half belt · 0.625"}
cmap = uplt.Colormap(style.SEQUENTIAL)
G_COLOUR = {"open-field": style.REFERENCE, "pine": cmap(0.05), "conifer": cmap(0.30), "screen": cmap(0.55), "half-belt-conifer": cmap(0.30)}
fig, axs = uplt.subplots(nrows=2, ncols=5, refwidth=1.6, refaspect=1, share=False, wspace=4.0, hspace=3.4)
for col, (arm, *_r) in enumerate(G_ARMS):
    rows = g_by_arm[arm]
    for row, (mk, pk, key, lim) in enumerate([("U_meas", "U_model", "score.U.ownApproach", (0.0, 1.1)), ("k_meas", "k_model", "score.k.ownApproach", (0.0, 0.09))]):
        ax = axs[row, col]
        o, p = column(rows, mk), column(rows, pk)
        style.one_to_one(ax, *lim)
        ax.scatter(o, p, s=14, color=style.OPENFOAM if arm != "open-field" else style.REFERENCE, edgecolor=style.SURFACE, linewidth=0.25, alpha=0.9, zorder=3)
        ax.format(xlim=lim, ylim=lim, xlabel="Field [–]" if row == 1 else None, ylabel=("|U|/U(7 m) [–]" if row == 0 else "k/U(7 m)$^2$ [–]") if col == 0 else None,
                  title=G_LABEL[arm] if row == 0 else None)
        style.stats(ax, stats_text(g_res[arm][key]), loc=(0.05, 0.95) if row == 0 else (0.05, 0.95))
style.finish(fig, "AIJ UWE Case G — Eddy3D (OpenFOAM 12, realizable k-ε) vs field, drag sweep behind a black-pine belt",
             handles=[style.marker(style.OPENFOAM, "Eddy3D at the 28 measured points"), style.marker(style.REFERENCE, "no belt (control)"),
                      style.line(style.REFERENCE, "1:1", lw=1.0), style.line(style.REFERENCE, "factor of two", lw=0.8, ls=":")])
style.save(fig, "case-g-openfoam-sweep.png")

fig, axs = uplt.subplots(nrows=1, ncols=2, refwidth=3.0, refaspect=1.2, share=False, wspace=5.0)
stations = g_res["conifer"]["byStation"]
xs = [s["xOverH"] for s in stations]
for ax, (mkey, okey, ylab) in zip(axs, [("modelU", "observedU", "mean U/U$_H$ over the four heights [–]"), ("modelK", "observedK", "mean k/U$_H^2$ over the four heights [–]")]):
    for arm, *_r in G_ARMS:
        st = g_res[arm]["byStation"]
        ax.plot(xs, [s[mkey] for s in st], color=G_COLOUR[arm], lw=1.8, ls="--" if arm == "half-belt-conifer" else "-")
    ax.plot(xs, [s[okey] for s in stations], color=style.MEASURED, lw=0, marker="o", ms=6, mec=style.SURFACE, mew=0.4, zorder=5)
    ax.format(xlabel="distance behind the leeward face x/H [–]", ylabel=ylab, xlim=(0, 5.3), ylim=(0, None))
style.finish(fig, "AIJ UWE Case G — mean speed and mean k by station behind the belt, field and Eddy3D's drag sweep",
             handles=[style.marker(style.MEASURED, "field")] + [style.line(G_COLOUR[a], G_LABEL[a], ls="--" if a == "half-belt-conifer" else "-") for a, *_r in G_ARMS], ncols=3)
style.save(fig, "case-g-openfoam-stations.png")
