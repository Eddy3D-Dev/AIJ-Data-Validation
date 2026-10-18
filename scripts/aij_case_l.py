"""Case L facts and geometry for scripts/aijdata.py (the cleaned table itself is clean/cases/L/points.csv).

aijdata.py imports CASE, DEFAULT_CONFIGURATION, RENDER_CAPTIONS, geometry and approach_flow from here; the
numbers that the cleaning measured (inflow fit) are read from clean/manifest.json so they cannot drift from it.
"""
from __future__ import annotations

import io
import json
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
H, PITCH, ROWS, COLS, X_FIRST, Y_FIRST = 0.06, 0.12, 14, 9, -0.96, -0.51


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
    return {"method": inf.get("method"), "u_star_m_s": ll.get("u_star_m_s"), "z0_mm": ll.get("z0_mm"), "U_H_measured_m_s": inf.get("U_H_m_s"),
            "log_law_error_at_H": f"{100 * ll.get('error_at_H_rel', 0):+.1f} %", "log_law_rms_residual": f"{100 * ll.get('rms_residual_rel', 0):.1f} %",
            "note": "derived during scoping, not published by AIJ; the boundary layer is unstably stratified, so a neutral log law is only a rough description"}


CASE = {
    "id": "L", "slug": "case-l", "title": "Case L — 9 x 14 cube array, line source, non-isothermal",
    "short": "14 rows by 9 columns of 0.06 m cubes with a tracer line source on the floor across the tunnel, in an unstably stratified boundary layer: velocity, temperature, concentration and their fluxes at 344 points in the streets and over the roofs.",
    "folder": "raw/cases/case-l",
    "reference_file": "raw/cases/case-l/RS_caseL.csv",
    "approach_flow_file": "raw/cases/case-l/AF_caseL.csv",
    "readme": "raw/cases/case-l/readme_caseL.md",
    "render": "validation/figures/geometry/case-l.png",  # the default configuration; see render_file
    "configuration": {
        "array": "14 rows (along x) by 9 columns (across y) of cubes, H = 0.06 m, pitch 0.12 m (street width = H, plan area ratio 25 %), published as BD_caseL.stl; the data paper calls it '9 rows by 14 columns'",
        "H_m": 0.06, "pitch_m": 0.12, "cubes": 126,
        "Re_H": 5600,
        "U_H_m_s": 1.339415,
        "wind_directions_deg": [0],
        "measurement_planes": ["8 heights (4 .. 150 mm) at 27 locations in the streets near the source", "4 heights (70 .. 150 mm) at 14 locations above the blocks", "3 heights (4 .. 30 mm) at 24 locations around"],
        "points": 344,
        "stratification": "unstable: floor 45.0 degC, air at z = H 14.75 degC (difference 30.3 K), bulk Richardson number -0.035 (workbook; the readme says -0.04); the workbook gives the building surface as 42.2 degC",
        "source": "floor line source across the tunnel at x = -0.15 m between rows 7 and 8: readme 0.037 m x 1.2 m, BD_caseL.stl patch 0.04 m x 1.02 m; 100 % ethylene, 8.33e-6 m3/s (500 cc/min) at 35 degC",
        "concentration_normalisation": "c0 = q / (U_H H^2) = 1728.23 ppm (the workbook's value)",
        "instrument": "split-fibre hot wire (velocity), cold wire (temperature), high-speed hydrocarbon analyser (concentration), 1000 Hz with a 200 Hz low-pass filter, 60 s per point",
        "tunnel": "thermally stratified wind tunnel, Tokyo Polytechnic University (Atsugi); 1.2 m wide, 1.0 m high; 26 aluminium angles 9 mm high every 200 mm as roughness; model floor 10 mm above the tunnel floor",
        "scale_note": "model scale; the sources state no model:full scale ratio",
    },
    "quantities": ["U", "V", "W", "uu", "vv", "ww", "k", "uv", "uw", "C", "c_rms", "concentration_ratio", "T", "T_rms", "uc", "vc", "wc", "uT", "vT", "wT"],
    "units": {"length": "m (model scale)", "velocity": "m/s", "variance": "m^2/s^2", "k": "m^2/s^2", "concentration": "ppm of the released ethylene", "temperature": "degC (T); K (T_rms); heat fluxes K m/s; concentration fluxes ppm m/s"},
    "frame": {
        "origin": "bottom centre of the windward wall of the 9th row (of 14) of the central column: x = 0 is that wall, y = 0 the centre line of the central column",
        "x": "+x streamwise (the wind blows toward +x); row k spans x in [0.12 (k-9), 0.12 (k-9) + 0.06], so the array spans x in [-0.96, 0.66]",
        "y": "+y lateral; column centres at y = 0, +-0.12, ... +-0.48 (the array spans y in [-0.51, 0.51])",
        "z": "+z up from the model floor; cube tops at z = 0.06; heated floor at z = 0",
        "lateral_sign_applied": 1,
        "coordinate_scale_applied": 1.0,
    },
    "people": {
        "data_collectors": ["Ryuichiro Yoshie (Tokyo Polytechnic University)", "Koudai Katada (Tokyo Polytechnic University)"],
        "editors_distributors": ["Yoshihide Tominaga (Niigata Institute of Technology)", "Hideki Kikumoto (The University of Tokyo)", "Tsubasa Okaze (Institute of Science Tokyo)"],
        "contact": "Ryuichiro Yoshie <yoshie@arch.t-kougei.ac.jp>",
    },
    "doi": "10.5281/zenodo.15487637",
    "citation_requested": "Yoshie, R., Nomura, K., Katada, K., Jiang, G. (2012). Non-isothermal large eddy simulation of pollutant and thermal dispersion in urban street canyons. 22nd National Symposium on Wind Engineering, 61-66 (in Japanese). https://doi.org/10.14887/kazekosymp.22.0.61.0; Jiang, G., Yoshie, R. (2018). Large-eddy simulation of flow and pollutant dispersion in a 3D urban street model located in an unstable boundary layer. Build. Environ. 142, 47-57. https://doi.org/10.1016/j.buildenv.2018.06.015",
    "inflow_fit": _inflow_fit("L"),
    "known_issues": [
        "RS_caseL.csv's temperature column is headed 'T(K)' but holds DEGREES CELSIUS (12.85 .. 29.86); AF_caseL.csv's 'T(K)' is kelvin (283 .. 295). The API serves degrees Celsius for both.",
        "The published CSV is the workbook rounded to 2-4 decimals; the table is rebuilt from the workbook. Its 'tc' column (temperature-concentration covariance, K ppm) and the workbook's 'Usc' (the vector magnitude of the mean velocity) are not in the table.",
        "The readme's file list names AF_caseK.csv and RS_caseK.csv; the files are AF_caseL.csv and RS_caseL.csv.",
        "The readme's 'building surface temperature T_b = 14.8 degC' is the approach-flow air temperature at z = H; the workbook gives the building surface as 42.2 degC.",
        "The line source is 0.037 m x 1.2 m in the readme and data paper but a 0.04 m x 1.02 m patch in BD_caseL.stl.",
        "The +y and -y halves are not mirror images: the same point differs in U by 26 %, in k by 23 %, in C by 36 % on average, and U is 0.11 m/s lower and T 1.3 K higher at +y at z = 0.15 m (0.09 m above the roofs), so the tunnel flow has a lateral gradient; do not assume symmetry.",
        "The workbook carries no expanded uncertainty (the data paper mentions one for Case J only).",
        "AF_caseL.csv lists the profile from the top (z = 0.32 m) down and has no k.",
        "The measured tracer flux through the cross-sections equals q / 1.2 m to 0.86 .. 1.0 (street and cube-column lines averaged), which fixes q and the unit ppm; the cube-column line alone carries only 0.2 .. 0.4 of it.",
    ],
}

