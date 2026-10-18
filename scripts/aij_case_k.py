"""Case K facts and geometry for scripts/aijdata.py (the cleaned table itself is clean/cases/K/points.csv).

aijdata.py imports CASE, DEFAULT_CONFIGURATION, RENDER_CAPTIONS, geometry and load_approach_flow from here; the
numbers that the cleaning measured (inflow fit) are read from clean/manifest.json so they cannot drift from it.
"""
from __future__ import annotations

import io
import json
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
H, PITCH, ROWS, COLS, X_FIRST, Y_FIRST = 0.06, 0.12, 9, 9, -0.36, -0.51


def _manifest_case(case):
    try:
        with io.open(os.path.join(REPO, "clean", "manifest.json"), encoding="utf-8") as f:
            return json.load(f)["cases"][case]
    except (OSError, KeyError, ValueError):
        return {}


def _inflow_fit(case):
    inf = _manifest_case(case).get("inflow") or {}
    ll = inf.get("log_law") or {}
    if not ll:
        return {"method": "log law, kappa = 0.41, least squares on the case's approach-flow file (clean/manifest.json, built by clean/build.py)"}
    return {"method": inf.get("method"), "u_star_m_s": ll.get("u_star_m_s"), "z0_mm": ll.get("z0_mm"), "U_H_measured_m_s": inf.get("U_H_m_s"), "U_H_stated_m_s": inf.get("U_H_stated_m_s"),
            "log_law_error_at_H": f"{100 * ll.get('error_at_H_rel', 0):+.1f} %", "log_law_rms_residual": f"{100 * ll.get('rms_residual_rel', 0):.1f} %",
            "note": inf.get("note")}


CASE = {
    "id": "K", "slug": "case-k", "title": "Case K — 9 x 9 cube array, point source",
    "short": "9 x 9 array of 0.06 m cubes with a tracer point source on the floor between rows 2 and 3: velocity and tracer concentration at 203 points in the streets and over the first rows.",
    "folder": "raw/cases/case-k",
    "reference_file": "raw/cases/case-k/RS_caseK.csv",
    "approach_flow_file": "raw/cases/case-k/AF_caseK.csv",
    "readme": "raw/cases/case-k/readme_caseK.md",
    "render": "validation/figures/geometry/case-k.png",  # the default configuration; see render_file
    "configuration": {
        "array": "9 rows (along x) by 9 columns (across y) of cubes, H = 0.06 m, pitch 0.12 m (street width = H, plan area ratio 25 %); the pitch is read from the MP drawings",
        "H_m": 0.06, "pitch_m": 0.12, "cubes": 81,
        "Re_H": 9800,
        "U_H_m_s": 2.33,
        "U_H_note": "stated by the readme and data paper; the approach-flow file (Case H's) gives 2.24 m/s at z = 0.06 m",
        "wind_directions_deg": [0],
        "measurement_planes": ["y/H = 0, +-1, +-2, +-3 (z up to 0.07 m)", "five heights from 4 mm to 70 mm; the three upper heights only on y = 0 and +-H"],
        "points": 203,
        "source": "5 mm floor outlet at (-0.15, 0, 0), between rows 2 and 3 on the centre line; 100 % ethylene, 3.6e-6 m3/s",
        "concentration_normalisation": "c0 = q / (U_H H^2) = 429.18 ppm with the cube's H and U_H; the legacy workbook uses H = 0.2 m and UH = 4.94 m/s instead (C0 = 18.218 ppm), see known issues",
        "instrument": "split-fibre hot wire (velocity), high-speed hydrocarbon analyser (concentration), 1000 Hz with a 200 Hz low-pass filter, 60 s per point",
        "tunnel": "Eiffel-type wind tunnel, Tokyo Polytechnic University (Atsugi); 1.2 m wide, 1.0 m high",
        "scale_note": "model scale; the sources state no model:full scale ratio",
    },
    "quantities": ["U", "V", "W", "uu", "vv", "ww", "k", "C", "c_rms", "concentration_ratio"],
    "units": {"length": "m (model scale)", "velocity": "m/s", "variance": "m^2/s^2", "k": "m^2/s^2", "concentration": "ppm of the released ethylene"},
    "frame": {
        "origin": "bottom centre of the windward wall of the 4th row of the central column: x = 0 is that wall, y = 0 the centre line of the central column",
        "x": "+x streamwise (the wind blows toward +x); row k spans x in [0.12 (k-4), 0.12 (k-4) + 0.06], so the array spans x in [-0.36, 0.66]",
        "y": "+y lateral; column centres at y = 0, +-0.12, ... +-0.48 (the array spans y in [-0.51, 0.51])",
        "z": "+z up; cube tops at z = 0.06",
        "lateral_sign_applied": 1,
        "coordinate_scale_applied": 1.0,
    },
    "people": {
        "data_collectors": ["Ryuichiro Yoshie (Tokyo Polytechnic University)", "Takumi Tachibana (Wind Engineering Institute)"],
        "editors_distributors": ["Yoshihide Tominaga (Niigata Institute of Technology)", "Hideki Kikumoto (The University of Tokyo)", "Tsubasa Okaze (Institute of Science Tokyo)"],
        "contact": "Ryuichiro Yoshie <yoshie@arch.t-kougei.ac.jp>",
    },
    "doi": "10.5281/zenodo.15448050",
    "citation_requested": "Yoshie, R. (2016). Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer. Adv Environ Wind Eng, 167-196. https://doi.org/10.1007/978-4-431-55912-2_9",
    "inflow_fit": _inflow_fit("K"),
    "known_issues": [
        "The legacy workbook normalises with H = 0.2 m (Case H's building), UH = 4.94009 m/s and C0 = 18.218 ppm, not the cube's H = 0.06 m and U_H = 2.33 m/s; its normalised columns are 23.6 times smaller in concentration. The API's concentration_ratio uses the cube's c0 = 429.18 ppm.",
        "RS_caseK.csv has no point numbers; point_id is the row order of the file.",
        "The published CSV is the workbook rounded (3 decimals, concentrations 2), with k recomputed from the rounded rms values; the table is rebuilt from the workbook.",
        "AF_caseK.csv is Case H's approach-flow file, row for row (x = -0.493 m, tabulated for a 0.2 m building); it gives 2.24 m/s at z = 0.06 m against the stated U_H = 2.33.",
        "The lateral velocity V is dominated by a cross-flow offset (about 0.06 m/s, also in the empty tunnel); the +y and -y halves cannot confirm its sign.",
        "The mean concentration is not mirror-symmetric (the +y and -y values of one point differ by 44 % on average), so the mirror pairs are not a repeatability estimate; velocity and k are (3 % and 5 %).",
        "The workbook's <usc> / sigma_usc ('velocity magnitude', never below |U|) is not in the table.",
        "Data paper section 3.11 describes the measurements as 'approximately 30 points at eight heights downwind of the line source'; Case K has 203 points at five heights and a point source.",
        "Workbook units: x and y in millimetres in both data sheets; z in millimetres in 'Measurement data' but metres in 'Inflow'.",
    ],
}

