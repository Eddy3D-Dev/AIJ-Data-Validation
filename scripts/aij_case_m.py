"""Case M facts for scripts/aijdata.py: its CASES entry, default configuration, render caption and loaders.

aijdata.py imports this module and passes itself (D) to the functions below; nothing here imports aijdata.
Numbers are the ones clean/case_m.py measured (clean/checks.json, clean/manifest.json) or the readme and the data paper state.
"""
from __future__ import annotations

import math
import os

SCALE = 600.0
DEFAULT_CONFIGURATION = "default"

CASE = {
    "id": "M", "slug": "case-m", "title": "Case M — TPU Atsugi campus",
    "short": "Tracer-gas release on the Tokyo Polytechnic University Atsugi campus: 1:600 tunnel (velocity at 180°, ethylene concentration at 175°, 180° and 185°) and 18 field runs with PMCH, 15 points 3 m above ground.",
    "folder": "raw/cases/case-m",
    "reference_file": "raw/cases/case-m/RS-WT_caseM.csv",
    "approach_flow_file": "raw/cases/case-m/AF_caseM.csv",
    "readme": "raw/cases/case-m/readme_caseM.md",
    "render": "validation/figures/geometry/case-m.png",
    "configuration": {
        "site": "Tokyo Polytechnic University, Atsugi campus; terrain falls from about 32 m (campus plateau) to 3.6 m at the east edge; tallest building about 32 m",
        "scale": "1:600",
        "points": 15, "measurement_height_m": 3, "measurement_height_note": "3 m above the local ground, full scale (0.005 m model)",
        "wind_directions_deg": [175, 180, 185],
        "wind_direction_velocity_deg": 180,
        "field_runs": 18, "field_wind_directions_deg": "78 ... 200.7 (mean direction at the reference point per run); 11 of 18 within 5° of 180°",
        "reference": {"U_R_m_s": 4.08, "H_R_m_model": 0.068, "H_R_m_full": 41, "R": "rooftop of the main building: the point is 41 m above the ground, 8 m above the roof in the STL"},
        "tracer": {"tunnel": "C2H4, 100 %, 6 mm outlet, 150 cc/min = 2.5e-6 m3/s (0.09 m/s)", "field": "PMCH (C7F14), 200 ppm, 5 L/min, 1.5 m above ground, 25-26 Feb 2014, 18 runs of 10 min sampling"},
        "normalisation": "concentration ratio = C / c0, c0 = q / (U_R H_R^2): 132.5 ppm in the tunnel (the paper rounds to 1.33e2); per run in the field (1,444 ... 7,379 ppq)",
        "instrument": "tunnel: DANTEC split-fibre probe (1000 Hz, 240 s) and high-speed hydrocarbon analyser; field: sorbent tubes with GC-ECD, sonic anemometer SAT-600 at the reference point",
        "tunnel": "Eiffel-type boundary-layer wind tunnel, Tokyo Polytechnic University; cross-section 1.0 m high, 1.2 m wide; power law exponent 0.27 (AIJ Loads category IV) with an upwind taper for the topography",
    },
    "quantities": ["U", "V", "W", "uu", "vv", "ww", "k", "C", "c_rms", "concentration_ratio"],
    "units": {"length": "m (FULL scale)", "velocity": "m/s (the tunnel's)", "variance": "m^2/s^2", "concentration": "ppm (the field's ppq converted)", "concentration_ratio": "dimensionless"},
    "frame": {
        "origin": "centre of the tunnel turntable on the floor plane (ground surface there at z = 33.07 m)",
        "x": "+x NORTH (full-scale metres)",
        "y": "+y WEST (compass rose of MP_caseM.png: N at +x, W at +y); the frame is right-handed",
        "z": "+z up from the TUNNEL FLOOR; the campus ground lies at z ~ 32 m",
        "wind_direction_rotation": "meteorological FROM-direction, so 180° blows toward +x; flow_dir = (-cos WD, +sin WD), and a larger WD turns the plume toward -y. Measured on the tunnel's 175 / 180 / 185° and on the 18 field runs.",
        "lateral_sign_applied": 1,
        "coordinate_scale_applied": SCALE,
    },
    "people": {
        "data_collectors": ["Ryuichiro Yoshie (Tokyo Polytechnic University)", "Takumi Tachibana (Wind Engineering Institute)"],
        "editors_distributors": ["Yoshihide Tominaga (Niigata Institute of Technology)", "Hideki Kikumoto (The University of Tokyo)", "Tsubasa Okaze (Institute of Science Tokyo)"],
        "contact": "Ryuichiro Yoshie <yoshie@arch.t-kougei.ac.jp>",
    },
    "doi": "10.5281/zenodo.15487857",
    "citation_requested": "Tachibana, T., Yoshie, R., Nakayama, S., Kishida, T., Miyashita, K., Sasaki, R. (2022). Comparison between field measurement and wind tunnel experiments of gas dispersion in an urban area and verification of similarity law. Journal of Wind Engineering 47(3), 39-52 (in Japanese). http://dx.doi.org/10.5359/jwe.47.39",
    "inflow_fit": {
        "method": "power law on the workbook's 40 heights (z 0.005 ... 0.6 m model) at x = -0.498 m; the data paper states exponent 0.27",
        "power_law_exponent_fitted": 0.272, "power_law_exponent_paper": 0.27,
        "U_at_R_height_m_s": 3.94, "U_R_m_s": 4.08,
        "note": "z is height above the empty tunnel floor; at the profile station the model's taper is already 0.052 m high, so the 10 lowest heights lie below it",
    },
    "known_issues": [
        "Field concentrations are in ppq (1e-15 volume fraction) and the tunnel's in ppm: 1 ppq = 1e-9 ppm. The cleaned table converts the field's to ppm and carries C / c0 for both, with the run's own c0 in the field.",
        "Every field run has its own reference speed U_R, mean direction WD_R and tracer flow q (clean/manifest.json -> cases.M.extra_measurements.field_runs); the row's wind_direction_deg is WD_R.",
        "The tunnel measured velocity only at 180°; at 175° and 185° the CSV has -999.9 in all seven velocity columns.",
        "RS-WT_caseM.csv is the legacy workbook rounded (2 dp velocity, 1 dp concentration), and its k is half the sum of the 2-dp RMS values, up to 0.005 m2/s2 from the workbook's; the cleaned table carries the workbook's values.",
        "The tunnel source is on the ground in the workbook, LC_caseM.csv and the STL (readme: 'on a rooftop'); the field source was 1.5 m above ground.",
        "H_R = 41 m is the anemometer height above the ground; the main roof under the reference point is about 33 m above it. c0 uses H_R = 0.068 m (41 m / 600 = 0.06833 m would give 131.2 ppm, -1 %).",
        "The field has an ambient floor of 8 - 11 ppq at points 11 - 15 in every run (not subtracted); the tunnel's concentration has a zero offset (two negative means at point 12) and an rms floor of 7 ppm.",
        "Only 11 of the 18 field runs are within 5° of 180°, the tunnel's direction; runs 1, 2 and 9 have U_R of 1.4 - 1.8 m/s.",
        "BD_caseM.stl is MODEL scale, wound inward on its ground and roof facets, and has 21 boundary and 7 non-manifold edges (7 on the rim of the panel, 14 on 7 slivers hanging on building roofs); the served geometry.stl is multiplied by 600, re-wound outward, without the slivers and closed with a base slab down to z = -1 m.",
        "The approach-flow heights are above the empty tunnel floor: at the profile station the model's taper is 0.052 m high, above the 10 lowest profile heights.",
    ],
}

