"""Validation figures for AIJ UWE Cases J (1:1:2 building, heated floor, floor tracer source) and L (9 x 14 cube array, heated floor, line source)
solved with Eddy3D on its buoyant microclimate engine, urbanMicroclimateFoam (UMF, an OpenFOAM 12 solver; the Outdoor+ plugin).

Three figures, each answering one question:

  case-j-umf-agreement.png   Does the model agree with the tunnel?  Case J under UMF's two closures (realizable k-epsilon, buoyantKEpsilon): measured
                      against modelled U, W, k and the floor-referenced temperature theta, with the 1:1 line and the factor-of-two band.
  case-j-umf-tracer.png      The tracer, one column per turbulent Schmidt number (0.3, 0.5, 0.7), one row per closure; the 27 points within a quarter of a
                      building height of the source are drawn open.
  case-l-umf-agreement.png   Case L (realizable k-epsilon): U, V, W, k, theta, and c* at the three Schmidt numbers.

Inputs, all in this repository: the cleaned measurement tables clean/cases/{J,L}/points.csv, and the per-point pairs
validation/results/case{J,L}_umf_*_pairs.csv built from them and from the probes the Eddy3D fixtures TestAijCaseJUmfContainerE2E and
TestAijCaseLUmfContainerE2E left in their solved cases (validation/results/*_probes.csv hold the last row of each probe file of
postProcessing/air/rsPoints, and Case L's approach column; the SHA-256 of every file they were read from is in each results file's `sources`).
They are refreshed from ~/Eddy3DVal/aij_J_umf and aij_L_umf when that folder exists (EDDY3D_VAL names another). The scores in
validation/results/case{J,L}_umf_*.json are computed FROM THE PAIRS by validation/dispersion_metrics.py; this script recomputes them on every
run and fails if a file disagrees. When the Eddy3D results are present it also scores the published CSVs the way the fixtures do, with the
fixtures' own probes, and requires their numbers to 1e-9, and prints the recomputed scores next to the fixtures' (the measured side differs: the
cleaned workbooks against the rounded CSVs).

Both scenes are the tunnel at a Froude scale (J 62.5, L 100): lengths times the scale, velocities times its square root, temperatures unchanged,
so the Richardson number, Pr and the tunnel's Kelvin values are kept and Re is not. Every pair is in the tunnel's units and frame (x streamwise,
V positive toward +y: the scene's own frame): coordinates divided by the scale, velocities by the scene's U_H, k by its square, the temperature
as the floor-referenced fraction theta = (T_f - T)/(T_f - T_H) (0 at the floor, 1 in the approach air at the building height; the workbook's own
normalisation), c* = C/c0 for the measurement against the model's tracer mass fraction turned into ppm of ethylene and divided by the same c0.

Colours follow plotstyle.py, except that the points of the agreement figures take the colour of the line or plane of the tunnel they were measured on
(layout.py; the same letters and colours as case-j-layout.png and case-l-layout.png).
"""
from __future__ import annotations

import math
import os
import re

import numpy as np
import ultraplot as uplt

import dispersion_metrics as DM
import layout
import plotstyle as style
from snapshot_common import (RESULTS, SPECIES, check_snapshot, clean_table, column, fnum, mirror_mean, panel, raw_table, read_json, read_pairs, sha256, stats_text,
                             validation_root, write_json, write_lf, write_pairs)

MW_AIR, MW_ETHYLENE = 28.96, 28.054
SPECIES_FILES = ["tracerSct03", "tracerSct05", "tracerSct07"]          # the fixtures' species names, in SPECIES order
PROBE_FIELDS = ["U", "T", "k"] + SPECIES_FILES


def ppm(mass_fraction):
    """The tracer's mass fraction as ppm of ethylene by volume (AijCaseJScene.ModelPpm)."""
    moles = mass_fraction / MW_ETHYLENE
    return 1e6 * moles / (moles + (1 - mass_fraction) / MW_AIR)


def theta_score(o, p):
    """The floor-referenced temperature fraction: positive, D = 0.25 and W = 0.05 (AijCaseL.Score, the fixture's 'floorDeficit')."""
    return DM.evaluate(o, p, DM.D_HIT, DM.W_VELOCITY)


def basic(o, p):
    """Mean bias, mean absolute and root-mean-square error and R of a quantity that is neither a velocity nor a concentration (AijCaseJStatistics.Basic)."""
    o, p = np.asarray(o, float), np.asarray(p, float)
    ok = np.isfinite(o) & np.isfinite(p)
    o, p = o[ok], p[ok]
    return {"Count": int(len(o)), "MeanObserved": float(o.mean()), "MeanPredicted": float(p.mean()), "Mbe": float((p - o).mean()), "Mae": float(np.abs(p - o).mean()),
            "Rmse": float(np.sqrt(((p - o) ** 2).mean())), "R": float(np.corrcoef(o, p)[0, 1]) if len(o) > 1 else None}


