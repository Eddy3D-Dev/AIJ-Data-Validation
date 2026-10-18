"""Validation figures for AIJ UWE Cases F (Shinjuku district) and M (TPU Atsugi campus) solved with Eddy3D / OpenFOAM 12.

Four figures, each answering one question:

  case-f-openfoam-agreement.png   Does the model agree with the tunnel and the field?  Case F, wind from NNW (the one direction solved): measured
                      against modelled speed, one row per vertical frame (the published z in the STL's frame, and the STL's ground plus the instrument
                      height), one column each for the tunnel's 9 m plane, all 33 tunnel points (5, 9 and 20 m) and the 13 field observations.
  case-f-openfoam-bias-map.png    WHERE does it agree?  log2(model / tunnel) of the scalar speed at the tunnel's 13 points of the 9 m plane on the plan
                      of the district, in both vertical frames.
  case-m-openfoam-agreement.png   Case M, WD 180: measured against modelled U, V, W, k and the dimensionless concentration c* at turbulent Schmidt
                      numbers 0.3, 0.5 and 0.7, and the tunnel's own WD 175 and WD 185 against its WD 180 (the noise floor of a single heading).
  case-m-openfoam-plan.png        WHERE is the tracer?  c* of the tunnel and of the three Schmidt numbers at the 15 points on the plan of the campus,
                      with the source and the reference mast.

Inputs, all in this repository: the cleaned measurement tables clean/cases/{F,M}/points.csv (and clean/manifest.json for the field runs of Case M), and
the per-point pairs validation/results/case{F,M}_openfoam12_realizableKE_pairs.csv built from them and from the probes the Eddy3D fixtures
TestAijCaseFContainerE2E and TestAijCaseMContainerE2E wrote (validation/results/case{F,M}_*probes*.csv and *_approach.csv are snapshots of those probe
files; the SHA-256 of every file a snapshot was read from is in each results file under `sources`). They are refreshed from ~/Eddy3DVal/aij_F_realizableKE_L3
and aij_M_realizableKE_L3_s3 when that folder exists (EDDY3D_VAL names another); everywhere else, the build included, the committed snapshots are checked
against the committed pairs and the figures are drawn from them. The scores in validation/results/case{F,M}_openfoam12_realizableKE_*.json are computed FROM
THE PAIRS by validation/dispersion_metrics.py; this script recomputes them on every run and fails if a file disagrees. When the Eddy3D results are present it
also scores the published CSVs the way the fixtures do, with the fixtures' own probes, and requires the fixtures' numbers to 1e-9 (the control that these
metrics are theirs), and prints the recomputed scores next to the fixtures' (the measured side differs: see below).

Case F. The thermistor's scalar speed is compared as sqrt(|U|^2 + 2k) and as |U|, both over the model's own approach speed U(500 m) = 9.862 m/s, probed
1100 m upwind of the centre (the CSVs are U / U(500 m)). The tunnel's 13 points at 5, 9 and 20 m (7, 13 and 13 of them) and the field's 13 cup-anemometer
observations are scored against the one solved direction, NNW. Two vertical frames are probed and scored, and neither is asserted: 'literal' is the published
z in the STL's frame (z measured from the tunnel floor, which the readme says is the ground plus 10 m) and 'agl' is the STL's own ground under the point plus
the instrument height; the STL's ground is 5 m, not 10, at all 13 points. The measured side is the cleaned table; it equals the published CSV at every
tunnel point, and differs at one field point (point 14, whose 16 rows in RS-FO_caseF.csv are shifted by one direction, clean/QUESTIONS.md QF1), so the
tunnel scores equal the fixture's and the field scores do not. The compass sense is tested by a free control: the solved field correlates with the tunnel's
NNW column and not with its SSE column.

Case M. The wind-tunnel run at WD 180 (the only heading with velocities) is scored; the field campaign is recorded beside it. The pairs are in the release's
frame (x north, y west, full-scale metres, z above the tunnel floor; the case's x east, y north is a quarter turn of it): U, V, W and k at the 15 points over
the tunnel's own U_R = 4.08 m/s on the measurement and over the SOLVED speed at the reference mast on the model (U_R is defined at the mast), c* = C/c0 for the
measurement (c0 = 132.514 ppm) against c U_R H_R^2 / Q (H_R = 0.068 m x 600, Q = 1 kg/s) for the model at the three turbulent Schmidt numbers, which are three
runs on one flow. The controls are the fixture's: the 15 points turned 180 degrees about the source, and mirrored across the plume
axis; and this script's own: the tunnel's WD 175 and WD 185 columns scored against its WD 180. The field band is the runs within 10 degrees of 180 at 3 m/s
or more (10 of 18), each with its own U_R and q, c0 per run with H_R = 41 m as the table states; the fixture divides by 40.8 m, which is the whole difference
in these numbers (1 %).

Colours follow plotstyle.py: the measurement is ink; reference geometry (1:1 line, factor-of-two band, building outlines) is recessive grey. The dots of
the two agreement figures take the colour of the group of the tunnel's points they were measured in (layout.py; the letters and colours of
case-f-layout.png and case-m-layout.png): Case F by plane (5, 9 and 20 m) or field anemometer, Case M by distance from the release point.
"""
from __future__ import annotations

import csv
import io
import math
import os
import re

import numpy as np
import ultraplot as uplt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

import dispersion_metrics as DM
import layout
import plotstyle as style
from snapshot_common import (REPO, RESULTS, SPECIES, check_snapshot, clean_table, column, fnum, non_scores, panel, read_json, read_lf, read_pairs, sha256,
                             stats_text, validation_root, write_json, write_lf, write_pairs)

F_STUDY = "aij_F_realizableKE_L3"
M_STUDY = "aij_M_realizableKE_L3_s3"
F_STEM = "caseF_openfoam12_realizableKE"
M_STEM = "caseM_openfoam12_realizableKE"
STAMP = "2026-10-18"


# ----------------------------------------------------------------------------- what the two solves share

