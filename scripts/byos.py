"""Bring your own solver: what scripts/build_api.py serves so that anyone can score a solver against the benchmark.

- cases/{id}/probes.csv: the published points to probe (the key columns a scored file must carry, the coordinates, and `scored_as`)
- cases/{id}.json `scoring`: the reference speed and constants validation/score_submissions.py scores with
- cases/{id}.json `inflow`: the benchmark's approach-flow data, and the inlet this repository recommends (a log law from
  `inflow_fit` with k and epsilon from the standard ABL relations); what Eddy3D's own runs used is quoted from their snapshots
- cases/{id}/inflow_openfoam.txt: the recommended inlet as OpenFOAM 12 files (0/U, 0/k, 0/epsilon, 0/nut, system/probes) in one text
- submissions/: every folder under submissions/ at the repository root, scored here in-tree by validation/score_submissions.py, its
  results written to validation/results/submissions/<slug>/ and served as submissions.json and submissions/<slug>.json

The scoring code is the script's, so a submission scores here exactly as `python validation/score_submissions.py <folder>` scores it.
"""
from __future__ import annotations

import io
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, "validation"))
import score_submissions as SC  # noqa: E402

KAPPA, CMU = 0.41, 0.09
SUBMISSIONS_DIR = os.path.join(REPO, "submissions")
SUBMISSION_RESULTS = os.path.join(REPO, "validation", "results", "submissions")

CONVENTIONS = SC.CONVENTIONS
U_REF = SC.U_REF
# How a wind direction becomes a flow vector in the case's frame (cases/{id}.json `frame`).
FLOW_DIRECTION = {
    **{c: "along_x" for c in "ABCDHIJKL"},
    "E": "geographic_x_east_y_north", "F": "geographic_x_east_y_north", "G": "along_x", "M": "x_north_y_west",
}
FLOW_DIRECTION_MEANING = {
    "along_x": "+x is along the wind at WD = 0: flowDir (1 0 0); another WD rotates it about +z by the case's rotation sense (frame.wind_direction_rotation)",
    "geographic_x_east_y_north": "meteorological FROM-direction theta, clockwise from north: flowDir (-sin theta, -cos theta, 0)",
    "x_north_y_west": "meteorological FROM-direction theta: flowDir (-cos theta, +sin theta, 0)",
}


def scoring_block(case, metric_meaning):
    return {**SC.scoring_block(case), "metric_meaning": metric_meaning}


def probes_rows(case, rows, scoring):
    """One row per measured row of the point table: the keys, the coordinates and what the row is scored as."""
    out = []
    for r in rows:
        fam = SC.families(SC.measured_values(r, scoring))
        if not fam:
            continue
        out.append([r["point_id"], r.get("config"), r.get("campaign"), r.get("instrument"), r.get("run") or None, r.get("wind_direction_deg"),
                    r["x"], r["y"], r["z"], "+".join(fam)])
    return out


PROBES_COLUMNS = ["point_id", "config", "campaign", "instrument", "run", "wind_direction_deg", "x", "y", "z", "scored_as"]
PROBES_COLUMNS_MEANING = ("the key columns of a scored file (point_id with config, campaign, instrument, run and wind_direction_deg as the case has them), "
                          "x, y, z in m (case frame), and scored_as: the families the row is scored in (vector, k, thermistor_bracket, concentration, theta, joined by +)")


def _log_law_fit(fit):
    """(u*, z0 in m, how) from a case's inflow_fit; None when the case has no log-law fit."""
    if not fit:
        return None
    if "u_star_m_s" in fit and "z0_mm" in fit:
        return fit["u_star_m_s"], fit["z0_mm"] / 1000.0, fit["method"]
    if fit.get("windows"):
        w = fit["windows"][0]
        return w["u_star_m_s"], w["z0_mm"] / 1000.0, f"{fit['method']}; the first window, {w.get('z_range_m') or w.get('z_range')}"
    return None


