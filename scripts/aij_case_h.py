"""Case H (1:1:2 building, floor point source) for scripts/aijdata.py: the CASES entry, the geometry, the approach flow.

Every number below is the one clean/case_h.py measured (clean/manifest.json, clean/checks.json); the cleaned table under
clean/cases/H/ is what the API serves."""
from __future__ import annotations

from aij_case_common import EDITORS, clean_approach_flow

DEFAULT_CONFIGURATION = "default"

RENDER_CAPTIONS = {
    ("H", "default"): ("Isolated 1:1:2 building, 0.10 m × 0.10 m × 0.20 m (model scale); the wind blows along +x. The tracer comes from a 4 mm "
                       "floor hole 0.25 H behind the leeward face (not drawn)."),
}

BOXES = [{"min": [-0.10, -0.05, 0.0], "max": [0.0, 0.05, 0.20]}]

CASE = {
    "id": "H", "slug": "case-h", "title": "Case H — 1:1:2 building with a floor point source",
    "short": "Isolated 1:1:2 building with an ethylene point source on the floor behind it: velocity (split-fibre hot wire) and concentration (hydrocarbon analyser) at 876 points.",
    "folder": "raw/cases/case-h",
    "reference_file": "raw/cases/case-h/RS_caseH.csv",
    "approach_flow_file": "raw/cases/case-h/AF_caseH.csv",
    "readme": "raw/cases/case-h/readme_caseH.md",
    "render": "validation/figures/geometry/case-h.png",  # the default configuration; see render_file
    "configuration": {
        "building": "1:1:2 (width : depth : height) prism, 0.10 × 0.10 × 0.20 m",
        "b_m": 0.10, "H_m": 0.20,
        "Re_H": 43000,
        "U_H_m_s": 3.226,
        "U_H_note": "the workbook's uH; the readme and the data paper state 3.23 m/s; the workbook's free-stream reference U0 is 5.279 m/s",
        "wind_directions_deg": [0],
        "source": "4 mm hole in the floor 0.25 H = 0.05 m behind the leeward face at (0.05, 0, 0); ethylene (C2H4), 100 %, 350 cc/min = 5.83e-6 m3/s",
        "reference_concentration": "c0 = cgas q / (UH H^2) = 45.18 ppm (45.2 in the paper); concentration_ratio = C / c0",
        "measurement_planes": ["vertical centre plane y/H = 0", "horizontal z/H = 1/16 (y in [-0.2, 0.2])", "horizontal z/H = 1/4 and 1/2 (y in [0, 0.2])"],
        "points": 876,
        "instrument": "velocity: constant-temperature anemometer (DANTEC 90C10) with a split-fibre probe (55R55, 55R56, 55R57), 1000 Hz, 120 s; concentration: high-speed total hydrocarbon analyser, 1000 Hz, 120 s",
        "tunnel": "Eiffel-type boundary-layer wind tunnel, Tokyo Polytechnic University, Atsugi (1.0 m high, 1.2 m wide)",
        "scale_note": "model scale; the source states no model:full-scale ratio; Eddy3D solves it at 1:100",
    },
    "quantities": ["U", "V", "W", "uu", "vv", "ww", "k", "C", "c_rms", "concentration_ratio"],
    "units": {"length": "m (model scale)", "velocity": "m/s", "variance": "m^2/s^2", "k": "m^2/s^2", "C": "ppm", "concentration_ratio": "dimensionless, C/c0"},
    "frame": {
        "origin": "the centre of the building's leeward face on the ground plane",
        "x": "+x streamwise (the wind blows toward +x); the building spans x in [-0.1, 0]; points at x = -0.2 ... 0.4 m",
        "y": "+y lateral; the building spans y in [-0.05, 0.05]; the z = 1/16 H plane covers y in [-0.2, 0.2]",
        "z": "+z up; roof at z = 0.2 m; points at z = 0.01 ... 0.3 m",
        "lateral_sign_applied": "-1 for point numbers 1-220 (the vertical-plane sheet of the workbook), +1 elsewhere",
        "coordinate_scale_applied": 1.0,
    },
    "people": {
        "data_collectors": ["Ryuichiro Yoshie (Tokyo Polytechnic University)", "Takumi Tachibana (Wind Engineering Institute)"],
        "editors_distributors": EDITORS,
        "contact": "Ryuichiro Yoshie <yoshie@arch.t-kougei.ac.jp>",
    },
    "doi": "10.5281/zenodo.15429871",
    "doi_note": "The readme and the data paper name this one DOI; no separate version DOI is stated.",
    "citation_requested": "Yoshie, R. (2016). Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer. Adv Environ Wind Eng, 167-196. https://doi.org/10.1007/978-4-431-55912-2_9",
    "inflow_fit": {
        "method": "log law, kappa = 0.41, least squares over z = 0.02 ... 2H on the workbook's 17-point approach profile (x = -0.493 m)",
        "u_star_m_s": 0.4065, "z0_mm": 7.449, "U_H_measured_m_s": 3.226, "log_law_error_at_H": "+1.1 %", "turbulence_intensity_at_H": 0.2165,
        "note": "derived during cleaning, not published by AIJ",
    },
    "known_issues": [
        "The table carries the legacy workbook's values (ratios at full precision x uH = 3.226 m/s), not RS_caseH.csv's: on the z/H = 1/2 and 1/4 planes (and in the approach profile) the CSV's U, V, W are the workbook ratios ROUNDED TO 0.01 before the scaling, a 0.032 m/s grid (+/-0.016 m/s).",
        "One row per instrument and point: velocity rows (split fibre) and concentration rows (hydrocarbon analyser) with the same point_id (the CSV's No.). The velocity line is x = 0.40 m and the concentration line x = 0.38 m, so 50 points have no velocity and 50 no concentration (-999.9 in the CSV); none of them is inside the building.",
        "V of the vertical-plane sheet (point numbers 1-220) is the exact negative of V at the same points in the horizontal-plane sheets (positive toward -y); it is multiplied by -1 so that V is positive toward +y everywhere, as in Cases A and D.",
        "The y = 0, z = 0.1 line (13 locations) is in two sheets and appears twice in the table, as exact copies once V is flipped; they are not independent repeat measurements.",
        "Concentration is the analyser's reading: upwind of the building (where the true value is zero) it is +/-0.1 ppm, and 97 of 826 values are negative (minimum -0.83 ppm). Log-based statistics (geometric mean, geometric variance) need a floor.",
        "The published header misspells w_rms as 'w_rsm'; the workbook's inflow sheet labels z as 'mm' but holds metres.",
        "The profile's uw and uv are published but the approach-flow table has no column for them.",
    ],
}


def geometry(D, case):
    note = "generated from the stated dimensions 0.10 × 0.10 × 0.20 m (MP-y_caseH.png, MP-z_caseH.png); leeward face at x = 0"
    return [("default", D.tris_of_boxes(BOXES), BOXES, note)]


def approach_flow(D, case):
    return clean_approach_flow(case)