def read_umf_probe(case_dir, name, field):
    """The last row of postProcessing/air/<name>/<latest time>/<field>: the probes' coordinates, their values (n x 3 for a vector, n x 1) and the row's time."""
    base = os.path.join(case_dir, "postProcessing", "air", name)
    times = sorted((d for d in os.listdir(base) if os.path.isfile(os.path.join(base, d, field))), key=float)
    path = os.path.join(base, times[-1], field)
    coords, last = [], None
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("# Probe "):
                coords.append([float(v) for v in line[line.index("(") + 1:line.index(")")].split()])
            elif line.strip() and not line.lstrip().startswith("#"):
                last = line
    if "(" in last:
        values = [[float(v) for v in part[:part.index(")")].split()] for part in last.split("(")[1:]]
    else:
        values = [[float(v)] for v in last.split()[1:]]
    assert len(values) == len(coords), (path, len(values), len(coords))
    return np.array(coords), np.array(values), last.split()[0], path


def read_probe_table(probe_dir_case, name, fields=PROBE_FIELDS):
    """Every field of one probe object at once: coordinates (scene), U (n x 3), T, k, the three species (mass fractions), the row time, the source files."""
    out, sources, times = {}, {}, set()
    for field in fields:
        coords, values, t, path = read_umf_probe(probe_dir_case, name, field)
        out[field] = values
        out["coords"] = coords if "coords" not in out else out["coords"]
        assert np.allclose(coords, out["coords"])
        sources[field] = path
        times.add(t)
    assert len(times) == 1, times
    return out, times.pop(), sources


def write_probe_csv(path, table):
    species = [s for s in SPECIES_FILES if s in table]
    cols = ["x", "y", "z", "U_x", "U_y", "U_z", "T", "k"] + species
    lines = [",".join(cols)]
    for i in range(len(table["coords"])):
        vals = [*table["coords"][i], *table["U"][i], table["T"][i][0], table["k"][i][0], *(table[s][i][0] for s in species)]
        lines.append(",".join(repr(float(v)) for v in vals))
    write_lf(path, "\n".join(lines) + "\n")


def read_probe_csv(path):
    rows = read_pairs(path)
    return {"coords": np.array([[r["x"], r["y"], r["z"]] for r in rows]), "U": np.array([[r["U_x"], r["U_y"], r["U_z"]] for r in rows]),
            "T": np.array([[r["T"]] for r in rows]), "k": np.array([[r["k"]] for r in rows]), **{s: np.array([[r[s]] for r in rows]) for s in SPECIES_FILES if s in rows[0]}}


