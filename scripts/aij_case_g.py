"""Case G (field observation behind a tree belt) for scripts/aijdata.py: the CASES entry, the geometry, the approach flow.

Every number below is the one clean/case_g.py measured (clean/manifest.json, clean/checks.json); the cleaned table under
clean/cases/G/ is what the API serves."""
from __future__ import annotations

from aij_case_common import EDITORS, clean_approach_flow

DEFAULT_CONFIGURATION = "default"

RENDER_CAPTIONS = {
    ("G", "default"): ("The Tsuiji-matsu tree belt, 2 m × 74 m × 7 m with a 1.2 m gap below (full scale; shown as its envelope — a porous canopy, "
                       "not a solid body); the wind blows along +x and the measurements are behind the belt."),
}

BOXES = [{"min": [-2.0, -37.0, 1.2], "max": [0.0, 37.0, 7.0]}]

CASE = {
    "id": "G", "slug": "case-g", "title": "Case G — flow behind a tree belt",
    "short": "Field observation behind the Tsuiji-matsu tree belt (a porous windbreak, 74 m × 2 m × 7 m with a 1.2 m gap below): normalised mean speed and k at 28 points on the centre section (sonic anemometers).",
    "folder": "raw/cases/case-g",
    "reference_file": "raw/cases/case-g/RS_caseG.csv",
    "approach_flow_file": "raw/cases/case-g/AF_caseG.csv",
    "readme": "raw/cases/case-g/readme_caseG.md",
    "render": "validation/figures/geometry/case-g.png",  # the default configuration; see render_file
    "configuration": {
        "belt": "Tsuiji-matsu (Japanese black pine), trimmed to a rectangle; 74 m long (y), 2 m deep (x), 7 m tall, 1.2 m bottom gap; shading rate 81 % after pruning (data paper section 3.7)",
        "H_m": 7.0, "depth_m": 2.0, "width_m": 74.0, "gap_m": 1.2,
        "campaign": "field (full scale)", "location": "Taisha-machi, Hikawa-gun, Shimane, Japan; west end of an elementary-school playground",
        "wind_directions_deg": [0],
        "measurement_lines": "0.25 H, 0.5 H, 1 H, 2 H, 3 H, 4 H, 5 H behind the belt = x 1.75, 3.5, 7, 14, 21, 28, 35 m (H = 7 m)",
        "measurement_heights_m": [1.5, 3.0, 4.5, 6.0],
        "points": 28,
        "instrument": "3-D ultrasonic anemometers (KAIJO DA-600 with TR-90Tx) at four heights on a movable tower, 5 Hz, 10 min or more per line (26 Dec 2000); approach flow 120 min (28 Dec 2000) at 1.5, 3, 6, 9 m",
        "normalisation": "velocity_ratio = U/UH and k_ratio = k/UH^2, UH = the mean wind speed at 7 m during each measurement period (interpolated with the approach flow's power law, index 0.22); nothing is published in m/s",
        "approach_flow_normalisation": "AF_caseG.csv is U/Ub and k/Ub^2 with Ub = U at 9 m; divide by UH/Ub = 0.946 (power law 0.22) for the table's normalisation",
        "scale_note": "full scale: a field observation, there is no model",
    },
    "quantities": ["velocity_ratio", "k_ratio"],
    "units": {"length": "m (full scale)", "velocity_ratio": "dimensionless, U/UH", "k_ratio": "dimensionless, k/UH^2"},
    "frame": {
        "origin": "the leeward face of the tree belt at ground level, on the vertical section through the belt's centre",
        "x": "+x downwind: the belt occupies x in [-2, 0] m, the measurement lines lie behind it at x = 1.75 ... 35 m",
        "y": "+y along the belt (y in [-37, 37] m); every point is on y = 0",
        "z": "+z up; the belt spans z in [1.2, 7] m; points at z = 1.5, 3, 4.5, 6 m",
        "wind_direction_rotation": "one direction, toward +x (perpendicular to the belt); the field wind's angle to the belt normal is not published",
        "lateral_sign_applied": 1,
        "coordinate_scale_applied": 1.0,
    },
    "people": {
        "data_collectors": ["Yasuo Kurotani (Shimane University)", "Nobuyoshi Kiyota (Hiroshima Institute of Technology)"],
        "editors_distributors": EDITORS,
        "contact": "Yoshihide Tominaga <tominaga@abe.niit.ac.jp>",
    },
    "doi": "10.5281/zenodo.15589666",
    "doi_note": "The readme and the data paper name this one DOI; no separate version DOI is stated.",
    "citation_requested": "Kurotani, Y., Kiyota, N., Kobayashi, S. (2001). Windbreak effect of Tsuijimatsu in Izumo Part. 2. Summaries of technical papers of Annual Meeting, Architectural Institute of Japan, D-2 Environmental engineering II, 745-746 (in Japanese).",
    "inflow_fit": {
        "method": "power law on the four published heights (1.5, 3, 6, 9 m) of U/Ub; the readme states the index 0.22",
        "power_law_index_fitted": 0.2073, "power_law_index_stated": 0.22, "UH_over_Ub_power_law_0.22": 0.9462, "UH_over_Ub_log_interpolation": 0.938,
        "note": "derived during cleaning, not published as a fit; the profile carries 2 decimals, so the fitted index is good to about +/-0.01",
    },
    "known_issues": [
        "FIELD data: full-scale metres, no model, and nothing in m/s. The table carries U/UH (velocity_ratio) and k/UH^2 (k_ratio), UH = the mean speed at 7 m during each period; the approach-flow table carries U/Ub and k/Ub^2 (Ub = U at 9 m) in its U and k columns, which are dimensionless here.",
        "The readme lists the heights of the lee measurement as 1.5, 3.0, 6.0, 9.0 m; the table, the workbook, the drawing and the data paper have 1.5, 3, 4.5, 6 m.",
        "The tree belt is a POROUS canopy (shading rate 81 % after pruning), not a solid body: the served geometry is its 2 m × 74 m × 7 m envelope with the 1.2 m gap, and a solver needs a canopy (drag) model, not a wall.",
        "The approach profile (28 Dec 2000, 120 min) and the lee measurements (26 Dec 2000, 10 min or more) are from different days. Behind the belt k/UH^2 is 0.040-0.072 at 5 H, 3-8 times below the approach flow's 0.26-0.31 at the same heights; the files do not say why.",
        "Only 28 numbers per quantity exist, on one centre section, one time-average each, with no repeats and no uncertainty.",
        "The wind direction relative to the belt normal during the measurement is not published; the case is two-dimensional by assumption.",
    ],
}


def geometry(D, case):
    note = ("generated from the stated dimensions (2 m deep, 74 m long, 7 m tall, 1.2 m bottom gap), centred on y = 0 with its leeward face at x = 0; "
            "a porous canopy drawn as its envelope")
    return [("default", D.tris_of_boxes(BOXES), BOXES, note)]


def approach_flow(D, case):
    return clean_approach_flow(case)
