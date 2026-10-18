"""Case I (cube, roof point source) for scripts/aijdata.py: the CASES entry, the geometry, the approach flow.

Every number below is the one clean/case_i.py measured (clean/manifest.json, clean/checks.json); the cleaned table under
clean/cases/I/ is what the API serves."""
from __future__ import annotations

from aij_case_common import EDITORS, clean_approach_flow

DEFAULT_CONFIGURATION = "default"

RENDER_CAPTIONS = {
    ("I", "default"): ("Isolated cube, 0.10 m on a side (model scale); the wind blows along +x. The tracer is released from a 6 mm outlet at the "
                       "centre of the roof (not drawn)."),
}

BOXES = [{"min": [-0.05, -0.05, 0.0], "max": [0.05, 0.05, 0.10]}]

CASE = {
    "id": "I", "slug": "case-i", "title": "Case I — cube with a roof point source",
    "short": "Isolated cube with an ethane point source at the centre of its roof: velocity (laser Doppler, 91 points) and concentration (hydrocarbon analyser, 539 points).",
    "folder": "raw/cases/case-i",
    "reference_file": "raw/cases/case-i/RS-w_caseI.csv",
    "reference_file_concentration": "raw/cases/case-i/RS-c_caseI.csv",
    "approach_flow_file": "raw/cases/case-i/AF_caseI.csv",
    "readme": "raw/cases/case-i/readme_caseI.md",
    "render": "validation/figures/geometry/case-i.png",  # the default configuration; see render_file
    "configuration": {
        "building": "cube, 0.10 m on a side (= H)",
        "H_m": 0.10,
        "Re_H": 11000,
        "U_H_m_s": 1.7,
        "U_H_note": "the readme and the velocity sheet; the approach flow at z = H is 1.6969 m/s and the workbook's inflow sheet divides by 1.697",
        "wind_directions_deg": [0],
        "source": "6 mm circular outlet at the centre of the roof (0, 0, 0.1); 10 % ethane in the mixture, 400 cc/min (= 6.67e-6 m3/s of mixture, 6.67e-7 m3/s of ethane); release velocity 0.236 m/s, M = Ve/UH = 0.14",
        "reference_concentration": "c0 = q / (UH H^2) = 39.22 ppm (39.2 in the paper), q the ETHANE flow; concentration_ratio = C / c0",
        "measurement_planes": ["velocity: y/H = 0 and z/H = 0.5", "concentration: y/H = 0 and z/H = 0 (the ground)"],
        "points": {"velocity": 91, "concentration": 539},
        "instrument": "velocity: laser Doppler anemometer (Dantec BSA F60), 200 Hz, 240 s; concentration: hydrocarbon analyser (Kimoto HADA-01), 1 Hz, 120 s",
        "tunnel": "AIST wind tunnel, 20 m long, 3.0 × 2.0 m cross-section; approach flow described as a 1/7 power law (data paper section 3.9)",
        "scale_note": "model scale; the source states no model:full-scale ratio; Eddy3D solves it at 1:60 (a 6 m cube)",
    },
    "quantities": ["U", "V", "W", "k", "C", "concentration_ratio"],
    "units": {"length": "m (model scale)", "velocity": "m/s", "k": "m^2/s^2", "C": "ppm", "concentration_ratio": "dimensionless, C/c0"},
    "frame": {
        "origin": "the centre of the cube on the ground plane",
        "x": "+x streamwise (the wind blows toward +x); the cube spans x in [-0.05, 0.05]; wind points x = -0.15 ... 0.25 m, concentration points x = 0.065 ... 2.7 m",
        "y": "+y lateral; the cube spans y in [-0.05, 0.05]; concentration points reach |y| = 0.44 m on the ground",
        "z": "+z up; roof at z = 0.1 m; the outlet at (0, 0, 0.1)",
        "lateral_sign_applied": 1,
        "coordinate_scale_applied": 1.0,
    },
    "people": {
        "data_collectors": ["Hiroaki Kondo (National Institute of Advanced Industrial Science and Technology)", "Katsuhiko Mutou (National Institute of Advanced Industrial Science and Technology)",
                            "Akihiro Hori (National Institute for Environmental Studies)"],
        "editors_distributors": EDITORS,
        "contact": "Yoshihide Tominaga <tominaga@abe.niit.ac.jp>",
    },
    "doi": "10.5281/zenodo.15430018",
    "doi_note": "The readme and the data paper name this one DOI; no separate version DOI is stated.",
    "citation_requested": "Japan Society for Atmospheric Environment (2013). Guidelines for Atmospheric Environment Assessment Methods Using CFD Models (DiMCFD). Japan Society for Atmospheric Environment (in Japanese).",
    "inflow_fit": {
        "method": "log law, kappa = 0.41, least squares over z = 0.02 ... 0.4 m on the workbook's 12-point approach profile",
        "u_star_m_s": 0.0928, "z0_mm": 0.0455, "U_H_measured_m_s": 1.6969, "log_law_error_at_H": "+2.6 %",
        "power_law_index_fitted": 0.115, "power_law_index_paper": "1/7",
        "note": "derived during cleaning, not published by AIJ; the workbook's own (z/H)^(1/7) column is within 4.6 % of the measured profile over z = 0.02 ... 0.7 m",
    },
    "known_issues": [
        "Two point sets, no point numbers: the velocity file (91 points: y = 0 plane and z/H = 0.5 plane) and the concentration file (539 points: y = 0 plane and the ground). The table stacks them, one row per instrument and point: velocity rows (instrument ldv) are numbered 1-91 and concentration rows (hydrocarbon_analyser) 92-630, in the files' order. 17 locations have both a velocity and a concentration value.",
        "V on the y = 0 plane (53 of 91 points) is 0 in the CSV and 1e-9 ... 4e-6 m/s in the workbook, a symmetry value. It is NaN in the table; V is measured only at the 38 off-plane points.",
        "The table carries the legacy workbook's values; the CSVs round to 3 decimals (velocity, k) and 1 decimal (concentration, ppm). Every concentration is a multiple of 0.1 ppm: a 0.4 ppm value carries +/-12 % of quantisation.",
        "The paper's c0 = 39.2 ppm needs the ETHANE flow (10 % of the 400 cc/min, 6.67e-7 m3/s); its sentence 'ethane released at 6.67e-6 m3/s' is the mixture. With the mixture flow c0 would be 392 ppm.",
        "The workbook normalises the approach flow with 1.697 m/s and the points with 1.7 m/s (0.18 % apart).",
        "AF_caseI.csv ends in 53 rows of ',,' and two stray cells, '0.5*' and '1.5*' (chart axis labels): a reader that does not test z for a number takes them for data.",
        "Thirteen ground-centreline locations (x, 0, 0) are measured twice (they are on both the y = 0 and the z = 0 plane) with values up to 8.5 % apart; both are kept. The four y = 0, z = 0.05 wind points that appear twice in the workbook are identical copies and appear once.",
        "Only the TKE is published, no variances and no concentration fluctuation: k cannot be checked against the components.",
    ],
}


def geometry(D, case):
    note = "generated from the stated 0.1 m cube centred on the origin (MP-y-c_caseI.png, MP-z-c_caseI.png)"
    return [("default", D.tris_of_boxes(BOXES), BOXES, note)]


def approach_flow(D, case):
    return clean_approach_flow(case)