def inflow_block(case, meta, af_rows, af_cols, af_units, af_download, run_facts):
    """The inlet contract of one case: the benchmark's data, this repository's recommendation, and what Eddy3D's runs used."""
    fit = meta.get("inflow_fit") or {}
    ll = _log_law_fit(fit)
    h = (meta.get("configuration") or {}).get("H_m") or {"C": 0.2}.get(case)   # Case C: U_H is U(z = D = 0.20 m) (its U_H_note)
    u_ref = U_REF[case][0]
    rec = None
    if ll:
        u_star, z0, how = ll
        rec = {
            "status": "RECOMMENDED by this repository (not part of the benchmark): a log-law inlet fitted to the case's own approach-flow file, "
                      "with k and epsilon from the standard neutral ABL relations. Any inlet may be submitted; say which in submission.yaml",
            "profile": "U(z) = u*/kappa ln((z + z0)/z0); k = u*^2 / sqrt(Cmu); epsilon = u*^3 / (kappa (z + z0))",
            "u_star_m_s": u_star, "z0_m": z0, "kappa": KAPPA, "Cmu": CMU,
            "k_m2_s2": u_star * u_star / math.sqrt(CMU),
            "fit": how,
            "U_ref_m_s": u_ref, "z_ref_m": h,
            "openfoam": "atmBoundaryLayerInletVelocity / atmBoundaryLayerInletK / atmBoundaryLayerInletEpsilon with Uref, Zref, z0 and d = 0; "
                        "nutkAtmRoughWallFunction with the same z0 on the ground: cases/{id}/inflow_openfoam.txt holds them",
        }
    else:
        rec = {
            "status": "RECOMMENDED by this repository (not part of the benchmark): no log law fits this case (inflow_fit says why); "
                      "use the measured approach-flow profile as a tabulated inlet (approach_flow.csv). Any inlet may be submitted; say which in submission.yaml",
            "profile": "U(z) and, where published, k(z) tabulated from approach_flow.csv; epsilon = Cmu^0.5 k dU/dz where k is published, else from your own closure",
            "kappa": KAPPA, "Cmu": CMU, "U_ref_m_s": u_ref, "z_ref_m": h,
            "openfoam": "fixedProfile (OpenFOAM.org) with the table, or timeVaryingMappedFixedValue: cases/{id}/inflow_openfoam.txt holds the table",
        }
    return {
        "benchmark_data": {"approach_flow_csv": af_download, "columns": af_cols, "units": af_units, "rows": len(af_rows),
                           "fit": fit, "note": "the measured profile and the fit of it are the benchmark's data as cleaned here; everything under `recommended` is a choice"},
        "recommended": rec,
        "flow_direction": {"convention": FLOW_DIRECTION[case], "meaning": FLOW_DIRECTION_MEANING[FLOW_DIRECTION[case]],
                           "wind_directions_deg": sorted({float(w) for w in (meta.get("configuration") or {}).get("wind_directions_deg", []) or []}) or None},
        "eddy3d_runs": run_facts,
        "domain": "the extents, blockage and cell sizes of Eddy3D's domains are not in its snapshots and are not stated here; mesh.cells and the scale are, where the snapshot has them",
    }


def eddy3d_run_facts(runs, results_dir):
    """What each snapshot of a case says about its inlet, scale, roughness and mesh: quoted, keys as the fixture wrote them."""
    keys = ("inflow", "inlet", "scale", "z0.model.m", "z0.full.m", "inflow.z0.fullScaleM", "inflow.speedAtHeight.mPerS", "inflow.height.fullScaleM",
            "mesh.cells", "airCells", "latticeCells", "cellsPerHeight", "froudeScale", "Uh", "UhImposed", "UhModel", "UhTunnel", "sceneUh")
    out = []
    for r in runs:
        with io.open(os.path.join(results_dir, r["results"]), encoding="utf-8") as f:
            res = json.load(f)
        facts = {k: res[k] for k in keys if k in res}
        out.append({"run_id": r["run_id"], "engine": r["engine"], **facts})
    return out