DEFAULT_CONFIGURATION = "default"

RENDER_CAPTIONS = {
    ("K", "default"): "9 x 9 array of 0.06 m cubes on a 0.12 m pitch (model scale); the orange ring marks the floor tracer source between rows 2 and 3; the wind blows along +x.",
}


def _cubes():
    boxes = []
    for i in range(ROWS):
        for j in range(COLS):
            x0, y0 = X_FIRST + PITCH * i, Y_FIRST + PITCH * j
            boxes.append({"min": [round(x0, 9), round(y0, 9), 0.0], "max": [round(x0 + H, 9), round(y0 + H, 9), H]})
    return boxes


def geometry(case):
    """[(configuration, triangles, boxes, note)]: the 81 cubes."""
    import aijdata as D
    boxes = _cubes()
    return [("default", D.tris_of_boxes(boxes), boxes, "generated: 81 cubes of 0.06 m on a 0.12 m pitch, 9 rows from x = -0.36 m and 9 columns centred on y = 0 (MP-y_caseK.png, MP-z_caseK.png); the pitch is bounded by the measurement points (clean/checks.json)")]


def load_approach_flow(case):
    """Rows of {z, U, k, u_rms} of AF_caseK.csv (x = -0.493 m, 17 heights; Case H's profile) and the file they come from."""
    import aijdata as D
    header, rows = D._read_csv(os.path.join(REPO, CASE["approach_flow_file"]))
    idx = {n: i for i, n in enumerate(header)}
    return [{"z": D._f(r[idx["z"]]), "U": D._f(r[idx["U"]]), "k": D._f(r[idx["k"]]), "u_rms": D._f(r[idx["u_rms"]])} for r in rows], CASE["approach_flow_file"]