def log_facts(log):
    """What the foamRun log of a SIMPLE solve says: the last time, the solver seconds, the initial residuals of the last iteration, how many iterations
    bounded k, and whether it ended on a convergence line (the logs are 3 to 7 MB, so the file is read once)."""
    with io.open(log, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    last = text.split("\nTime = ")[-1]
    clock = re.findall(r"ExecutionTime = ([0-9.]+) s\s+ClockTime = (\d+) s", text)[-1]
    stopped = ("the solver's convergence line" if "solution converged" in text else
               "the iteration limit: the log has no 'solution converged' line (residualControl not met)")
    return {"iterationsRun": int(re.findall(r"^Time = (\d+)s", text, re.M)[-1]), "stoppedBy": stopped,
            "finalInitialResiduals": {m.group(1): float(m.group(2)) for m in re.finditer(r"Solving for (\w+), Initial residual = ([0-9.eE+-]+)", last)},
            "solverSeconds": float(clock[0]), "clockSeconds": int(clock[1]), "boundingKLines": text.count("bounding k,")}


def mesh_facts(path):
    """The cells and the verdict of a checkMesh log (the mesh the solve ran on)."""
    t = read_lf(path)
    skew = re.search(r"Max skewness = ([0-9.eE+-]+)(?:, (\d+) highly skew faces)?", t)
    return {"cells": int(re.search(r"^\s*cells:\s+(\d+)", t, re.M).group(1)),
            "verdict": "Mesh OK." if "Mesh OK." in t else re.search(r"Failed \d+ mesh checks\.", t).group(0),
            "maxNonOrthogonalityDeg": float(re.search(r"Mesh non-orthogonality Max: ([0-9.eE+-]+)", t).group(1)),
            "maxSkewness": float(skew.group(1)), "highlySkewFaces": int(skew.group(2) or 0)}


def read_raw_rows(case_folder, name):
    with io.open(os.path.join(REPO, "raw", "cases", case_folder, name), encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def same_all(mine, fixture, label):
    """Every score of `mine` that the fixture also wrote reproduces it to 1e-9 (FB, NMSE and NAD where this module leaves them undefined are skipped)."""
    checked = 0
    for key, want in fixture.items():
        got = mine[key]
        if isinstance(got, dict):
            assert DM.same(got, want, fixture=True), (label, key, got, want)
        elif isinstance(got, bool) or isinstance(want, bool):
            assert got == want, (label, key, got, want)
        else:
            assert abs(got - want) <= 1e-9 * max(1.0, abs(want)), (label, key, got, want)
        checked += 1
    return checked


def parity_line(name, a, b):
    fb = lambda v: "n/a" if v is None else format(v, "+.4f")  # noqa: E731
    r = lambda v: "n/a" if v is None else format(v, "+.4f")  # noqa: E731
    return f"{name}: R {r(a['R'])} -> {r(b['R'])}  FAC2 {a['Fac2']:.4f} -> {b['Fac2']:.4f}  FB {fb(a['Fb'])} -> {fb(b['Fb'])}  n {a['Count']} -> {b['Count']}"


# ----------------------------------------------------------------------------- Case F

F_DIRECTION, F_OPPOSITE = "NNW", "SSE"
F_UR, F_RAISE, F_SCALE = 10.0, 10.0, 800.0                    # imposed U(500 m) [m/s]; the readme's raise of z over the ground [m]; full-scale metres per model metre
F_FRAMES = ("literal", "agl")
F_PLANES = (5, 9, 20)
F_CONFIG = {5: "h5", 9: "default", 20: "h20"}                  # the cleaned table's config of each tunnel plane
F_PAIR_FIELDS = ["frame", "source", "plane_m", "point_id", "x", "y", "z_published", "z_probe", "height_above_stl_ground", "observed", "observed_sd",
                 "observed_sse", "Umag_model", "rms_model", "k_model"]
F_QUANTITY = ("the thermistor's (tunnel) and the cup anemometer's (field) mean speed over U(500 m) against the model's |U| and sqrt(|U|^2 + 2k) over its own approach "
              "U(500 m) = 9.862 m/s (probed 1100 m upwind of the centre; the imposed U(500 m) is 10 m/s), at the 33 tunnel points (planes at 5, 9 and 20 m) and the 13 field "
              "observations of wind from NNW; frame {frame}")
F_FRAME_MEANING = {"literal": "the published z in the STL's frame (z from the tunnel floor: the readme's ground plus 10 m, which samples 10, 14 and 25 m above the STL's ground of 5 m)",
                   "agl": "the STL's own ground under the point plus the instrument height (5, 9 and 20 m for the tunnel; 3 to 11 m for the field)"}
F_RECORDED_DROP = ("wt.", "fo.", "ceiling.", "sense.", "anemometer.")


def f_plan(src):
    """model_NNW.csv, the order of mp_NNW.probe.csv: one row per point probed (both frames; the two rooftop anemometers last)."""
    with io.open(os.path.join(src, "model_NNW.csv"), encoding="utf-8") as f:
        return list(csv.DictReader(f))


def f_rows(plan, probe, u500):
    """The pairs of Case F: the cleaned table's NNW rows (and its SSE column) against the probes at the same points, in both frames."""
    clean = clean_table("F")
    tunnel = {(r["config"], int(r["point_id"])): r for r in clean if r["campaign"] == "wind_tunnel" and r["wind_direction"] == F_DIRECTION}
    field = {int(r["point_id"]): r for r in clean if r["campaign"] == "field" and r["wind_direction"] == F_DIRECTION}
    sse = {int(r["point_id"]): fnum(r["velocity_ratio"]) for r in clean if r["campaign"] == "wind_tunnel" and r["config"] == "default" and r["wind_direction"] == F_OPPOSITE}
    assert len(plan) == len(probe), (len(plan), len(probe))
    ground = {}
    for m, p in zip(plan, probe):
        if m["frame"] == "agl" and m["source"] in ("wt", "fo"):
            ground[(m["source"], int(m["no"]), int(m["aglM"]))] = float(p["z"]) - int(m["aglM"])
    rows = []
    for frame in F_FRAMES:
        for source in ("wt", "fo"):
            for m, p in zip(plan, probe):
                if m["frame"] != frame or m["source"] != source:
                    continue
                for k in ("x", "y", "z"):
                    assert abs(float(m[k]) - float(p[k])) < 1e-5, (m, p)
                no, plane = int(m["no"]), int(m["aglM"])
                row = tunnel[(F_CONFIG[plane], no)] if source == "wt" else field[no]
                z_pub = float(row["z"])
                assert abs(float(row["x"]) - float(m["x"])) < 1e-6 and abs(float(row["y"]) - float(m["y"])) < 1e-6, (frame, source, no)
                assert abs(z_pub - F_RAISE - plane) < 1e-6, (source, no, z_pub, plane)
                if frame == "literal":
                    assert abs(float(p["z"]) - z_pub) < 1e-6
                mag, k = float(p["U_mag"]), float(p["k"])
                # model_NNW.csv carries the fixture's own division by U(500 m): the pairs reproduce it from the probe
                assert abs(mag / u500 - float(m["Umag/U500"])) < 1e-12 and abs(math.sqrt(mag * mag + 2 * k) / u500 - float(m["rms/U500"])) < 1e-12, (frame, source, no)
                rows.append({"frame": frame, "source": "tunnel" if source == "wt" else "field", "plane_m": plane, "point_id": no, "x": float(row["x"]), "y": float(row["y"]),
                             "z_published": z_pub, "z_probe": float(p["z"]), "height_above_stl_ground": float(p["z"]) - ground[(source, no, plane)],
                             "observed": fnum(row["velocity_ratio"]), "observed_sd": fnum(row["velocity_ratio_sd"]) if source == "fo" else math.nan,
                             "observed_sse": sse.get(no, math.nan) if source == "wt" and plane == 9 else math.nan,
                             "Umag_model": mag / u500, "rms_model": math.sqrt(mag * mag + 2 * k) / u500, "k_model": k})
    return rows


def f_scores(rows, u500):
    """Every score of one frame of Case F from its pairs. Keys follow the fixture's results.json (wt.NNW.<frame>.<h>m.<q> is tunnel.<h>m.<q>, fo.NNW.<frame>.<q> is field.<q>)."""
    out = {}
    tun = [r for r in rows if r["source"] == "tunnel"]
    fld = [r for r in rows if r["source"] == "field"]
    for name, sel in [(f"{h}m", [r for r in tun if r["plane_m"] == h]) for h in F_PLANES] + [("all", tun)]:
        out[f"tunnel.{name}.Umag"] = DM.velocity(column(sel, "observed"), column(sel, "Umag_model"))
        out[f"tunnel.{name}.rms"] = DM.velocity(column(sel, "observed"), column(sel, "rms_model"))
    out["field.Umag"] = DM.velocity(column(fld, "observed"), column(fld, "Umag_model"))
    out["field.rms"] = DM.velocity(column(fld, "observed"), column(fld, "rms_model"))
    nine = sorted((r for r in tun if r["plane_m"] == 9), key=lambda r: r["point_id"])
    out["tunnel.9m.rms.byImposedUR"] = DM.velocity(column(nine, "observed"), column(nine, "rms_model") * u500 / F_UR)
    # the tunnel's 9 m column as a model of the field, point for point: no model enters, so the bar no model is expected to clear
    by_field = {r["point_id"]: r["observed"] for r in fld}
    common = [r for r in nine if r["point_id"] in by_field]
    out["control.tunnelAsModelOfField"] = DM.velocity([by_field[r["point_id"]] for r in common], column(common, "observed"))
    # the compass sense: the solved field against the tunnel's column for the wind from NNW (= tunnel.9m.rms) and for the opposite wind, SSE
    out["control.sense.opposite"] = DM.velocity(column(nine, "observed_sse"), column(nine, "rms_model"))
    return out


def f_anemometers(plan, probe, u500):
    """The model's U / U(500 m) at the workbook's two rooftop anemometers (SMB, KDD), recorded and not scored."""
    out = {}
    for m, p in zip(plan, probe):
        if m["source"] in ("smb", "kdd"):
            mag, k = float(p["U_mag"]), float(p["k"])
            out[f"{m['source']}.Umag"] = mag / u500
            out[f"{m['source']}.rms"] = math.sqrt(mag * mag + 2 * k) / u500
    return out


def f_snapshot(root):
    src = os.path.join(root, F_STUDY)
    probe_path = os.path.join(src, "mp_NNW.probe.csv")
    approach_path = os.path.join(src, "approach_NNW.probe.csv")
    write_lf(os.path.join(RESULTS, f"{F_STEM}_probes.csv"), read_lf(probe_path))
    write_lf(os.path.join(RESULTS, f"{F_STEM}_approach.csv"), read_lf(approach_path))
    fx = read_json(os.path.join(src, "results.json"))
    u500 = fx["approach.NNW.U500"]
    plan = f_plan(src)
    probe = list(csv.DictReader(io.StringIO(read_lf(probe_path))))
    rows = f_rows(plan, probe, u500)
    write_pairs(os.path.join(RESULTS, f"{F_STEM}_pairs.csv"), F_PAIR_FIELDS, rows)
    study = os.path.join(src, "study", "case_338")
    sources = {f"{F_STUDY}/{n}": sha256(os.path.join(src, n)) for n in ("mp_NNW.probe.csv", "mp_NNW.points.csv", "model_NNW.csv", "approach_NNW.probe.csv", "approach_NNW.points.csv",
                                                                         "results.json", "geometry/buildings.stl", "study/case_338/run_01_foamRun.txt", "study/mesh/06_checkMesh.txt")}
    keep = non_scores(fx, drop=F_RECORDED_DROP)
    for frame in F_FRAMES:
        frame_rows = [r for r in rows if r["frame"] == frame]
        res = {**keep, "quantity": F_QUANTITY.format(frame=frame), "frame": frame, "frameMeaning": F_FRAME_MEANING[frame], "points.measured": len(frame_rows),
               "U500": u500, "pairs": f"{F_STEM}_pairs.csv", "probes": f"{F_STEM}_probes.csv", "approach": f"{F_STEM}_approach.csv",
               "solveLog": log_facts(os.path.join(study, "run_01_foamRun.txt")), "meshCheck": mesh_facts(os.path.join(src, "study", "mesh", "06_checkMesh.txt")),
               "anemometers": f_anemometers(plan, probe, u500),
               "scoresFrom": "the pairs file (validation/dispersion_metrics.py); the fixture's own scores, computed against RS-WT_caseF.csv and RS-FO_caseF.csv, are in Eddy3D's results.json",
               "sources": sources, **f_scores(frame_rows, u500)}
        write_json(os.path.join(RESULTS, f"{F_STEM}_{frame}.json"), res)
    print(f"snapshot {F_STEM}: {len(rows)} pairs in {len(F_FRAMES)} frames")


def f_fixture_keys(frame):
    """Mine -> the fixture's key, for the scores both write."""
    out = {}
    for name in [f"{h}m" for h in F_PLANES] + ["all"]:
        for q in ("Umag", "rms"):
            out[f"tunnel.{name}.{q}"] = f"wt.{F_DIRECTION}.{frame}.{name}.{q}"
    for q in ("Umag", "rms"):
        out[f"field.{q}"] = f"fo.{F_DIRECTION}.{frame}.{q}"
    if frame == "literal":
        out["tunnel.9m.rms.byImposedUR"] = f"wt.{F_DIRECTION}.literal.9m.rms.byImposedUR"
    return out


def f_control(root, fx):
    """Case F scored the way the fixture scores it: the published CSVs' values at the same points, the fixture's probes. Its results.json to 1e-9."""
    src = os.path.join(root, F_STUDY)
    u500 = fx["approach.NNW.U500"]
    plan = f_plan(src)
    probe = list(csv.DictReader(io.StringIO(read_lf(os.path.join(src, "mp_NNW.probe.csv")))))
    rows = f_rows(plan, probe, u500)
    wt = {(r["WD"], int(r["No."]), round(float(r["z"]) * F_SCALE, 6)): float(r["U/R"]) for r in read_raw_rows("case-f", "RS-WT_caseF.csv")}
    fo = {(r["WD"], int(r["No."]), float(r["z"])): float(r["U/R"]) for r in read_raw_rows("case-f", "RS-FO_caseF.csv")}
    ctrl, moved = [], set()
    for r in rows:
        want = wt[(F_DIRECTION, r["point_id"], round(r["z_published"], 6))] if r["source"] == "tunnel" else fo[(F_DIRECTION, r["point_id"], r["z_published"])]
        if abs(want - r["observed"]) > 1e-12:
            moved.add((r["source"], r["point_id"]))
        sse = wt.get((F_OPPOSITE, r["point_id"], round(r["z_published"], 6)), math.nan) if r["source"] == "tunnel" and r["plane_m"] == 9 else math.nan
        ctrl.append({**r, "observed": want, "observed_sse": sse})
    # the cleaned table and the CSVs agree at every tunnel point and at every field point but one
    assert moved == {("field", 14)}, moved
    checked = 0
    for frame in F_FRAMES:
        mine = f_scores([r for r in ctrl if r["frame"] == frame], u500)
        checked += same_all(mine, {k: fx[v] for k, v in f_fixture_keys(frame).items()}, f"{F_STEM}_{frame}")
        if frame == "literal":                      # the fixture records the compass sense and the ceiling on the published z only
            assert abs(mine["tunnel.9m.rms"]["R"] - fx["sense.NNW.R.stated"]) < 1e-9
            assert abs(mine["control.sense.opposite"]["R"] - fx["sense.NNW.R.opposite"]) < 1e-9
            assert DM.same(mine["control.tunnelAsModelOfField"], fx["ceiling.NNW.tunnelVsField"], fixture=True)
            checked += 3
    print(f"fixture control {F_STEM}: {checked} scores reproduced from RS-WT_caseF.csv, RS-FO_caseF.csv and the fixture's probes (the tunnel's values are identical in the cleaned table)")


def f_parity(fx):
    for frame in F_FRAMES:
        mine = read_json(os.path.join(RESULTS, f"{F_STEM}_{frame}.json"))
        for key, fkey in list(f_fixture_keys(frame).items()):
            if key in ("tunnel.9m.rms", "tunnel.all.rms", "field.rms", "tunnel.5m.rms", "tunnel.20m.rms"):
                print(parity_line(f"{F_STEM}_{frame} {key}", fx[fkey], mine[key]))
    mine = read_json(os.path.join(RESULTS, f"{F_STEM}_literal.json"))
    print(parity_line("ceiling tunnel 9 m as a model of the field", fx["ceiling.NNW.tunnelVsField"], mine["control.tunnelAsModelOfField"]))
    print(f"compass sense: R stated {fx['sense.NNW.R.stated']:+.4f} -> {mine['tunnel.9m.rms']['R']:+.4f}, opposite {fx['sense.NNW.R.opposite']:+.4f} -> {mine['control.sense.opposite']['R']:+.4f}")


# ----------------------------------------------------------------------------- Case M

M_UR_TUNNEL = 4.08                                             # the tunnel's speed at the reference point R [m/s]
M_HR_MODEL, M_SCALE = 0.068, 600.0                             # H_R in the tunnel [m] and full-scale metres per model metre
M_HR = M_HR_MODEL * M_SCALE                                    # 40.8 m: the model's H_R in c* = c U_R H_R^2 / Q (Q = 1 kg/s)
M_Q = 1.0
M_BAND_MIN_SPEED, M_BAND_HALF = 3.0, 10.0                      # the field runs a steady solve at WD 180 can be compared with
M_HEADING = 180
M_PAIR_FIELDS = (["point_id", "x", "y", "z", "U_meas", "V_meas", "W_meas", "speed_meas", "k_meas", "U_model", "V_model", "W_model", "speed_model", "k_model", "cstar_meas",
                  "cstar_wd175", "cstar_wd185"] + [f"cstar_{sp}" for sp, _ in SPECIES] + [f"cstar_{sp}_turned180" for sp, _ in SPECIES] +
                 [f"cstar_{sp}_mirrored" for sp, _ in SPECIES] + ["cstar_field_geomean", "cstar_field_min", "cstar_field_max"])
M_RUN_DROP = ("cstar.", "control.", "field.", "velocity.")
M_QUANTITY = ("U, V, W and k at the 15 points of the tunnel's WD 180 run over the tunnel's U_R = 4.08 m/s (measured) and over the solved speed at the reference mast (modelled; "
              "U_R is defined at the mast), and the dimensionless concentration c* = C/c0 (c0 = q/(U_R H_R^2) = 132.5 ppm) against the model's c U_R H_R^2/Q for turbulent Schmidt "
              "number {sct}; the field campaign (18 runs) is recorded beside it")


def m_probe_rows(path):
    return list(csv.DictReader(io.StringIO(read_lf(path))))


def m_cstar(c, ur):
    """c* = c U_R H_R^2 / Q, the fixture's TpuCampusCase.CaseCStar (NaN stays NaN)."""
    return c * ur * M_HR ** 2 / M_Q


def m_field(manifest_runs):
    """Per point (1..15): the geometric mean (strictly positive values), the minimum and the maximum of c* over the runs of the band, from the cleaned table."""
    speed = {int(r["run"]): float(r["U_R_m_s"]) for r in manifest_runs}
    rows = [r for r in clean_table("M") if r["campaign"] == "field"]
    band = sorted({int(r["run"]) for r in rows if abs(float(r["wind_direction_deg"]) - M_HEADING) <= M_BAND_HALF and speed[int(r["run"])] >= M_BAND_MIN_SPEED})
    geo, lo, hi = [], [], []
    for pt in range(1, 16):
        v = np.array([fnum(r["concentration_ratio"]) for r in rows if int(r["point_id"]) == pt and int(r["run"]) in band])
        assert len(v) == len(band)
        pos = v[v > 0]
        geo.append(float(np.exp(np.log(pos).mean())) if len(pos) else math.nan)
        lo.append(float(v.min()))
        hi.append(float(v.max()))
    return band, {n: speed[n] for n in band}, np.array(geo), np.array(lo), np.array(hi)


def m_rows(src):
    """The 15 pairs of Case M: the cleaned table (tunnel velocities and c* at WD 175, 180 and 185, the field band) against the probe at the same points."""
    clean = clean_table("M")
    sfx = {r["point_id"]: r for r in clean if r["instrument"] == "split_fibre"}
    hc = {int(wd): {r["point_id"]: r for r in clean if r["instrument"] == "hydrocarbon_analyser" and float(r["wind_direction_deg"]) == wd} for wd in (175, 180, 185)}
    probe = m_probe_rows(os.path.join(src, "mp_180.probe.csv"))
    turned = m_probe_rows(os.path.join(src, "controlTurned_180.probe.csv"))
    mirrored = m_probe_rows(os.path.join(src, "controlMirrored_180.probe.csv"))
    approach = m_probe_rows(os.path.join(src, "approach_180.probe.csv"))
    ur = float(approach[0]["U_mag"])                                        # the first row is the reference mast
    manifest = read_json(os.path.join(REPO, "clean", "manifest.json"))
    band, speeds, geo, lo, hi = m_field(manifest["cases"]["M"]["extra_measurements"]["field_runs"])
    rows = []
    for i, p in enumerate(probe):
        pid = str(i + 1)
        s = sfx[pid]
        x, y, z = float(s["x"]), float(s["y"]), float(s["z"])
        # the case frame (x east, y north) is the release's (x north, y west) turned a quarter turn: (x, y) = (-y_release, x_release)
        assert abs(float(p["x"]) + y) < 1e-5 and abs(float(p["y"]) - x) < 1e-5 and abs(float(p["z"]) - z) < 1e-5, (pid, p, (x, y, z))
        u, v, w, k = fnum(s["U"]), fnum(s["V"]), fnum(s["W"]), fnum(s["k"])
        row = {"point_id": i + 1, "x": x, "y": y, "z": z,
               "U_meas": u / M_UR_TUNNEL, "V_meas": v / M_UR_TUNNEL, "W_meas": w / M_UR_TUNNEL, "speed_meas": math.sqrt(u * u + v * v + w * w) / M_UR_TUNNEL, "k_meas": k / M_UR_TUNNEL ** 2,
               "U_model": float(p["U_y"]) / ur, "V_model": -float(p["U_x"]) / ur, "W_model": float(p["U_z"]) / ur, "speed_model": float(p["U_mag"]) / ur,
               "k_model": float(p["k"]) / ur ** 2,
               "cstar_meas": fnum(hc[180][pid]["concentration_ratio"]), "cstar_wd175": fnum(hc[175][pid]["concentration_ratio"]), "cstar_wd185": fnum(hc[185][pid]["concentration_ratio"])}
        for sp, _ in SPECIES:
            row[f"cstar_{sp}"] = m_cstar(float(p[f"c_{sp}"]), ur)
            row[f"cstar_{sp}_turned180"] = m_cstar(float(turned[i][f"c_{sp}"]), ur)
            row[f"cstar_{sp}_mirrored"] = m_cstar(float(mirrored[i][f"c_{sp}"]), ur)
        row.update({"cstar_field_geomean": float(geo[i]), "cstar_field_min": float(lo[i]), "cstar_field_max": float(hi[i])})
        rows.append(row)
    return rows, ur, band, speeds


def m_scores(rows, sp, ur, imposed):
    """Every score of the run at one Schmidt number from the pairs. Keys follow the fixture's results.json (cstar.180.c_<sp>.x is cstar.x, control.180.c_<sp>.x is control.x)."""
    c = lambda key: column(rows, key)  # noqa: E731
    tun, cs = c("cstar_meas"), c(f"cstar_{sp}")
    top = lambda v: sorted(sorted(range(len(v)), key=lambda i: -v[i])[:5])  # noqa: E731
    out = {"cstar": DM.concentration(tun, cs), "cstar.byImposedMastSpeed": DM.concentration(tun, cs * imposed / ur), "cstar.byPaperUR": DM.concentration(tun, cs * M_UR_TUNNEL / ur),
           "cstar.peakMeasured": float(tun.max()), "cstar.peakModel": float(np.nanmax(cs)), "cstar.topFiveOverlap": len(set(top(tun)) & set(top(cs))),
           "cstar.nearThreeMean": float(cs[:3].mean()), "cstar.farTwoMean": float(cs[13:].mean()), "cstar.nearBeatsFar": bool(cs[:3].mean() > cs[13:].mean()),
           "cstar.tunnel.nearThreeMean": float(tun[:3].mean()), "cstar.tunnel.farTwoMean": float(tun[13:].mean())}
    turned, mirrored = c(f"cstar_{sp}_turned180"), c(f"cstar_{sp}_mirrored")
    both = np.isfinite(cs) & np.isfinite(turned)
    out.update({"control.turned180": DM.concentration(tun, turned), "control.mirrored": DM.concentration(tun, mirrored), "control.turned180.finitePoints": int(both.sum()),
                "control.meanReal": float(cs[both].mean()), "control.meanTurned180": float(turned[both].mean()),
                "control.tunnelWD175AsModelOfWD180": DM.concentration(tun, c("cstar_wd175")), "control.tunnelWD185AsModelOfWD180": DM.concentration(tun, c("cstar_wd185")),
                "control.tunnelNeighbourMeanAsModelOfWD180": DM.concentration(tun, 0.5 * (c("cstar_wd175") + c("cstar_wd185")))})
    geo, lo, hi = c("cstar_field_geomean"), c("cstar_field_min"), c("cstar_field_max")
    out.update({"field.vsGeometricMean": DM.concentration(geo, cs), "field.insideFieldRange": int(((cs >= lo) & (cs <= hi)).sum()),
                "field.tunnelAsModelOfGeometricMean": DM.concentration(geo, tun), "field.spreadAtPoint1": float(hi[0] / lo[0])})
    # the flow does not depend on the Schmidt number: the same velocity scores belong to all three runs
    out.update({"velocity.U": DM.velocity(c("U_meas"), c("U_model")), "velocity.V": DM.velocity(c("V_meas"), c("V_model")), "velocity.V.flipped": DM.velocity(c("V_meas"), -c("V_model")),
                "velocity.W": DM.velocity(c("W_meas"), c("W_model")), "velocity.magnitude": DM.velocity(c("speed_meas"), c("speed_model")), "k": DM.turbulence(c("k_meas"), c("k_model")),
                "velocity.U.mean.tunnel": float(c("U_meas").mean()), "velocity.U.mean.model": float(c("U_model").mean())})
    return out


def m_name(sp):
    return f"{M_STEM}_{sp}"


def m_snapshot(root):
    src = os.path.join(root, M_STUDY)
    for name, dest in (("mp_180.probe.csv", "probes"), ("approach_180.probe.csv", "approach"), ("controlTurned_180.probe.csv", "turned_probes"), ("controlMirrored_180.probe.csv", "mirrored_probes")):
        write_lf(os.path.join(RESULTS, f"{M_STEM}_{dest}.csv"), read_lf(os.path.join(src, name)))
    fx = read_json(os.path.join(src, "results.json"))
    rows, ur, band, speeds = m_rows(src)
    write_pairs(os.path.join(RESULTS, f"{M_STEM}_pairs.csv"), M_PAIR_FIELDS, rows)
    imposed = fx["reference.U.imposedAtMastElevation"]
    study = os.path.join(src, "study", "case_180")
    sources = {f"{M_STUDY}/{n}": sha256(os.path.join(src, n)) for n in ("mp_180.probe.csv", "mp_180.points.csv", "controlTurned_180.probe.csv", "controlTurned_180.points.csv",
                                                                         "controlMirrored_180.probe.csv", "controlMirrored_180.points.csv", "approach_180.probe.csv",
                                                                         "approach_180.points.csv", "model_180.csv", "results.json", "geometry/buildings.stl", "geometry/terrain.stl",
                                                                         "geometry/source.stl", "study/case_180/run_01_foamRun.txt", "study/mesh/06_checkMesh.txt")}
    keep = non_scores(fx, drop=M_RUN_DROP)
    for sp, label in SPECIES:
        res = {**keep, "configuration": sp, "sct": float(label.split()[-1]), "quantity": M_QUANTITY.format(sct=label.split()[-1]), "points.measured": len(rows),
               "referenceSpeed.solvedAtMast": ur, "referenceSpeed.tunnel": M_UR_TUNNEL, "referenceHeight.full": M_HR, "field.band.runs": band, "field.band.speedsMps": {str(n): v for n, v in speeds.items()}, "field.band.minSpeed": M_BAND_MIN_SPEED,
               "field.band.halfWidthDegrees": M_BAND_HALF, "pairs": f"{M_STEM}_pairs.csv", "probes": f"{M_STEM}_probes.csv", "approach": f"{M_STEM}_approach.csv",
               "controlProbes": [f"{M_STEM}_turned_probes.csv", f"{M_STEM}_mirrored_probes.csv"], "solveLog": log_facts(os.path.join(study, "run_01_foamRun.txt")),
               "meshCheck": mesh_facts(os.path.join(src, "study", "mesh", "06_checkMesh.txt")),
               "scoresFrom": "the pairs file (validation/dispersion_metrics.py); the fixture's own scores, computed against RS-WT_caseM.csv and RS-FO_caseM.csv, are in Eddy3D's results.json",
               "sources": sources, **m_scores(rows, sp, ur, imposed)}
        write_json(os.path.join(RESULTS, f"{m_name(sp)}.json"), res)
    print(f"snapshot {M_STEM}: {len(rows)} pairs, three Schmidt numbers")


def m_fixture_keys(sp):
    out = {"cstar": f"cstar.180.c_{sp}"}
    for tail in ("byImposedMastSpeed", "byPaperUR", "peakMeasured", "peakModel", "topFiveOverlap", "nearThreeMean", "farTwoMean", "nearBeatsFar"):
        out[f"cstar.{tail}"] = f"cstar.180.c_{sp}.{tail}"
    out.update({"cstar.tunnel.nearThreeMean": "cstar.180.tunnel.nearThreeMean", "cstar.tunnel.farTwoMean": "cstar.180.tunnel.farTwoMean"})
    for tail in ("turned180", "mirrored", "turned180.finitePoints", "meanReal", "meanTurned180"):
        out[f"control.{tail}"] = f"control.180.c_{sp}.{tail}"
    out.update({"field.vsGeometricMean": f"field.180.c_{sp}.vsGeometricMean", "field.insideFieldRange": f"field.180.c_{sp}.insideFieldRange",
                "field.tunnelAsModelOfGeometricMean": "field.tunnel180AsModelOfFieldGeometricMean", "field.spreadAtPoint1": "field.cstar.spreadAtPoint1"})
    for k in ("velocity.U", "velocity.V", "velocity.V.flipped", "velocity.W", "velocity.magnitude", "k", "velocity.U.mean.tunnel", "velocity.U.mean.model"):
        out[k] = k
    return out


def m_control(root, fx):
    """Case M scored the way the fixture scores it: RS-WT_caseM.csv (rounded) and RS-FO_caseM.csv with the fixture's H_R = 40.8 m for the field, the fixture's probes. Its results.json to 1e-9."""
    src = os.path.join(root, M_STUDY)
    rows, ur, _, _ = m_rows(src)
    tunnel = {}
    for r in read_raw_rows("case-m", "RS-WT_caseM.csv"):
        tunnel[(int(r["WD (deg)"]), int(r["No."]))] = {k.split(" (")[0].strip(): float(v) for k, v in r.items() if k not in ("No.",) and v.strip() != ""}
    c0 = 2.5e-6 / (M_UR_TUNNEL * M_HR_MODEL ** 2) * 1e6
    field = read_raw_rows("case-m", "RS-FO_caseM.csv")
    runs = {int(r["Run"]): (float(r["U_R (m/s)"]), float(r["WD_R (deg)"]), float(r["q (m3/s)"])) for r in field}
    band = sorted(n for n, (sp_, wd, q) in runs.items() if sp_ >= M_BAND_MIN_SPEED and abs(wd - M_HEADING) <= M_BAND_HALF)
    geo, lo, hi = [], [], []
    for pt in range(1, 16):
        v = np.array([float(r["C (ppq)"]) * 1e-15 * runs[int(r["Run"])][0] * M_HR ** 2 / runs[int(r["Run"])][2] for r in field if int(r["No."]) == pt and int(r["Run"]) in band])
        pos = v[v > 0]
        geo.append(float(np.exp(np.log(pos).mean())))
        lo.append(float(v.min()))
        hi.append(float(v.max()))
    ctrl = []
    for i, r in enumerate(rows):
        t = {wd: tunnel[(wd, i + 1)] for wd in (175, 180, 185)}
        ctrl.append({**r, "U_meas": t[180]["U"] / M_UR_TUNNEL, "V_meas": t[180]["V"] / M_UR_TUNNEL, "W_meas": t[180]["W"] / M_UR_TUNNEL,
                     "speed_meas": math.sqrt(t[180]["U"] ** 2 + t[180]["V"] ** 2 + t[180]["W"] ** 2) / M_UR_TUNNEL, "k_meas": t[180]["k"] / M_UR_TUNNEL ** 2,
                     "cstar_meas": t[180]["C"] / c0, "cstar_wd175": t[175]["C"] / c0, "cstar_wd185": t[185]["C"] / c0,
                     "cstar_field_geomean": geo[i], "cstar_field_min": lo[i], "cstar_field_max": hi[i]})
    assert band == read_json(os.path.join(root, M_STUDY, "results.json"))["field.band.runs"]
    checked = 0
    for sp, _ in SPECIES:
        mine = m_scores(ctrl, sp, ur, fx["reference.U.imposedAtMastElevation"])
        want = {k: fx[v] for k, v in m_fixture_keys(sp).items()}
        checked += same_all(mine, want, m_name(sp))
    print(f"fixture control {M_STEM}: {checked} scores reproduced from RS-WT_caseM.csv, RS-FO_caseM.csv and the fixture's probes")


def m_parity(fx):
    for sp, _ in SPECIES:
        mine = read_json(os.path.join(RESULTS, f"{m_name(sp)}.json"))
        for key in ("cstar", "control.turned180", "control.mirrored", "field.vsGeometricMean"):
            print(parity_line(f"{m_name(sp)} {key}", fx[m_fixture_keys(sp)[key]], mine[key]))
    for key in ("velocity.U", "velocity.V", "velocity.W", "velocity.magnitude", "k"):
        print(parity_line(f"{M_STEM} {key}", fx[key], read_json(os.path.join(RESULTS, f"{m_name('sct03')}.json"))[key]))
    print(parity_line("field: tunnel as a model of the field's geometric mean", fx["field.tunnel180AsModelOfFieldGeometricMean"],
                      read_json(os.path.join(RESULTS, f"{m_name('sct03')}.json"))["field.tunnelAsModelOfGeometricMean"]))


# ----------------------------------------------------------------------------- snapshots, checks

root = validation_root(F_STUDY, M_STUDY)
if root:
    f_fx = read_json(os.path.join(root, F_STUDY, "results.json"))
    m_fx = read_json(os.path.join(root, M_STUDY, "results.json"))
    f_control(root, f_fx)
    m_control(root, m_fx)
    f_snapshot(root)
    m_snapshot(root)
    f_parity(f_fx)
    m_parity(m_fx)

f_pairs = read_pairs(os.path.join(RESULTS, f"{F_STEM}_pairs.csv"))
f_res = {fr: read_json(os.path.join(RESULTS, f"{F_STEM}_{fr}.json")) for fr in F_FRAMES}
f_by_frame = {fr: [p for p in f_pairs if p["frame"] == fr] for fr in F_FRAMES}
for fr in F_FRAMES:
    assert len(f_by_frame[fr]) == 46, fr
    check_snapshot(os.path.join(RESULTS, f"{F_STEM}_{fr}.json"), f_scores(f_by_frame[fr], f_res[fr]["U500"]))
m_pairs = read_pairs(os.path.join(RESULTS, f"{M_STEM}_pairs.csv"))
assert len(m_pairs) == 15
m_res = {sp: read_json(os.path.join(RESULTS, f"{m_name(sp)}.json")) for sp, _ in SPECIES}
for sp, _ in SPECIES:
    check_snapshot(os.path.join(RESULTS, f"{m_name(sp)}.json"), m_scores(m_pairs, sp, m_res[sp]["referenceSpeed.solvedAtMast"], m_res[sp]["reference.U.imposedAtMastElevation"]))


# ----------------------------------------------------------------------------- geometry outlines

def outlines(stl, project):
    """The plan-view outline of an ASCII STL: the vertical facets (walls) project to line segments; `project` maps (x, y) of the file's frame to the drawing's.
    The base slab that closes the terrain (its skirt lies below z = -0.5 m) is not a wall and is left out."""
    segs, v = set(), []
    with io.open(stl, encoding="utf-8") as f:
        for line in f:
            t = line.split()
            if t and t[0] == "vertex":
                v.append((float(t[1]), float(t[2]), float(t[3])))
                if len(v) == 3:
                    (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = v
                    if min(z1, z2, z3) > -0.5 and abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) < 1e-6:        # a vertical facet: its plan projection is a segment (or a point)
                        pts = sorted({(round(a, 2), round(b, 2)) for a, b, _ in v})
                        if len(pts) == 2:
                            segs.add((pts[0], pts[1]))
                    v = []
    return [(project(*a), project(*b)) for a, b in sorted(segs)]


# ----------------------------------------------------------------------------- figure: Case F, agreement
style.apply()
F_LABEL = {"literal": "Published z (STL frame)", "agl": "STL ground + instrument height"}
F_PANELS = [("Tunnel, 9 m plane", "tunnel.9m"), ("Tunnel, 5, 9 and 20 m", "tunnel.all"), ("Field observations", "field")]


def f_colours(sel):
    """The layout group of each pair: the tunnel's plane by its published z, the field's cup anemometer (layout.py)."""
    return layout.grouped_colours("F", [{"x": p["x"], "y": p["y"], "z": p["z_published"], "instrument": "cup_anemometer" if p["source"] == "field" else "thermistor"} for p in sel])


hi = 1.1 * max(max(p["observed"], p["Umag_model"], p["rms_model"]) for p in f_pairs)
fig, axs = uplt.subplots(nrows=2, ncols=3, refwidth=2.2, refaspect=1, share=False, wspace=4.0, hspace=3.4)
for r, fr in enumerate(F_FRAMES):
    tun = [p for p in f_by_frame[fr] if p["source"] == "tunnel"]
    fld = [p for p in f_by_frame[fr] if p["source"] == "field"]
    for c, (title, key) in enumerate(F_PANELS):
        ax = axs[r, c]
        style.one_to_one(ax, 0, hi)
        if key == "tunnel.9m":
            sel = [p for p in tun if p["plane_m"] == 9]
        elif key == "tunnel.all":
            sel = [p for h in F_PLANES for p in tun if p["plane_m"] == h]
        else:
            sel = fld
            ax.errorbar(column(fld, "observed"), column(fld, "rms_model"), xerr=column(fld, "observed_sd"), fmt="none", ecolor=style.REFERENCE, elinewidth=0.6, capsize=0, zorder=2)
        colours = f_colours(sel)
        ax.scatter(column(sel, "observed"), column(sel, "Umag_model"), s=22, facecolor="none", edgecolor=colours, linewidth=0.8, alpha=0.9, zorder=2)
        ax.scatter(column(sel, "observed"), column(sel, "rms_model"), s=22, color=colours, edgecolor=style.SURFACE, linewidth=0.4, zorder=3)
        m = f_res[fr][f"{key}.rms" if key != "field" else "field.rms"]
        style.stats(ax, stats_text(m), loc=(0.05, 0.80))
        ax.format(xlim=(0, hi), ylim=(0, hi), title=title if r == 0 else None, xlabel="Observed U/U(500 m) [–]" if r == 1 else None, ylabel="Eddy3D [–]" if c == 0 else None)
legend = layout.legend_rows("F", [style.marker(style.REFERENCE, "Eddy3D √(|U|²+2k)"), style.marker(style.REFERENCE, "Eddy3D |U|", filled=False),
                                  style.line(style.REFERENCE, "field σ of the 10-min means", lw=0.8), style.line(style.REFERENCE, "1:1", lw=1.0),
                                  style.line(style.REFERENCE, "factor of two", lw=0.8, ls=":")])
style.finish(fig, "AIJ UWE Case F — Eddy3D (OpenFOAM 12, realizable k-ε), wind from NNW, vs wind tunnel and field, speed over U(500 m)",
             handles=legend[0], ncols=legend[1],
             leftlabels=[F_LABEL[fr] for fr in F_FRAMES])
style.save(fig, "case-f-openfoam-agreement.png")

# ----------------------------------------------------------------------------- figure: Case F, bias map
fig2, axs2 = uplt.subplots(nrows=1, ncols=2, refwidth=3.6, refaspect=1, share=True)
f_segs = outlines(os.path.join(REPO, "clean", "cases", "F", "geometry.stl"), lambda x, y: (x, y))
for i, fr in enumerate(F_FRAMES):
    ax = axs2[i]
    ax.add_collection(LineCollection(f_segs, colors=style.FOOTPRINT_FOCUS, linewidths=0.25, zorder=1))
    nine = sorted((p for p in f_by_frame[fr] if p["source"] == "tunnel" and p["plane_m"] == 9), key=lambda p: p["point_id"])
    sc = style.bias_scatter(ax, [p["x"] for p in nine], [p["y"] for p in nine], [p["rms_model"] for p in nine], [p["observed"] for p in nine], s=44)
    for p in nine:
        ax.text(p["x"] + 14, p["y"] + 14, f"{int(p['point_id'])}", fontsize=7.5, color=style.INK, zorder=5)
    d = np.array([0.382683, -0.923880])                    # wind from NNW blows toward SSE (clean/directions.csv: flow_dir)
    tail = np.array([-420.0, 420.0])
    style.arrow(ax, tail, tail + 130 * d)
    ax.format(xlim=(-560, 560), ylim=(-560, 560), aspect="equal", title=F_LABEL[fr])
style.outer_ticks(axs2, 1, 2)
style.bias_colorbar(fig2, sc, "Eddy3D √(|U|²+2k) / tunnel")
style.finish(fig2, "AIJ UWE Case F — where the model is slow (red) or fast (blue), 9 m plane, wind from NNW", xlabel="x, east [m]", ylabel="y, north [m]")
style.save(fig2, "case-f-openfoam-bias-map.png")

# ----------------------------------------------------------------------------- figure: Case M, agreement
M_PANELS = [("U/U$_R$", "U_meas", "U_model", "velocity.U", False), ("V/U$_R$", "V_meas", "V_model", "velocity.V", False), ("W/U$_R$", "W_meas", "W_model", "velocity.W", False),
            ("k/U$_R^2$", "k_meas", "k_model", "k", False)] + \
           [(f"c* = C/c$_0$, {lab}", "cstar_meas", f"cstar_{sp}", f"cstar.c_{sp}", True) for sp, lab in SPECIES]
fig3, axs3 = uplt.subplots(nrows=2, ncols=4, refwidth=1.9, refaspect=1, share=False, wspace=4.2, hspace=3.4)
m_colours = np.array(layout.grouped_colours("M", m_pairs), dtype=object)       # the distance of each point from the release point (layout.py)
for i, (label, mk, pk, key, log) in enumerate(M_PANELS):
    ax = axs3[i // 4, i % 4]
    res = m_res["sct03"] if not log else m_res[key.split("_")[-1]]
    score = res[key] if not log else res["cstar"]
    shown = panel(ax, column(m_pairs, mk), column(m_pairs, pk), m_colours, log=log, xlab="Tunnel [–]" if i // 4 == 1 else None, ylab="Eddy3D [–]" if i % 4 == 0 else None, decades=8)
    ax.format(title=label)
    style.stats(ax, stats_text(score, shown if log else None), loc=(0.40, 0.36) if log else (0.05, 0.80))
ax = axs3[1, 3]
c180 = column(m_pairs, "cstar_meas")
for col, lab, hollow in (("cstar_wd175", "WD 175", False), ("cstar_wd185", "WD 185", True)):
    o, p = c180, column(m_pairs, col)
    keep = (o > 0) & (p > 0)
    style.one_to_one(ax, 1e-3, 5)
    ax.scatter(o[keep], p[keep], s=14, facecolor="none" if hollow else list(m_colours[keep]), edgecolor=list(m_colours[keep]) if hollow else style.SURFACE,
               linewidth=0.8 if hollow else 0.25, alpha=0.9, zorder=3)
ax.format(xscale="log", yscale="log", xlim=(1e-3, 5), ylim=(1e-3, 5), title="Tunnel WD 175, 185 vs 180", xlabel="Tunnel, WD 180 [–]")
style.stats(ax, f"FAC2 {m_res['sct03']['control.tunnelWD175AsModelOfWD180']['Fac2']:.2f} (WD 175)\nFAC2 {m_res['sct03']['control.tunnelWD185AsModelOfWD180']['Fac2']:.2f} (WD 185)", loc=(0.05, 0.80))
legend = layout.legend_rows("M", [style.marker(style.REFERENCE, "Eddy3D at the measured points"), style.marker(style.REFERENCE, "tunnel WD 175"), style.marker(style.REFERENCE, "tunnel WD 185", filled=False),
                                  style.line(style.REFERENCE, "1:1", lw=1.0), style.line(style.REFERENCE, "factor of two", lw=0.8, ls=":")])
style.finish(fig3, "AIJ UWE Case M — Eddy3D (OpenFOAM 12, realizable k-ε) vs wind tunnel, WD 180, 15 points 3 m above the ground",
             handles=legend[0], ncols=legend[1])
style.save(fig3, "case-m-openfoam-agreement.png")

# ----------------------------------------------------------------------------- figure: Case M, plan
fig4, axs4 = uplt.subplots(nrows=1, ncols=4, refwidth=2.2, refaspect=1, share=True, wspace=1.0)
east_north = lambda x, y: (-y, x)  # noqa: E731  the release's (x north, y west) as a map: x east, y north
segs = outlines(os.path.join(REPO, "clean", "cases", "M", "geometry.stl"), east_north)
SOURCE = (-0.1369 * M_SCALE, 0.1033 * M_SCALE)                        # LC_caseM.csv Gas_source, the release's frame in model metres, full scale
MAST = (-0.1115 * M_SCALE, -0.0062 * M_SCALE)
panels = [("Tunnel", "cstar_meas")] + [(lab, f"cstar_{sp}") for sp, lab in SPECIES]
LOGLO, LOGHI = -3.0, 0.5
for i, (title, key) in enumerate(panels):
    ax = axs4[i]
    ax.add_collection(LineCollection(segs, colors=style.FOOTPRINT_FOCUS, linewidths=0.25, zorder=1))
    pts = [east_north(p["x"], p["y"]) for p in m_pairs]
    v = column(m_pairs, key)
    lv = np.log10(np.where(v > 0, v, np.nan))
    on = np.isfinite(lv) & (lv >= LOGLO)
    sc = ax.scatter([pts[j][0] for j in range(15) if on[j]], [pts[j][1] for j in range(15) if on[j]], c=lv[on], cmap=style.SEQUENTIAL, vmin=LOGLO, vmax=LOGHI, s=46,
                    edgecolor=style.REFERENCE, linewidth=0.4, zorder=3)
    ax.scatter([pts[j][0] for j in range(15) if not on[j]], [pts[j][1] for j in range(15) if not on[j]], s=46, facecolor="none", edgecolor=style.INK, linewidth=0.8, zorder=3)
    ax.scatter([-SOURCE[1]], [SOURCE[0]], marker="*", s=90, facecolor=style.SURFACE, edgecolor=style.INK, linewidth=0.9, zorder=4)
    ax.scatter([-MAST[1]], [MAST[0]], marker="s", s=34, facecolor=style.SURFACE, edgecolor=style.INK, linewidth=0.9, zorder=4)
    style.arrow(ax, np.array([-330.0, -250.0]), np.array([-330.0, -170.0]))
    ax.format(xlim=(-360, 360), ylim=(-300, 320), aspect="equal", title=title)
style.outer_ticks(axs4, 1, 4)
fig4.colorbar(sc, loc="b", ticks=[-3, -2, -1, 0], length=0.5, label="log$_{\\mathrm{10}}$ c* = C/c$_0$ [–]  (open: below 10$^{-3}$ or zero)")
style.finish(fig4, "AIJ UWE Case M — the tracer at the 15 points, wind tunnel and Eddy3D at three turbulent Schmidt numbers, WD 180", xlabel="x, east [m]", ylabel="y, north [m]",
             handles=[style.marker(style.REFERENCE, "points 3 m above the ground"),
                      Line2D([], [], ls="none", marker="*", markersize=10, markerfacecolor=style.SURFACE, markeredgecolor=style.INK, label="gas source"),
                      Line2D([], [], ls="none", marker="s", markersize=6, markerfacecolor=style.SURFACE, markeredgecolor=style.INK, label="reference mast")])
style.save(fig4, "case-m-openfoam-plan.png")
