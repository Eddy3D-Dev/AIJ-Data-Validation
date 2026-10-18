"""Case J facts and geometry for scripts/aijdata.py (the cleaned table itself is clean/cases/J/points.csv).

aijdata.py imports CASE, DEFAULT_CONFIGURATION, RENDER_CAPTIONS, geometry and load_approach_flow from here; the
numbers that the cleaning measured (inflow fit) are read from clean/manifest.json so they cannot drift from it.
"""
from __future__ import annotations

import io
import json
import os

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
B_WIDTH, HEIGHT = 0.08, 0.16


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
    "id": "J", "slug": "case-j", "title": "Case J — 1:1:2 building, non-isothermal",
    "short": "Isolated 1:1:2 building with a floor tracer source in an unstably stratified boundary layer: velocity, temperature, tracer concentration and their turbulent fluxes at 444 points on three planes.",
    "folder": "raw/cases/case-j",
    "reference_file": "raw/cases/case-j/RS_caseJ.csv",
    "approach_flow_file": "raw/cases/case-j/AF_caseJ.csv",
    "readme": "raw/cases/case-j/readme_caseJ.md",
    "render": "validation/figures/geometry/case-j.png",  # the default configuration; see render_file
    "configuration": {
        "building": "1:1:2 (width : depth : height) prism, b = 0.08 m, H = 2b = 0.16 m",
        "b_m": 0.08, "H_m": 0.16,
        "Re_H": 16000,
        "U_H_m_s": 1.4581,
        "wind_directions_deg": [0],
        "measurement_planes": ["vertical centre plane y/H = 0", "horizontal z/H = 0.025 (y <= 0 side only)", "horizontal z/H = 0.25"],
        "points": 444,
        "stratification": "unstable: heated floor 45.8 degC, air at z = H 12.2 degC (difference 33.6 K), bulk Richardson number -0.086; building surface 22.0 .. 28.9 degC (mean 24.5 degC, 121 points in clean/cases/J/surface_temperature.csv)",
        "source": "5 mm floor outlet at (0.04, 0, 0), 0.25 H beyond the leeward wall; 5 % ethylene in air at 30.4 degC, 9.17e-6 m3/s",
        "concentration_normalisation": "c0 = 0.05 q / (U_H H^2) = 12.283 ppm (the workbook's value; the 5 % gas fraction is in it)",
        "instrument": "split-fibre hot wire (velocity), cold wire (temperature), high-speed hydrocarbon analyser (concentration), 1000 Hz, 120 s per point",
        "tunnel": "thermally stratified wind tunnel, Tokyo Polytechnic University (Atsugi); 1.2 m wide, 1.0 m high",
        "scale_note": "model scale; the sources state no model:full scale ratio",
    },
    "quantities": ["U", "V", "W", "uu", "vv", "ww", "k", "C", "c_rms", "concentration_ratio", "T", "T_rms", "uT", "vT", "wT"],
    "units": {"length": "m (model scale)", "velocity": "m/s", "variance": "m^2/s^2", "k": "m^2/s^2", "concentration": "ppm of the released ethylene", "temperature": "degC (T); K (T_rms); heat fluxes K m/s"},
    "frame": {
        "origin": "the building's leeward (downwind) wall centre on the ground; x = 0 is the leeward wall",
        "x": "+x streamwise (the wind blows toward +x); the building spans x in [-0.08, 0]; the floor source is at x = +0.04",
        "y": "+y lateral; the building spans y in [-0.04, 0.04]; the z/H = 0.025 plane is measured on the y <= 0 side only",
        "z": "+z up; roof at z = 0.16; heated floor at z = 0",
        "lateral_sign_applied": 1,
        "coordinate_scale_applied": 1.0,
    },
    "people": {
        "data_collectors": ["Ryuichiro Yoshie (Tokyo Polytechnic University)", "Hideyuki Tanaka (Takenaka Corporation)", "Tsuyoshi Kobayashi (Tokyo Polytechnic University)"],
        "editors_distributors": ["Yoshihide Tominaga (Niigata Institute of Technology)", "Hideki Kikumoto (The University of Tokyo)", "Tsubasa Okaze (Institute of Science Tokyo)"],
        "contact": "Ryuichiro Yoshie <yoshie@arch.t-kougei.ac.jp>",
    },
    "doi": "10.5281/zenodo.15447887",
    "citation_requested": "Yoshie, R. (2016). Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer. Adv Environ Wind Eng, 167-196. https://doi.org/10.1007/978-4-431-55912-2_9",
    "inflow_fit": _inflow_fit("J"),
    "known_issues": [
        "Temperature is in KELVIN in all three published CSVs; the API serves degrees Celsius (T) and kelvin differences (T_rms, heat fluxes).",
        "The published CSV is the legacy workbook's non-dimensional values rounded to 3-4 decimals and scaled back; the table is rebuilt from the workbook. The CSV's heat fluxes sit on a 0.0049 K m/s grid and k on 0.00021 m^2/s^2.",
        "c0 = 12.283 ppm includes the 5 % ethylene fraction of the released gas (workbook cell Co); q / (U_H H^2) alone is 245.7 ppm. The data paper states no c0 for Case J.",
        "RS_caseJ.csv lists the location (-0.16, 0, 0.004) twice (No. 1 and 153, identical values): a score over the table counts that point twice.",
        "The workbook's <u'2> is not always the square of its sigma_u (up to 3 % in single rows); the table uses the variances, which reproduce k.",
        "The workbook lists an expanded uncertainty beside every quantity (no column here; clean/manifest.json cases.J.extra_measurements.expanded_uncertainty). The mean concentration is below its own uncertainty (about 1 ppm) at 42 % of the rows, and 193 uncertainty cells of the w'theta' flux are an Excel fill series, not values.",
        "The empty-tunnel profile changes along the tunnel: U at z = 0.019 H is 0.33 U_H at x/H = -2.5 (the published AF_caseJ.csv), 0.58 at the building's own position. The workbook has all three stations (clean/cases/J/approach_flow_full.csv).",
        "The readme's Reynolds number (43,000) is Case H's; U_H H / nu = 1.6e4 as the data paper states.",
        "uv, uw, vw are not published at the points; uc, vc, wc were not measured.",
    ],
}

DEFAULT_CONFIGURATION = "default"

RENDER_CAPTIONS = {
    ("J", "default"): "Isolated 1:1:2 building, b = 0.08 m, H = 0.16 m (model scale); the orange ring marks the floor tracer source, 0.25 H behind the building (seen through it); the wind blows along +x.",
}


def geometry(case):
    """[(configuration, triangles, boxes, note)]: the building as one box."""
    import aijdata as D
    boxes = [{"min": [-B_WIDTH, -B_WIDTH / 2, 0.0], "max": [0.0, B_WIDTH / 2, HEIGHT]}]
    return [("default", D.tris_of_boxes(boxes), boxes, "generated from the readme's stated dimensions b = 0.08 m, H = 0.16 m; the leeward wall is the origin (MP-y_caseJ.png, MP-z_caseJ.png)")]


def load_approach_flow(case):
    """Rows of {z, U, k, u_rms} of AF_caseJ.csv (x = -0.4 m, 20 heights) and the file they come from."""
    import aijdata as D
    header, rows = D._read_csv(os.path.join(REPO, CASE["approach_flow_file"]))
    idx = {n: i for i, n in enumerate(header)}
    return [{"z": D._f(r[idx["z"]]), "U": D._f(r[idx["U"]]), "k": D._f(r[idx["k"]]), "u_rms": D._f(r[idx["u_rms"]])} for r in rows], CASE["approach_flow_file"]
