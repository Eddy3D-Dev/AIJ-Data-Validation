"""Case F facts for scripts/aijdata.py: its CASES entry, default configuration, render caption and loaders.

aijdata.py imports this module and passes itself (D) to the functions below; nothing here imports aijdata.
Numbers are the ones clean/case_f.py measured (clean/checks.json, clean/manifest.json) or the readme and the data paper state.
"""
from __future__ import annotations

import math
import os

SCALE = 800.0
DEFAULT_CONFIGURATION = "default"   # the one geometry; the points' config "default" is the 9 m tunnel plane and the field

CASE = {
    "id": "F", "slug": "case-f", "title": "Case F — Shinjuku district",
    "short": "Shinjuku sub-centre, Tokyo, November 1978: 1:800 tunnel (thermistor, 5 / 9 / 20 m) and a year of field cup anemometers; velocity ratio to the 500 m wind, 12 tunnel and 16 field directions.",
    "folder": "raw/cases/case-f",
    "reference_file": "raw/cases/case-f/RS-WT_caseF.csv",
    "approach_flow_file": "raw/cases/case-f/AF_caseF.csv",
    "readme": "raw/cases/case-f/readme_caseF.md",
    "render": "validation/figures/geometry/case-f.png",
    "configuration": {
        "district": "Shinjuku sub-centre during construction of the high-rise group, building configuration of November 1978",
        "scale": "1:800",
        "model": "terrain and buildings in a disc of radius 725 m (BD_caseF.stl; the readme and the data paper say 800 m / 1600 m diameter)",
        "points": 13, "point_numbers": "1-3, 5-11, 13-15 (4 and 12 absent; points 16 and later belong to later construction stages and are not in the dataset)",
        "wind_directions": ["N", "NNE", "NE", "ENE", "SE", "SSE", "S", "SSW", "SW", "WNW", "NW", "NNW"],
        "wind_directions_field": ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"],
        "measurement_planes_above_ground_m": [5, 9, 20],
        "measurement_planes_z_m": [15, 19, 30],
        "ground_offset_m": 10,
        "normalisation": "velocity ratio = mean speed / the approaching mean speed at the boundary-layer height 500 m (full scale); the field values were converted to it with the tunnel (readme). U(500 m) is 10 m/s in the data paper and 10.65 m/s implied by the profile",
        "instrument": "tunnel: thermistor anemometer, 30 s averaging; field: three-cup anemometer with wind vane, 10-minute means above 5 m/s at the reference roof, December 1977 - November 1978",
        "tunnel": "Shimizu Corporation wind tunnel; cross-section 1.55 m wide, 2.2 m high; power-law inflow, exponent 1/4",
        "reference_roofs": {"SMB": "Shinjuku-Mitsui Building, roof G.L.+210 m, anemometer G.L.+237 m, for NW-NE", "KDD": "KDD Building, roof G.L.+165 m, anemometer G.L.+187 m, for the other directions"},
    },
    "quantities": ["velocity_ratio", "velocity_ratio_sd"],
    "units": {"length": "m (FULL scale)", "velocity_ratio": "dimensionless", "velocity_ratio_sd": "dimensionless"},
    "frame": {
        "origin": "centre of the reproduced district, tunnel floor plane",
        "x": "+x EAST (full-scale metres)",
        "y": "+y NORTH (compass rose in MP_caseF.png)",
        "z": "+z up from the TUNNEL FLOOR; the readme's rule is ground = z - 10 m (the STL's terrain under the points is at z = 5 m)",
        "wind_direction_rotation": "compass FROM-direction (N = 0, E = 90): N blows toward -y; flow_dir = (-sin WD, -cos WD). Not stated by the sources; supported by the reference-building choice and by upwind roughness (status 'unverified').",
        "lateral_sign_applied": 1,
        "coordinate_scale_applied": SCALE,
    },
    "people": {
        "data_collectors": ["K. Fujii, Y. Asami, Y. Iwasa et al. (the original 1978 investigation; the readme names no data collectors)"],
        "editors_distributors": ["Yoshihide Tominaga (Niigata Institute of Technology)", "Hideki Kikumoto (The University of Tokyo)", "Tsubasa Okaze (Institute of Science Tokyo)"],
        "contact": "Tsubasa Okaze <okaze.t.f356@m.isct.ac.jp>",
    },
    "doi": "10.5281/zenodo.15589621",
    "citation_requested": "Fujii, K., Asami, Y., Iwasa, Y. et al. (1978). Wind in Shinjuku Sub-Central Area — Comparison Between Field Measurement and Wind Tunnel Experiment. Proc. 5th Symposium on Wind Resistance of Structures, 91-98 (in Japanese).",
    "inflow_fit": {
        "method": "power law on the 18 published heights (z 10 ... 400 m full scale); the data paper states exponent 1/4",
        "power_law_exponent_fitted": 0.277, "power_law_exponent_paper": 0.25,
        "U_500m_m_s": {"data_paper": 10.0, "implied_by_profile": 10.65},
        "note": "AF_caseF.csv stops at 400 m (U = 10.0 m/s); the workbook's U/UR profile (0.94 at 400 m) puts the 500 m speed at 10.65 m/s",
    },
    "known_issues": [
        "The 16 field rows of point 14 in RS-FO_caseF.csv hold the workbook's value of the NEXT wind direction clockwise (the series is shifted by one); the cleaned table follows the workbook (clean/QUESTIONS.md QF1).",
        "Tunnel and STL coordinates are MODEL scale (1:800); the field's are full scale. The case frame is full scale; the tunnel's x, y, z and the STL are multiplied by 800.",
        "z is height above the tunnel floor. The readme's rule 'ground = z - 10 m' gives the 5 / 9 / 20 m planes, but the STL's terrain under all 13 points is at z = 5 m, so the planes stand 10 / 14 / 25 m above it.",
        "BD_caseF.stl is wound inward on every ground, roof and sampled wall facet and is open along the rim of its 725 m disc (812 boundary edges); the served geometry.stl is re-wound outward.",
        "MP_caseF.csv names the two reference points the other way round from the workbook, the STL and MP_caseF.png (the workbook's Shinjuku-Mitsui Building is the 225 m tower at (-17.5, 96.0), the KDD Building the 180 m one at (85.8, -347.1)).",
        "Field values are the legacy workbook's roof-anemometer ratios times 0.940 (NW-NE) or 0.963 (other directions); sigma is the workbook's S.D. rounded to 0.01 times that factor, so it moves in steps of 0.0094 / 0.0096.",
        "The tunnel did not run E, ESE, WSW or W; the field data cover all 16. The 5 m and 20 m planes exist at some points only (29 and 79 rows).",
        "One tunnel value (point 8, SW, 9 m: 0.474) has no counterpart in the workbook's results sheet, and the flat 'Sheet1' table has 0.63 there.",
        "Field anemometer heights above the tunnel floor are 13 - 21 m (3 - 11 m above ground by the readme's rule); the data paper says 3 - 9 m, so points 13 and 14 (11 m) disagree.",
        "The thermistor reads a SCALAR speed and the cup anemometer a 10-minute mean: a RANS |U| is biased low against both.",
    ],
}