# ----------------------------------------------------------------------------- submissions

def submissions():
    """[(slug, meta, {case: rows})] for every folder under submissions/, validated the way `aij submit-check` validates it."""
    out = []
    if not os.path.isdir(SUBMISSIONS_DIR):
        return out
    for slug in sorted(os.listdir(SUBMISSIONS_DIR)):
        folder = os.path.join(SUBMISSIONS_DIR, slug)
        if not os.path.isdir(folder) or slug.startswith("."):
            continue
        problems, meta, cases = SC.check_folder(folder)
        if problems:
            raise SystemExit(f"submissions/{slug}: " + "; ".join(problems))
        out.append((slug, meta, cases))
    return out


def score_submission(slug, points_rows):
    """(meta, {case: result}) scored in-tree by validation/score_submissions.py; the results go to validation/results/submissions/<slug>/<case>.json."""
    return SC.score_folder(os.path.join(SUBMISSIONS_DIR, slug), os.path.join(SUBMISSION_RESULTS, slug), points_rows)


def stale_submission_results(slugs):
    """validation/results/submissions/ folders that no submission produces any more."""
    if not os.path.isdir(SUBMISSION_RESULTS):
        return []
    return sorted(n for n in os.listdir(SUBMISSION_RESULTS) if os.path.isdir(os.path.join(SUBMISSION_RESULTS, n)) and n not in slugs)




# ----------------------------------------------------------------------------- the recommended inlet as OpenFOAM files

OF_HEADER = """/*--------------------------------*- C++ -*----------------------------------*\\
  cases/{case}/inflow_openfoam.txt of the AIJ UWE API (release {release}), written by scripts/build_api.py; the walk: {site}/byos/
  {status}
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    format      ascii;
    class       {cls};
    object      {obj};
}}
"""
V2XXX = ("OpenFOAM 12 (openfoam.org) syntax. ESI OpenFOAM v2xxx: the three atmBoundaryLayerInlet* conditions and nutkAtmRoughWallFunction take the "
         "same entries there; fixedProfile is openfoam.org only (use timeVaryingMappedFixedValue or codedFixedValue).")


def flow_dir(convention, wd_deg):
    th = math.radians(wd_deg)
    if convention == "along_x":
        return (1.0, 0.0, 0.0)
    if convention == "geographic_x_east_y_north":
        return (-math.sin(th), -math.cos(th), 0.0)
    if convention == "x_north_y_west":
        return (-math.cos(th), math.sin(th), 0.0)
    raise ValueError(convention)


def _vec(v):
    return "(" + " ".join(f"{x:.6g}" if abs(x) > 1e-12 else "0" for x in v) + ")"


def _patches(kind):
    """The other patches, placeholders for the user's names."""
    if kind == "U":
        return ("    outlet          { type inletOutlet; inletValue uniform (0 0 0); value $internalField; }\n"
                "    ground          { type noSlip; }\n    buildings       { type noSlip; }\n    top             { type slip; }\n    sides           { type slip; }\n}\n")
    wf = "kqRWallFunction" if kind == "k" else "epsilonWallFunction"
    return ("    outlet          { type inletOutlet; inletValue $internalField; value $internalField; }\n"
            f"    ground          {{ type {wf}; value $internalField; }}\n    buildings       {{ type {wf}; value $internalField; }}\n"
            "    top             { type slip; }\n    sides           { type slip; }\n}\n")