def umf_final_residuals(log):
    """The initial residuals of the last inner iteration of the air region in a UMF solver log."""
    with open(log, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    block = text.rsplit("Internal iteration number:", 1)[-1].split("air region solution ended")[0]
    return {m.group(1): float(m.group(2)) for m in re.finditer(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)", block)}, \
        int(re.search(r"air region solution ended in (\d+) iterations", text).group(1))


def sources_of(root, case_dir, table_sources, extra):
    names = {**{os.path.relpath(p, root).replace(os.sep, "/"): sha256(p) for p in table_sources.values()},
             **{os.path.relpath(p, root).replace(os.sep, "/"): sha256(p) for p in extra}}
    return dict(sorted(names.items()))


def run_scores(rows, quantities, subsets, extra_controls):
    """Every score of a run from its pairs: each quantity over all points and over each subset; `extra_controls(rows)` adds the controls."""
    out = {}
    for sname, mask in [("", np.ones(len(rows), bool))] + [(f"{n}.", m(rows)) for n, m in subsets]:
        if mask.sum() < 3:
            continue
        for q, mk, pk, fn in quantities:
            out[f"{sname}{q}"] = fn(column(rows, mk)[mask], column(rows, pk)[mask])
    out.update(extra_controls(rows))
    return out


# ----------------------------------------------------------------------------- Case J

J_ROOT = "aij_J_umf"
J_PROBE = "rsPoints"                                                     # the probe objects the fixtures added (AijCaseJScene.RsProbe, AijCaseLScene.MeasuredProbe)
J_CLOSURES = [("realizableKE", "aijJ_umf_realizableKE"), ("buoyantKEpsilon", "aijJ_umf_buoyantKEpsilon")]
J_SCALE, J_UH_T, J_H, J_B, J_SRC_X = 62.5, 1.4581, 0.16, 0.08, 0.04
J_UH_M = J_UH_T * math.sqrt(J_SCALE)
J_C0 = 0.05 * 9.17e-6 / (J_UH_T * J_H ** 2) * 1e6                       # 12.283 ppm: the ethylene share (5 %) of q over U_H H^2
J_TF_K, J_TH_K, KELVIN = 318.95, 285.32, 273.15
J_DT = J_TF_K - J_TH_K                                                   # 33.63 K: floor minus the approach air at the building height
J_PAIR_FIELDS = ["point_id", "x", "y", "z", "region", "near_source", "U_meas", "V_meas", "W_meas", "U_model", "V_model", "W_model", "k_meas", "k_model", "T_meas_degC",
                 "T_model_degC", "theta_meas", "theta_model", "cstar_meas", "cstar_sct03", "cstar_sct05", "cstar_sct07"]
J_REGIONS = {"aboveRoof": lambda x, z: z > J_H + 1e-9, "upstream": lambda x, z: z <= J_H + 1e-9 and x < -J_B - 1e-9,
             "beside": lambda x, z: z <= J_H + 1e-9 and -J_B - 1e-9 <= x <= 1e-9, "nearWake": lambda x, z: z <= J_H + 1e-9 and 1e-9 < x <= J_H + 1e-9,
             "farWake": lambda x, z: z <= J_H + 1e-9 and x > J_H + 1e-9}
J_QUANTITY = ("U, V, W over U_H = 1.4581 m/s and k over U_H^2 (the tunnel's units, 443 distinct points); theta = (T_f - T)/(T_f - T_H) with T_f = 318.95 K and "
              "T_H = 285.32 K; c* = C/c0 (c0 = 12.28 ppm) against the model's ethylene mass fraction as ppm over the same c0, for turbulent Schmidt numbers 0.3, 0.5 and 0.7; "
              "the 27 points within a quarter of a building height of the source are scored with and without. The scene is the tunnel at Froude scale 62.5")


def j_key(x, y, z):
    return (round(x, 6), round(y, 6), round(z, 6))


def j_region(x, z):
    return next(n for n, f in J_REGIONS.items() if f(x, z))


def j_near(x, y, z):
    return math.sqrt((x - J_SRC_X) ** 2 + y * y) <= 0.25 * J_H and z <= 0.25 * J_H + 1e-9


def j_rows(measured, probe):
    """The pairs of Case J: the cleaned table's rows (point 153 repeats point 1 and is left out, as in the fixture) against the probes at the same points."""
    index = {j_key(*(c / J_SCALE)): i for i, c in enumerate(probe["coords"])}
    rows, seen = [], set()
    for m in measured:
        x, y, z = float(m["x"]), float(m["y"]), float(m["z"])
        if j_key(x, y, z) in seen:
            continue
        seen.add(j_key(x, y, z))
        i = index[j_key(x, y, z)]
        t_c = probe["T"][i][0] - KELVIN
        r = {"point_id": int(m["point_id"]), "x": x, "y": y, "z": z, "region": j_region(x, z), "near_source": int(j_near(x, y, z))}
        for q, c in zip("UVW", range(3)):
            r[f"{q}_meas"], r[f"{q}_model"] = fnum(m[q]) / J_UH_T, probe["U"][i][c] / J_UH_M
        r["k_meas"], r["k_model"] = fnum(m["k"]) / J_UH_T ** 2, probe["k"][i][0] / J_UH_M ** 2
        r["T_meas_degC"], r["T_model_degC"] = fnum(m["T"]), t_c
        r["theta_meas"], r["theta_model"] = (J_TF_K - KELVIN - fnum(m["T"])) / J_DT, (J_TF_K - KELVIN - t_c) / J_DT
        r["cstar_meas"] = fnum(m["concentration_ratio"])
        for (sp, _), name in zip(SPECIES, SPECIES_FILES):
            r[f"cstar_{sp}"] = ppm(probe[name][i][0]) / J_C0
        rows.append(r)
    assert len(rows) == len(probe["coords"]) == 443 and len(seen) == 443
    return rows


def species_quantities():
    return [(f"cstar.c_{sp}", "cstar_meas", f"cstar_{sp}", DM.concentration) for sp, _ in SPECIES]


J_QUANTITIES = [("velocity.U", "U_meas", "U_model", DM.velocity), ("velocity.V", "V_meas", "V_model", DM.velocity), ("velocity.W", "W_meas", "W_model", DM.velocity),
                ("k", "k_meas", "k_model", DM.turbulence), ("theta", "theta_meas", "theta_model", theta_score)] + species_quantities()
J_SUBSETS = [("farFromSource", lambda rows: column(rows, "near_source") == 0), ("plane.z0.025H", lambda rows: np.abs(column(rows, "z") - 0.004) < 1e-9),
             ("plane.z0.25H", lambda rows: np.abs(column(rows, "z") - 0.04) < 1e-9), ("plane.centre", lambda rows: np.abs(column(rows, "y")) < 1e-9)] + \
            [(f"region.{n}", (lambda rows, n=n: np.array([r["region"] == n for r in rows]))) for n in J_REGIONS]


def j_controls(rows):
    pts = np.c_[column(rows, "x"), column(rows, "y"), column(rows, "z")]
    return {"velocity.U.symmetryCeiling": DM.velocity(column(rows, "U_meas"), mirror_mean(pts, column(rows, "U_meas"))),
            "temperature.all": basic(column(rows, "T_meas_degC"), column(rows, "T_model_degC"))}


def j_scores(rows):
    out = run_scores(rows, J_QUANTITIES, J_SUBSETS, j_controls)
    for name, m in J_SUBSETS:
        if m(rows).sum() >= 3:
            out[f"temperature.{name}"] = basic(column(rows, "T_meas_degC")[m(rows)], column(rows, "T_model_degC")[m(rows)])
    cm = column(rows, "cstar_meas")
    out["cstar.peakMeasured"] = float(np.nanmax(cm))
    for sp, _ in SPECIES:
        out[f"cstar.c_{sp}.peakAtReferencePoints"] = float(np.nanmax(column(rows, f"cstar_{sp}")))
    return out


def j_name(closure):
    return f"caseJ_umf_{closure}"


J_KEEP = ("engine", "turbulenceModel", "sceneVersion", "froudeScale", "sceneH", "sceneUh", "bulkRichardson", "tracer", "airIterations", "airIterationCap", "measuredPoints",
          "airCells", "wake.LrOverH.z0.25H", "wake.LrOverH.z0.25H.truncated", "wake.LrOverH.z0.025H", "wake.LrOverH.z0.025H.truncated", "wake.measuredLrOverH.z0.25H",
          "wake.measuredLrOverH.z0.25H.truncated", "wake.measuredLrOverH.z0.025H", "wake.measuredLrOverH.z0.025H.truncated", "approach.T.firstCell", "approach.T.atH",
          "approach.T.top", "approach.firstCellInletMeanT")


def j_snapshot(root):
    measured = clean_table("J")
    for closure, folder in J_CLOSURES:
        case_dir = os.path.join(root, J_ROOT, folder)
        table, row_time, files = read_probe_table(case_dir, J_PROBE)
        write_probe_csv(os.path.join(RESULTS, f"{j_name(closure)}_probes.csv"), table)
        rows = j_rows(measured, read_probe_csv(os.path.join(RESULTS, f"{j_name(closure)}_probes.csv")))
        write_pairs(os.path.join(RESULTS, f"{j_name(closure)}_pairs.csv"), J_PAIR_FIELDS, rows)
        fx = read_json(os.path.join(case_dir, "results.json"))
        log = os.path.join(case_dir, "23_urbanMicroClimateFoamLog.txt")
        residuals, iterations = umf_final_residuals(log)
        res = {"case": "AIJ UWE Case J (112CT) - 1:1:2 building on a heated floor, floor tracer source, unstable", "turbulenceModel": closure,
               **{k: fx[k] for k in J_KEEP if k in fx}, **{k: v for k, v in fx.items() if k.startswith("tracer.")},
               "quantity": J_QUANTITY, "iterations": iterations, "scale": J_SCALE, "UhTunnel": J_UH_T, "UhModel": J_UH_M, "c0Ppm": J_C0,
               "solveLog": {"iterationsRun": iterations, "stoppedBy": "the iteration cap (maxFluidIteration 1500): the log has no 'solution converged' line",
                            "finalInitialResiduals": residuals},
               "pairs": f"{j_name(closure)}_pairs.csv", "probes": f"{j_name(closure)}_probes.csv", "probeRowTime": row_time,
               "scoresFrom": "the pairs file (validation/dispersion_metrics.py); the fixture's own scores, computed against RS_caseJ.csv, are in Eddy3D's results.json",
               "sources": sources_of(root, case_dir, files, [os.path.join(case_dir, "results.json"), log]), **j_scores(rows)}
        write_json(os.path.join(RESULTS, f"{j_name(closure)}.json"), res)
        print(f"snapshot {j_name(closure)}: {len(rows)} pairs")


def j_control(root):
    """Case J's published CSV scored the way the fixture scores it, with its own probes: its results.json to 1e-9."""
    rs = raw_table("case-j/RS_caseJ.csv")
    for closure, folder in J_CLOSURES:
        fx = read_json(os.path.join(root, J_ROOT, folder, "results.json"))
        table, _, _ = read_probe_table(os.path.join(root, J_ROOT, folder), J_PROBE)
        index = {j_key(*(c / J_SCALE)): i for i, c in enumerate(table["coords"])}
        rows, seen = [], set()
        for n in range(len(rs["x"])):
            x, y, z = rs["x"][n], rs["y"][n], rs["z"][n]
            if j_key(x, y, z) in seen:
                continue
            seen.add(j_key(x, y, z))
            i = index[j_key(x, y, z)]
            r = {"x": x, "y": y, "z": z, "region": j_region(x, z), "near_source": int(j_near(x, y, z))}
            for q, c in zip("UVW", range(3)):
                r[f"{q}_meas"], r[f"{q}_model"] = rs[q][n] / J_UH_T, table["U"][i][c] / J_UH_M
            r["k_meas"], r["k_model"] = rs["k"][n] / J_UH_T ** 2, table["k"][i][0] / J_UH_M ** 2
            r["T_meas_degC"], r["T_model_degC"] = rs["T"][n], table["T"][i][0]               # kelvin on both sides: only the errors are compared
            r["theta_meas"] = r["theta_model"] = 0.0
            r["cstar_meas"] = rs["C"][n] / J_C0
            for (sp, _), name in zip(SPECIES, SPECIES_FILES):
                r[f"cstar_{sp}"] = ppm(table[name][i][0]) / J_C0
            rows.append(r)
        got, checked = j_scores(rows), 0
        for subset in ["all"] + [n for n, _ in J_SUBSETS]:
            pre = "" if subset == "all" else subset + "."
            for q, fq in (("velocity.U", "U"), ("velocity.V", "V"), ("velocity.W", "W"), ("k", "k"), *[(f"cstar.c_{sp}", f"cstar.{SPECIES_FILES[i]}") for i, (sp, _) in enumerate(SPECIES)]):
                if pre + q not in got:
                    continue
                want = fx.get(f"{fq}.{subset}")
                if want is None:
                    continue
                assert DM.same(got[pre + q], want, fixture=True), (closure, subset, q, got[pre + q], want)
                checked += 1
            want = fx.get(f"T.{subset}")
            if want is not None:
                for m in ("Count", "Mbe", "Mae", "Rmse", "R"):
                    assert abs(got["temperature." + subset if subset != "all" else "temperature.all"][m] - want[m]) <= 1e-9 * max(1.0, abs(want[m])), (closure, subset, m)
                checked += 1
        print(f"fixture control {j_name(closure)}: {checked} scores reproduced from RS_caseJ.csv and the fixture's probes")


def j_parity(root):
    for closure, folder in J_CLOSURES:
        fx = read_json(os.path.join(root, J_ROOT, folder, "results.json"))
        mine = read_json(os.path.join(RESULTS, f"{j_name(closure)}.json"))
        for key, fkey in (("velocity.U", "U.all"), ("velocity.V", "V.all"), ("velocity.W", "W.all"), ("k", "k.all"), ("cstar.c_sct03", "cstar.tracerSct03.all"),
                          ("cstar.c_sct05", "cstar.tracerSct05.all"), ("cstar.c_sct07", "cstar.tracerSct07.all")):
            a, b = fx[fkey], mine[key]
            fb = "n/a" if b["Fb"] is None else format(b["Fb"], "+.4f")
            print(f"{j_name(closure)} {key}: R {a['R']:+.4f} -> {b['R']:+.4f}  FAC2 {a['Fac2']:.4f} -> {b['Fac2']:.4f}  FB {a['Fb']:+.4f} -> {fb}  n {a['Count']} -> {b['Count']}")
        a, b = fx["T.all"], mine["temperature.all"]
        print(f"{j_name(closure)} temperature: MBE {a['Mbe']:+.4f} -> {b['Mbe']:+.4f}  MAE {a['Mae']:.4f} -> {b['Mae']:.4f}  RMSE {a['Rmse']:.4f} -> {b['Rmse']:.4f}  R {a['R']:+.4f} -> {b['R']:+.4f}")


# ----------------------------------------------------------------------------- Case L

L_STUDY = "aij_L_umf/aijL_umf_cell3"
L_STEM = "caseL_umf_realizableKE"
L_PROBE = "caseL"
L_APPROACH_FIELDS = ["U", "T", "k"]
L_SCALE, L_UH_T, L_H = 100.0, 1.339415, 0.06
L_UH_M = L_UH_T * math.sqrt(L_SCALE)
L_C0 = 1728.228230096583                                                  # the workbook's c0 = 1e6 q/(U_H H^2), ppm
L_FLOOR_C, L_DT = 45.009118949967807, 30.256731727745589                  # floor temperature [degC], floor minus the approach air at the cube height [K]
# the measured points' (x, y) by region, AijCaseL.RoadLocations / BlockLocations / SurroundLocations (heights follow from the table)
L_ROAD = {(-0.21, 0.06), (-0.15, -0.06), (-0.15, -0.03), (-0.15, 0.0), (-0.15, 0.03), (-0.15, 0.06), (-0.12, -0.06), (-0.12, 0.06), (-0.09, -0.06), (-0.09, 0.06), (-0.06, -0.06),
          (-0.06, 0.06), (-0.03, -0.06), (-0.03, -0.03), (-0.03, 0.0), (-0.03, 0.03), (-0.03, 0.06), (0.03, 0.06), (0.09, 0.0), (0.09, 0.06), (0.15, 0.06), (0.21, 0.0),
          (0.21, 0.06), (0.27, 0.06), (0.33, 0.0), (0.33, 0.06), (0.39, 0.06)}
L_BLOCK = {(-0.21, 0.0), (-0.12, -0.03), (-0.12, 0.0), (-0.12, 0.03), (-0.09, -0.03), (-0.09, 0.0), (-0.09, 0.03), (-0.06, -0.03), (-0.06, 0.0), (-0.06, 0.03), (0.03, 0.0),
           (0.15, 0.0), (0.27, 0.0), (0.39, 0.0)}
L_PAIR_FIELDS = ["point_id", "x", "y", "z", "region", "U_meas", "V_meas", "W_meas", "S_meas", "U_model", "V_model", "W_model", "S_model", "k_meas", "k_model", "T_meas_degC",
                 "T_model_degC", "theta_meas", "theta_model", "cstar_meas", "cstar_sct03", "cstar_sct05", "cstar_sct07", "U_approach", "theta_approach"]
L_QUANTITY = ("U, V, W, the speed |U| over U_H = 1.3394 m/s and k over U_H^2 (the tunnel's units, 344 points); theta = (T_f - T)/(T_f - T_H) with T_f = 45.01 degC and "
              "T_f - T_H = 30.26 K; c* = C/c0 (c0 = 1728 ppm) against the model's ethylene mass fraction as ppm over the same c0, for turbulent Schmidt numbers 0.3, 0.5 and 0.7; "
              "also the 242 points at or above 30 mm, the first four fine cells above the floor. The scene is the tunnel at Froude scale 100")
L_SUBSETS = [("comparable", lambda rows: column(rows, "z") >= 0.03 - 1e-9)] + [(f"region.{n}", (lambda rows, n=n: np.array([r["region"] == n for r in rows])))
                                                                                  for n in ("road", "block", "surround")]
L_QUANTITIES = [("velocity.U", "U_meas", "U_model", DM.velocity), ("velocity.V", "V_meas", "V_model", DM.velocity), ("velocity.W", "W_meas", "W_model", DM.velocity),
                ("speed", "S_meas", "S_model", DM.velocity), ("k", "k_meas", "k_model", DM.turbulence), ("theta", "theta_meas", "theta_model", theta_score)] + species_quantities()


def l_key(x, y, z):
    return (round(x * 1000), round(y * 1000), round(z * 10000))


def l_region(x, y):
    return "road" if (round(x, 6), round(y, 6)) in L_ROAD else "block" if (round(x, 6), round(y, 6)) in L_BLOCK else "surround"


def l_rows(measured, probe, approach):
    """The pairs of Case L: the cleaned table's 344 rows against the probes at the same points, and the model's undisturbed approach column at each height."""
    index = {l_key(*(c / L_SCALE)): i for i, c in enumerate(probe["coords"])}
    z_app = approach["coords"][:, 2] / L_SCALE
    u_app = approach["U"][:, 0] / L_UH_M
    th_app = (L_FLOOR_C - (approach["T"][:, 0] - KELVIN)) / L_DT
    rows = []
    for m in measured:
        x, y, z = float(m["x"]), float(m["y"]), float(m["z"])
        i = index[l_key(x, y, z)]
        t_c = probe["T"][i][0] - KELVIN
        r = {"point_id": int(m["point_id"]), "x": x, "y": y, "z": z, "region": l_region(x, y)}
        for q, c in zip("UVW", range(3)):
            r[f"{q}_meas"], r[f"{q}_model"] = fnum(m[q]) / L_UH_T, probe["U"][i][c] / L_UH_M
        r["S_meas"] = math.sqrt(sum(fnum(m[q]) ** 2 for q in "UVW")) / L_UH_T
        r["S_model"] = float(np.sqrt((probe["U"][i] ** 2).sum())) / L_UH_M
        r["k_meas"], r["k_model"] = fnum(m["k"]) / L_UH_T ** 2, probe["k"][i][0] / L_UH_M ** 2
        r["T_meas_degC"], r["T_model_degC"] = fnum(m["T"]), t_c
        r["theta_meas"], r["theta_model"] = (L_FLOOR_C - fnum(m["T"])) / L_DT, (L_FLOOR_C - t_c) / L_DT
        r["cstar_meas"] = fnum(m["concentration_ratio"])
        for (sp, _), name in zip(SPECIES, SPECIES_FILES):
            r[f"cstar_{sp}"] = ppm(probe[name][i][0]) / L_C0
        r["U_approach"], r["theta_approach"] = float(np.interp(z, z_app, u_app)), float(np.interp(z, z_app, th_app))
        rows.append(r)
    assert len(rows) == len(probe["coords"]) == 344
    return rows


def l_controls(rows):
    pts = np.c_[column(rows, "x"), column(rows, "y"), column(rows, "z")]
    return {"control.V.flippedSign": DM.velocity(column(rows, "V_meas"), -column(rows, "V_model")),
            "control.U.approachOnly": DM.velocity(column(rows, "U_meas"), column(rows, "U_approach")),
            "control.theta.approachOnly": theta_score(column(rows, "theta_meas"), column(rows, "theta_approach")),
            "velocity.U.symmetryCeiling": DM.velocity(column(rows, "U_meas"), mirror_mean(pts, column(rows, "U_meas"))),
            "temperature.all": basic(column(rows, "T_meas_degC"), column(rows, "T_model_degC"))}


def l_scores(rows):
    out = run_scores(rows, L_QUANTITIES, L_SUBSETS, l_controls)
    out["cstar.peakMeasured"] = float(np.nanmax(column(rows, "cstar_meas")))
    for sp, _ in SPECIES:
        out[f"cstar.c_{sp}.peakAtReferencePoints"] = float(np.nanmax(column(rows, f"cstar_{sp}")))
    return out


L_KEEP = ("engine", "closure", "scene", "conditions", "mesh", "solveSeconds", "tracerBalance.outflowOverEmission", "road.model", "firstCellPoints", "mirror",
          "approach.maxRelUDifferenceAbove30mm", "approach.maxFloorDeficitDifferenceAbove30mm", "cstar.tracerSct03.peak", "cstar.tracerSct05.peak", "cstar.tracerSct07.peak")


def l_snapshot(root):
    case_dir = os.path.join(root, L_STUDY)
    table, row_time, files = read_probe_table(case_dir, L_PROBE)
    approach, _, afiles = read_probe_table(case_dir, "approach", L_APPROACH_FIELDS)
    write_probe_csv(os.path.join(RESULTS, f"{L_STEM}_probes.csv"), table)
    write_probe_csv(os.path.join(RESULTS, f"{L_STEM}_approach.csv"), approach)
    rows = l_rows(clean_table("L"), read_probe_csv(os.path.join(RESULTS, f"{L_STEM}_probes.csv")), read_probe_csv(os.path.join(RESULTS, f"{L_STEM}_approach.csv")))
    write_pairs(os.path.join(RESULTS, f"{L_STEM}_pairs.csv"), L_PAIR_FIELDS, rows)
    fx = read_json(os.path.join(root, "aij_L_umf", "results.json"))
    log = os.path.join(case_dir, "23_urbanMicroClimateFoamLog.txt")
    residuals, iterations = umf_final_residuals(log)
    res = {"case": "AIJ UWE Case L (ArraysCT) - 9 x 14 cube array on a heated floor, floor line source, unstable", "turbulenceModel": "realizableKE",
           **{k: fx[k] for k in L_KEEP if k in fx}, "quantity": L_QUANTITY, "iterations": iterations, "scale": L_SCALE, "UhTunnel": L_UH_T, "UhModel": L_UH_M, "c0Ppm": L_C0,
           "solveLog": {"iterationsRun": iterations, "stoppedBy": "the iteration cap (maxFluidIteration 1500): the log has no 'solution converged' line",
                        "finalInitialResiduals": residuals},
           "pairs": f"{L_STEM}_pairs.csv", "probes": f"{L_STEM}_probes.csv", "approachColumn": f"{L_STEM}_approach.csv", "probeRowTime": row_time,
           "scoresFrom": "the pairs file (validation/dispersion_metrics.py); the fixture's own scores, computed against RS_caseL.csv, are in Eddy3D's results.json",
           "sources": sources_of(root, case_dir, {**files, **{"a" + k: v for k, v in afiles.items()}}, [os.path.join(root, "aij_L_umf", "results.json"), log]), **l_scores(rows)}
    write_json(os.path.join(RESULTS, f"{L_STEM}.json"), res)
    print(f"snapshot {L_STEM}: {len(rows)} pairs")


def l_control(root):
    """Case L's published CSV scored the way the fixture scores it, with its own probes: its results.json to 1e-9."""
    rs = raw_table("case-l/RS_caseL.csv")
    fx = read_json(os.path.join(root, "aij_L_umf", "results.json"))
    case_dir = os.path.join(root, L_STUDY)
    table, _, _ = read_probe_table(case_dir, L_PROBE)
    approach, _, _ = read_probe_table(case_dir, "approach", L_APPROACH_FIELDS)
    index = {l_key(*(c / L_SCALE)): i for i, c in enumerate(table["coords"])}
    measured = []
    for n in range(len(rs["x"])):
        assert l_key(rs["x"][n], rs["y"][n], rs["z"][n]) in index
        measured.append({"point_id": n + 1, **{k: float(rs[k][n]) for k in ("x", "y", "z", "U", "V", "W", "k", "T")}, "concentration_ratio": float(rs["C"][n] / L_C0)})
    got = l_scores(l_rows(measured, table, approach))
    checked = 0
    for subset in ["all"] + [n for n, _ in L_SUBSETS]:
        pre = "" if subset == "all" else subset + "."
        for q, fq in (("velocity.U", "U"), ("velocity.V", "V"), ("velocity.W", "W"), ("speed", "speed"), ("k", "k"), ("theta", "floorDeficit"),
                      *[(f"cstar.c_{sp}", f"cstar.{SPECIES_FILES[i]}") for i, (sp, _) in enumerate(SPECIES)]):
            want = fx.get(f"{fq}.{subset.replace('region.', '')}")
            if want is not None and pre + q in got:
                assert DM.same(got[pre + q], want, fixture=True), (subset, q, got[pre + q], want)
                checked += 1
    for q, fq in (("control.V.flippedSign", "control.V.flippedSign.all"), ("control.U.approachOnly", "control.U.approachOnly.all"),
                  ("control.theta.approachOnly", "control.floorDeficit.approachOnly.all")):
        assert DM.same(got[q], fx[fq], fixture=True), (q, got[q], fx[fq])
        checked += 1
    print(f"fixture control {L_STEM}: {checked} scores reproduced from RS_caseL.csv and the fixture's probes")


def l_parity(root):
    fx = read_json(os.path.join(root, "aij_L_umf", "results.json"))
    mine = read_json(os.path.join(RESULTS, f"{L_STEM}.json"))
    for key, fkey in (("velocity.U", "U.all"), ("velocity.V", "V.all"), ("velocity.W", "W.all"), ("speed", "speed.all"), ("k", "k.all"), ("theta", "floorDeficit.all"),
                      ("cstar.c_sct03", "cstar.tracerSct03.all"), ("cstar.c_sct05", "cstar.tracerSct05.all"), ("cstar.c_sct07", "cstar.tracerSct07.all"),
                      ("comparable.velocity.U", "U.comparable"), ("comparable.cstar.c_sct05", "cstar.tracerSct05.comparable")):
        a, b = fx[fkey], mine[key]
        fb = "n/a" if b["Fb"] is None else format(b["Fb"], "+.4f")
        print(f"{L_STEM} {key}: R {a['R']:+.4f} -> {b['R']:+.4f}  FAC2 {a['Fac2']:.4f} -> {b['Fac2']:.4f}  FB {a['Fb']:+.4f} -> {fb}  n {a['Count']} -> {b['Count']}")


# ----------------------------------------------------------------------------- snapshots, checks

root = validation_root(J_ROOT, "aij_L_umf")
if root:
    j_control(root)
    l_control(root)
    j_snapshot(root)
    l_snapshot(root)
    j_parity(root)
    l_parity(root)

j_pairs = {c: read_pairs(os.path.join(RESULTS, f"{j_name(c)}_pairs.csv")) for c, _ in J_CLOSURES}
for c, _ in J_CLOSURES:
    check_snapshot(os.path.join(RESULTS, f"{j_name(c)}.json"), {k: v for k, v in j_scores(j_pairs[c]).items()})
l_pairs = read_pairs(os.path.join(RESULTS, f"{L_STEM}_pairs.csv"))
check_snapshot(os.path.join(RESULTS, f"{L_STEM}.json"), l_scores(l_pairs))

# ----------------------------------------------------------------------------- figures
style.apply()
CLOSURE_LABEL = {"realizableKE": "realizable k-ε", "buoyantKEpsilon": "buoyantKEpsilon"}


def grid(case, title, runs, columns, ncols, fname, row_labels=None, handles_extra=(), decades=5):
    """runs = [(pairs, results)], one row each; columns = [(label, meas key, model key, score key, log, hollow key or None)] laid out ncols to a row
    (one row of panels per run when they fit in one, with the run's name down the left; otherwise a title on every panel)."""
    per = math.ceil(len(columns) / ncols)
    nrows = len(runs) * per
    fig, axs = uplt.subplots(nrows=nrows, ncols=ncols, refwidth=1.9, refaspect=1, share=False, wspace=4.2, hspace=3.4)
    for r, (pairs, res) in enumerate(runs):
        colours = layout.grouped_colours(case, pairs)          # the line or plane of the tunnel each point was measured on
        for i, (label, mk, pk, key, log, hollow) in enumerate(columns):
            ax = axs[r * per + i // ncols, i % ncols]
            hol = None if hollow is None else column(pairs, hollow) == 1
            shown = panel(ax, column(pairs, mk), column(pairs, pk), colours, log=log, xlab="Tunnel [–]" if r * per + i // ncols == nrows - 1 else None,
                          ylab="Eddy3D (UMF) [–]" if i % ncols == 0 else None, hollow=hol, decades=decades, trim=True)
            if per > 1:
                ax.format(title=label)
            style.stats(ax, stats_text(res[key], shown if log else None), loc=(0.40, 0.36) if log else (0.05, 0.80), halo="auto")
    handles = [*layout.legend_handles(case), *handles_extra, style.line(style.REFERENCE, "1:1", lw=1.0),
               style.line(style.REFERENCE, "factor of two", lw=0.8, ls=":")]
    labels = {"toplabels": [c[0] for c in columns[:ncols]], "leftlabels": row_labels} if per == 1 else {}
    style.finish(fig, title, handles=handles, **labels)
    style.save(fig, fname)


j_res = {c: read_json(os.path.join(RESULTS, f"{j_name(c)}.json")) for c, _ in J_CLOSURES}
J_FLOW = [("U/U$_H$", "U_meas", "U_model", "velocity.U", False, None), ("W/U$_H$", "W_meas", "W_model", "velocity.W", False, None), ("k/U$_H^2$", "k_meas", "k_model", "k", False, None),
          ("θ = (T$_f$ − T)/(T$_f$ − T$_H$)", "theta_meas", "theta_model", "theta", False, None)]
grid("J", "AIJ UWE Case J — Eddy3D (UMF) vs wind tunnel, 1:1:2 building on a heated floor", [(j_pairs[c], j_res[c]) for c, _ in J_CLOSURES], J_FLOW, 4, "case-j-umf-agreement.png",
     row_labels=[CLOSURE_LABEL[c] for c, _ in J_CLOSURES])
J_TRACER = [(f"c* = C/c$_0$, {lab}", "cstar_meas", f"cstar_{sp}", f"cstar.c_{sp}", True, "near_source") for sp, lab in SPECIES]
grid("J", "AIJ UWE Case J — the tracer, Eddy3D (UMF) vs wind tunnel, three turbulent Schmidt numbers", [(j_pairs[c], j_res[c]) for c, _ in J_CLOSURES], J_TRACER, 3, "case-j-umf-tracer.png",
     row_labels=[CLOSURE_LABEL[c] for c, _ in J_CLOSURES], handles_extra=[style.marker(style.REFERENCE, "within a quarter of H of the source", filled=False)], decades=7)
l_res = read_json(os.path.join(RESULTS, f"{L_STEM}.json"))
L_PANELS = [("U/U$_H$", "U_meas", "U_model", "velocity.U", False, None), ("W/U$_H$", "W_meas", "W_model", "velocity.W", False, None), ("k/U$_H^2$", "k_meas", "k_model", "k", False, None),
            ("θ = (T$_f$ − T)/(T$_f$ − T$_H$)", "theta_meas", "theta_model", "theta", False, None), ("V/U$_H$", "V_meas", "V_model", "velocity.V", False, None)] + \
           [(f"c* = C/c$_0$, {lab}", "cstar_meas", f"cstar_{sp}", f"cstar.c_{sp}", True, None) for sp, lab in SPECIES]
grid("L", "AIJ UWE Case L — Eddy3D (UMF, realizable k-ε) vs wind tunnel, 9 × 14 cube array on a heated floor", [(l_pairs, l_res)], L_PANELS, 4, "case-l-umf-agreement.png", decades=7)