RENDER_CAPTIONS = {
    ("F", "default"): "Shinjuku sub-centre, November 1978: terrain and buildings of the 1:800 model over a disc of 725 m radius (full-scale metres); north is +y, the towers over 100 m are blue.",
}


def _horizontal_down_up(tris):
    down = up = 0
    for (ax, ay, az), (bx, by, bz), (cx, cy, cz) in tris:
        nx, ny, nz = (by - ay) * (cz - az) - (bz - az) * (cy - ay), (bz - az) * (cx - ax) - (bx - ax) * (cz - az), (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        n = math.sqrt(nx * nx + ny * ny + nz * nz)
        if n > 0 and abs(nz) > 0.9999 * n:
            down += nz < 0
            up += nz > 0
    return down, up


def geometry(D, case):
    """[(configuration, triangles, boxes, note)]: BD_caseF.stl x800 (model -> full-scale metres), re-wound outward."""
    raw = D.read_ascii_stl(os.path.join(D.REPO, CASE["folder"], "BD_caseF.stl"))
    tris = [tuple(tuple(v * SCALE for v in p) for p in t) for t in raw]
    down, up = _horizontal_down_up(tris)
    if down > up:
        tris = [(a, c, b) for a, b, c in tris]
    return [("default", tris, None,
             f"BD_caseF.stl (terrain + buildings, November 1978) scaled x800 from model to full-scale metres; {down} of {down + up} horizontal facets faced down as published, "
             "so every triangle is reversed to point outward; one shell, open along the rim of the 725 m disc")]


def approach_flow(D, case):
    """Rows of {z, U, u_rms}: z in full-scale metres (the file's model metres x 800), U and u_rms in the tunnel's m/s."""
    header, rows = D._read_csv(os.path.join(D.REPO, CASE["approach_flow_file"]))
    idx = {n: i for i, n in enumerate(header)}
    return [{"z": D._f(r[idx["z"]]) * SCALE, "U": D._f(r[idx["U"]]), "u_rms": D._f(r[idx["u_rms"]])} for r in rows], CASE["approach_flow_file"]