def inflow_openfoam_text(case, meta, af_rows, af_cols, probes, site="https://aij.eddy3d.com", release=""):
    """One text holding 0/U, 0/k, 0/epsilon, 0/nut and system/probes for the case's first wind direction, each after a `==== <path>` line.

    The inlet is the recommendation of inflow_block (a log law with k and epsilon from the ABL relations, or the tabulated profile);
    the probes are the benchmark's points. What is data and what is a choice is said in each file's header."""
    fit = meta.get("inflow_fit") or {}
    ll = _log_law_fit(fit)
    h = (meta.get("configuration") or {}).get("H_m") or {"C": 0.2}.get(case)
    u_ref = U_REF[case][0]
    conv = FLOW_DIRECTION[case]
    wds = sorted({float(w) for w in (meta.get("configuration") or {}).get("wind_directions_deg", []) or []}) or [0.0]
    fd = flow_dir(conv, wds[0])

    def file(status, cls, obj, body):
        return OF_HEADER.format(site=site, case=case, release=release, status=status, cls=cls, obj=obj) + body

    files = {}
    direction = (f"flowDir is the case's wind direction {wds[0]:g} deg by the convention {conv} (cases/{case}.json inflow.flow_direction); "
                 f"the case has {len(wds)} direction(s): rotate flowDir for another" if len(wds) > 1 else
                 f"flowDir is the case's wind direction by the convention {conv} (cases/{case}.json inflow.flow_direction)")
    if ll:
        u_star, z0, how = ll
        note = (f"RECOMMENDED inlet (this repository's choice, not the benchmark's): U(z) = u*/kappa ln((z + z0)/z0) with u* = {u_star} m/s, z0 = {z0:.6g} m "
                f"fitted to the measured profile ({how}); k = u*^2/sqrt(Cmu); epsilon = u*^3/(kappa (z + z0)). {direction}.\n  {V2XXX}")
        abl = (f"        flowDir         {_vec(fd)};\n        zDir            (0 0 1);\n        Uref            {u_ref};\n        Zref            {h};\n"
               f"        z0              uniform {z0:.6g};\n        d               uniform 0;\n        kappa           {KAPPA};\n        Cmu             {CMU};\n")
        k = u_star * u_star / math.sqrt(CMU)
        eps = u_star ** 3 / (KAPPA * (h + z0))
        files["0/U"] = file(note, "volVectorField", "U", f"dimensions      [0 1 -1 0 0 0 0];\ninternalField   uniform {_vec(tuple(u_ref * x for x in fd))};\nboundaryField\n{{\n    inlet\n    {{\n"
                            f"        type            atmBoundaryLayerInletVelocity;\n{abl}        value           $internalField;\n    }}\n" + _patches("U"))
        files["0/k"] = file(note, "volScalarField", "k", f"dimensions      [0 2 -2 0 0 0 0];\ninternalField   uniform {k:.6g};\nboundaryField\n{{\n    inlet\n    {{\n"
                            f"        type            atmBoundaryLayerInletK;\n{abl}        value           $internalField;\n    }}\n" + _patches("k"))
        files["0/epsilon"] = file(note, "volScalarField", "epsilon", f"dimensions      [0 2 -3 0 0 0 0];\ninternalField   uniform {eps:.6g};\nboundaryField\n{{\n    inlet\n    {{\n"
                                  f"        type            atmBoundaryLayerInletEpsilon;\n{abl}        value           $internalField;\n    }}\n" + _patches("epsilon"))
        files["0/nut"] = file("RECOMMENDED ground roughness: the same z0 as the inlet, so the profile holds along an empty fetch", "volScalarField", "nut",
                              "dimensions      [0 2 -1 0 0 0 0];\ninternalField   uniform 0;\nboundaryField\n{\n    inlet           { type calculated; value uniform 0; }\n"
                              "    outlet          { type calculated; value uniform 0; }\n    ground\n    {\n        type            nutkAtmRoughWallFunction;\n"
                              f"        z0              uniform {z0:.6g};\n        value           uniform 0;\n    }}\n"
                              "    buildings       { type nutkWallFunction; value uniform 0; }\n    top             { type calculated; value uniform 0; }\n"
                              "    sides           { type calculated; value uniform 0; }\n}\n")
    else:
        units = {c: {"z": "m", "U": "m/s", "k": "m^2/s^2", "u_rms": "m/s"}.get(c) for c in af_cols}
        units.update(meta.get("approach_flow_units", {}))
        note = (f"RECOMMENDED inlet (this repository's choice, not the benchmark's): the measured approach-flow profile (approach_flow.csv, the benchmark's data) "
                f"as a table; U is {units.get('U')}, z is {units.get('z')}. {direction}.\n  {V2XXX}")
        tab_u = "\n".join(f"            ({r['z']:g} {_vec(tuple(r['U'] * x for x in fd))})" for r in af_rows)
        files["0/U"] = file(note, "volVectorField", "U", f"dimensions      [0 1 -1 0 0 0 0];\ninternalField   uniform (0 0 0);\nboundaryField\n{{\n    inlet\n    {{\n"
                            f"        type            fixedProfile;\n        direction       (0 0 1);\n        origin          0;\n        profile         table\n        (\n{tab_u}\n        );\n    }}\n" + _patches("U"))
        ks = [r for r in af_rows if r.get("k") is not None]
        if ks:
            tab_k = "\n".join(f"            ({r['z']:g} {r['k']:g})" for r in ks)
            files["0/k"] = file(f"RECOMMENDED: the measured k as a table; k is {units.get('k')}", "volScalarField", "k",
                                f"dimensions      [0 2 -2 0 0 0 0];\ninternalField   uniform {ks[0]['k']:g};\nboundaryField\n{{\n    inlet\n    {{\n"
                                f"        type            fixedProfile;\n        direction       (0 0 1);\n        origin          0;\n        profile         table\n        (\n{tab_k}\n        );\n    }}\n" + _patches("k"))
            eps_rows = []   # epsilon = Cmu^0.5 k dU/dz (the relation Case E's workbook uses), central differences on the table: a recommendation
            for i, r in enumerate(ks):
                lo, hi = ks[max(i - 1, 0)], ks[min(i + 1, len(ks) - 1)]
                dudz = (hi["U"] - lo["U"]) / (hi["z"] - lo["z"]) if hi["z"] != lo["z"] else 0.0
                eps_rows.append((r["z"], max(math.sqrt(CMU) * r["k"] * abs(dudz), 1e-12)))
            tab_e = "\n".join(f"            ({z:g} {e:.6g})" for z, e in eps_rows)
            files["0/epsilon"] = file("RECOMMENDED: epsilon = Cmu^0.5 k dU/dz from the tabulated U and k (central differences)", "volScalarField", "epsilon",
                                      f"dimensions      [0 2 -3 0 0 0 0];\ninternalField   uniform {eps_rows[0][1]:.6g};\nboundaryField\n{{\n    inlet\n    {{\n"
                                      f"        type            fixedProfile;\n        direction       (0 0 1);\n        origin          0;\n        profile         table\n        (\n{tab_e}\n        );\n    }}\n" + _patches("epsilon"))
        else:
            files["0/k"] = file("the profile publishes no k: set k and epsilon from your own closure (no recommendation)", "volScalarField", "k",
                                "// no measured k for this case: see cases/{case}.json inflow\n")
    locs = "\n".join(f"        ({p[6]:g} {p[7]:g} {p[8]:g})   // point_id {p[0]}" + "".join(f", {c} {v}" for c, v in zip(("config", "campaign", "instrument", "run"), p[1:5]) if v)
                     + (f", WD {float(p[5]):g}" if p[5] is not None else "") for p in probes)
    files["system/probes"] = file(f"the benchmark's measurement points (cases/{case}/probes.csv, the data), in the case frame and units: include from controlDict functions",
                                  "dictionary", "probes",
                                  "probes\n{\n    type            probes;\n    libs            (\"libsampling.so\");\n    writeControl    writeTime;\n"
                                  "    fields          (U k epsilon);\n    probeLocations\n    (\n" + locs + "\n    );\n}\n")
    return "".join(f"==== {path}\n{text}\n" for path, text in files.items())