RENDER_CAPTIONS = {
    ("M", "default"): "TPU Atsugi campus: terrain and buildings of the 1:600 model (full-scale metres, 1080 m by 720 m); the arrow is the wind at WD = 180°, blowing toward +x (north).",
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
    """[(configuration, triangles, boxes, note)]: BD_caseM.stl x600 (model -> full-scale metres), re-wound outward, slivers removed, closed with a base slab."""
    raw = D.read_ascii_stl(os.path.join(D.REPO, CASE["folder"], "BD_caseM.stl"))
    tris = [tuple(tuple(v * SCALE for v in p) for p in t) for t in raw]
    down, up = _horizontal_down_up(tris)
    pub = D.stl_stats(tris)
    tris, closed = D.G.close_terrain(tris, digits=6)
    return [("default", tris, None,
             f"BD_caseM.stl (terrain + buildings) scaled x600 from model to full-scale metres; {down} of {down + up} horizontal facets faced down as published, "
             f"so every triangle is reversed to point outward; the published STL has {pub['edges_boundary']} boundary and {pub['edges_non_manifold']} non-manifold edges: "
             f"{closed['flaps_removed']} slivers (together {closed['flap_area']:.2f} m^2) hanging on building-roof edges are removed, and the 1080 m by 720 m panel is closed with a base slab: "
             f"vertical walls from its rim down to z = {D.G.BASE_Z:g} m and a bottom cap at z = {D.G.BASE_Z:g} m ({closed['base_triangles']} added triangles)")]


def approach_flow(D, case):
    """Rows of {z, U, k, u_rms}: z in full-scale metres (the file's model metres x 600), U and k in the tunnel's units (2 dp, as published)."""
    header, rows = D._read_csv(os.path.join(D.REPO, CASE["approach_flow_file"]))
    idx = {n: i for i, n in enumerate(header)}
    return [{"z": D._f(r[idx["Z"]]) * SCALE, "U": D._f(r[idx["U"]]), "k": D._f(r[idx["k"]]), "u_rms": D._f(r[idx["u_rms"]])} for r in rows], CASE["approach_flow_file"]