DEFAULT_CONFIGURATION = "default"

RENDER_CAPTIONS = {
    ("L", "default"): "14 x 9 array of 0.06 m cubes on a 0.12 m pitch (model scale); the orange line is the floor tracer source between rows 7 and 8; the wind blows along +x.",
}


def _cubes():
    boxes = []
    for i in range(ROWS):
        for j in range(COLS):
            x0, y0 = X_FIRST + PITCH * i, Y_FIRST + PITCH * j
            boxes.append({"min": [round(x0, 9), round(y0, 9), 0.0], "max": [round(x0 + H, 9), round(y0 + H, 9), H]})
    return boxes


def geometry(D, case):
    """[(configuration, triangles, boxes, note)]: the 126 cubes of BD_caseL.stl."""
    boxes = _cubes()
    return [("default", D.tris_of_boxes(boxes), boxes, "the 126 cubes of BD_caseL.stl (checked equal to this 14 x 9 grid of 0.06 m cubes on a 0.12 m pitch in clean/checks.json; the published file is watertight and outward-wound); the line-source patch of that file is not a building and is not included")]


def approach_flow(D, case):
    """Rows of {z, U, u_rms} of AF_caseL.csv (x = -0.4 m, 25 heights, ascending in z; the file has no k) and the file they come from."""
    header, rows = D._read_csv(os.path.join(REPO, CASE["approach_flow_file"]))
    idx = {n: i for i, n in enumerate(header)}
    out = [{"z": D._f(r[idx["z"]]), "U": D._f(r[idx["U"]]), "u_rms": D._f(r[idx["u_rms"]])} for r in rows]
    return sorted(out, key=lambda d: d["z"]), CASE["approach_flow_file"]
