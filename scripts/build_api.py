"""Generate the static API under docs/api/ (and the generated site pages) from the cleaned data.

    python scripts/build_api.py            # build, then verify
    python scripts/build_api.py --check    # verify what is on disk; build nothing

Requirements: requirements.lock at the repository root (one pinned environment for every build here).

GitHub Pages serves docs/ at <site>/; every API file is a plain GET of a static file. The build is a pure
function of the repository: the same inputs give byte-identical outputs (no timestamps, no commit hashes),
so CI can rebuild and diff. Inputs:

- clean/                      the cleaned point tables (aijdata.load_points)
- the case folders            approach-flow profiles, Case D's STL, Case E's 3dm (aijdata)
- validation/results/         snapshots of the Eddy3D fixtures' results.json and per-point pairs, one entry
                              per run in RUNS below
- validation/figures/         the figures and geometry renders the site shows (1200 dpi masters)

Outputs: docs/api/** (the API), docs/assets/{figures,geometry}/ (the masters, copied), docs/assets/web/ (a 1600 px
copy of each, which the pages and the README embed, linked to its master), docs/_data/figures.json (their sizes, for
the include docs/_includes/figure.html), the figure blocks of README.md (between its <!--fig ...--> markers), docs/cases/<slug>.md and
docs/cases/<slug>/{data,validation}.md (three pages per case), docs/_includes/{case-gallery,cases-table,
cases-frames,validation-matrix,known-issues-fm,api-changelog}.md, docs/_includes/{version-label,dataset-jsonld}.html and
docs/llms.txt. The citations (scripts/citation.py) go into index.json `cite.api`, cases/{id}.json `citation`, the include
docs/_includes/cite.md, the Cite section of every Data page, the <!--cite--> block of README.md, CITATION.cff and
.zenodo.json. Every JSON document names its JSON Schema in `$schema`; the schemas are in scripts/api_schemas.py
and are enforced here before anything is reported OK.

The API is served twice, by the same code. Each release is a frozen copy of the whole API under docs/api/<release>/
(<release> is VERSION), every URL inside it pointing back into it; docs/api/ itself is the latest alias, the same
files addressed without the release. docs/api/versions.json, the one file that belongs to neither, lists every
release. A build rewrites the copy of VERSION and the alias and never touches another release's copy (released
copies are immutable: scripts/release.py check compares them with their tags). A release from before the layout
(LEGACY_RELEASES) is not regenerated. verify() checks every tree on its own, that the alias is the newest release
file for file, and the registry.
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import io
import json
import os
import re
import shutil
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aijdata as D  # noqa: E402
import api_schemas as S  # noqa: E402
import citation as C  # noqa: E402
import mathtext as MT  # noqa: E402
import nomenclature as NM  # noqa: E402
import page_prose as P  # noqa: E402
import release as R  # noqa: E402


def _load_layout():
    """validation/layout.py (standard library at import): the measurement groups of each case and the captions of its layout figure."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("aij_layout", os.path.join(D.REPO, "validation", "layout.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["aij_layout"] = mod
    spec.loader.exec_module(mod)
    return mod


LAYOUT = _load_layout()

REPO = D.REPO
DOCS = os.path.join(REPO, "docs")
API_ROOT = os.path.join(DOCS, "api")   # the latest alias, versions.json, and one frozen <release>/ tree per release
ASSETS = os.path.join(DOCS, "assets")
WEB = os.path.join(ASSETS, "web")      # the 1600 px copies the pages and the README show; the 1200 dpi masters stay the downloads
DATA_FILES = os.path.join(DOCS, "_data")
WEB_WIDTH = 1600
FIGURES = os.path.join(REPO, "validation", "figures")
FIGURE_INFO = {}                       # file name -> what a page needs to embed the figure; filled by copy_assets()
RESULTS_DIR = os.path.join(REPO, "validation", "results")

REPO_URL = C.REPO_URL
SITE = C.SITE
LIVE_BASE = SITE + "/api"         # the unversioned alias: always the newest release
RAW_BASE = "https://raw.githubusercontent.com/Eddy3D-Dev/AIJ-Data-Validation/main/docs/api"
SCHEMA_VERSION = "2.4.0"
RELEASE = R.version()             # the repository's release (VERSION); the API names it, it does not set it
RELEASE_DATE = R.release_date()
PINNED_BASE = f"{LIVE_BASE}/{RELEASE}"   # this release, frozen: nothing under it changes once the release is tagged
RELEASE_BASE = f"{RAW_BASE.replace('/main/', f'/v{RELEASE}/')}/{RELEASE}"   # the same frozen files, raw, at the tag

# Releases that predate the versioned layout. They are never regenerated. Their tree under docs/api/<release>/ is
# the tag's files with only their addresses rewritten (scripts/host_release.py); without one, the registry lists the
# tag and its raw files instead. Both values are the ones the release's own docs/api/index.json carries
# (git show v2.0.0:docs/api/index.json).
LEGACY_RELEASES = {
    "2.0.0": {"schema_version": "2.2.0", "data_version": "5af8c81571e452c1925b3efe58c698908066f64886eba5efd9b2f0348ecdc019"},
}

# State of the tree being written (see use_tree): build() writes the release tree, then the latest alias.
TREE = None              # "release" | "latest"
API = None               # the tree's directory
API_BASE = None          # the URL every document in the tree uses for its own files
FALLBACK_BASE = None     # the same tree, raw from the repository

CHANGELOG = [
    {"version": "2.4.0", "date": "2026-10-18", "changes": [
        "Added to index.json: `cite.api`, the citation of the API release (`title`, `version`, `url`, `release_url`, `doi`, `apa`, `bibtex`, "
        "`csl_json`). `url` is the pinned address of the release, `/api/<release>/index.json`; `doi` is null until Zenodo mints one for the release.",
        "Added to cases/{id}.json: `citation`, the Zenodo dataset of the case as `apa` and `bibtex`.",
        "Added to the `stats` of geometry.json and to the entries of the geometry index: `bodies`, `body_contacts`, `inconsistent_triangles` and "
        "`min_body_volume`, beside `edges_boundary`. `watertight` is true when every body is closed, consistently wound and positive in volume.",
        "Changed: the `geometry.stl` of Cases E, F and M. Every body is a closed, consistently wound, outward body; Cases F and M stand on a 1 m base "
        "slab, so the bounding box of each starts at z = -1 m, and `triangles` and `data_version` change with the files.",
        "Added: the layout figure of each case, `case-<id>-layout.png`, is the first entry of `figures` of the validation results of that case "
        "(Cases A to M); the agreement figures colour their points by the groups of that figure.",
    ]},
    {"version": "2.3.0", "date": "2026-10-18", "changes": [
        "Added: release-numbered paths. Every release is a frozen copy of the whole API under `/api/<release>/` (for example "
        "`/api/3.0.0/index.json`, `/api/3.0.0/cases/F.json`). Every URL to a file of the API inside a copy points into the same copy "
        "(versions.json, served only at the unversioned path, aside), so a client that starts there never leaves it, and "
        "nothing under it changes once the release is tagged. The unversioned "
        "`/api/` paths are unchanged and always equal the newest release (the `latest` alias).",
        "Added: `/api/versions.json` (schema `versions`), the list of every release, newest first: version, date, status "
        "(`latest` or `superseded`), schema_version, data_version, base_url, tag, release page and changelog. Release 2.0.0 "
        "predates the layout and is not regenerated: `/api/2.0.0/` holds the files of its tag byte for byte, with only their "
        "own addresses rewritten into the copy (scripts/host_release.py derives it and the release check re-derives it).",
        "Added to index.json: `tree` (`release` in a frozen copy, `latest` in the alias), `release_base_url` (the frozen copy "
        "of `versions.release`; equal to `base_url` inside that copy) and `versions_url`. In a frozen copy `base_url` and "
        "`fallback_base_url` name that copy, and `release.base_url` (the raw files at the release tag) now ends in the "
        "release number; paths below it are unchanged.",
        "Added: Cases F to M, thirteen cases in all (the `case_ids` of index.json): their cases.json entries, `cases/{id}.json`, "
        "points, approach flow, geometry (STL) and validation documents, and `pairs` files for the runs that exist. Every case has at "
        "least one scored run; an engine that has none for a case is `pending` there. `cases.json` and "
        "`validation.json` list thirteen cases (the schemas fixed the length at five).",
        "Added: the point table's columns of schema 2.0.0 (the cleaned release) are served in `points.json` and `points.csv`: "
        "`campaign` and `run`, `uv` `uw` `vw`, `C` `c_rms` `concentration_ratio`, `T` `T_rms`, `uc` `vc` `wc`, `uT` `vT` `wT`, "
        "`velocity_ratio_sd` and `k_ratio`; `instrument` takes the new values `cup_anemometer`, `sonic_anemometer`, `ldv`, "
        "`hydrocarbon_analyser` and `sorbent_gc_ecd`. A document lists only the columns a case has.",
        "Added: four engines, `openfoam12-kEpsilon` and `openfoam12-kOmegaSST`, which exist for Case I only (the closures other than "
        "realizable k-epsilon, solved on one mesh), and `umf-realizableKE` and `umf-buoyantKEpsilon`, Eddy3D's buoyant microclimate engine "
        "(urbanMicroclimateFoam, an OpenFOAM 12 solver) under its two closures, which exist for Cases J and L (`umf-buoyantKEpsilon` for J only). "
        "`engines` in `cases.json` and `cases/{id}.json` lists an engine only for the cases it applies to.",
        "Added to each result of validation.json: `notes`, a list of the caveats that come with the run (what the model leaves out, what the "
        "measurement cannot say, how the solve ended); empty where the run has none recorded. Cases F, G and M have several runs on one engine "
        "(Case F: one per vertical frame, Case G: one per arm of a drag sweep, Case M: one per turbulent Schmidt number, each as `configuration`), all sharing the engine's pairs file; "
        "the first column of Case F's and Case G's names the frame or the arm, and Case M's holds the three Schmidt numbers as columns.",
    ]},
    {"version": "2.2.0", "date": "2026-10-18", "changes": [
        "Added: `versions.release`, the semantic version of the published data and API (the repository's VERSION; "
        "tag vX.Y.Z; rules in CHANGELOG.md), and `release` with its date, tag, release page and `base_url`, the raw "
        "files of exactly that release (the tag never moves). `schema_version` stays the version of this JSON contract.",
    ]},
    {"version": "2.1.0", "date": "2026-10-15", "changes": [
        "Correction: index.json gave each templated endpoint (cases/{id}.json, schemas/{name}.schema.json, ...) its "
        "URI template under `url`, which is not a URL and answered 404 when followed. A templated endpoint now says "
        "`templated: true` and lists every concrete file under `urls`; `url` is given only for single-file "
        "endpoints, and no URL anywhere contains a brace. llms.txt lists the concrete files the same way.",
    ]},
    {"version": "2.0.0", "date": "2026-10-15", "changes": [
        "Breaking: cases/{id}.json `gotchas` is renamed `known_issues`.",
        "Breaking: `licence` is replaced by `license`, the SPDX identifier CC-BY-4.0; index.json `licence_detail` is `license_detail`.",
        "Breaking: `generated_from` and `generated_at` are removed. `data_version`, a SHA-256 over every served measurement, "
        "geometry and score file, changes when, and only when, the data does; the build is reproducible byte for byte.",
        "Breaking: links to JSON resources are named `url` (was `file`, `endpoint`, `endpoint_json`); file downloads are objects "
        "with `url`, `path`, `media_type`, `bytes` and `sha256` (points `csv`, approach-flow `csv`, run `pairs`, geometry files, "
        "the archive, and every entry of index.json `files`).",
        "Breaking: a validation result's `figures` is a list of {url, caption}.",
        "Added: validation.json, every case and engine in one table with each run's headline scores.",
        "Added: cases/{id}/pairs/{engine}.csv, the per-point measured and modelled values behind every scored run, so any score "
        "can be recomputed; linked from each result as `pairs`.",
        "Added: cases/{id}/approach_flow.csv, the measured approach-flow profile in SI units.",
        "Added: schemas/{name}.schema.json, the JSON Schema (draft 2020-12) of every document, named by its `$schema` and "
        "embedded in openapi.json.",
        "Added: `run_id` on every validation result; geometry renders and captions in geometry.json.",
        "Added: download URLs carry `?v=<SHA-256 prefix>`, so a changed file has a new URL and no cache serves a stale copy.",
        "Added: /llms.txt at the site root, and schema.org Dataset metadata on the home page.",
    ]},
    {"version": "1.0.0", "date": "2026-10-14", "changes": ["First release."]},
]
COMPATIBILITY = ("Semantic versioning, twice. `versions.release` versions what is served (MAJOR: a file, field or "
                 "column renamed or removed, or a unit or frame changed; MINOR: something added; PATCH: a value "
                 "corrected). Every release is also a frozen copy of the whole API under `/api/<release>/` whose files never "
                 "change (`release_base_url`; all releases in versions.json), and the unversioned /api/ paths always equal "
                 "the newest release: pin an analysis to a release by using that release's base URL. "
                 "`schema_version` versions this JSON contract: within a major version it only adds new fields, "
                 "endpoints and runs, clients must ignore fields they do not know, and a field is renamed or removed "
                 "only in a new major version, which the changelog names. `data_version` is a fingerprint: "
                 "the SHA-256 of the served data.")
CACHING = ("GitHub Pages sends JSON with a 10-minute max-age and CSV and ZIP files with a 186-day max-age. Every "
           "download URL therefore carries ?v=<first 12 hex digits of the file's SHA-256>: the server ignores the "
           "query, and a changed file gets a new URL. Fetch the JSON documents for the current URLs; check "
           "downloads against `sha256`.")

CASE_SPAN = f"{D.CASE_IDS[0]}-{D.CASE_IDS[-1]}"   # "A-M"
if f"Cases {CASE_SPAN}:" not in C.TITLE:
    raise SystemExit(f"scripts/citation.py TITLE names other cases than {CASE_SPAN}")

ENGINES = [
    {"id": "openfoam12-realizableKE", "name": "OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor)", "kind": "RANS"},
    {"id": "openfoam12-kEpsilon", "name": "OpenFOAM 12, standard k-epsilon (Eddy3D Outdoor)", "kind": "RANS"},
    {"id": "openfoam12-kOmegaSST", "name": "OpenFOAM 12, k-omega SST (Eddy3D Outdoor)", "kind": "RANS"},
    {"id": "umf-realizableKE", "name": "urbanMicroclimateFoam, realizable k-epsilon (Eddy3D Outdoor+)", "kind": "RANS"},
    {"id": "umf-buoyantKEpsilon", "name": "urbanMicroclimateFoam, buoyantKEpsilon (Eddy3D Outdoor+)", "kind": "RANS"},
    {"id": "openlb", "name": "OpenLB (Eddy3D LBM)", "kind": "LBM"},
    {"id": "fluidx3d", "name": "FluidX3D (Eddy3D GPU LBM)", "kind": "LBM"},
    {"id": "ml-surrogate", "name": "Eddy3D ML wind surrogate (pedestrian height)", "kind": "surrogate"},
]
STATUS_MEANING = {
    "scored": "a validation run exists and its scores are in cases/{id}/validation.json",
    "running": "the solve is in progress; no scores yet",
    "pending": "not run yet",
    "not comparable": ("the engine cannot produce the measured quantity at the measured location: OpenLB at the resolution "
                       "this hardware runs, FluidX3D without a ground wall function; the measurement behind each is on the "
                       "Validation page"),
}
# The closures other than realizable k-epsilon were solved for Case I alone (simpleFoam) and Case J (UMF): they are listed for the cases they apply to
# (ENGINE_STATUS has no entry for them elsewhere) and left out of the all-cases matrix. The matrix has one column for UMF, which applies to J and L only.
CLOSURE_VARIANTS = {"openfoam12-kEpsilon", "openfoam12-kOmegaSST", "umf-buoyantKEpsilon"}
_NOT_RUN = {"openfoam12-realizableKE": "pending", "openlb": "pending", "fluidx3d": "pending", "ml-surrogate": "pending"}
ENGINE_STATUS = {
    "A": {"openfoam12-realizableKE": "scored", "openlb": "scored", "fluidx3d": "scored", "ml-surrogate": "scored"},
    "B": {"openfoam12-realizableKE": "scored", "openlb": "scored", "fluidx3d": "scored", "ml-surrogate": "scored"},
    "C": {"openfoam12-realizableKE": "scored", "openlb": "not comparable", "fluidx3d": "not comparable", "ml-surrogate": "scored"},
    "D": {"openfoam12-realizableKE": "scored", "openlb": "not comparable", "fluidx3d": "not comparable", "ml-surrogate": "scored"},
    "E": {"openfoam12-realizableKE": "scored", "openlb": "not comparable", "fluidx3d": "not comparable", "ml-surrogate": "scored"},
    # Cases F to M: F, G, H, I, K and M have OpenFOAM 12 runs (I under three closures, G as a drag sweep, F in two vertical frames, M at three Schmidt
    # numbers); J and L, which are non-isothermal, have runs on UMF (J under two closures) and none on the isothermal solver. Nothing else has been run on F to M.
    "F": {**_NOT_RUN, "openfoam12-realizableKE": "scored"},
    "G": {**_NOT_RUN, "openfoam12-realizableKE": "scored"},
    "H": {**_NOT_RUN, "openfoam12-realizableKE": "scored"},
    "I": {**_NOT_RUN, "openfoam12-realizableKE": "scored", "openfoam12-kEpsilon": "scored", "openfoam12-kOmegaSST": "scored"},
    "J": {**_NOT_RUN, "umf-realizableKE": "scored", "umf-buoyantKEpsilon": "scored"},
    "K": {**_NOT_RUN, "openfoam12-realizableKE": "scored"},
    "L": {**_NOT_RUN, "umf-realizableKE": "scored"},
    "M": {**_NOT_RUN, "openfoam12-realizableKE": "scored"},
}
ENGINE_STATUS = {c: {e["id"]: st[e["id"]] for e in ENGINES if e["id"] in st} for c, st in ENGINE_STATUS.items()}   # in ENGINES order
QUEUED = "The solves for this case are queued; no result exists yet."


def case_engines(case):
    """The engines that apply to a case, in ENGINES order: those with a status for it."""
    return [e for e in ENGINES if e["id"] in ENGINE_STATUS[case]]


MATRIX_ENGINES = [e for e in ENGINES if e["id"] not in CLOSURE_VARIANTS]

# ----------------------------------------------------------------------------- runs
# Every validation run snapshotted in validation/results/: its case, engine and configuration, the scores
# to quote (label -> key in its results.json), its per-point pairs and what their columns are, the
# figures that show it, and how to reproduce it. A results file that is not listed here is an error.

PAIRS_AB = ("point_id; x, y, z in m (case frame); U, V, W measured (_meas) and modelled (_model), each divided by U_H; "
            "V in the unified sign (positive toward +y)")
PAIRS_ML = ("set (the scored subset); x_tunnel, y_tunnel in m (case frame); x_scene, y_scene in m (the scaled scene the "
            "surrogate was given); observed_over_UH and predicted_over_UH, the speeds divided by U_H (Case E: by U at 15.9 m)")


def run(case, engine, configuration, results, headline, figures, reproduce, pairs, pairs_columns, normalisation=None, notes=()):
    """normalisation: this run's own sentence where the default (velocities by U_H, k by U_H^2) does not say it; notes: the caveats that come with it."""
    return {"case": case, "engine": engine, "configuration": configuration, "results": results, "headline": headline,
            "figures": figures, "reproduce": reproduce, "pairs": pairs, "pairs_columns": pairs_columns, "normalisation": normalisation, "notes": list(notes),
            "run_id": f"{case}.{engine}" + (f".{configuration}" if configuration else "")}


PAIRS_H = ("point_id (the table's, the CSV's No.); x, y, z in m (case frame); U, V, W and k measured (_meas: the cleaned workbook values) and modelled (_model), "
           "velocities divided by U_H (measured by the tunnel's 3.226 m/s, modelled by the 3.23 m/s the solve was driven with), k by U_H^2, V in the unified sign "
           "(positive toward +y); cstar_meas, the measured concentration ratio C/c0 (c0 = 45.18 ppm), and cstar_sct03 / _sct05 / _sct07, the modelled "
           "c* = c U_H H^2 / Q for turbulent Schmidt numbers 0.3, 0.5 and 0.7 (one row per published point, empty where the quantity was not measured)")
PAIRS_I = ("instrument (ldv or hydrocarbon_analyser), point_id (the table's: wind points 1-91, concentration points 92-630); x, y, z in m (case frame); U, V, W and k "
           "measured (_meas: the cleaned workbook values; V is empty on the y = 0 plane) and modelled (_model), velocities by U_H = 1.7 m/s, k by U_H^2; cstar_meas, "
           "the measured C/c0 (c0 = 39.22 ppm), and cstar_sct03 / _sct05 / _sct07, the modelled c* for turbulent Schmidt numbers 0.3, 0.5 and 0.7 (a wind row has "
           "no concentration columns and a concentration row no velocity columns)")
_HI_REPRO = "Eddy3D fixture {fixture} (numerics level 3, 3000 iterations); figures validation/plot_cases_hi_openfoam.py; scores recomputed from the pairs by validation/dispersion_metrics.py"
_HI_HEADLINE = {"U": "velocity.U", "V": "velocity.V", "W": "velocity.W", "k": "k", "c*, Sct 0.3": "cstar.c_sct03", "c*, Sct 0.5": "cstar.c_sct05", "c*, Sct 0.7": "cstar.c_sct07"}
_FOAM_A_B = {"U": "velocity.U", "V": "velocity.V", "W": "velocity.W", "k": "k"}
_FOAM_C = {f"WD {wd} {q}": f"vs.{lab}.{key}" for wd, lab in (("0°", "wd-0"), ("22.5°", "wd22_5"), ("45°", "wd45"))
           for q, key in (("√(|U|²+2k)", "scalar"), ("|U|", "vector"))}
_ML_REPRO = "Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot_ml_surrogate.py"
RUNS = [
    *[run(c, "openfoam12-realizableKE", None, f"case{c}_openfoam12_realizableKE.json", _FOAM_A_B,
          [f"case-{c.lower()}-layout.png", "cases-ab-openfoam-agreement.png", "cases-ab-openfoam-profiles.png"],
          f"Eddy3D fixture TestAijCase{c}ContainerE2E; figures validation/plot_cases_ab_openfoam.py",
          f"case{c}_openfoam12_realizableKE_pairs.csv", PAIRS_AB) for c in ("A", "B")],
    *[run("C", "openfoam12-realizableKE", cb, f"caseC_openfoam12_realizableKE_{cb}.json", _FOAM_C,
          ["case-c-layout.png", "case-c-openfoam-agreement.png", "case-c-openfoam-bias-map.png"],
          f"Eddy3D fixture TestAijCaseC{cb}ContainerE2E; figures validation/plot_case_c_openfoam.py",
          "caseC_openfoam12_realizableKE_pairs.csv",
          "config (0D/1D/2D), wind_direction_deg, point_id; x, y, z in m (case frame); measured_over_UH, the thermistor "
          "Vs/U_H; scalar_over_UH, the modelled sqrt(|U|^2 + 2k)/U_H; vector_over_UH, the modelled |U|/U_H (all nine "
          "configurations in one file)") for cb in ("0D", "1D", "2D")],
    *[run(c, "openlb", None, f"case{c}_openlb.json",
          {"U": "velocity.U", "U, points ≥ 2 dx": "velocity.U.aboveTwoCells", "V": "velocity.V", "W": "velocity.W",
           "k (resolved)": "k.resolved", "V, lateral sign flipped (control)": "control.V.lateralSignFlipped"},
          ["cases-ab-engine-comparison.png"],
          f"Eddy3D fixture TestAijCase{c}OpenLbContainerE2E (OpenLB eddy3dWind, CPU image, dx = 1.6 m); "
          "figure validation/plot_cases_ab_engines.py", f"case{c}_openlb_pairs.csv", PAIRS_AB) for c in ("A", "B")],
    # FluidX3D is scored on the heights where its own empty-domain control holds the imposed log law within 5 %
    # (its bounce-back ground has no roughness wall function); the approach flow alone is the control to beat.
    # Case B's V is not a headline: every comparable point lies on the centre plane, where mean V is zero.
    *[run(c, "fluidx3d", None, f"case{c}_fluidx3d.json",
          {"U, comparable heights": "velocity.U.comparable",
           **({"V, comparable heights": "velocity.V.comparable"} if c == "A" else {}),
           "W, comparable heights": "velocity.W.comparable", "U, all points": "velocity.U.all",
           "U, approach flow alone (control)": "negativeControl.noBuilding.components.U.control"},
          ["cases-ab-engine-comparison.png"],
          f"Eddy3D fixture TestAijCase{c}FluidX3DE2E (Eddy3DCli.Tests/Validation/TestAijVelocityFluidX3DE2E; FluidX3D "
          f"GPU lattice Boltzmann, D3Q19 Smagorinsky LES, dx = H/64, {'40 + 200' if c == 'A' else '100 + 500'} H/U_H "
          "spin-up + averaging, with an empty-domain control on the same lattice); figure validation/plot_cases_ab_engines.py",
          f"case{c}_fluidx3d_pairs.csv", PAIRS_AB) for c in ("A", "B")],
    run("D", "openfoam12-realizableKE", None, "caseD_openfoam12_realizableKE.json",
        {"WD 0°, thermistor Vs · √(|U|²+2k)": "vs.0.corrected", "WD 0°, thermistor Vs · |U|": "vs.0.uncorrected",
         "WD 0°, split fibre |U|": "splitfibre.speed", "WD 0°, split fibre U": "splitfibre.U",
         "WD 22.5°, thermistor Vs · √(|U|²+2k)": "vs.22.5.corrected", "WD 22.5°, thermistor Vs · |U|": "vs.22.5.uncorrected",
         "WD 22.5°, rotation sense mirrored (control)": "vs.22.5.mirrored.corrected",
         "WD 45°, thermistor Vs · √(|U|²+2k)": "vs.45.corrected", "WD 45°, thermistor Vs · |U|": "vs.45.uncorrected",
         "WD 45°, rotation sense mirrored (control)": "vs.45.mirrored.corrected"},
        ["case-d-layout.png", "case-d-openfoam-agreement.png"],
        "Eddy3D fixture TestAijCaseDContainerE2E (EDDY3D_AIJD_HEADINGS=0,22.5,45); figure "
        "validation/plot_case_d_openfoam.py", "caseD_openfoam12_realizableKE_pairs.csv",
        "instrument (thermistor / split_fibre), wind_direction_deg, point_id; x, y, z in m (model frame); "
        "measured_over_UH, the thermistor's Vs or the split fibre's |U| over U_H; scalar_over_UH and vector_over_UH, "
        "the modelled sqrt(|U|^2 + 2k) and |U| over U_H; for the split fibre also U, V, W measured (_meas) and "
        "modelled (_model) over U_H"),
    run("E", "openfoam12-realizableKE", "SW", "caseE_openfoam12_realizableKE.json",
        {"before, √(|U|²+2k)": "vr.bc.SW.rms", "before, |U|": "vr.bc.SW.Umag", "after, √(|U|²+2k)": "vr.ac.SW.rms",
         "after, |U|": "vr.ac.SW.Umag", "no-construction ceiling control": "noConstruction.SW"},
        ["case-e-layout.png", "case-e-openfoam-agreement.png", "case-e-openfoam-bias-map.png"],
        "Eddy3D fixture TestAijCaseEContainerE2E (EDDY3D_AIJ_E_DIRECTIONS=SW, tabulated inlet); figures "
        "validation/plot_case_e_openfoam.py", "caseE_openfoam12_realizableKE_pairs.csv",
        "config (bc before / ac after construction), wind_direction, point_id; x, y, z in full-scale m (+x east, +y north); "
        "measured_ratio, the tunnel's velocity ratio; scalar_ratio and vector_ratio, the modelled sqrt(|U|^2 + 2k) and |U| "
        "over the model's own U at 15.9 m"),
    run("A", "ml-surrogate", None, "caseA_ml.json",
        {"|U| (z = 0.01 m plane)": "speed.vectorMagnitude", "|U|, lattice cut at ±250 m": "halfExtent250.forward",
         "wind reversed (control)": "negativeControl.reversedWind"},
        ["ml-surrogate-agreement.png"], _ML_REPRO, "caseA_ml_pairs.csv", PAIRS_ML),
    run("B", "ml-surrogate", None, "caseB_ml.json",
        {"|U| (z = H/16 plane)": "speed.vectorMagnitude", "|U|, lattice cut at ±250 m": "halfExtent250.forward",
         "wind reversed (control)": "negativeControl.reversedWind"},
        ["ml-surrogate-agreement.png"], _ML_REPRO, "caseB_ml_pairs.csv", PAIRS_ML),
    run("C", "ml-surrogate", None, "caseC_ml.json",
        {"Vs, 9 configurations": "speed.thermistor", "Vs, 2D WD 0, lattice cut at ±250 m": "halfExtent250.forward",
         "wind reversed (control)": "negativeControl.reversedWind"},
        ["ml-surrogate-agreement.png"], _ML_REPRO, "caseC_ml_pairs.csv", PAIRS_ML),
    run("D", "ml-surrogate", None, "caseD_ml.json",
        {"Vs, thermistor, 3 WD": "speed.thermistor", "|U|, split fibre, WD 0": "speed.vectorMagnitude",
         "Vs, WD 0, lattice cut at ±250 m": "halfExtent250.forward", "wind reversed (control)": "negativeControl.reversedWind"},
        ["ml-surrogate-agreement.png"], _ML_REPRO, "caseD_ml_pairs.csv", PAIRS_ML),
    run("E", "ml-surrogate", None, "caseE_ml.json",
        {"Vs/U(15.9 m), 16 WD, bc + ac": "speed.thermistor", "after construction": "speed.thermistor.after",
         "after − before": "delta.afterMinusBefore", "after, lattice cut at ±250 m": "halfExtent250.forward",
         "wind reversed (control)": "negativeControl.reversedWind"},
        ["ml-surrogate-agreement.png"], _ML_REPRO, "caseE_ml_pairs.csv", PAIRS_ML),
    # Cases H and I (Eddy3D's solves, scored against the cleaned tables): the closures other than realizable k-epsilon are separate engine ids
    run("H", "openfoam12-realizableKE", None, "caseH_openfoam12_realizableKE.json", _HI_HEADLINE, ["case-h-layout.png", "cases-hi-openfoam-agreement.png"],
        _HI_REPRO.format(fixture="TestAijCaseHContainerE2E (realizable k-ε, 1:100)"), "caseH_openfoam12_realizableKE_pairs.csv", PAIRS_H),
    run("I", "openfoam12-realizableKE", None, "caseI_openfoam12_realizableKE.json", _HI_HEADLINE, ["case-i-layout.png", "cases-hi-openfoam-agreement.png", "case-i-openfoam-closures.png"],
        _HI_REPRO.format(fixture="TestAijCubeContainerE2E (realizable k-ε, 1:60)"), "caseI_openfoam12_realizableKE_pairs.csv", PAIRS_I),
    run("I", "openfoam12-kEpsilon", None, "caseI_openfoam12_kEpsilon.json", _HI_HEADLINE, ["case-i-openfoam-closures.png"],
        _HI_REPRO.format(fixture="TestAijCubeContainerE2E (standard k-ε, 1:60)"), "caseI_openfoam12_kEpsilon_pairs.csv", PAIRS_I),
    run("I", "openfoam12-kOmegaSST", None, "caseI_openfoam12_kOmegaSST.json", _HI_HEADLINE, ["case-i-openfoam-closures.png"],
        _HI_REPRO.format(fixture="TestAijCubeContainerE2E (k-ω SST, 1:60)"), "caseI_openfoam12_kOmegaSST_pairs.csv", PAIRS_I),
]

# ---- Cases K, G, J and L (Eddy3D's solves of 2026-10-18, scored against the cleaned tables) ------------------------------------------------------------
PAIRS_K = ("point_id (the table's: the row order of RS_caseK.csv); x, y, z in m (model scale, case frame: +x streamwise, V positive toward +y); region (aboveRoof, lateralStreet = a street along the wind, "
           "crossStreet = across it) and near_source (1 within one cube height of the floor outlet); U, V, W and k measured (_meas: the cleaned workbook values) and modelled (_model), velocities by "
           "the stated U_H = 2.33 m/s on both sides, k by U_H^2; cstar_meas, the measured C/c0 (c0 = 429.2 ppm), and cstar_sct03 / _sct05 / _sct07, the modelled c* = c U_H H^2 / Q for turbulent "
           "Schmidt numbers 0.3, 0.5 and 0.7")
PAIRS_G = ("arm (open-field, pine, conifer, screen or half-belt-conifer: the five runs share this file), point_id (the table's, 1-28), x (m behind the leeward face) and z (m above ground), full scale; "
           "U_meas and k_meas, the field's U/U_H and k/U_H^2; U_model and Urms_model, the modelled |U| and sqrt(|U|^2 + 2k) over the arm's own U(7 m) at x = -35 m (u7_mps, in m/s), k_model, k over "
           "u7_mps^2; U_model_imposed and Urms_model_imposed, the same over the imposed U_H = 5.299 m/s")
PAIRS_J = ("point_id (the table's; point 153, a repeat of point 1, is left out); x, y, z in m (the tunnel's units and frame: x streamwise, the leeward wall at x = 0, V positive toward +y); region (aboveRoof, "
           "upstream, beside, nearWake, farWake) and near_source (1 within a quarter of the building height of the source, at or below z = H/4); U, V, W and k measured (_meas: the cleaned workbook values) "
           "and modelled (_model), velocities by U_H (1.4581 m/s for the measurement, the Froude-scaled 11.53 m/s for the model), k by U_H^2; T_meas_degC and T_model_degC; theta_meas and theta_model, "
           "(T_f - T)/(T_f - T_H) with T_f = 45.8 degC and T_f - T_H = 33.63 K; cstar_meas, the measured C/c0 (c0 = 12.28 ppm), and cstar_sct03 / _sct05 / _sct07, the modelled ethylene mass fraction "
           "as ppm over the same c0, for turbulent Schmidt numbers 0.3, 0.5 and 0.7")
PAIRS_L = ("point_id (the table's); x, y, z in m (the tunnel's units and frame: x streamwise, z from the block floor, V positive toward +y); region (road = in the streets between the cubes, block = above "
           "a cube, surround = beside the array); U, V, W, S (the speed |U|) and k measured (_meas: the cleaned workbook values) and modelled (_model), by U_H (1.3394 m/s for the measurement, the "
           "Froude-scaled 13.39 m/s for the model) and U_H^2; T_meas_degC and T_model_degC; theta_meas and theta_model, (T_f - T)/(T_f - T_H) with T_f = 45.01 degC and T_f - T_H = 30.26 K; cstar_meas, "
           "the measured C/c0 (c0 = 1728 ppm), and cstar_sct03 / _sct05 / _sct07, the modelled ethylene mass fraction as ppm over the same c0; U_approach and theta_approach, the model's own undisturbed "
           "approach column at the point's height: the control a model of the array has to beat")
_KG_REPRO = ("Eddy3D fixture {fixture} ({what}; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, {cells} cells, solved 2026-10-18); figures validation/plot_cases_gk_openfoam.py; scores recomputed "
             "from the pairs by validation/dispersion_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`")
_JL_REPRO = ("Eddy3D fixture {fixture} ({what}; urbanMicroclimateFoam, {closure}, {cells} air cells at Froude scale {scale}, 1500 air iterations, solved 2026-10-18); figures validation/plot_cases_jl_umf.py; "
             "scores recomputed from the pairs by validation/dispersion_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`")
_K_HEADLINE = {"U": "velocity.U", "V": "velocity.V", "W": "velocity.W", "k": "k",
               **{f"c*, Sct {s}": f"cstar.c_sct{s.replace('0.', '0')}" for s in ("0.3", "0.5", "0.7")},
               **{f"c*, Sct {s}, without the 4 near-source points": f"cstar.c_sct{s.replace('0.', '0')}.excludingNearSource" for s in ("0.3", "0.5", "0.7")},
               "U, y-symmetric ceiling (control)": "velocity.U.symmetryCeiling", "c*, y-symmetric ceiling (control)": "cstar.symmetryCeiling"}
_K_NORM = ("U, V, W by the stated U_H = 2.33 m/s and k by U_H^2, the same divisor on both sides; c* is the measured C/c0 (c0 = q/(U_H H^2) = 429.2 ppm) against the modelled c U_H H^2/Q (full scale, "
           "Q = 1 kg/s) for turbulent Schmidt numbers 0.3, 0.5 and 0.7, with one detection limit of 10^-3 of the largest measured value; hit rate D = 0.25, W = 0.05 in U_H")
_K_NOTES = [
    "The inflow is the measured approach profile (3.23 m/s at 0.2 m, z0 fitted to 13.5 mm). The stated U_H = 2.33 m/s is not on that profile: the solved U at z = H is 1.97 m/s, 0.85 of the "
    "stated U_H. Measured and modelled velocities are both divided by 2.33 m/s, so the modelled velocity sits under the measured mean.",
    "The inlet k from that log law, u*^2/sqrt(Cmu) = 0.77 m^2/s^2, is about 1.7 times the tunnel's 0.33 to 0.45.",
    "The first measurement point is the source location: the four points within one cube height of the floor outlet hold the four largest c* (8.73, 5.31, 3.02 and 2.86 against 1.03 for the next). "
    "The model's source is the 4 cells (0.75 m across) that a 0.44 m square cuts; the outlet is 5 mm. Those four points are scored with and without.",
    "47 of the 203 points (the z = 4 mm plane, 0.4 m at 1:100) lie inside the first ground cell (0.735 m): their modelled values are that cell's, pulled toward the wall's zero by the point interpolation.",
    "The measured plume is not y-symmetric (C at -y exceeds C at +y at 74 of 74 mirror pairs; its lateral centroid lies 0.011 to 0.017 m toward -y at every station) and the solve is. The "
    "'y-symmetric ceiling' controls score the measurement against the mean of each mirror pair, the best a y-symmetric model can do on this file.",
    "V has a constant offset and almost no antisymmetric part, so it does not score the flow's divergence; a model with V = 0 everywhere hits 0.91 of the points at W = 0.05 U_H, so V's hit rate says nothing.",
    "The solve stopped at the 3000-iteration limit with the residualControl unmet (no 'solution converged' line); the epsilon initial residual at the last iteration was 7e-3.",
    "The air over the roofs outruns the street along the wind, which outruns the cavity across it; the plume leaves the source, is clean 1 to 1.5 H ahead of the array, decays through four cavities and is "
    "cleaner over the roofs than in them; the solved velocity is y-symmetric to twice the tunnel's own mirror-pair difference.",
]
_G_ARMS = [("open-field", "no belt", 90576, " (control: no belt)"), ("pine", "pine, Cd·LAD 0.30 1/m", 90576, ""), ("conifer", "conifer, Cd·LAD 0.625 1/m", 90576, ""),
           ("screen", "screen, Cd·LAD 0.875 1/m", 90576, ""), ("half-belt-conifer", "the real 74 m belt as a half domain, conifer, Cd·LAD 0.625 1/m", 625252, "")]
_G_NORM = ("the field's U/U_H and k/U_H^2 (U_H = the wind at the tree height, 7 m, during each period) against the model's |U| and k over the model's own U(7 m) at x = -35 m ('own approach') and, in the "
           "second set of scores, over the imposed U_H = 5.299 m/s ('imposed'); the model is also scored as sqrt(|U|^2 + 2k), because the field is the mean of an instantaneous speed; hit rate D = 0.25, W = 0.05")
_G_CAL = "LAD and Cd are not in the dataset (only the shading rate, 81 %). The drag values are crowns of the Eddy3D vegetation library."
_G_NOTES = [
    _G_CAL,
    "The three crowns are entries of the Eddy3D vegetation library (Cd·LAD 0.30, 0.625 and 0.875 1/m, loss coefficients 1.2, 2.5 and 3.5). The arm nearest the 28 values says which "
    "library crown the belt resembles.",
    "Eddy3D models trees as a Darcy-Forchheimer momentum sink only: there are no canopy k or epsilon source terms. The modelled k behind the belt follows from the inflow and the shear layer over the belt.",
    "The slab arms idealise the belt as two-dimensional (the belt through both slip planes, infinite width; the data paper's Figure 7 draws a two-dimensional tree); the half-belt arm is the real 74 m belt "
    "on a half domain with its centre plane on the symmetry plane. Both are scored against the same 28 values.",
    "The tabulated inlet carries the workbook's inflow over a smooth floor (the site's roughness is not in the model), so the approach flow does not stay the imposed profile: in the open-field arm it is "
    "1.19 of it at 1.5 m and 0.995 at 7 m at x = -10 m, and the model's U(7 m) at x = -35 m is 0.976 to 0.984 of the imposed U_H. The headline scores divide the model by that own U(7 m).",
    "The field is the mean of the instantaneous speed of a 3-D sonic anemometer, which exceeds |U| in a turbulent wake: the model is scored as |U| and as sqrt(|U|^2 + 2k), the bracket of Cases C to E.",
    "The approach profile and the wake were measured on different days (28 and 26 December 2000), and the approach k does not match the workbook's own inflow note (k/U_b^2 = 0.20 at 9 m against the "
    "note's constant 3.02 m^2/s^2, 0.096 U_b^2). The files do not explain the mismatch.",
    "Every arm ran to the 3000-iteration limit with the residualControl unmet; the epsilon initial residual at the last iteration was 2.7e-2 to 3.6e-2 in the slab arms and 3.2e-2 in the half belt.",
    "Every arm with trees shows a velocity deficit directly behind the belt against the open field, recovery with distance, a speed-up through the 1.2 m gap, and more drag slowing the lee more and "
    "pushing more wind through the gap.",
]
_J_HEADLINE = {"U": "velocity.U", "V": "velocity.V", "W": "velocity.W", "k": "k", "θ, floor-referenced temperature": "theta",
               **{f"c*, Sct {s}": f"cstar.c_sct{s.replace('0.', '0')}" for s in ("0.3", "0.5", "0.7")},
               **{f"c*, Sct {s}, without the near-source points": f"farFromSource.cstar.c_sct{s.replace('0.', '0')}" for s in ("0.3", "0.5", "0.7")},
               "U, y-symmetric ceiling (control)": "velocity.U.symmetryCeiling"}
_J_NORM = ("the tunnel's units: velocities by U_H (1.4581 m/s measured, the Froude-scaled 11.53 m/s modelled), k by U_H^2, temperature as theta = (T_f - T)/(T_f - T_H) (T_f = 45.8 degC, T_f - T_H = 33.63 K), "
           "c* = C/c0 (c0 = 12.28 ppm) against the modelled ethylene mass fraction as ppm over the same c0; hit rate D = 0.25, W = 0.05 in those units, concentration with one detection limit of 10^-3 of the "
           "largest measured value; 443 points (point 153 repeats point 1)")
# per closure: outflow over emission at Sct 0.3, 0.5, 0.7; reattachment length at z/H = 0.25 and 0.025; initial residuals of U_y, p_rgh and the tracers at the last air iteration
_J_CLOSURES = {"realizableKE": ("realizable k-ε", (0.89, 0.75, 0.62), (1.35, 1.35), "1.3e-2", "1.5e-2", "1.1e-3 to 1.7e-3"),
               "buoyantKEpsilon": ("buoyantKEpsilon", (0.95, 0.84, 0.73), (1.35, 1.56), "1.3e-2", "1.1e-2", "1.2e-3 to 1.6e-3")}


def _j_notes(closure):
    _, bal, lr, uy, prgh, tracer = _J_CLOSURES[closure]
    return [
        "The scene is the tunnel at Froude scale 62.5 (the production case writer cannot mesh a 0.16 m building): lengths times 62.5, velocities times 7.9, temperatures unchanged. That keeps the bulk "
        "Richardson number (-0.0856), Pr, the tunnel's Kelvin values and the dimensionless tracer, and does not keep Re (1.6e4 in the tunnel, 8e6 here), where UMF's wall functions belong and the "
        "tunnel's laminar-sublayer heat transfer does not exist.",
        "UMF's first cell is 0.75 m, 12 mm at tunnel scale: the tunnel's 24 K drop in air temperature between the floor and the first measurement at 3 mm lies inside it, so near-floor temperature is a "
        "wall-function result, and the data's tracer peak 4 mm above the 5 mm hole is a source-cell-limited number. The source is a mass rate into one pair of cells, with no release momentum and no heat "
        "from the 30.4 degC gas. The 27 points within a quarter of a building height of the source are scored with and without.",
        "The building is not adiabatic here: its walls are held at the measured mean surface temperature, 297.62 K, and the measured 4 K vertical gradient up the walls is not modelled. There is no sun, and the radiation exchange is at the least the view-factor model accepts (air-side emissivity 0.01).",
        f"The tracer is solved steady beside the flow, as three species of one flow. The outlet carried {bal[0]:.2f}, {bal[1]:.2f} and {bal[2]:.2f} of the emission for Sct 0.3, 0.5 and 0.7, "
        "within the factor of two accepted as a check on the wiring.",
        f"The air region ended at its 1500-iteration cap with the residualControl unmet (no 'solution converged' line); at the last iteration the initial residuals were {uy} (U_y), {prgh} (p_rgh) and "
        f"{tracer} (the tracers).",
        f"The steady closure gives a longer recirculation than the tunnel: reattachment at z/H = 0.25 and 0.025 is {lr[0]:.2f} H and {lr[1]:.2f} H, against the measured 0.68 H and 0.80 H.",
        "The measured +y half of the z/H = 0.25 plane runs 11 % slower than the -y half (97 mirror pairs, R 0.955, recomputed from the cleaned table): the y-symmetric ceiling control scores the measurement "
        "against the mean of each mirror pair.",
        "The wake recirculates behind the leeward face and reattaches within 3 H; the approach layer is unstable and the first cell above the heated floor is warmer "
        "than the air that entered it; every species is emitted, with clean air 25 m ahead of the building and its maximum at the source, and leaves through the outlet at 0.5 to 2 times the emission.",
    ]


_L_HEADLINE = {"U": "velocity.U", "V": "velocity.V", "W": "velocity.W", "|U|": "speed", "k": "k", "θ, floor-referenced temperature": "theta",
               **{f"c*, Sct {s}": f"cstar.c_sct{s.replace('0.', '0')}" for s in ("0.3", "0.5", "0.7")},
               "U, points at or above 30 mm": "comparable.velocity.U", "k, points at or above 30 mm": "comparable.k", "θ, points at or above 30 mm": "comparable.theta",
               **{f"c*, Sct {s}, points at or above 30 mm": f"comparable.cstar.c_sct{s.replace('0.', '0')}" for s in ("0.3", "0.5", "0.7")},
               "V, lateral sign flipped (control)": "control.V.flippedSign", "U, approach column alone (control)": "control.U.approachOnly",
               "θ, approach column alone (control)": "control.theta.approachOnly", "U, y-symmetric ceiling (control)": "velocity.U.symmetryCeiling"}
_L_NORM = ("the tunnel's units: velocities by U_H (1.3394 m/s measured, the Froude-scaled 13.39 m/s modelled), k by U_H^2, temperature as theta = (T_f - T)/(T_f - T_H) (T_f = 45.01 degC, T_f - T_H = 30.26 K), "
           "c* = C/c0 (c0 = 1728 ppm) against the modelled ethylene mass fraction as ppm over the same c0; hit rate D = 0.25, W = 0.05 in those units, concentration with one detection limit of 10^-3 of the "
           "largest measured value")
_L_NOTES = [
    "The scene is the tunnel at Froude scale 100 (lengths times 100, velocities times 10, temperatures unchanged), which keeps the bulk Richardson number (-0.034) and the tunnel's Kelvin values and does not keep Re.",
    "What the model does not represent: the gas's own heat and the buried slot (a mass rate into 624 whole cells, a strip 3 m wide), the tunnel's near-floor temperature drop (below the "
    "first cell), the measured velocity profile (UMF's inlet is a log law), the tunnel's no-slip side walls and ceiling (slip here), radiation (emissivity 0.01, effectively off) and the 10 mm raised block floor.",
    "51 of the 344 points (z = 4 mm, 0.4 m here) lie inside the first fine cell (0.75 m), a wall-function cell. The 242 points at or above 30 mm are scored separately.",
    "The street air is nearly stagnant in the model: the mean U/U_H in the streets is 0.045 below 30 mm and 1.11 above 110 mm, against the tunnel's 0.297 and 1.068; the model's "
    "approach column differs from the tunnel's AF profile by up to 39 % above 30 mm (UMF's inlet is a log law, the tunnel's profile is not).",
    "The tracer is solved steady beside the flow, as three species of one flow. The outlet carried 0.86, 0.73 and 0.70 of the emission for Sct 0.3, 0.5 and 0.7, within the factor of two accepted as a check "
    "on the wiring. The largest modelled c* over the 344 points is in the source street for every species, at y = -0.12 m (Sct 0.3) and y = +0.18 m (Sct 0.5 "
    "and 0.7), against the tunnel's 1.929 at (-0.15, -0.12, 0.004).",
    "The air region ended at its 1500-iteration cap with the residualControl unmet (no 'solution converged' line); at the last iteration the initial residuals were 2.6e-2 (U_y), 3.0e-2 (p_rgh) and "
    "1.1e-3 to 2.0e-3 (the tracers).",
    "The tunnel is not y-symmetric although the array is: over 110 mirror pairs the mean |U(y) - U(-y)| is 0.143 U_H in the tunnel and 0.058 U_H in the model. V is barely antisymmetric in the tunnel, "
    "so it cannot be scored as a pattern; the sign-flipped control shows what a wrong sign scores.",
    "The inlet's U_H reaches the array within 20 %; the approach air is warmest at the floor; the street air near the floor is warmer than the approach air at H and "
    "cools with height; the street flow is slower than the flow above the array; every species emits and its largest value is in the source street.",
]
RUNS += [
    run("K", "openfoam12-realizableKE", None, "caseK_openfoam12_realizableKE.json", _K_HEADLINE, ["case-k-layout.png", "case-k-openfoam-agreement.png"],
        _KG_REPRO.format(fixture="Eddy3DCli.Tests/Validation/TestAijCaseKContainerE2E", what="9 x 9 cubes, floor point source, 1:100", cells="972,637"), "caseK_openfoam12_realizableKE_pairs.csv", PAIRS_K,
        normalisation=_K_NORM, notes=_K_NOTES),
    *[run("G", "openfoam12-realizableKE", arm, f"caseG_openfoam12_realizableKE_{arm}.json",
          {f"|U|/U(7 m){sfx}": "score.U.ownApproach", f"√(|U|²+2k)/U(7 m){sfx}": "score.rms.ownApproach", f"k/U(7 m)²{sfx}": "score.k.ownApproach",
           f"|U|/U_H, imposed{sfx}": "score.U.imposedUH", f"√(|U|²+2k)/U_H, imposed{sfx}": "score.rms.imposedUH"},
          ["case-g-layout.png", "case-g-openfoam-sweep.png", "case-g-openfoam-stations.png"],
          _KG_REPRO.format(fixture="Eddy3DCli.Tests/Validation/TestAijCaseGContainerE2E", what=f"arm: {what}, full scale", cells=f"{cells:,}"), "caseG_openfoam12_realizableKE_pairs.csv", PAIRS_G,
          normalisation=_G_NORM, notes=_G_NOTES) for arm, what, cells, sfx in _G_ARMS],
    *[run("J", f"umf-{closure}", None, f"caseJ_umf_{closure}.json", _J_HEADLINE, ["case-j-layout.png", "case-j-umf-agreement.png", "case-j-umf-tracer.png"],
          _JL_REPRO.format(fixture="MetaFOAM.Lib.Tests/TestAijCaseJUmfContainerE2E", what="1:1:2 building, heated floor, floor point source", closure=_J_CLOSURES[closure][0], cells="236,408", scale="62.5"),
          f"caseJ_umf_{closure}_pairs.csv", PAIRS_J, normalisation=_J_NORM, notes=_j_notes(closure)) for closure in _J_CLOSURES],
    run("L", "umf-realizableKE", None, "caseL_umf_realizableKE.json", _L_HEADLINE, ["case-l-layout.png", "case-l-umf-agreement.png"],
        _JL_REPRO.format(fixture="MetaFOAM.Lib.Tests/TestAijCaseLUmfContainerE2E", what="9 x 14 cubes, heated floor, floor line source", closure="realizable k-ε", cells="754,940", scale="100"),
        "caseL_umf_realizableKE_pairs.csv", PAIRS_L, normalisation=_L_NORM, notes=_L_NOTES),
]

# ---- Cases F and M (Eddy3D's solves of 2026-10-18, scored against the cleaned tables) ------------------------------------------------------------
PAIRS_F = ("frame (literal or agl: the two runs share this file), source (tunnel: the thermistor at 5, 9 and 20 m; field: the cup anemometers), plane_m (the instrument height above ground by the readme's "
           "rule: 5, 9 or 20 for the tunnel, 3 to 11 for the field), point_id (the table's); x and y in m and z_published, the height above the tunnel floor in m, full scale (+x east, +y north); "
           "z_probe, the height the model was probed at (the published z in the literal frame; the STL's own ground under the point plus plane_m in the agl frame) and height_above_stl_ground, the "
           "probe's height above that ground; observed, the cleaned table's U/U(500 m) for wind from NNW, and observed_sd, the standard deviation of the 10-minute means behind a field value; "
           "observed_sse, the tunnel's 9 m value for the opposite wind (SSE) at the same point, for the compass control; Umag_model and rms_model, the modelled |U| and sqrt(|U|^2 + 2k) over the "
           "model's own approach U(500 m) (U500 in the results file); k_model, k in m^2/s^2")
PAIRS_M = ("point_id (the tunnel's); x, y, z in m (the release's frame, full scale: x north, y west, z above the tunnel floor); U, V, W, speed (the magnitude of the velocity vector) and k at WD 180, measured "
           "(_meas: the cleaned workbook values over the tunnel's U_R = 4.08 m/s, k over U_R^2) and modelled (_model: over the solved speed at the reference mast, 4.686 m/s; U is the case's +y, V = -U_x, "
           "W = U_z); cstar_meas, the measured C/c0 at WD 180 (c0 = 132.514 ppm), cstar_wd175 and cstar_wd185, the same at the tunnel's neighbouring headings, and cstar_sct03 / _sct05 / _sct07, the "
           "modelled c* = c U_R H_R^2 / Q (H_R = 40.8 m, Q = 1 kg/s) for turbulent Schmidt numbers 0.3, 0.5 and 0.7; cstar_<sct>_turned180 and cstar_<sct>_mirrored, the model's c* at the 15 points turned "
           "180 degrees about the source and mirrored across the plume axis (3 m above the ground or a roof there; empty where the control point is not in the fluid); cstar_field_geomean, _min and _max, "
           "the field campaign's geometric mean, minimum and maximum of c* over its 10 runs within 10 degrees of 180 at 3 m/s or more (each run's own U_R and q, H_R = 41 m)")
_FM_REPRO = ("Eddy3D fixture {fixture} ({what}; OpenFOAM 12 realizable k-ε, numerics level 3, {iterations} iterations, {cells} cells, solved 2026-10-18); figures validation/plot_cases_fm_openfoam.py; "
             "scores recomputed from the pairs by validation/dispersion_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`")
_F_HEADLINE = {**{f"Tunnel, {lab}, √(|U|²+2k)": f"tunnel.{key}.rms" for lab, key in (("9 m plane", "9m"), ("5 m plane", "5m"), ("20 m plane", "20m"), ("all 33 points", "all"))},
               **{f"Tunnel, {lab}, |U|": f"tunnel.{key}.Umag" for lab, key in (("9 m plane", "9m"), ("5 m plane", "5m"), ("20 m plane", "20m"), ("all 33 points", "all"))},
               "Field, √(|U|²+2k)": "field.rms", "Field, |U|": "field.Umag", "Tunnel, 9 m plane, √(|U|²+2k) over the imposed U(500 m) = 10 m/s": "tunnel.9m.rms.byImposedUR",
               "Tunnel's 9 m column as a model of the field (ceiling control)": "control.tunnelAsModelOfField",
               "Tunnel's SSE column, the opposite wind, against the solved NNW field (compass control)": "control.sense.opposite"}
_F_NORM = ("the thermistor's (tunnel) and the cup anemometer's (field) mean speed over U(500 m), the benchmark's own ratio, against the model's |U| and sqrt(|U|^2 + 2k) over its own approach U(500 m) "
           "= 9.862 m/s (the imposed U(500 m) is 10 m/s); hit rate D = 0.25, W = 0.05 in those units; 33 tunnel points and 13 field observations of wind from NNW; FB is positive when the model is low")
_M_HEADLINE = {"c*": "cstar", "c*, over the imposed speed at the mast's height (3.934 m/s)": "cstar.byImposedMastSpeed", "c*, over the tunnel's U_R = 4.08 m/s": "cstar.byPaperUR",
               "c*, points turned 180° about the source (control)": "control.turned180", "c*, points mirrored across the plume axis (control)": "control.mirrored",
               "c*, tunnel WD 175 as a model of its WD 180 (control)": "control.tunnelWD175AsModelOfWD180", "c*, tunnel WD 185 as a model of its WD 180 (control)": "control.tunnelWD185AsModelOfWD180",
               "c*, mean of the tunnel's WD 175 and WD 185 as a model of its WD 180 (control)": "control.tunnelNeighbourMeanAsModelOfWD180",
               "c* against the field's geometric mean (10 runs)": "field.vsGeometricMean", "c*, tunnel WD 180 as a model of the field's geometric mean (control)": "field.tunnelAsModelOfGeometricMean",
               "U": "velocity.U", "V": "velocity.V", "V, sign flipped (control)": "velocity.V.flipped", "W": "velocity.W", "|U|": "velocity.magnitude", "k": "k"}
_M_NORM = ("U, V, W and k at the 15 points over the tunnel's U_R = 4.08 m/s on the measurement and over the solved speed at the reference mast on the model (U_R is defined at the mast), k over U_R^2; "
           "c* = C/c0 (c0 = q/(U_R H_R^2) = 132.5 ppm) against the model's c U_R H_R^2/Q (H_R = 0.068 m x 600, Q = 1 kg/s) for turbulent Schmidt number {sct}, with one detection limit of 10^-3 of the "
           "largest measured value; hit rate D = 0.25, W = 0.05 in those units; the Schmidt numbers are three runs on one flow")


def _res(name):
    with io.open(os.path.join(RESULTS_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def _f_notes(frame):
    a, b = _res("caseF_openfoam12_realizableKE_literal.json"), _res("caseF_openfoam12_realizableKE_agl.json")
    me, other = (a, b) if frame == "literal" else (b, a)
    nine = lambda r: r["tunnel.9m.rms"]  # noqa: E731
    sl = me["solveLog"]
    res = sl["finalInitialResiduals"]
    mesh = me["meshCheck"]
    anem = me["anemometers"]
    notes = [
        "One direction of the tunnel's twelve was solved: wind from NNW, which with ENE has the most tunnel rows (33). The other eleven tunnel directions "
        "and the field's other fifteen were not run.",
        ("Frame 'literal': the model is probed at the published z in the STL's frame. The readme says z is measured from the tunnel floor and the ground is z - 10 m, but the STL's own ground under all 13 points is "
         "5 m, so the 5, 9 and 20 m planes are probed 10, 14 and 25 m above the STL's ground (height_above_stl_ground in the pairs). The other frame, 'agl' (the STL's ground plus 5, 9 and 20 m), is the other run "
         "of this case." if frame == "literal" else
         "Frame 'agl': the model is probed at the STL's own ground under each point plus the instrument height (5, 9 and 20 m for the tunnel, 3 to 11 m for the field). The readme says z is measured from the tunnel "
         "floor and the ground is z - 10 m, but the STL's ground under all 13 points is 5 m, so the published z would sit 5 m higher; that frame is the other run of this case, 'literal'.")
        + f" The files do not say which frame the tunnel meant: the 9 m plane's √(|U|²+2k) scores R {nine(a)['R']:.2f} and FB {nine(a)['Fb']:+.2f} in the literal frame and R {nine(b)['R']:.2f} "
          f"and FB {nine(b)['Fb']:+.2f} in the agl frame.",
        f"Both sides are U/U(500 m): the tunnel's ratio is as published, the model's is over its own approach U(500 m) = {me['U500']:.3f} m/s, probed 1100 m upwind of the centre ({me['U500'] / 10:.3f} of the imposed 10 m/s). "
        f"Over the imposed 10 m/s the 9 m plane's √(|U|²+2k) scores R {me['tunnel.9m.rms.byImposedUR']['R']:.2f} and FB {me['tunnel.9m.rms.byImposedUR']['Fb']:+.2f}.",
        "The thermistor reads a scalar speed and so does the cup anemometer: the model is scored as |U|, which is the lower bound, and as √(|U|²+2k), the speed of a velocity with the modelled turbulent kinetic "
        "energy in all three components, which is the upper bracket (as in Cases C to E).",
        f"The field is a year of 10-minute means above 5 m/s at a rooftop reference, over a sector 22.5° wide, at 3 to 11 m above ground; the standard deviation of the means behind each value is 0.075 to 0.15 of "
        f"U(500 m), 0.20 to 0.78 of the value itself (the horizontal bars of the figure), and a RANS field is one steady state for one exact direction. The tunnel's 9 m column scored as a model of the field, point "
        f"for point, gives R {me['control.tunnelAsModelOfField']['R']:.2f}, FAC2 {me['control.tunnelAsModelOfField']['Fac2']:.2f}, FB {me['control.tunnelAsModelOfField']['Fb']:+.2f}: the bar a model of the tunnel is not expected to clear.",
        "The field values of point 14 are the cleaned table's, realigned with the workbook: the published RS-FO_caseF.csv holds them shifted by one direction (clean/QUESTIONS.md QF1). The field scores here therefore differ "
        "from Eddy3D's own results file in the third decimal (√(|U|²+2k) in the literal frame: R 0.8729 here, 0.8731 there; in the agl frame 0.8893 and 0.8872); the tunnel scores are identical to it.",
        f"The published STL is open along the rim of its 725 m disc (812 boundary edges, one shell, wound inward), which the canvas's pre-meshing pass cannot close (it removed 3 degenerate faces). The mesh has {mesh['cells']:,} cells "
        f"and checkMesh fails one check ({mesh['highlySkewFaces']} highly skew faces, maximum skewness {mesh['maxSkewness']:.1f}, maximum non-orthogonality {mesh['maxNonOrthogonalityDeg']:.1f}°), so the solve started on the "
        "hardened numerics of Eddy3D's mesh-quality tier.",
        f"The solve ran to its {sl['iterationsRun']}-iteration limit with the residualControl unmet (no 'solution converged' line); the initial residuals at the last iteration were U_x {res['Ux']:.1e}, U_y {res['Uy']:.1e}, "
        f"U_z {res['Uz']:.1e}, p {res['p']:.1e}, epsilon {res['epsilon']:.1e} and k {res['k']:.1e}, and the log has {sl['boundingKLines']:,} 'bounding k' lines.",
        f"The solved field correlates R {a['tunnel.9m.rms']['R']:.2f} with the tunnel's 9 m column for the wind from NNW and R {a['control.sense.opposite']['R']:.2f} with its column for the opposite wind, SSE (agl frame: "
        f"{b['tunnel.9m.rms']['R']:.2f} and {b['control.sense.opposite']['R']:.2f}). A RANS field knows no compass, so this supports reading the direction labels as the direction the wind comes from "
        "(clean/QUESTIONS.md QF9), at this one direction.",
        f"The model's U/U(500 m) at the workbook's two rooftop anemometers (SMB {anem['smb.Umag']:.2f} for |U|, KDD {anem['kdd.Umag']:.2f}) is in the results file and not scored: the tunnel's anchors for them "
        "exist for the north and south tests only.",
    ]
    if frame == "agl":
        notes.insert(2, "At the 4 m surface cells of the mesh the lowest probes of this frame (the 7 points of the 5 m plane, 1.25 cells above the ground, and the field's point at 3 m) sit in the first cell, where the point "
                        "interpolation is pulled toward the wall's zero.")
    return notes


def _m_notes(sp):
    runs = {s: _res(f"caseM_openfoam12_realizableKE_{s}.json") for s in ("sct03", "sct05", "sct07")}
    r = runs[sp]
    sl, mesh = r["solveLog"], r["meshCheck"]
    res = sl["finalInitialResiduals"]
    c = lambda m: f"R {m['R']:+.2f}, FAC2 {m['Fac2']:.2f}, FB {m['Fb']:+.2f}"  # noqa: E731
    each = lambda key, fmt: " / ".join(format(x[key], fmt) for x in runs.values())  # noqa: E731
    tn, tf = r["cstar.tunnel.nearThreeMean"], r["cstar.tunnel.farTwoMean"]
    reversed_ = [sct for sct, x in zip(("0.3", "0.5", "0.7"), runs.values()) if not x["cstar.nearBeatsFar"]]
    # The readings below are written for these numbers; a rebuilt solve that breaks one has to be read again.
    assert reversed_ == ["0.7"], reversed_
    assert all(x["control.mirrored"]["R"] > x["cstar"]["R"] and x["control.meanTurned180"] < 1e-3 * x["control.meanReal"] for x in runs.values())
    return [
        f"One heading and one steady solve: WD 180, the only heading with measured velocities. The tunnel's WD 175 scored as a model of its WD 180 gives {c(r['control.tunnelWD175AsModelOfWD180'])}, "
        f"its WD 185 {c(r['control.tunnelWD185AsModelOfWD180'])}, and the mean of the two {c(r['control.tunnelNeighbourMeanAsModelOfWD180'])}; 8 of the 15 points change by more than a factor of two between "
        "WD 175 and WD 185 (computed from the pairs).",
        "The turbulent Schmidt number does not change the flow: the three runs of this case are one solve with three passive tracers, so U, V, W and k are the same in all three and only c* differs.",
        f"U_R is the solved speed at the reference mast, {r['referenceSpeed.solvedAtMast']:.3f} m/s, which is {r['reference.180.U.overImposed']:.2f} of the tabulated inlet's speed at the mast's elevation "
        f"({r['reference.U.imposedAtMastElevation']:.3f} m/s) and {r['reference.180.U.overTunnelUR']:.2f} of the tunnel's 4.08 m/s. Over the imposed speed c* scores FB {r['cstar.byImposedMastSpeed']['Fb']:+.2f} and over "
        f"4.08 m/s FB {r['cstar.byPaperUR']['Fb']:+.2f}, against {r['cstar']['Fb']:+.2f} over the solved speed.",
        "Model set-up: a cylinder of 540 m radius and 240 m height on the terrain sheet; the tabulated approach profile over a smooth floor; no counterpart of the tunnel's side walls (at ±360 m) and 600 m ceiling "
        "(blockage 5 %). The 6 mm outlet is 3.6 m at 1:600; the source here is a 4 m cube on the ground (a zone of 20 cells, 2 m surface cells), 1 kg/s as a volume source with no exit "
        "momentum. The 15 points are 3 m above the ground.",
        f"Mean c* over the three points nearest the source: {tn:.2f} (tunnel), {each('cstar.nearThreeMean', '.2f')} (model, Sct 0.3 / 0.5 / 0.7); over the two far downwind points: {tf:.2f} (tunnel), "
        f"{each('cstar.farTwoMean', '.2f')} (model). Peak c*: {r['cstar.peakMeasured']:.2f} (tunnel), {each('cstar.peakModel', '.2f')} (model); "
        f"{each('cstar.topFiveOverlap', 'd')} of the five highest points are shared with the tunnel.",
        f"The tunnel's three points nearest the source carry about {tn / tf:.0f} times its two far downwind ones; the modelled plume carries less, and Sct {' and '.join(reversed_)} reverses the order.",
        f"Controls on the same solution: the points turned 180° about the source score {c(r['control.turned180'])} ({r['control.turned180']['Count']} of the 15 lie in the fluid; the model's mean over those points is "
        f"{r['control.meanTurned180']:.1e} against {r['control.meanReal']:.3f} at the real ones), and the points mirrored across the plume axis score {c(r['control.mirrored'])} (the real points: {c(r['cstar'])}).",
        "The tracer goes downwind: the model's mean over the points turned 180° about the source is far below its mean at the real points. The mirrored points score above the real points because the modelled "
        "plume is displaced sideways against the tunnel's. The tunnel's neighbouring headings WD 175 and WD 185 are the noise floor of a single heading.",
        f"Field campaign (18 runs): the 10 runs within 10° of 180 at 3 m/s or more, each with its own U_R and q and H_R = 41 m as the cleaned table states (the scores divide by 40.8 m, a 1 % difference). "
        f"The model against the field's geometric mean scores {c(r['field.vsGeometricMean'])}, and lies inside the field's minimum-maximum range at {r['field.insideFieldRange']} of 15 points; "
        f"the tunnel's WD 180 against the same mean scores {c(r['field.tunnelAsModelOfGeometricMean'])}; the spread of the field at point 1 is a factor of {r['field.spreadAtPoint1']:.1f}.",
        f"The velocity at the 15 points: the mean U/U_R is {r['velocity.U.mean.model']:.3f} modelled against {r['velocity.U.mean.tunnel']:.3f} measured. FB is not defined for V and W (their means are not both positive); V "
        f"correlates at R {r['velocity.V']['R']:+.2f} and flipping its sign gives {r['velocity.V.flipped']['R']:+.2f}.",
        f"The solve ran to its {sl['iterationsRun']}-iteration limit with the residualControl unmet (no 'solution converged' line); the initial residuals at the last iteration were U_x {res['Ux']:.1e}, "
        f"U_z {res['Uz']:.1e}, p {res['p']:.1e}, epsilon {res['epsilon']:.1e}, k {res['k']:.1e} and the tracers {res['c_sct03']:.1e} to {res['c_sct07']:.1e}. checkMesh: {mesh['verdict']} {mesh['cells']:,} cells. "
        "The tracer probe prints seven significant digits; a probe at six decimals moved no c* value by more than 0.003.",
    ]


RUNS += [
    *[run("F", "openfoam12-realizableKE", frame, f"caseF_openfoam12_realizableKE_{frame}.json", _F_HEADLINE, ["case-f-layout.png", "case-f-openfoam-agreement.png", "case-f-openfoam-bias-map.png"],
          _FM_REPRO.format(fixture="Eddy3DCli.Tests/Validation/TestAijCaseFContainerE2E (EDDY3D_AIJ_F_DIRECTIONS=NNW, the default)", what=f"Shinjuku district, 1:800, wind from NNW, frame {frame}",
                           iterations="2000", cells="2,143,488"),
          "caseF_openfoam12_realizableKE_pairs.csv", PAIRS_F, normalisation=_F_NORM, notes=_f_notes(frame)) for frame in ("literal", "agl")],
    *[run("M", "openfoam12-realizableKE", sp, f"caseM_openfoam12_realizableKE_{sp}.json", _M_HEADLINE, ["case-m-layout.png", "case-m-openfoam-agreement.png", "case-m-openfoam-plan.png"],
          _FM_REPRO.format(fixture="Eddy3DCli.Tests/Validation/TestAijCaseMContainerE2E (WD 180, the default)", what=f"TPU Atsugi campus, 1:600, tunnel WD 180, turbulent Schmidt number {sct}",
                           iterations="3000", cells="1,394,053"),
          "caseM_openfoam12_realizableKE_pairs.csv", PAIRS_M, normalisation=_M_NORM.format(sct=sct), notes=_m_notes(sp)) for sp, sct in (("sct03", "0.3"), ("sct05", "0.5"), ("sct07", "0.7"))],
]

# One caption per validation figure, used on the case pages and served with each result.
FIGURE_CAPTIONS = {
    "cases-ab-openfoam-agreement.png": ("Cases A and B, OpenFOAM 12 (realizable k-ε): measured against modelled U, V, W and k at "
                                        "every measured point, normalised by U_H, with the 1:1 line and the factor-of-two band."),
    "cases-ab-openfoam-profiles.png": ("Cases A and B, OpenFOAM 12: centre-plane vertical profiles of U/U_H at the measurement "
                                       "stations, measured points against the modelled line."),
    "case-c-openfoam-agreement.png": ("Case C, OpenFOAM 12: measured Vs/U_H against the modelled √(|U|²+2k)/U_H (filled) and "
                                      "|U|/U_H (hollow), one panel per configuration (centre block × wind direction)."),
    "case-c-openfoam-bias-map.png": ("Case C, OpenFOAM 12: log₂(model / tunnel) of the scalar speed at each of the 120 points "
                                     "on the plan of the array, per configuration — where the model is slow and where it is fast."),
    "case-e-openfoam-agreement.png": ("Case E, OpenFOAM 12, wind from SW: measured velocity ratio against the modelled "
                                      "√(|U|²+2k)/U_ref (filled) and |U|/U_ref (hollow), before and after construction, and the "
                                      "change the construction makes."),
    "case-e-openfoam-bias-map.png": ("Case E, OpenFOAM 12, wind from SW: log₂(model / tunnel) of the scalar speed at the 80 "
                                     "points on the plan of the district, before and after construction."),
    "cases-ab-engine-comparison.png": ("Cases A and B, every engine on the same points: measured against modelled U/U_H and "
                                       "V/U_H, one row per engine (OpenFOAM 12; OpenLB at dx = 1.6 m; FluidX3D at H/64). FluidX3D "
                                       "is scored on the filled points, the heights where its empty-domain control holds the "
                                       "imposed log law; the hollow points near the ground are excluded."),
    "case-d-openfoam-agreement.png": ("Case D, OpenFOAM 12, wind directions 0°, 22.5° and 45°: measured thermistor Vs/U_H against the "
                                      "modelled √(|U|²+2k)/U_H (filled) and |U|/U_H (hollow), and the split-fibre |U| against "
                                      "the modelled |U| at 0°. At 0° the 66 thermistor points are 33 mirror pairs."),
    "cases-hi-openfoam-agreement.png": ("Cases H and I, OpenFOAM 12 (realizable k-ε): measured against modelled U, W, k and the dimensionless "
                                        "concentration c* = C/c0 (turbulent Schmidt number 0.5; log axes show the positive pairs only), with the 1:1 line and the "
                                        "factor-of-two band where the values do not change sign."),
    "case-i-openfoam-closures.png": ("Case I, OpenFOAM 12 under standard k-ε, realizable k-ε and k-ω SST on one mesh: measured against modelled U, k and c* "
                                     "(Sct 0.5)."),
    "case-k-openfoam-agreement.png": ("Case K, OpenFOAM 12 (realizable k-ε): measured against modelled U, W and k, and the dimensionless concentration c* = C/c0 at turbulent Schmidt "
                                      "numbers 0.3, 0.5 and 0.7 (log axes show the positive pairs within five decades only), with the 1:1 line and the factor-of-two band where the values do not "
                                      "change sign. The four points within one cube height of the source are open."),
    "case-g-openfoam-sweep.png": ("Case G, OpenFOAM 12 (realizable k-ε), the drag sweep: the field's U/U_H and k/U_H² at the 28 points against the modelled |U| and k over the model's own "
                                  "U(7 m), one column per arm: no belt, three crowns of rising Cd·LAD and the real 74 m belt as a half domain. LAD and Cd are not in the dataset."),
    "case-g-openfoam-stations.png": ("Case G, OpenFOAM 12: the mean U/U_H and the mean k/U_H² over the four heights at each of the seven stations behind the belt (x/H = 0.25 to 5), the field "
                                     "against each arm of the drag sweep."),
    "case-j-umf-agreement.png": ("Case J, urbanMicroclimateFoam (Froude scale 62.5) under realizable k-ε and buoyantKEpsilon: measured against modelled U, W, k and the floor-referenced "
                                 "temperature θ = (T_f − T)/(T_f − T_H), in the tunnel's units, with the 1:1 line and the factor-of-two band where the values do not change sign."),
    "case-j-umf-tracer.png": ("Case J, urbanMicroclimateFoam: measured against modelled c* = C/c0 for turbulent Schmidt numbers 0.3, 0.5 and 0.7 under both closures (log axes show the "
                              "positive pairs within seven decades only). The points within a quarter of a building height of the source are open."),
    "case-l-umf-agreement.png": ("Case L, urbanMicroclimateFoam (Froude scale 100, realizable k-ε): measured against modelled U, W, k, θ, V and c* at three turbulent Schmidt numbers at the 344 "
                                 "points, in the tunnel's units (log axes show the positive pairs within seven decades only)."),
    "case-f-openfoam-agreement.png": ("Case F, OpenFOAM 12 (realizable k-ε), wind from NNW: the tunnel's and the field's U/U(500 m) against the modelled √(|U|²+2k) (filled) and |U| (hollow) over "
                                      "the model's own U(500 m), in two vertical frames (top: the published z in the STL's frame; bottom: the STL's ground plus the instrument height), for the 9 m plane, "
                                      "all 33 tunnel points (planes at 5, 9 and 20 m) and the 13 field observations (bars: the standard deviation of the 10-minute means)."),
    "case-f-openfoam-bias-map.png": ("Case F, OpenFOAM 12, wind from NNW: log₂(model / tunnel) of the scalar speed at the tunnel's 13 points of the 9 m plane on the plan of the district (full-scale metres, "
                                     "north up; the arrow is the wind), in the two vertical frames."),
    "case-m-openfoam-agreement.png": ("Case M, OpenFOAM 12 (realizable k-ε), WD 180: measured against modelled U, V, W and k over the tunnel's U_R and the solved speed at the mast, and the dimensionless "
                                      "concentration c* = C/c0 at turbulent Schmidt numbers 0.3, 0.5 and 0.7 (log axes show the positive pairs within eight decades only); the last panel is the tunnel's own "
                                      "WD 175 and WD 185 against its WD 180, the noise floor of a single heading."),
    "case-m-openfoam-plan.png": ("Case M, OpenFOAM 12, WD 180: log₁₀ of c* at the 15 points on the plan of the campus (north up; the arrow is the wind), the tunnel and the three Schmidt numbers on one scale; "
                                 "a point below 10⁻³ (or zero) is open. The star is the gas source and the square the reference mast."),
    "ml-surrogate-agreement.png": ("Eddy3D ML surrogate (Yel-2.0): measured against predicted pedestrian-height speed, one "
                                   "panel per case, with the 1:1 line and the factor-of-two band."),
}
# The layout figure of each case (validation/plot_layout.py): the caption is written by layout.py from the same groups that colour the agreement figures.
FIGURE_CAPTIONS.update({f"case-{c.lower()}-layout.png": LAYOUT.caption(c) for c in LAYOUT.SPECS})
for _fig in ("cases-ab-openfoam-agreement.png", "cases-hi-openfoam-agreement.png", "case-i-openfoam-closures.png", "case-k-openfoam-agreement.png",
             "case-g-openfoam-sweep.png", "case-j-umf-agreement.png", "case-j-umf-tracer.png", "case-l-umf-agreement.png"):
    FIGURE_CAPTIONS[_fig] += " Dots take the colour of the line or plane they were measured on: the letters and colours of the layout figure of the case."
FIGURE_CAPTIONS["case-g-openfoam-stations.png"] += " The letters A to G mark the seven lines of the layout figure."
for _fig in ("case-c-openfoam-agreement.png", "case-d-openfoam-agreement.png", "case-e-openfoam-agreement.png", "case-f-openfoam-agreement.png", "case-m-openfoam-agreement.png"):
    FIGURE_CAPTIONS[_fig] += " Dots take the colour of the group of points they belong to: the letters and colours of the layout figure of the case."

METRIC_MEANING = {
    "Count": "number of measured points scored",
    "MeanObserved": "mean of the measured, normalised quantity", "MeanPredicted": "mean of the modelled, normalised quantity",
    "Fb": "fractional bias, 2 (mean_obs - mean_pred) / (mean_obs + mean_pred); positive = model low",
    "Nmse": "normalised mean square error", "Nad": "normalised absolute difference",
    "Fac2": "fraction of points within a factor of two (harsh near zero for sign-changing V and W)",
    "HitRate": "fraction of points within D = 0.25 relative or W = 0.05 U_H absolute",
    "Mg": "geometric mean bias", "Vg": "geometric variance", "GeometricPairs": "pairs with both values positive (used for Mg/Vg)",
    "R": "Pearson correlation coefficient",
    "null": "a metric that is undefined for the data (for example Mg and Vg when no pair has both values positive; Fb, Nmse and Nad of a signed velocity "
            "component of Case H or I whose observed and predicted means are not both positive)",
}

COLUMN_MEANING = {
    "point_id": "the tunnel's own measurement point number",
    "config": "configuration key: 'default', Case C centre building '0D'/'1D'/'2D', Case E state 'bc' (before) / 'ac' (after construction)",
    "instrument": "'split_fibre' (vector components) or 'thermistor' (omnidirectional scalar speed)",
    "wind_direction": "compass name of the direction the wind comes FROM (Case E)",
    "wind_direction_deg": "AIJ wind direction in degrees; 0 is the case's reference direction (see frame)",
    "x": "m, case frame", "y": "m, case frame", "z": "m above ground, case frame",
    "U": "m/s, mean velocity along +x", "V": "m/s, mean velocity along +y (sign unified: positive toward +y)", "W": "m/s, mean velocity along +z",
    "uu": "m^2/s^2, variance of u", "vv": "m^2/s^2, variance of v", "ww": "m^2/s^2, variance of w",
    "k": "m^2/s^2, turbulent kinetic energy",
    "Vs": "m/s, mean omnidirectional scalar wind speed (thermistor); Case D also lists |U| of the split-fibre probe under Vs for its 33 vector points",
    "velocity_ratio": "dimensionless, mean speed over the case's reference speed (Case E: Vs / U(15.9 m), U(15.9 m) = 3.935 m/s; see the case's normalisation)",
    "campaign": "'wind_tunnel' (model scale) or 'field' (a full-scale observation: Cases F, G, M)",
    "run": "replicate label within a campaign where the dataset publishes individual runs (Case M); empty elsewhere",
    "uv": "m^2/s^2, Reynolds shear stress <u'v'> as published",
    "uw": "m^2/s^2, Reynolds shear stress <u'w'> as published",
    "vw": "m^2/s^2, Reynolds shear stress <v'w'> as published",
    "C": "ppm, mean tracer-gas concentration as published (volume fraction x 1e6 of the released gas diluted in air)",
    "c_rms": "ppm, rms of the concentration fluctuation",
    "concentration_ratio": "C / c0, c0 = q / (U_ref L_ref^2) as the benchmark defines it for the case (manifest cases.<id>.normalisation)",
    "T": "degC, mean air temperature as published (Cases J, L)",
    "T_rms": "K, rms of the temperature fluctuation",
    "uc": "ppm m/s, turbulent concentration flux <u'c'>",
    "vc": "ppm m/s, turbulent concentration flux <v'c'>",
    "wc": "ppm m/s, turbulent concentration flux <w'c'>",
    "uT": "K m/s, turbulent heat flux <u'theta'>",
    "vT": "K m/s, turbulent heat flux <v'theta'>",
    "wT": "K m/s, turbulent heat flux <w'theta'>",
    "velocity_ratio_sd": "standard deviation of velocity_ratio over the observations behind a field value (Case F)",
    "k_ratio": "k / U_ref^2 where the dataset publishes only normalised values (Case G; U_ref = U at the tree height)",
}

# (path, media type, schema name or None, description); the order is the order of index.json and openapi.json.
ENDPOINTS = [
    ("index.json", "application/json", "index", "every endpoint and file with its size and SHA-256, versions, compatibility policy, changelog, licence, how to cite the API (cite.api)"),
    ("versions.json", "application/json", "versions", "every release, newest first: version, date, status (latest or superseded), schema and data version, base URL, tag, changelog; always at the unversioned /api/ path"),
    ("cases.json", "application/json", "cases", "every case: id, title, frame, units, counts, engine status, links"),
    ("cases/{id}.json", "application/json", "case", "one case in full: configurations, frame, units, inflow fit and approach-flow profile, point-table summary, geometry files, validation status, known data issues, attribution, citation of the case's dataset"),
    ("cases/{id}/points.json", "application/json", "points", "the cleaned measurement table: SI units, one frame, null where not measured"),
    ("cases/{id}/points.csv", "text/csv", None, "the same table as CSV (empty cell = not measured)"),
    ("cases/{id}/approach_flow.csv", "text/csv", None, "the measured approach-flow profile: z (m), U (m/s), and k (m^2/s^2) or u_rms (m/s) where published; Case G's U and k are dimensionless (U/Ub, k/Ub^2)"),
    ("cases/{id}/geometry.json", "application/json", "geometry", "the case's STL files with statistics, renders, and the boxes where the geometry is boxes"),
    ("cases/{id}/geometry.stl", "model/stl", None, "cleaned ASCII STL of the default configuration: metres, case frame, outward normals"),
    ("cases/{id}/geometry_{configuration}.stl", "model/stl", None, "the other configurations' STLs (C: 0D, 1D; E: bc, before construction)"),
    ("cases/{id}/validation.json", "application/json", "validation", "Eddy3D's scores per engine and run, with figures and the per-point pairs"),
    ("cases/{id}/pairs/{engine}.csv", "text/csv", None, "per-point measured and modelled values of one engine's runs on the case (columns described by the result's pairs_columns)"),
    ("validation.json", "application/json", "validation-summary", "every case and engine in one table: status, runs, headline scores"),
    ("geometry.json", "application/json", "geometry-index", "every STL of every case in one list: case, configuration, units, frame, bounding box, size, SHA-256"),
    ("geometry.zip", "application/zip", None, "every STL in one archive (each keeps its own case's frame and units: they are not one scene)"),
    ("schemas/{name}.schema.json", "application/schema+json", None, "the JSON Schema (draft 2020-12) of each JSON document"),
    ("openapi.json", "application/json", None, "OpenAPI 3.1 description of every endpoint"),
    ("llms.txt", "text/plain", None, "plain-text entry point for agents"),
]
ROOT_ENDPOINTS = {"versions.json"}   # served once, at the unversioned /api/ path, not inside any tree
MEDIA_TYPES = {".json": "application/json", ".csv": "text/csv", ".stl": "model/stl", ".zip": "application/zip", ".txt": "text/plain"}

WRITTEN = set()          # every file this build wrote into the current tree (relative); anything else there is stale
DATA_VERSION = None      # set once the data files are written


def release_citation():
    """The release the citations name: VERSION, its date in CHANGELOG.md and this build's data version."""
    return C.Release(RELEASE, RELEASE_DATE, DATA_VERSION)


# ----------------------------------------------------------------------------- trees

def is_release_dir(name):
    """docs/api/<name>/ is a frozen release tree if <name> is a MAJOR.MINOR.PATCH version."""
    return bool(R.SEMVER.match(name))


def release_dirs():
    """The versions that have a frozen tree under docs/api/, oldest first."""
    names = [n for n in os.listdir(API_ROOT) if is_release_dir(n) and os.path.isdir(os.path.join(API_ROOT, n))]
    return sorted(names, key=R.parse)


def tree_files(root):
    """Relative paths of every file in a tree. The alias's root also holds the frozen trees and versions.json, which
    belong to no tree's file list."""
    out = set()
    for dirpath, dirs, names in os.walk(root):
        if os.path.abspath(dirpath) == API_ROOT:
            dirs[:] = [d for d in dirs if not is_release_dir(d)]
            names = [n for n in names if n not in ROOT_ENDPOINTS]
        out.update(os.path.relpath(os.path.join(dirpath, n), root).replace(os.sep, "/") for n in names)
    return out


def use_tree(kind):
    """Point every writer at one tree: the frozen copy docs/api/<release>/ or the latest alias docs/api/. The two
    are built by the same code, so they differ only in the address each document gives its own files."""
    # shortcut: module globals switched between two sequential builds; make the tree an object if they ever run in parallel
    global TREE, API, API_BASE, FALLBACK_BASE, WRITTEN
    WRITTEN = set()
    TREE = kind
    if kind == "release":
        API, API_BASE, FALLBACK_BASE = os.path.join(API_ROOT, RELEASE), PINNED_BASE, RELEASE_BASE
    else:
        API, API_BASE, FALLBACK_BASE = API_ROOT, LIVE_BASE, RAW_BASE
    os.makedirs(API, exist_ok=True)


# ----------------------------------------------------------------------------- files and URLs

def url(rel):
    return f"{API_BASE}/{rel}"


def schema_url_in(base, name):
    return f"{base}/schemas/{name}.schema.json"


def schema_url(name):
    return schema_url_in(API_BASE, name)


def render_url(case, configuration=None):
    """The site URL of a configuration's render (the case's default configuration if None)."""
    return f"{SITE}/assets/geometry/{D.render_file(case, configuration)}"


def _sha256(rel, root=None):
    with io.open(os.path.join(root or API, rel), "rb") as f:
        body = f.read()
    return hashlib.sha256(body).hexdigest(), len(body)


def media_type(rel):
    if rel.startswith("schemas/"):
        return "application/schema+json"
    return MEDIA_TYPES[os.path.splitext(rel)[1]]


def download(rel):
    """A file to fetch: versioned URL, path, media type, size and SHA-256 of the bytes on disk."""
    sha, n = _sha256(rel)
    return {"url": f"{url(rel)}?v={sha[:12]}", "path": rel, "media_type": media_type(rel), "bytes": n, "sha256": sha}


def _target(rel):
    path = os.path.join(API, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    WRITTEN.add(rel)
    return path


def write_text(rel, text):
    with io.open(_target(rel), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return rel


def write_csv(rel, header, rows):
    with io.open(_target(rel), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(["" if v is None else v for v in r])
    return rel


def copy_file(src, rel):
    shutil.copyfile(src, _target(rel))
    return rel


def dump(obj):
    return json.dumps(obj, indent=1, ensure_ascii=False, allow_nan=False) + "\n"


def write_json(rel, schema, obj):
    """A JSON document: the four header keys, then the body."""
    body = {"$schema": schema_url(schema), "schema_version": SCHEMA_VERSION, "data_version": DATA_VERSION,
            "license": D.LICENSE["spdx"]}
    body.update(obj)
    return write_text(rel, dump(body))


# ----------------------------------------------------------------------------- phase 1: data files

def points_summary(rows):
    cols = [c for c in D.POINT_COLUMNS if any(r[c] not in (None, "") for r in rows)]
    by = lambda key: sorted({str(r[key]) for r in rows})  # noqa: E731
    counts = {}
    for key in ("config", "instrument", "wind_direction_deg"):
        if key in cols:
            counts[key] = {k: sum(1 for r in rows if str(r[key]) == k) for k in by(key)}
    nulls = {c: sum(1 for r in rows if r[c] is None) for c in cols if c not in ("config", "instrument", "wind_direction")}
    xyz = [(r["x"], r["y"], r["z"]) for r in rows if None not in (r["x"], r["y"], r["z"])]
    return {
        "rows": len(rows),
        "distinct_points": len({r["point_id"] for r in rows}),
        "columns": cols,
        "counts": counts,
        "nulls": {k: v for k, v in nulls.items() if v},
        "bbox_min": [round(min(p[i] for p in xyz), 6) for i in range(3)],
        "bbox_max": [round(max(p[i] for p in xyz), 6) for i in range(3)],
    }


# Boxes the case states (the building, the belt, the array), in the case frame. F's STL is a 725 m disc drawn as a polygon, so its
# extent in y is short of the radius by up to 3 mm; F and M stand on a base slab (geometry_checks.BASE_Z) below the ground at z = 0.
BBOX_TOLERANCE = {"F": 0.01}
EXPECTED_BBOX = {
    "F": ([-725.0, -725.0, -1.0], [725.0, 725.0, 225.0]),              # the 725 m disc of terrain on a 1 m base slab, the 225 m roof of the tallest tower (readme, STL)
    "G": ([-2.0, -37.0, 1.2], [0.0, 37.0, 7.0]),                       # the belt: 2 m deep, 74 m long, 7 m tall, 1.2 m gap below
    "H": ([-0.1, -0.05, 0.0], [0.0, 0.05, 0.2]),                       # the 0.10 x 0.10 x 0.20 m building, leeward face at x = 0
    "I": ([-0.05, -0.05, 0.0], [0.05, 0.05, 0.1]),                     # the 0.1 m cube, centred on the origin
    "J": ([-0.08, -0.04, 0.0], [0.0, 0.04, 0.16]),                     # b = 0.08 m, H = 0.16 m
    "K": ([-0.36, -0.51, 0.0], [0.66, 0.51, 0.06]),                    # 9 x 9 cubes of 0.06 m on a 0.12 m pitch
    "L": ([-0.96, -0.51, 0.0], [0.66, 0.51, 0.06]),                    # 14 x 9 cubes of 0.06 m on a 0.12 m pitch
    "M": ([-540.0, -360.0, -1.0], [540.0, 360.0, 64.9152]),            # the 1.8 x 1.2 m model, x600, on a 1 m base slab
}


def expected_bbox(case, cfg):
    c = D.CASES[case]["configuration"]
    if case in EXPECTED_BBOX:
        return EXPECTED_BBOX[case]
    if case == "A":
        return [-c["b_m"] / 2, -c["b_m"] / 2, 0.0], [c["b_m"] / 2, c["b_m"] / 2, c["H_m"]]
    if case == "B":
        return [-c["depth_m"] / 2, -c["width_m"] / 2, 0.0], [c["depth_m"] / 2, c["width_m"] / 2, c["H_m"]]
    if case == "C":
        return [-0.5, -0.5, 0.0], [0.5, 0.5, 0.4 if cfg == "2D" else 0.2]
    if case == "D":
        e = c["array_extent_m"]
        return [e["x"][0], e["y"][0], e["z"][0]], [e["x"][1], e["y"][1], e["z"][1]]
    return None, None


def stl_rel(case, cfg):
    return f"cases/{case}/geometry.stl" if cfg == D.DEFAULT_CONFIGURATION[case] else f"cases/{case}/geometry_{cfg}.stl"


def write_data(case):
    """Points CSV, approach-flow CSV, STLs and pairs of one case; returns what the JSON phase needs."""
    rows, src = D.load_points(case)
    summ = points_summary(rows)
    write_csv(f"cases/{case}/points.csv", summ["columns"], ([r[c] for c in summ["columns"]] for r in rows))

    af, af_src = D.load_approach_flow(case)
    af_cols = [c for c in ("z", "U", "k", "u_rms") if any(c in r for r in af)]
    write_csv(f"cases/{case}/approach_flow.csv", af_cols, ([r.get(c) for c in af_cols] for r in af))

    geometry = []
    for cfg, tris, boxes, note in D.case_geometry(case):
        stats = D.stl_stats(tris)
        rel = stl_rel(case, cfg)
        D.write_ascii_stl(_target(rel), tris, f"AIJ_case{case}_{cfg}")
        lo, hi = expected_bbox(case, cfg)
        ok = None
        if lo is not None:
            tol = BBOX_TOLERANCE.get(case, 1e-6)
            ok = all(abs(a - b) < tol for a, b in zip(stats["bbox_min"], lo)) and all(abs(a - b) < tol for a, b in zip(stats["bbox_max"], hi))
            if not ok:
                raise SystemExit(f"geometry check failed for {case}/{cfg}: bbox {stats['bbox_min']}..{stats['bbox_max']} != {lo}..{hi}")
        if not stats["watertight"]:
            raise SystemExit(f"geometry check failed for {case}/{cfg}: not every body is closed, consistently wound and outward ({stats})")
        geometry.append({"configuration": cfg, "rel": rel, "stats": stats, "boxes": boxes, "note": note, "bbox_ok": ok})
    geometry.sort(key=lambda g: g["configuration"] != D.DEFAULT_CONFIGURATION[case])

    for r in RUNS:
        if r["case"] == case:
            copy_file(os.path.join(RESULTS_DIR, r["pairs"]), f"cases/{case}/pairs/{r['engine']}.csv")
    return {"rows": rows, "src": src, "summ": summ, "af": af, "af_src": af_src, "af_cols": af_cols, "geometry": geometry}


def write_archive(data):
    """geometry.zip: every STL under a self-describing name, with fixed timestamps and order.

    Deflate output depends on the zlib version (1.2.13 and 1.3.1 encode the same bytes differently), so an
    archive whose members already equal the current STLs is kept as it is: its bytes then depend on the
    geometry alone, and a rebuild on any platform reproduces the committed file."""
    rel = "geometry.zip"
    if TREE == "latest":   # the alias holds the release tree's archive itself, so the two cannot differ by a zlib
        shutil.copyfile(os.path.join(API_ROOT, RELEASE, rel), _target(rel))
        return rel
    members = []
    for case in D.CASE_IDS:
        for g in data[case]["geometry"]:
            with io.open(os.path.join(API, g["rel"]), "rb") as f:
                members.append((archive_name(case, g["configuration"]), f.read()))
    path = _target(rel)
    if os.path.isfile(path):
        try:
            with zipfile.ZipFile(path) as z:
                infos = z.infolist()
                if ([i.filename for i in infos] == [n for n, _ in members]
                        and all(i.date_time == (1980, 1, 1, 0, 0, 0) and i.compress_type == zipfile.ZIP_DEFLATED for i in infos)
                        and all(z.read(n) == body for n, body in members)):
                    return rel
        except zipfile.BadZipFile:
            pass
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, body in members:
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, body)
    return rel


def archive_name(case, cfg):
    return f"AIJ_case{case}_{cfg}.stl"


def compute_data_version():
    """SHA-256 over (path, SHA-256) of every data file served and every score snapshot behind validation.json.

    The served files are written here with LF endings, so their bytes are their content. The score snapshots
    are hashed as canonical JSON (sorted keys, no whitespace), so a checkout's line endings cannot move it."""
    entries = []
    for rel in sorted(WRITTEN):
        if rel.endswith((".csv", ".stl")):
            entries.append(f"api/{rel}\t{_sha256(rel)[0]}")
    for r in sorted({r["results"] for r in RUNS}):
        with io.open(os.path.join(RESULTS_DIR, r), encoding="utf-8") as f:
            canonical = json.dumps(json.load(f), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        entries.append(f"validation/results/{r}\t{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}")
    return hashlib.sha256("\n".join(entries).encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------- phase 2: JSON documents

def check_runs_registry():
    """Every snapshot is registered and every registered snapshot exists: nothing is served by accident."""
    on_disk = {n for n in os.listdir(RESULTS_DIR) if n.endswith(".json")}
    listed = {r["results"] for r in RUNS}
    if on_disk != listed:
        raise SystemExit(f"validation/results/ and RUNS disagree: unregistered {sorted(on_disk - listed)}, "
                         f"missing {sorted(listed - on_disk)}")
    missing = sorted({r["pairs"] for r in RUNS if not os.path.isfile(os.path.join(RESULTS_DIR, r["pairs"]))})
    if missing:
        raise SystemExit(f"RUNS names pairs files that are not in validation/results/: {missing}")


def is_metric(v):
    return isinstance(v, dict) and "Fb" in v and "R" in v


def defined(metric):
    """A metric with every undefined value (NaN or an infinity, which some fixtures write as the strings
    "NaN", "Infinity") as None: JSON has no NaN, and a string where a number belongs breaks clients."""
    out = {}
    for k, v in metric.items():
        if isinstance(v, str) and v in ("NaN", "Infinity", "-Infinity"):
            v = None
        elif isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
            v = None
        out[k] = v
    return out


def flat_scores(res, prefix=""):
    """Every score in a results.json as {dotted key: metrics}. A score nested as {"score": {...}} takes its
    parent's key (velocity.U.comparable); other nesting joins the keys
    (negativeControl.noBuilding.components.U.control)."""
    out = {}
    for k, v in res.items():
        key = f"{prefix}{k}"
        if is_metric(v):
            out[key] = defined(v)
        elif isinstance(v, dict):
            if is_metric(v.get("score")):
                out[key] = defined(v["score"])
            else:
                out.update(flat_scores(v, key + "."))
    return out


def _quantity(text):
    """A snapshot's own description of what it scored, in the words of this page (the snapshot is a fixture's output and stays as written)."""
    return text and text.replace("the field campaign (18 runs) is recorded beside it", "the 18-run field campaign is compared as well")


def validation_entries(case):
    out = []
    for r in RUNS:
        if r["case"] != case:
            continue
        with io.open(os.path.join(RESULTS_DIR, r["results"]), encoding="utf-8") as f:
            res = json.load(f)
        scores = flat_scores(res)
        for label, key in r["headline"].items():
            if key not in scores:
                raise SystemExit(f"{r['results']}: headline '{label}' -> '{key}' is not a score in the file")
        out.append({
            "run_id": r["run_id"],
            "engine": r["engine"],
            "configuration": r["configuration"],
            "solver": res.get("engine") or res.get("turbulenceModel"), "numerics_level": res.get("numericsLevel"),
            "scale": res.get("scale"), "solved_time": res.get("solvedTime"), "iterations": res.get("iterations"),
            "points_measured": res.get("points.measured"),
            "lateral_sign_applied_in_fixture": res.get("lateralSign"),
            "recirculation_Lr_over_H": res.get("recirculation.LrOverH",
                                               (res.get("recirculation.z=0.05H") or {}).get("LrOverH")),
            "quantity": _quantity(res.get("quantity")),
            "normalisation": r["normalisation"] or ("velocities by U_H, k by U_H^2 (the benchmark's own convention; Case E by U at 15.9 m, "
                                                    "as it is published); hit rate D = 0.25, W = 0.05 in those units"),
            "notes": r["notes"],
            "metric_meaning": METRIC_MEANING,
            "headline": dict(r["headline"]),
            "scores": scores,
            "figures": [{"url": f"{SITE}/assets/figures/{fig}", "caption": FIGURE_CAPTIONS[fig]} for fig in r["figures"]],
            "pairs": download(f"cases/{case}/pairs/{r['engine']}.csv"),
            "pairs_columns": r["pairs_columns"],
            "reproduce": r["reproduce"],
            "source_file": f"validation/results/{r['results']}",
            "source_url": f"{REPO_URL}/blob/main/validation/results/{r['results']}",
            # The benchmark's citation from one place, not the fixture's free-text reference line.
            "cite": D.CITATION["benchmark"],
        })
    return out


def configurations(case, rows):
    configs = []
    if case == "C":
        for cb in ("0D", "1D", "2D"):
            for wd in (0.0, 22.5, 45.0):
                configs.append({"config": cb, "wind_direction_deg": wd, "points": sum(1 for r in rows if r["config"] == cb and r["wind_direction_deg"] == wd)})
    elif case == "D":
        for inst in ("thermistor", "split_fibre"):
            for wd in sorted({r["wind_direction_deg"] for r in rows if r["instrument"] == inst}):
                sel = [r for r in rows if r["instrument"] == inst and r["wind_direction_deg"] == wd]
                configs.append({"instrument": inst, "wind_direction_deg": wd, "points": len(sel),
                                "measured": sum(1 for r in sel if (r["Vs"] if inst == "thermistor" else r["U"]) is not None)})
    elif case == "E":
        for st in ("bc", "ac"):
            configs.append({"config": st, "wind_directions": D.COMPASS, "points_per_direction": sum(1 for r in rows if r["config"] == st and r["wind_direction"] == "N")})
    elif case in ("A", "B"):
        configs.append({"config": "default", "wind_direction_deg": 0.0, "points": len(rows)})
    else:
        # Cases F to M: one entry per campaign, instrument, run and direction the table holds, in table order.
        groups = {}
        for r in rows:
            groups.setdefault((r["config"], r["campaign"], r["instrument"], r["run"], r["wind_direction"], r["wind_direction_deg"]), []).append(r)
        for (cfg, camp, inst, run, name, wd), sel in groups.items():
            c = {"config": cfg, "campaign": camp, "instrument": inst}
            if run:
                c["run"] = run
            if name:
                c["wind_direction"] = name
            configs.append({**c, "wind_direction_deg": wd, "points": len(sel)})
    return configs


def write_case_documents(case, d):
    meta = D.CASES[case]
    summ = d["summ"]
    cols = summ["columns"]
    units_label = "metres" + (" (full scale)" if case in D.FULL_SCALE else " (model scale)")

    write_json(f"cases/{case}/points.json", "points", {
        "case": case, "title": meta["title"],
        "points_source": d["src"],
        "units": meta["units"], "frame": meta["frame"],
        "columns": cols,
        "column_meaning": {c: COLUMN_MEANING[c] for c in cols},
        "n": len(d["rows"]),
        "csv": download(f"cases/{case}/points.csv"),
        "points": [{c: r[c] for c in cols} for r in d["rows"]],
    })

    files = []
    for g in d["geometry"]:
        entry = {"configuration": g["configuration"], **download(g["rel"]), "format": "ASCII STL, LF line endings, outward normals, every body closed and consistently wound",
                 "source": g["note"], "stats": g["stats"], "bbox_matches_stated_dimensions": g["bbox_ok"],
                 "render": render_url(case, g["configuration"]), "render_caption": D.RENDER_CAPTIONS[(case, g["configuration"])]}
        if g["boxes"] is not None:
            b = g["boxes"]
            entry.update({"boxes": b, "box_count": len(b), "analytic_volume": round(sum(
                (x["max"][0] - x["min"][0]) * (x["max"][1] - x["min"][1]) * (x["max"][2] - x["min"][2]) for x in b), 9)})
        files.append(entry)
    write_json(f"cases/{case}/geometry.json", "geometry", {
        "case": case, "title": meta["title"], "units": units_label, "frame": meta["frame"],
        "default_configuration": D.DEFAULT_CONFIGURATION[case],
        "configurations": [f["configuration"] for f in files],
        "is_boxes": files[0].get("boxes") is not None,
        "files": files,
        "render": render_url(case),
    })

    results = validation_entries(case)
    write_json(f"cases/{case}/validation.json", "validation", {
        "case": case, "title": meta["title"],
        "status": "scored" if results else "pending",
        "status_meaning": STATUS_MEANING,
        "engines": [{"engine": e["id"], "status": ENGINE_STATUS[case][e["id"]]} for e in case_engines(case)],
        "results": results,
        "note": (None if results else "No validation has been run for this case yet; results is an empty list. "
                 f"{QUEUED}"),
    })

    configs = configurations(case, d["rows"])
    write_json(f"cases/{case}.json", "case", {
        "id": case, "slug": meta["slug"], "title": meta["title"], "summary": meta["short"],
        "configuration": meta["configuration"],
        "configurations": configs,
        "quantities": meta["quantities"],
        "units": meta["units"], "frame": meta["frame"],
        "inflow_fit": meta["inflow_fit"],
        "approach_flow": {"source": d["af_src"], "units": {c: {**{"z": "m", "U": "m/s", "k": "m^2/s^2", "u_rms": "m/s"}, **meta.get("approach_flow_units", {})}[c] for c in d["af_cols"]},
                          "rows": d["af"], "csv": download(f"cases/{case}/approach_flow.csv")},
        "points": {"url": url(f"cases/{case}/points.json"), "csv": download(f"cases/{case}/points.csv"), "source": d["src"], **summ},
        "geometry": {"url": url(f"cases/{case}/geometry.json"),
                     "files": [{"configuration": f["configuration"], "url": f["url"], "triangles": f["stats"]["triangles"],
                                "watertight": f["stats"]["watertight"]} for f in files]},
        "validation": {"url": url(f"cases/{case}/validation.json"), "status": "scored" if results else "pending",
                       "engines": ENGINE_STATUS[case]},
        "known_issues": meta["known_issues"],
        "people": meta["people"], "doi": meta["doi"], "doi_note": meta.get("doi_note"),
        "citation_requested": meta["citation_requested"],
        "citation": C.case(case, meta),
        "files_in_repository": {"folder": f"{REPO_URL}/tree/main/{meta['folder']}", "reference": meta["reference_file"],
                                "approach_flow": meta["approach_flow_file"], "readme": meta["readme"]},
        "render": render_url(case),
        "page": f"{SITE}/cases/{meta['slug']}/",
    })
    return {"summ": summ, "configs": configs, "results": results, "files": files}


def write_cases_index(percase):
    items = []
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        p = percase[case]
        items.append({
            "id": case, "slug": meta["slug"], "title": meta["title"], "summary": meta["short"],
            "configuration": meta["configuration"],
            "quantities": meta["quantities"], "units": meta["units"],
            "frame": {k: meta["frame"][k] for k in ("origin", "x", "y", "z")},
            "counts": {"rows": p["summ"]["rows"], "distinct_points": p["summ"]["distinct_points"], "configurations": len(p["configs"])},
            "engines": ENGINE_STATUS[case],
            "doi": meta["doi"],
            "links": {"case": url(f"cases/{case}.json"), "points": url(f"cases/{case}/points.json"),
                      "points_csv": download(f"cases/{case}/points.csv")["url"],
                      "geometry": url(f"cases/{case}/geometry.json"), "geometry_stl": p["files"][0]["url"],
                      "validation": url(f"cases/{case}/validation.json"), "page": f"{SITE}/cases/{meta['slug']}/",
                      "render": render_url(case)},
        })
    write_json("cases.json", "cases", {"cases": items})


def write_geometry_index(data):
    """One index of every STL. The STLs are NOT merged into one scene: each case has its own origin, E, F, G and M are
    full scale (hundreds of times larger than the model-scale cases), and C's three centre-block variants and E's
    before/after states are alternatives that cannot share one CFD domain."""
    items = []
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        for g in data[case]["geometry"]:
            items.append({
                "case": case, "configuration": g["configuration"], **download(g["rel"]),
                "archive_name": archive_name(case, g["configuration"]),
                "units": "metres" + (" (full scale)" if case in D.FULL_SCALE else " (model scale)"),
                "frame": {k: meta["frame"][k] for k in ("origin", "x", "y", "z")},
                "bbox_min": g["stats"]["bbox_min"], "bbox_max": g["stats"]["bbox_max"],
                "triangles": g["stats"]["triangles"], **{k: g["stats"][k] for k in S.GEOMETRY_FACTS},
                "render": render_url(case, g["configuration"]),
            })
    write_json("geometry.json", "geometry-index", {
        "description": ("Every cleaned STL, one entry per case and configuration. Each file is in its own case's frame "
                        "and units — points.json of the same case lives in that frame — so they are not one "
                        "scene: overlaid, the cases would stack at the origin, and Cases E, F, G and M are full scale while the "
                        "others are model scale. geometry.zip holds the same files under archive_name."),
        "archive": download("geometry.zip"),
        "files": items,
    })


def write_validation_summary(percase):
    cases = []
    for case in D.CASE_IDS:
        engines = []
        for e in case_engines(case):
            runs = []
            for res in percase[case]["results"]:
                if res["engine"] != e["id"]:
                    continue
                runs.append({"run_id": res["run_id"], "configuration": res["configuration"], "headline": [
                    {"label": label, "score": key, **{m: res["scores"][key].get(m) for m in ("Count", "R", "Fac2", "Fb", "HitRate")}}
                    for label, key in res["headline"].items()]})
            engines.append({"engine": e["id"], "status": ENGINE_STATUS[case][e["id"]], "runs": runs})
        cases.append({"case": case, "title": D.CASES[case]["title"], "url": url(f"cases/{case}/validation.json"), "engines": engines})
    write_json("validation.json", "validation-summary", {
        "description": ("Every case and engine in one table. Headline scores are the ones to quote; every score, the "
                        "figures and the per-point pairs are in each case's validation.json."),
        "engines": ENGINES, "status_meaning": STATUS_MEANING, "metric_meaning": METRIC_MEANING, "cases": cases,
    })


def write_schemas():
    for name, schema in S.published(API_BASE).items():
        write_text(f"schemas/{name}.schema.json", dump(schema))


def write_openapi():
    ids = D.CASE_IDS
    variants = sorted({g for case in ids for (c, g) in D.RENDER_CAPTIONS if c == case and g != D.DEFAULT_CONFIGURATION[case]})
    params = {
        "id": {"name": "id", "in": "path", "required": True, "description": "case id", "schema": {"type": "string", "enum": ids}},
        "configuration": {"name": "configuration", "in": "path", "required": True, "schema": {"type": "string", "enum": variants},
                          "description": "a non-default geometry configuration: C 0D or 1D (2D is geometry.stl); E bc (ac is geometry.stl)"},
        "engine": {"name": "engine", "in": "path", "required": True, "description": "an engine with a scored run on the case",
                   "schema": {"type": "string", "enum": [e["id"] for e in ENGINES]}},
        "name": {"name": "name", "in": "path", "required": True, "description": "a document schema",
                 "schema": {"type": "string", "enum": list(S.DOCUMENTS)}},
        "v": {"name": "v", "in": "query", "required": False, "schema": {"type": "string", "pattern": "^[0-9a-f]{12}$"},
              "description": "the file's SHA-256 prefix, as in the URLs the JSON documents give; ignored by the server, it keeps caches from serving a stale copy"},
    }
    op_ids = {
        "index.json": ("getIndex", "discovery"), "versions.json": ("getVersions", "discovery"), "cases.json": ("listCases", "cases"), "cases/{id}.json": ("getCase", "cases"),
        "cases/{id}/points.json": ("getPoints", "points"), "cases/{id}/points.csv": ("getPointsCsv", "points"),
        "cases/{id}/approach_flow.csv": ("getApproachFlowCsv", "points"),
        "cases/{id}/geometry.json": ("getGeometry", "geometry"), "cases/{id}/geometry.stl": ("getGeometryStl", "geometry"),
        "cases/{id}/geometry_{configuration}.stl": ("getGeometryVariantStl", "geometry"),
        "cases/{id}/validation.json": ("getValidation", "validation"), "cases/{id}/pairs/{engine}.csv": ("getPairsCsv", "validation"),
        "validation.json": ("getValidationSummary", "validation"), "geometry.json": ("listGeometry", "geometry"),
        "geometry.zip": ("getGeometryArchive", "geometry"), "schemas/{name}.schema.json": ("getSchema", "discovery"),
        "openapi.json": ("getOpenApi", "discovery"), "llms.txt": ("getLlmsTxt", "discovery"),
    }
    names = {n: "".join(w.capitalize() for w in n.split("-")) for n in S.DOCUMENTS}
    stl_note = (" GitHub Pages labels .stl responses `application/vnd.ms-pki.stl` (a certificate type); the body is "
                "ASCII STL whatever the header says.")
    not_found = {"description": "No such case, configuration, engine or file. GitHub Pages answers with an HTML page, not JSON."}
    paths = {}
    for path, media, schema, desc in ENDPOINTS:
        op_id, tag = op_ids[path]
        if schema:
            body = {"schema": {"$ref": f"#/components/schemas/{names[schema]}"}}
        elif media == "application/zip":
            body = {"schema": {"type": "string", "format": "binary"}}
        elif media == "application/schema+json":
            body = {"schema": {"type": "object"}}
        else:
            body = {"schema": {"type": "string"}}
        op = {"operationId": op_id, "tags": [tag], "summary": desc[0].upper() + desc[1:].split(":")[0],
              "description": desc + (stl_note if media == "model/stl" else ""),
              "responses": {"200": {"description": "OK", "content": {media: body}}, "404": not_found}}
        ps = [params[p] for p in ("id", "configuration", "engine", "name") if "{" + p + "}" in path]
        if not path.endswith(".json") and path != "llms.txt" or path.endswith(".schema.json"):
            ps.append(params["v"])
        if ps:
            op["parameters"] = ps
        paths["/" + path] = {"get": op}
        if path in ROOT_ENDPOINTS:   # one home, whichever tree this document is in: say so, or a release tree's server would 404
            paths["/" + path]["servers"] = [{"url": LIVE_BASE, "description": "the unversioned alias; versions.json is not copied into release trees"}]
    components = {names[n]: {k: v for k, v in s.items() if k not in ("$schema", "$id")} for n, s in S.DOCUMENTS.items()}
    doc = {
        "openapi": "3.1.0",
        "jsonSchemaDialect": S.DRAFT,
        "info": {"title": "AIJ UWE — cleaned data API", "version": SCHEMA_VERSION,
                 "summary": f"Wind-tunnel and field reference data of the AIJ UWE benchmark (Cases {CASE_SPAN}), cleaned, with Eddy3D's validation against it.",
                 "description": ("Static files, one GET each; nothing is computed on request. Lengths in metres, velocities in "
                                 "m/s, variances and k in m^2/s^2, in one frame per case. " + COMPATIBILITY + " " + CACHING),
                 "license": {"name": D.LICENSE["name"], "identifier": D.LICENSE["spdx"]}},
        "servers": [{"url": API_BASE, "description": ("release " + RELEASE + ", frozen" if TREE == "release" else "the latest release")},
                    {"url": FALLBACK_BASE, "description": "the same files, raw from the repository (fallback)"}],
        "tags": [{"name": "discovery", "description": "where everything is"}, {"name": "cases", "description": f"the {len(D.CASE_IDS)} cases"},
                 {"name": "points", "description": "measurement tables"}, {"name": "geometry", "description": "STL geometry"},
                 {"name": "validation", "description": "Eddy3D's scores and the per-point pairs behind them"}],
        "paths": paths,
        "components": {"schemas": components},
    }
    write_text("openapi.json", dump(doc))


def llms_text(percase):
    walk = [
        "# AIJ UWE — cleaned data API",
        "",
        "> Wind-tunnel and field reference data from the Architectural Institute of Japan Urban Wind Environment (UWE)",
        f"> benchmark, Cases {CASE_SPAN}, cleaned into one schema, plus Eddy3D's validation against it. Static files, plain GET.",
        "",
        f"Base URL: {API_BASE}",
        f"Fallback (raw files from the repository): {FALLBACK_BASE}",
        f"Repository: {REPO_URL}",
        f"Release: {RELEASE} ({RELEASE_DATE}). " + (
            "This is the frozen copy of that release: its files never change and every URL below stays inside it."
            if TREE == "release" else
            f"This is the latest alias, which always equals the newest release; the frozen copy of {RELEASE} is {PINNED_BASE}."),
        f"All releases: {endpoint_url('versions.json')}",
        f"API schema version: {SCHEMA_VERSION}. Data version (SHA-256 of the served data): {DATA_VERSION}.",
        "Licence: CC-BY-4.0. Data: Kikumoto et al. (2026); the collectors, DOI and requested citation of each case are in cases/{id}.json.",
        "",
        "## How to use this",
        "",
        "1. GET index.json — every endpoint and file (with size and SHA-256), versions, changelog, citation.",
        f"2. GET cases.json — every case with its frame, units, counts and links. Pick an id ({', '.join(D.CASE_IDS)}).",
        "3. GET cases/{id}.json — read `frame`, `units` and `known_issues` BEFORE the numbers; they differ per case.",
        "4. GET cases/{id}/points.json (or points.csv) — every value is SI (m, m/s, m^2/s^2; concentrations in ppm, temperatures in",
        "   degC) in ONE frame per case; unmeasured values are null. Cases E, F and G publish dimensionless ratios (velocity_ratio,",
        "   k_ratio), not speeds in m/s; Case M has wind-tunnel and field rows (`campaign`). Read `units` and the normalisation first.",
        "5. GET cases/{id}/geometry.stl — ASCII STL in metres, outward normals, in the case's own frame (cases/{id}.json `frame`).",
        "   Cases A-D and H-L are model-scale with +x along the wind at WD = 0; E to G and M are full-scale: E and F keep their",
        "   geographic frame (+x east, +y north), G has +x downwind, and M has +x north and +y west.",
        "   geometry.json lists the boxes where the geometry IS boxes (A, B, C, D, G, H, I, J, K, L), so you need not parse the STL at all.",
        "6. GET validation.json for every case and engine at once, or cases/{id}/validation.json for one case in full.",
        "   Quote the `headline` scores. An engine whose status is not \"scored\" has NO result for that case: do not",
        "   infer one. Each result's `pairs` is the per-point measured and modelled values, so any score can be recomputed. Status: "
        + "; ".join(f"{c}: " + ", ".join(f"{e} {s}" for e, s in ENGINE_STATUS[c].items()) for c in D.CASE_IDS) + ".",
        "7. All geometry at once: GET geometry.json (every STL with its case, configuration, units, frame and SHA-256)",
        "   or geometry.zip. Each STL stays in its own case's frame and units; they are NOT one scene.",
        "8. Every JSON document names its JSON Schema in `$schema` (schemas/{name}.schema.json); openapi.json describes",
        "   every endpoint. Download URLs carry ?v=<SHA-256 prefix>: use the URLs the documents give, not hand-built ones.",
        "9. Send a descriptive User-Agent: the site's CDN answers HTTP 403 to Python urllib's default one and to some AI",
        "   crawlers. If you are refused, the fallback URL above serves byte-identical files from the repository.",
        "10. To make a result reproducible, pin the release: GET versions.json, take the base_url of the release you used,",
        "   and fetch every path below from it instead of from the unversioned base. A release's files never change, and",
        "   every URL to an API file inside its documents points back into it. Quote the release number with any number you report.",
        "",
        "## Endpoints",
        "",
    ]
    for p, _, _, d in ENDPOINTS:
        if "{" not in p:
            walk.append(f"- {endpoint_url(p)} — {d}")
            continue
        # A template is not a URL to fetch: name it as a path and list the files it stands for.
        walk.append(f"- {p} (base URL + path, one file per value) — {d}:")
        walk += [f"  - {link(rel)}" for rel in expand(p)]
    walk += ["", "## Cases", ""]
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        summ = percase[case]["summ"]
        walk.append(f"- {case}: {meta['title']}. {meta['short']} {summ['rows']} rows, {summ['distinct_points']} points, "
                    f"columns {', '.join(summ['columns'])}. Engines: " + ", ".join(f"{k} {v}" for k, v in ENGINE_STATUS[case].items()) + ".")
    walk += ["", "## Known data issues", ""]
    for case in D.CASE_IDS:
        for g in D.CASES[case]["known_issues"]:
            walk.append(f"- [{case}] {g}")
    walk += [
        "",
        "## Validation method",
        "",
        "Each case is solved through Eddy3D's production case writer (build-case -> run -> probe); the probe sits at",
        "exactly the tunnel's measurement coordinates. Scores are normalised by U_H",
        "(k by U_H^2; Case E by U at 15.9 m); hit rate uses D = 0.25, W = 0.05 in those units. FAC2 is harsh by",
        "construction on sign-changing V and W, where R and hit rate are the usable scores. The lateral sign of Case B is corrected",
        "before scoring. Cases C-E measure an omnidirectional SCALAR speed (thermistor): the model is scored as",
        "sqrt(|U|^2 + 2k) and as |U|, the two ends of the bracket the measurement must fall in.",
        "The ML surrogate predicts |U|/U_ref at 1.8 m; each case is scaled so its measurement plane lands there.",
        "On the full prediction window it does not respond to the wind direction at all (reversing the wind changes",
        "the field by < 1e-4 U_ref), so its scores grade the geometry it was given.",
        "",
        "## Cite",
        "",
        f"- {D.CITATION['benchmark']}",
        f"- {D.CITATION['guidelines']}",
        "- Each case's own requested citation and Zenodo DOI are in cases/{id}.json.",
        "- Cite the API: cite.api in index.json",
        "",
    ]
    return "\n".join(walk)


def write_dataset_jsonld(percase):
    """schema.org Dataset metadata for the home page (docs/_includes/dataset-jsonld.html), so search engines
    that index datasets (Google Dataset Search among them) find the data, its licence and its downloads."""
    editors = sorted({p for c in D.CASE_IDS for p in D.CASES[c]["people"]["editors_distributors"]})
    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": C.TITLE,
        "identifier": C.pinned_url(RELEASE),
        "description": ("Wind-tunnel and field reference data of the Architectural Institute of Japan Urban Wind Environment (UWE) "
                        f"benchmark, Cases {CASE_SPAN}: isolated buildings and arrays of blocks and cubes, a high-rise among city "
                        "blocks, districts of Niigata, Shinjuku and Atsugi, a tree belt, and tracer-gas dispersion around buildings and cube "
                        "arrays, some non-isothermal. Cleaned into SI units and one frame per case, with cleaned STL geometry and "
                        "Eddy3D's CFD validation scores."),
        "url": SITE + "/",
        "sameAs": REPO_URL,
        "version": RELEASE,
        "dateModified": RELEASE_DATE,
        "license": D.LICENSE["url"],
        "isAccessibleForFree": True,
        "keywords": ["computational fluid dynamics", "CFD validation", "wind tunnel", "urban wind environment",
                     "pedestrian wind", "tracer gas dispersion", "Architectural Institute of Japan", "benchmark"],
        "creator": [{"@type": "Person", "name": n.split(" (")[0]} for n in editors],
        "citation": D.CITATION["benchmark"],
        "isBasedOn": [f"https://doi.org/{D.CASES[c]['doi']}" for c in D.CASE_IDS if D.CASES[c]["doi"]],
        "measurementTechnique": ["hot-wire anemometry (split-fibre probes)", "thermistor anemometry", "laser Doppler velocimetry",
                                 "sonic and cup anemometry (field)", "hydrocarbon analyser and sorbent-tube sampling (tracer gas)"],
        "variableMeasured": ["mean velocity components U, V, W", "velocity variances", "turbulent kinetic energy k",
                             "mean scalar wind speed", "velocity ratio", "tracer-gas concentration", "air temperature and turbulent fluxes"],
        "distribution": [
            {"@type": "DataDownload", "name": f"{D.CASES[c]['title']}, measurement table",
             "encodingFormat": "text/csv", "contentUrl": download(f"cases/{c}/points.csv")["url"]} for c in D.CASE_IDS
        ] + [
            {"@type": "DataDownload", "name": "Geometry of every case (STL, metres)", "encodingFormat": "application/zip",
             "contentUrl": download("geometry.zip")["url"]},
            {"@type": "DataDownload", "name": "API index", "encodingFormat": "application/json", "contentUrl": url("index.json")},
        ],
    }
    body = json.dumps(dataset, indent=1, ensure_ascii=False).replace("</", "<\\/")
    os.makedirs(os.path.join(DOCS, "_includes"), exist_ok=True)
    with io.open(os.path.join(DOCS, "_includes", "dataset-jsonld.html"), "w", encoding="utf-8", newline="\n") as f:
        f.write("<!-- Generated by scripts/build_api.py (write_dataset_jsonld). -->\n"
                f'<script type="application/ld+json">\n{body}\n</script>\n')


def write_citation_files():
    """The citations that are not part of the API: docs/_includes/cite.md, the <!--cite--> block of README.md, CITATION.cff
    and .zenodo.json, all rendered by scripts/citation.py for this release."""
    rel = release_citation()
    with io.open(os.path.join(DOCS, "_includes", "cite.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(C.site_include(rel))
    path = os.path.join(REPO, "README.md")
    with io.open(path, encoding="utf-8", newline="") as f:
        text = f.read()
    new = C.readme_with_cite(text, rel)
    if new != text:
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
    for name, body in (("CITATION.cff", C.cff(rel, D.CASES)), (".zenodo.json", C.zenodo_json(D.CASES))):
        with io.open(os.path.join(REPO, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(body)


def write_changelog_include():
    """docs/_includes/api-changelog.md: the changelog index.json serves, as Markdown for the API page."""
    L = ["<!-- Generated by scripts/build_api.py from CHANGELOG. -->", ""]
    for entry in CHANGELOG:
        for c in entry["changes"]:   # the text is Markdown here and plain text in index.json: a bare <word> would open an HTML tag
            if re.search(r"<[A-Za-z/!?]", re.sub(r"`[^`]*`", "", c)):
                raise SystemExit(f"CHANGELOG {entry['version']}: put the text with a '<' in `code` so Markdown does not read it as HTML: {c[:80]}")
        L += [f"### {entry['version']} ({entry['date']})", ""] + [f"- {c}" for c in entry["changes"]] + [""]
    with io.open(os.path.join(DOCS, "_includes", "api-changelog.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))


def expand(template):
    """The files a templated path stands for: every file this build wrote that the template matches."""
    rx = re.compile("^" + re.sub(r"\\\{[a-z]+\\\}", "[^/]+", re.escape(template)) + "$")
    return sorted(r for r in WRITTEN | {"index.json"} if rx.match(r))


def link(rel):
    """The URL a document gives for a file: plain for JSON, versioned (?v=) for downloads."""
    return url(rel) if rel.endswith(".json") else download(rel)["url"]


def endpoint_entry(path, media, schema, description):
    """A single-file endpoint carries its `url`; a templated one (cases/{id}.json) is not a URL to follow, so
    it says `templated` and lists every concrete file under `urls` (the template stays in `path`)."""
    entry = {"path": path, "method": "GET", "media_type": media, "description": description,
             "schema": schema_url(schema) if schema else None}
    if "{" in path:
        entry.update({"templated": True, "urls": [link(rel) for rel in expand(path)]})
    else:
        entry.update({"templated": False, "url": endpoint_url(path)})
    return entry


def endpoint_url(path):
    """Where a single-file endpoint is served: inside the tree, except the registry, which has one home."""
    return f"{LIVE_BASE}/{path}" if path in ROOT_ENDPOINTS else url(path)


def write_index():
    """Last: index.json lists every other file of the tree with its size and SHA-256."""
    files = sorted(WRITTEN - {"index.json"})
    write_json("index.json", "index", {
        "name": "AIJ UWE — cleaned data API",
        "description": ("Static JSON/CSV/STL endpoints for the Architectural Institute of Japan Urban Wind Environment "
                        f"benchmark (Cases {CASE_SPAN}) and Eddy3D's validation against it. Every file is a plain HTTP GET; nothing is computed on request."),
        "base_url": API_BASE,
        "tree": TREE,
        "release_base_url": PINNED_BASE,
        "versions_url": endpoint_url("versions.json"),
        "fallback_base_url": FALLBACK_BASE,
        "fallback_note": (f"the same files, served raw from the repository at the tag v{RELEASE}, which never moves (use when "
                          "the Pages site is not reachable)" if TREE == "release" else
                          "the same files, served raw from the repository's main branch (use when the Pages site is not reachable)"),
        "repository": REPO_URL, "site": SITE,
        "versions": {"release": RELEASE, "schema": SCHEMA_VERSION, "data": DATA_VERSION,
                     "clean_manifest": (D.clean_manifest() or {}).get("version")},
        "release": {"version": RELEASE, "date": RELEASE_DATE, "tag": f"v{RELEASE}",
                    "url": f"{REPO_URL}/releases/tag/v{RELEASE}", "base_url": RELEASE_BASE,
                    "changelog": f"{REPO_URL}/blob/v{RELEASE}/CHANGELOG.md"},
        "compatibility": COMPATIBILITY,
        "caching": CACHING,
        "changelog": CHANGELOG,
        "endpoints": [endpoint_entry(p, m, s, d) for p, m, s, d in ENDPOINTS],
        "case_ids": D.CASE_IDS,
        "files": [download(rel) for rel in files],
        "license_detail": D.LICENSE,
        "cite": {"api": C.api(release_citation()), **D.CITATION},
        "agents": {
            "start_here": url("llms.txt"),
            "pin_a_version": f"GET {endpoint_url('versions.json')} and use the base_url of the release you want; paths are the same in every release",
            "walk": ["GET index.json", "GET cases.json and pick an id", "GET cases/{id}.json for frame, units and known_issues",
                     "GET cases/{id}/points.json (SI units, one frame) and cases/{id}/geometry.stl (metres)",
                     "GET validation.json or cases/{id}/validation.json before quoting any Eddy3D score; an engine that is not 'scored' has no result"],
        },
    })


def remove_stale():
    """Delete anything in the current tree this build did not write (a renamed or retired file). Other releases'
    frozen trees and versions.json belong to no tree and are never touched."""
    for rel in sorted(tree_files(API) - WRITTEN):
        os.remove(os.path.join(API, rel))
        print("removed stale", os.path.relpath(os.path.join(API, rel), API_ROOT).replace(os.sep, "/"))
    dirs_below = []
    for root, dirs, _ in os.walk(API):
        if root == API_ROOT:
            dirs[:] = [d for d in dirs if not is_release_dir(d)]
        dirs_below += [os.path.join(root, d) for d in dirs]
    for p in sorted(dirs_below, key=len, reverse=True):
        if not os.listdir(p):
            os.rmdir(p)


# ----------------------------------------------------------------------------- the registry of releases

def release_record(v):
    """One entry of versions.json. A release with a tree under docs/api/ is described by that tree's own index.json;
    one without (a release from before the layout) by its tag and what LEGACY_RELEASES records."""
    date = R.release_date(v)
    if not date:
        raise SystemExit(f"CHANGELOG.md has no dated section for {v}, which versions.json lists")
    base = f"{LIVE_BASE}/{v}"
    raw_tag = RAW_BASE.replace("/main/", f"/v{v}/")
    rec = {"version": v, "date": date, "status": None}
    tree_index = os.path.join(API_ROOT, v, "index.json")
    if os.path.isfile(tree_index):
        with io.open(tree_index, encoding="utf-8") as f:
            idx = json.load(f)
        hosted_later = v in LEGACY_RELEASES   # put there by scripts/host_release.py, so the copy is on main, not in the tag; its fallback is the tag
        if hosted_later and (idx["versions"]["schema"], idx["versions"]["data"]) != tuple(LEGACY_RELEASES[v].values()):
            raise SystemExit(f"docs/api/{v}/index.json and LEGACY_RELEASES disagree on release {v}'s schema or data version")
        rec.update({"schema_version": idx["versions"]["schema"], "data_version": idx["versions"]["data"],
                    "base_url": base, "index_url": f"{base}/index.json",
                    "fallback_base_url": raw_tag if hosted_later else f"{raw_tag}/{v}", "self_contained": True})
        if hosted_later:
            rec["note"] = (f"Released before the versioned layout and hosted here afterwards by scripts/host_release.py: the files of "
                           f"tag v{v}, byte for byte, with only their own addresses rewritten into this copy. The raw files at the tag "
                           f"(release.base_url in this copy's index.json) are the originals.")
    else:
        rec.update({**LEGACY_RELEASES[v], "base_url": raw_tag, "index_url": f"{raw_tag}/index.json", "fallback_base_url": None,
                    "self_contained": False,
                    "note": ("Released before the versioned layout and not regenerated: base_url is the raw files at the release "
                             "tag. Its documents link to the live /api/ paths, not back into base_url, so fetch its files by the "
                             "paths in its index.json instead of following those links.")})
    rec.update({"tag": f"v{v}", "tag_url": f"{REPO_URL}/releases/tag/v{v}", "changelog_url": f"{REPO_URL}/blob/v{v}/CHANGELOG.md"})
    return rec


def versions_document(data_version):
    """versions.json: every release newest first. A pure function of docs/api/'s frozen trees, CHANGELOG.md and
    LEGACY_RELEASES, so verify() can rebuild it and compare."""
    found = sorted({*LEGACY_RELEASES, *release_dirs(), RELEASE}, key=R.parse, reverse=True)
    if found[0] != RELEASE:
        raise SystemExit(f"VERSION {RELEASE} is older than {found[0]}, which has a release tree: versions only move forward")
    records = [release_record(v) for v in found]
    for i, rec in enumerate(records):
        rec["status"] = "latest" if i == 0 else "superseded"
    return {
        "$schema": schema_url_in(LIVE_BASE, "versions"), "schema_version": SCHEMA_VERSION, "data_version": data_version,
        "license": D.LICENSE["spdx"],
        "description": ("Every release of the data and API, newest first. The unversioned /api/ paths serve `latest`. To pin an "
                        "analysis to a release, fetch its files from its `base_url` instead (the paths are those of its "
                        "index.json): a release's files never change. `data_version` is the latest release's."),
        "latest": RELEASE, "latest_base_url": LIVE_BASE, "versions": records,
    }


def write_versions(data_version):
    """docs/api/versions.json: one registry, served from the unversioned root only (it changes at every release, so no
    frozen tree can hold it)."""
    with io.open(os.path.join(API_ROOT, "versions.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(dump(versions_document(data_version)))


# ----------------------------------------------------------------------------- assets

def _png_size(path):
    """(width, height) of a PNG, from its IHDR chunk."""
    with open(path, "rb") as f:
        return struct.unpack(">II", f.read(24)[16:24])


def web_copy(src, dst):
    """A WEB_WIDTH px wide copy of a 1200 dpi master, for the pages; returns its (width, height).

    Deterministic: LANCZOS resampling, the encoder's own settings, no metadata chunks, so two builds write the same bytes.
    An opaque RGBA master is stored as RGB (the page is white; an alpha channel only adds bytes). Pillow is imported here,
    so --check needs none; the masters are up to 120 MP, which is why the pixel limit is lifted in this function only."""
    from PIL import Image
    limit = Image.MAX_IMAGE_PIXELS
    Image.MAX_IMAGE_PIXELS = None
    try:
        with Image.open(src) as master:
            im = master
            im.load()
            if im.mode == "RGBA" and im.getchannel("A").getextrema() == (255, 255):
                im = im.convert("RGB")
            if im.width > WEB_WIDTH:
                im = im.resize((WEB_WIDTH, round(im.height * WEB_WIDTH / im.width)), Image.LANCZOS)
            im.save(dst, format="PNG", optimize=True)
            return im.size
    finally:
        Image.MAX_IMAGE_PIXELS = limit


def copy_assets():
    """docs/assets/geometry/ = every render, docs/assets/figures/ = every figure a run names, docs/assets/web/ = a 1600 px
    copy of each (same file name), docs/_data/figures.json = what a page needs to embed them; nothing else."""
    wanted = {
        "geometry": {D.render_file(c, cfg) for (c, cfg) in D.RENDER_CAPTIONS},
        "figures": {fig for r in RUNS for fig in r["figures"]},
    }
    clash = wanted["geometry"] & wanted["figures"]
    if clash:
        raise SystemExit(f"a render and a figure share the file name {sorted(clash)}; the web copies are named alike in one folder")
    masters = {}
    for sub_dir, names in wanted.items():
        src = os.path.join(FIGURES, "geometry") if sub_dir == "geometry" else FIGURES
        dst = os.path.join(ASSETS, sub_dir)
        os.makedirs(dst, exist_ok=True)
        for stale in set(os.listdir(dst)) - names:
            os.remove(os.path.join(dst, stale))
        for name in sorted(names):
            shutil.copyfile(os.path.join(src, name), os.path.join(dst, name))
            masters[name] = (sub_dir, os.path.join(dst, name))
    os.makedirs(WEB, exist_ok=True)
    for stale in set(os.listdir(WEB)) - set(masters):
        os.remove(os.path.join(WEB, stale))
    FIGURE_INFO.clear()
    for name in sorted(masters):
        sub_dir, master = masters[name]
        web = os.path.join(WEB, name)
        width, height = web_copy(master, web)
        FIGURE_INFO[name] = {"master": f"/assets/{sub_dir}/{name}", "master_bytes": os.path.getsize(master),
                             "master_width": _png_size(master)[0], "master_height": _png_size(master)[1],
                             "web": f"/assets/web/{name}", "web_bytes": os.path.getsize(web), "width": width, "height": height}
    os.makedirs(DATA_FILES, exist_ok=True)
    with io.open(os.path.join(DATA_FILES, "figures.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(FIGURE_INFO, indent=1, ensure_ascii=False, sort_keys=True) + "\n")


# ----------------------------------------------------------------------------- the README's figures

# README.md is written by hand, except for the figures: each sits between <!--fig name="x.png" alt="..." width="700"-->
# and <!--/fig--> on one line, and the build writes what is between them (the 1600 px copy at the width given, linked to
# the full-size file).
FIG_MARKER = re.compile(r'<!--fig ((?:\w+="[^"]*"\s*)+)-->(.*?)<!--/fig-->')


def _readme_figure(attrs, info):
    name, width = attrs["name"], int(attrs["width"])
    f = info[name]
    master = "validation/figures/" + ("geometry/" if f["master"].startswith("/assets/geometry/") else "") + name
    img = (f'<img src="docs/assets/web/{name}" width="{width}" height="{round(width * f["height"] / f["width"])}" '
           f'loading="lazy" alt="{attrs["alt"]}">')
    return f'<a href="{master}">{img}</a>'


def readme_with_figures(text, info):
    def one(m):
        attrs = dict(re.findall(r'(\w+)="([^"]*)"', m.group(1)))
        return f"<!--fig {m.group(1)}-->{_readme_figure(attrs, info)}<!--/fig-->"
    return FIG_MARKER.sub(one, text)


README_FILES = ["README.md", "clean/README.md", "clean/SCHEMA.md", "clean/QUESTIONS.md"]     # GitHub renders these without Jekyll


def sync_readme():
    """The figures of README.md and the nomenclature blocks of the files GitHub renders without Jekyll, written from their sources."""
    for rel in README_FILES:
        path = os.path.join(REPO, rel)
        with io.open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        new = NM.with_blocks(readme_with_figures(text, FIGURE_INFO) if rel == "README.md" else text)
        if new != text:
            with io.open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new)


# ----------------------------------------------------------------------------- site pages

# Row labels for the case pages' tables: the API keeps its snake_case keys, the pages read as prose.
LABELS = {
    "D_m": "Block size D (m)", "H_m": "Height H (m)", "Re": "Reynolds number", "Re_D": "Reynolds number Re_D",
    "Re_H": "Reynolds number Re_H", "U_H_m_s": "U_H (m/s)", "U_H_note": "U_H, note", "array": "Array",
    "array_extent_m": "Array extent (m)", "b_m": "Width b (m)", "blocks": "Blocks", "building": "Building",
    "centre_building": "Centre building", "configurations": "Configurations", "configurations_note": "Configurations, note",
    "depth_m": "Depth (m)", "district": "District", "instrument": "Instrument", "measurement_height_m": "Measurement height (m)",
    "measurement_height_note": "Measurement height, note", "measurement_planes": "Measurement planes",
    "new_buildings": "New buildings", "normalisation": "Normalisation", "pitch_note": "Pitch, note", "points": "Points",
    "roads": "Roads", "scale": "Scale", "scale_note": "Scale, note", "states": "States", "tower": "Tower",
    "tunnel": "Wind tunnel", "values": "Values", "width_m": "Width (m)", "wind_directions": "Wind directions",
    "wind_directions_deg": "Wind directions (°)",
    "coordinate_scale_applied": "Coordinate scale applied", "lateral_sign_applied": "Lateral sign applied",
    "origin": "Origin", "wind_direction_rotation": "Wind direction convention",
    "U_H_measured_m_s": "U_H, measured (m/s)", "U_ref_15_9m_m_s": "U_ref at 15.9 m (m/s)", "log_law": "Log law",
    "log_law_error_at_H": "Log-law error at H", "method": "Method", "note": "Note", "power_law_exponent": "Power-law exponent",
    "power_law_exponent_fitted": "Power-law exponent, fitted", "power_law_exponent_paper": "Power-law exponent, data paper",
    "turbulence_intensity_at_D": "Turbulence intensity at D", "u_star_m_s": "Friction velocity u* (m/s)",
    "z0_mm": "Roughness length z₀ (mm)", "length": "Length", "variance": "Variance", "velocity": "Velocity",
    "velocity_ratio": "Velocity ratio", "concentration_ratio": "Concentration ratio", "campaign": "Campaign",
}


def _label(k):
    return LABELS.get(k, k.replace("_", " "))


def _config_part(k, v):
    """'2D', 'WD 22.5°', 'split fibre', 'before construction': one part of a configuration's name."""
    if k == "wind_direction_deg":
        return f"WD {v:g}°"
    if k == "config":
        return {"bc": "before construction", "ac": "after construction", "default": "default"}.get(v, v)
    return str(v).replace("_", " ")


def _escape(piece):
    for ch in "\\*_<>[]|'\"":             # quotes too: kramdown's smart quotes turn '-' into two opening quotes
        piece = piece.replace(ch, "\\" + ch)
    return piece


def _esc(text, math=False, lead=False, bare=False):
    """Plain text from the data, safe in Markdown on GitHub and in kramdown: emphasis, HTML, link and pipe characters are
    backslash-escaped (a line with a bare pipe is a table to kramdown), and a Liquid delimiter (which the site build would try to run) stops the build.
    `math`: the symbols and formulas in it become LaTeX between $$ (scripts/mathtext.py); `lead`: a symbol at its head is a symbol (a score label),
    `bare`: the whole text is a table cell, so a bare symbol is a symbol."""
    text = str(text)
    if "{{" in text or "{%" in text:
        raise SystemExit(f"a Liquid delimiter in text that becomes a page: {text[:80]!r}")
    out = []
    for i, piece in enumerate(re.split(r"(https?://[^\s<>]+)", text)):
        if i % 2:                                  # a URL becomes an autolink, which GitHub and kramdown both follow
            url, tail = re.match(r"(.*?)([.,;:]*)$", piece).groups()
            out.append(f"<{url}>" + tail)
            continue
        out.append(MT.to_markdown(piece, _escape, lead=lead and i == 0, bare=bare) if math else _escape(piece))
    return "".join(out)


def _tex(text, **kw):
    """_esc with the math of the text as LaTeX: what a page says about the quantities."""
    return _esc(text, math=True, **kw)


def _cell(text, **kw):
    """A table cell's text: _tex, which also escapes the pipe that would end the cell."""
    return _tex(text, **kw)


def _md_value(v, sink=None):
    """A configuration value as the text of one table cell: escaped once (the cell's pipes too, as in |y|). The
    reasoning part of a text (page_prose) is appended to `sink`, for the collapsed section under the table; a text
    that has one needs a sink."""
    if isinstance(v, dict):
        return "<br>".join(f"**{_tex(_label(k))}**: {_md_value(x, sink)}" for k, x in v.items())
    if isinstance(v, list):
        return ", ".join(_cell(x) for x in v)
    if isinstance(v, int) and not isinstance(v, bool) and abs(v) >= 10000:
        return f"{v:,}"
    if isinstance(v, str):
        shown, collapsed = P.split(v, cell=True)
        if collapsed:
            if sink is None:
                raise SystemExit(f"a text with a collapsed part where the page has no place for it: {v[:70]!r}")
            sink.append(collapsed)
        return _cell(shown)
    return _cell(v)


MIN_SECTION = 150      # a collapsed section shorter than this is a fragment: keep its text visible or give it neighbours


def _sections(collapsed):
    """Collapsed sections for [(kind, topic, text)]: one <details> per (kind, topic).
    `Interpretation: <topic>` holds a reading of a result, `Data notes: <topic>` the evidence behind a data convention.
    The texts of one topic read as one paragraph."""
    groups = {}
    for kind, topic, text in collapsed:
        if text not in groups.setdefault((kind, topic), []):
            groups[(kind, topic)].append(text)
    L = []
    for (kind, topic), texts in groups.items():
        if len(" ".join(texts)) < MIN_SECTION:
            raise SystemExit(f"a collapsed section is a fragment ({P.SUMMARY[kind]}: {topic}): {' '.join(texts)!r}")
        L += ['<details markdown="block">', f"<summary>{P.SUMMARY[kind]}: {topic}</summary>", "", _tex(" ".join(texts)), "", "</details>", ""]
    return L


def _asset(rel):
    return f"{{{{ '{rel}' | relative_url }}}}"


def _plain(html):
    """A caption as plain text (for alt attributes): tags dropped, quotes escaped."""
    out, inside = [], False
    for ch in html:
        inside = True if ch == "<" else False if ch == ">" else inside
        if not inside and ch != ">":
            out.append(ch)
    return "".join(out).replace('"', "&quot;")


def _web_img(f, alt):
    return (f'<img src="{_asset(f["web"])}" width="{f["width"]}" height="{f["height"]}" loading="lazy" '
            f'alt="{_plain(alt)}">')


def figure(src, alt, caption, cls="figure", markdown=False):
    """One image with its caption, as HTML (<figure>), so the caption stays attached to the image. The page shows the
    1600 px copy; the image links to the full-size file. `markdown`: the caption is Markdown (with formulas), which kramdown
    reads inside <figcaption markdown="span">; GitHub shows these pages as source, where the images are broken anyway."""
    f = FIGURE_INFO[src.rsplit("/", 1)[-1]]
    return [f'<figure class="{cls}">', f'<a href="{_asset(f["master"])}">{_web_img(f, alt)}</a>',
            f'<figcaption{" markdown=" + chr(34) + "span" + chr(34) if markdown else ""}>{caption}</figcaption>', "</figure>", ""]


def figure_table(cells, columns, caption=None):
    """Images side by side in a Markdown table marked {: .figures } (see docs/_sass/custom/custom.scss):
    cells are (src, alt, caption, link or None); the header row is blank and hidden by the stylesheet. An image with
    a link leads there; one without leads to the full-size file."""
    L = ["|" + " |" * columns, "|" + "---|" * columns]
    for i in range(0, len(cells), columns):
        row = []
        for src, alt, cap, link in cells[i:i + columns]:
            f = FIGURE_INFO[src.rsplit("/", 1)[-1]]
            img = f'<a href="{_asset(link or f["master"])}">{_web_img(f, alt)}</a>'
            row.append(f"{img}<br><span class=\"caption\">{cap.replace('|', '&#124;')}</span>")
        row += [" "] * (columns - len(row))
        L.append("| " + " | ".join(row) + " |")
    L += ["{: .figures }", ""]
    if caption:
        L += [f'<p class="caption">{caption}</p>', ""]
    return L


# What the gallery says under each render. A case without an entry gets its one-line summary and its counts, so a
# new case needs no change here.
GALLERY_CAPTIONS = {
    "A": "Isolated building · {points} points · U, V, W and k",
    "B": "Isolated slab · {points} points · U, V, W and k",
    "C": "Centre block at 0D, 1D or 2D (2D shown) · {rows} scalar speeds at pedestrian height, 3 wind directions",
    "D": "A tower among 82 low blocks · {rows} measurements: scalar speed at 3 wind directions, velocity at 33 points",
    "E": "Before and after a 60 m high-rise (after shown) · {rows} velocity ratios over 16 wind directions",
}
# The caption of a case page's figure when the case has several renders (configurations on one scale).
RENDER_GROUP_CAPTIONS = {
    "C": "The three configurations of the centre block, on one scale; 120 measurement points each, at three wind directions.",
    "E": "The two states, on one scale (full-scale metres, +x east, +y north); the arrow marks SW, the direction Eddy3D is scored at.",
}

ENGINE_SHORT = {"openfoam12-realizableKE": "OpenFOAM 12", "openfoam12-kEpsilon": "OpenFOAM 12 k-ε", "openfoam12-kOmegaSST": "OpenFOAM 12 k-ω SST",
                "umf-realizableKE": "UMF", "umf-buoyantKEpsilon": "UMF buoyantKEpsilon",
                "openlb": "OpenLB", "fluidx3d": "FluidX3D", "ml-surrogate": "ML surrogate"}
STATUS_CLASS = {"scored": "label-green", "running": "label-blue", "pending": "label-yellow", "not comparable": "label-grey"}
# Where the hand-written validation pages show each figure, beside its reading. A case's own Validation page links
# there instead of repeating the figure, so a figure is on the site once. A figure that is not listed is shown on the
# case's Validation page, unless it illustrates runs of ALL_CASES_FIGURE_MIN or more cases: then it is an all-cases
# figure, and the case pages link to the Validation overview instead of each repeating it.
FIGURE_HOME = {
    "cases-ab-openfoam-agreement.png": ("/validation/cases-ab/", "Cases A and B (OpenFOAM)"),
    "cases-ab-openfoam-profiles.png": ("/validation/cases-ab/", "Cases A and B (OpenFOAM)"),
    "cases-ab-engine-comparison.png": ("/validation/engines/", "OpenLB and FluidX3D"),
    "case-c-openfoam-agreement.png": ("/validation/case-c/", "Case C (OpenFOAM)"),
    "case-c-openfoam-bias-map.png": ("/validation/case-c/", "Case C (OpenFOAM)"),
    "case-d-openfoam-agreement.png": ("/validation/case-d/", "Case D (OpenFOAM)"),
    "case-e-openfoam-agreement.png": ("/validation/case-e/", "Case E (OpenFOAM)"),
    "case-e-openfoam-bias-map.png": ("/validation/case-e/", "Case E (OpenFOAM)"),
    "cases-hi-openfoam-agreement.png": ("/validation/cases-hi/", "Cases H and I (OpenFOAM)"),
    "case-i-openfoam-closures.png": ("/validation/cases-hi/", "Cases H and I (OpenFOAM)"),
    "case-k-openfoam-agreement.png": ("/validation/cases-gk/", "Cases G and K (OpenFOAM)"),
    "case-g-openfoam-sweep.png": ("/validation/cases-gk/", "Cases G and K (OpenFOAM)"),
    "case-g-openfoam-stations.png": ("/validation/cases-gk/", "Cases G and K (OpenFOAM)"),
    "case-j-umf-agreement.png": ("/validation/cases-jl/", "Cases J and L (UMF)"),
    "case-j-umf-tracer.png": ("/validation/cases-jl/", "Cases J and L (UMF)"),
    "case-l-umf-agreement.png": ("/validation/cases-jl/", "Cases J and L (UMF)"),
    "case-f-openfoam-agreement.png": ("/validation/cases-fm/", "Cases F and M (OpenFOAM)"),
    "case-f-openfoam-bias-map.png": ("/validation/cases-fm/", "Cases F and M (OpenFOAM)"),
    "case-m-openfoam-agreement.png": ("/validation/cases-fm/", "Cases F and M (OpenFOAM)"),
    "case-m-openfoam-plan.png": ("/validation/cases-fm/", "Cases F and M (OpenFOAM)"),
    "ml-surrogate-agreement.png": ("/validation/ml-surrogate/", "ML surrogate"),
    "case-a-layout.png": ("/validation/cases-ab/", "Cases A and B (OpenFOAM)"),
    "case-b-layout.png": ("/validation/cases-ab/", "Cases A and B (OpenFOAM)"),
    "case-g-layout.png": ("/validation/cases-gk/", "Cases G and K (OpenFOAM)"),
    "case-k-layout.png": ("/validation/cases-gk/", "Cases G and K (OpenFOAM)"),
    "case-h-layout.png": ("/validation/cases-hi/", "Cases H and I (OpenFOAM)"),
    "case-i-layout.png": ("/validation/cases-hi/", "Cases H and I (OpenFOAM)"),
    "case-j-layout.png": ("/validation/cases-jl/", "Cases J and L (UMF)"),
    "case-l-layout.png": ("/validation/cases-jl/", "Cases J and L (UMF)"),
    "case-c-layout.png": ("/validation/case-c/", "Case C (OpenFOAM)"),
    "case-d-layout.png": ("/validation/case-d/", "Case D (OpenFOAM)"),
    "case-e-layout.png": ("/validation/case-e/", "Case E (OpenFOAM)"),
    "case-f-layout.png": ("/validation/cases-fm/", "Cases F and M (OpenFOAM)"),
    "case-m-layout.png": ("/validation/cases-fm/", "Cases F and M (OpenFOAM)"),
}
ALL_CASES_FIGURE_MIN = 3
# A score table stays open up to this many rows, a table of configurations up to OPEN_LIST_ROWS; a longer one sits in
# a closed <details>.
OPEN_TABLE_ROWS = 12
OPEN_LIST_ROWS = 8
# Facts the case page's "At a glance" table shows, one row per group: the first configuration key present in it,
# under that key's label. The Data page has everything.
GLANCE = [("building", "array", "tower", "district"), ("scale",), ("Re_H", "Re_D", "Re"), ("U_H_m_s", "normalisation"),
          ("wind_directions", "wind_directions_deg"), ("measurement_height_m", "measurement_planes")]


def _engine_name(engine_id):
    return ENGINE_SHORT.get(engine_id, engine_id)


def status_label(status):
    return f'<span class="label {STATUS_CLASS[status]} status">{status}</span>'


def _front(title, nav_order, parent=None, grand_parent=None, has_children=None, has_toc=None, description=None):
    """Front matter of a generated page. `generated: true` makes the footer point at this script, not at the page."""
    L = ["---", f'title: "{title}"']
    if parent:
        L.append(f'parent: "{parent}"')
    if grand_parent:
        L.append(f'grand_parent: "{grand_parent}"')
    L.append(f"nav_order: {nav_order}")
    if has_children is not None:
        L.append(f"has_children: {'true' if has_children else 'false'}")
    if has_toc is not None:
        L.append(f"has_toc: {'true' if has_toc else 'false'}")
    L.append("generated: true")
    if description:
        L.append(f'description: "{description.replace(chr(34), chr(39))}"')
    return L + ["---", ""]


def _write(rel, lines):
    path = os.path.join(DOCS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines).rstrip("\n") + "\n")


def _page_url(slug, sub=""):
    return f"/cases/{slug}/" + (f"{sub}/" if sub else "")


def _link(text, url, anchor=""):
    return f"[{text}]({_asset(url)}{anchor})"


SCORE_COLUMN = re.compile(r"\|\s*(?:R|FAC2|FB|Hit rate|n)(?: \(range\))?\s*(?=\|)")


def _legend(table):
    """The include that goes under a table (scripts/nomenclature.py): the scores for a table of scores, the whole nomenclature for a table that
    shows a symbol (it is the lines [header, delimiter, rows...]); nothing for a table that shows none. A blank line first, none after."""
    if SCORE_COLUMN.search(table[0]):
        kind = "scores"
    elif any("$$" in line for line in table):
        kind = "full"
    else:
        return []
    return ["", "{% include " + NM.INCLUDES[kind] + " %}"]


def _toc():
    """just-the-docs' collapsible table of contents of a page's headings."""
    return ['<details open markdown="block">', "  <summary>", "    Contents", "  </summary>", "  {: .text-delta }",
            "1. TOC", "{:toc}", "</details>", ""]


def _is_control(label):
    """A headline whose label says 'control' is a negative control (the frame flipped, the wind reversed, the
    building removed): it shows the test can fail, it is not a result, so no summary of results includes it."""
    return "control" in label.lower()


def _compared_with(case, label):
    """'Field' or 'Wind tunnel': what a headline score is compared with. Case G is field data alone; F and M have both, and
    their field scores are the ones whose label names the field."""
    return "Field" if case == "G" or (case in ("F", "M") and "field" in label.lower()) else "Wind tunnel"


def _headline_ranges(entries, case=None, source=None):
    """{'R': (lo, hi), 'Fac2': (lo, hi)} over the headline scores of these validation entries, controls excluded, and only
    those compared with `source` when it is given; None when there is none."""
    vals = {"R": [], "Fac2": []}
    for e in entries:
        for label, key in e["headline"].items():
            if _is_control(label) or (source and _compared_with(case, label) != source):
                continue
            for m in vals:
                v = e["scores"][key].get(m)
                if v is not None:
                    vals[m].append(v)
    if not vals["R"]:
        return None
    return {m: (min(v), max(v)) for m, v in vals.items() if v}


def _range(lo_hi, signed):
    if lo_hi is None:
        return "—"
    lo, hi = (f"{x:+.2f}" if signed else f"{x:.2f}" for x in lo_hi)
    return lo if lo == hi else f"{lo} … {hi}"


def _shared_figures(percase):
    """Figures of runs of at least ALL_CASES_FIGURE_MIN cases: {file name: set of case ids}."""
    users = {}
    for case, p in percase.items():
        for e in p["results"]:
            for fig in e["figures"]:
                users.setdefault(fig["url"].rsplit("/", 1)[-1], set()).add(case)
    return {name: cases for name, cases in users.items() if len(cases) >= ALL_CASES_FIGURE_MIN}


def build_gallery(percase):
    """docs/_includes/case-gallery.md: every case, two to a row (three once there are more than six), each render
    linked to its page."""
    cells = []
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        summ = percase[case]["summ"]
        counts = dict(points=f"{summ['distinct_points']:,}", rows=f"{summ['rows']:,}")
        cap = (_tex(GALLERY_CAPTIONS[case].format(**counts)) if case in GALLERY_CAPTIONS
               else f"{_tex(meta['short'])} · {counts['rows']} rows")
        cells.append((f"/assets/geometry/{D.render_file(case)}", meta["title"], f"<strong>{meta['title']}</strong><br>{cap}",
                      _page_url(meta["slug"])))
    _write("_includes/case-gallery.md",
           ["<!-- Generated by scripts/build_api.py; edit GALLERY_CAPTIONS there. -->", ""]
           + figure_table(cells, 2 if len(cells) <= 6 else 3))


def build_cases_table(percase):
    """docs/_includes/cases-table.md: one row per case, what it is, what was measured, which engines have a validation run."""
    L = ["<!-- Generated by scripts/build_api.py. -->", "",
         "| Case | What it is | Measured | Validation |", "|---|---|---|---|"]
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        summ = percase[case]["summ"]
        scored = [_engine_name(e["id"]) for e in case_engines(case) if ENGINE_STATUS[case][e["id"]] == "scored"]
        measured = f"{summ['rows']:,} rows over {summ['distinct_points']:,} points; {NM.column_symbols(meta['quantities'])}"
        L.append(f"| {_link(_esc(meta['title']), _page_url(meta['slug']))} | {_cell(meta['short'])} | {measured} | "
                 f"{', '.join(scored) if scored else 'none yet'} |")
    _write("_includes/cases-table.md", L)


def build_cases_frames():
    """docs/_includes/cases-frames.md: each case's length unit, the unit of what it measures, and its origin."""
    L = ["<!-- Generated by scripts/build_api.py. -->", "", "| Case | Length unit | Measured in | Origin |", "|---|---|---|---|"]
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        units = meta["units"]
        measured = units.get("velocity", next((v for k, v in units.items() if k != "length"), ""))
        L.append(f"| {_link(_esc(meta['title']), _page_url(meta['slug'], 'data'), '#frame-and-units')} | {_cell(units.get('length', ''))} | "
                 f"{_cell(measured)} | {_cell(meta['frame'].get('origin', ''))} |")
    _write("_includes/cases-frames.md", L)


def build_validation_matrix(percase):
    """docs/_includes/validation-matrix.md: every case against every engine, status and the range of the headline
    R and FAC2 (negative controls excluded). Five columns of short cells: it needs no sideways scrolling."""
    L = ["<!-- Generated by scripts/build_api.py. -->", "",
         "| Case | " + " | ".join(_engine_name(e["id"]) for e in MATRIX_ENGINES) + " |", "|---" * (len(MATRIX_ENGINES) + 1) + "|"]
    for case in D.CASE_IDS:
        meta = D.CASES[case]
        cells = []
        for e in MATRIX_ENGINES:
            if e["id"] not in ENGINE_STATUS[case]:       # UMF applies to the non-isothermal cases J and L only
                cells.append("—")
                continue
            status = ENGINE_STATUS[case][e["id"]]
            entries = [r for r in percase[case]["results"] if r["engine"] == e["id"]]
            cell = status_label(status)
            ranges = _headline_ranges(entries) if entries else None
            if ranges:
                cell += (f'<br><span class="caption">R {_range(ranges["R"], True)}'
                         f'<br>FAC2 {_range(ranges.get("Fac2"), False)}</span>')
            cells.append(cell)
        got = {_compared_with(case, label) for r in percase[case]["results"] for label in r["headline"] if not _is_control(label)}
        note = "" if got == {"Wind tunnel"} else '<br><span class="caption">compared with ' + " and ".join(
            {"Wind tunnel": "the wind tunnel", "Field": "the field"}[s] for s in ("Wind tunnel", "Field") if s in got) + "</span>"
        L.append(f"| {_link(_esc(meta['title']), _page_url(meta['slug'], 'validation'))}{note} | " + " | ".join(cells) + " |")
    _write("_includes/validation-matrix.md", L)


def build_nomenclature():
    """docs/_includes/nomenclature.md, nomenclature-scores.md and metrics.md: the one nomenclature (scripts/nomenclature.py), as the pages include it."""
    for kind, name in NM.INCLUDES.items():
        _write(f"_includes/{name}", NM.include_text(kind).rstrip("\n").split("\n"))


def build_known_issues():
    """docs/_includes/known-issues-fm.md: the known issues of the cases whose sections are not hand-written (F to M), one
    section per case, from the same lists the Data pages and llms.txt carry."""
    L = ["<!-- Generated by scripts/build_api.py from each case's known_issues. -->", ""]
    for case in D.CASE_IDS:
        if case in "ABCDE":
            continue
        meta = D.CASES[case]
        L += [f"## Case {case}", "", f"{_esc(meta['title'])}.", ""] + _issue_list(meta["known_issues"])
    _write("_includes/known-issues-fm.md", L)


def build_version_label():
    """docs/_includes/version-label.html: the release, the API schema version and the data fingerprint, for the
    sidebar footer. The numbers are this build's, so the label cannot say something the files do not."""
    _write("_includes/version-label.html", [
        "<!-- Generated by scripts/build_api.py. -->",
        f'<span class="version-label"><a href="{{{{ \'/api-reference/versions/\' | relative_url }}}}">Release {RELEASE}</a>'
        f' · API schema {SCHEMA_VERSION}'
        f' · <abbr title="SHA-256 of the served data; the full value is in api/index.json">data {DATA_VERSION[:8]}</abbr></span>'])


def _lower_first(s):
    """'In the CSV's own frame' -> 'in the CSV's own frame' after a label; an acronym or a symbol keeps its form."""
    return s[0].lower() + s[1:] if re.match(r"[A-Z][a-z]+\b", s) else s


def _frame_facts(meta):
    """One line per fact a comparison depends on, read from the case's frame and units: where the cleaned table
    differs from the published files, and the wind-direction convention."""
    frame, facts = meta["frame"], []
    facts.append(f"Origin: {_tex(frame['origin'])}. Length unit: {_tex(meta['units']['length'])}.")
    if frame.get("coordinate_scale_applied") not in (None, 1, 1.0):
        facts.append(f"The published coordinates are multiplied by {frame['coordinate_scale_applied']:g} in the cleaned table "
                     "(`coordinate_scale_applied`).")
    if frame.get("lateral_sign_applied") not in (None, 1):
        facts.append(f"The lateral velocity V is multiplied by {frame['lateral_sign_applied']} in the cleaned table "
                     "(`lateral_sign_applied`): the published file's V has the other sign convention.")
    if "wind_direction_rotation" in frame:
        shown, _ = P.split(frame["wind_direction_rotation"], cell=True)
        facts.append(f"Wind direction: {_tex(_lower_first(shown).rstrip('.'))}.")
    return facts


# One line a case's pages show beside its scores, where the scores alone would be read as more than they are.
CASE_CAVEATS = {"G": _G_CAL}


def _case_page(case, meta, p, shared):
    summ, results = p["summ"], p["results"]
    base, data_url, val_url = _page_url(meta["slug"]), _page_url(meta["slug"], "data"), _page_url(meta["slug"], "validation")
    n = D.CASE_IDS.index(case) + 1
    L = _front(meta["title"], n, parent="Cases", has_children=True, has_toc=False, description=meta["short"])
    L += [f"# {meta['title']}", "", f"{_tex(meta['short'])}", "{: .fs-5 .fw-300 .lede }", "",
          f"{_link('Reference data', data_url)}{{: .btn .btn-primary }} {_link('Validation', val_url)}{{: .btn }} "
          f"{_link('Case as JSON', f'/api/cases/{case}.json')}{{: .btn }}", ""]
    cfgs = [cfg for (c, cfg) in D.RENDER_CAPTIONS if c == case]
    if not cfgs:
        pass                                           # a case without a render has no figure
    elif len(cfgs) == 1:
        L += figure(f"/assets/geometry/{D.render_file(case)}", meta["title"], D.RENDER_CAPTIONS[(case, cfgs[0])], "figure render")
    else:
        group = RENDER_GROUP_CAPTIONS.get(case, f"The configurations of {meta['title']}, on one scale.")
        L += figure_table([(f"/assets/geometry/{D.render_file(case, cfg)}", f"{meta['title']}, {cfg}",
                            D.RENDER_CAPTIONS[(case, cfg)], None) for cfg in cfgs], min(len(cfgs), 3), group)
    glance = ["| Fact | Value |", "|---|---|"]
    conf = meta["configuration"]
    for keys in GLANCE:
        key = next((k for k in keys if k in conf), None)
        if key:
            glance.append(f"| {_cell(_label(key))} | {_md_value(conf[key])} |")
    glance.append(f"| Measured | {summ['rows']:,} rows over {summ['distinct_points']:,} points: {NM.column_symbols(meta['quantities'])} |")
    L += ["## At a glance", ""] + glance + _legend(glance) + ["", "## Validation", ""]
    if results:
        status = ["| Engine | Status | Compared with | R (range) | FAC2 (range) |", "|---|---|---|---|---|"]
        for e in case_engines(case):
            mine = [r for r in results if r["engine"] == e["id"]]
            head = f"| {_engine_name(e['id'])} | {status_label(ENGINE_STATUS[case][e['id']])} | "
            rows = [(source, _headline_ranges(mine, case, source)) for source in ("Wind tunnel", "Field")]
            rows = [(source, ranges) for source, ranges in rows if ranges]
            for source, ranges in rows or [("—", None)]:
                status.append(head + f"{source} | " + (" | ".join((_range(ranges["R"], True), _range(ranges.get("Fac2"), False))) if ranges else "— | —") + " |")
        L += status + ["{: .scores }"] + _legend(status) + [""]
        if case in CASE_CAVEATS:
            L += [CASE_CAVEATS[case], ""]
    else:
        L += [f"**No validation has been run for this case yet.** {QUEUED} Engine status: "
              + " · ".join(f"{_engine_name(k)} {status_label(v)}" for k, v in ENGINE_STATUS[case].items()), ""]
    L += ["{: .warning-title }", "> Before you compare", ">",
          "> - The cleaned table is in SI units and one frame, with this case's corrections applied once. Do not apply them again."]
    for t in _frame_facts(meta):
        L.append(f"> - {t}")
    L += [f"> - {len(meta['known_issues'])} known issues in the published files are listed under "
          f"{_link('Known data issues', data_url, '#known-data-issues')}.", ""]
    return L


def _issue_list(issues):
    """The known issues as a list of the facts, then the collapsed Data notes behind them; ends with a blank line."""
    L, collapsed = [], []
    for g in issues:
        shown, c = P.split(g)
        L.append(f"- {_tex(shown)}")
        if c:
            collapsed.append(c)
    return L + [""] + _sections(collapsed)


def _case_data_page(case, meta, p):
    summ, configs = p["summ"], p["configs"]
    n = D.CASE_IDS.index(case) + 1
    L = _front("Data", 1, parent=meta["title"], grand_parent="Cases", has_children=False,
               description=f"{meta['title']}: configuration, frame and units, reference data, inflow and known data issues.")
    L += [f"# Case {case}: reference data", "{: .no_toc }", ""] + _toc()
    sink = []
    table = ["| Parameter | Value |", "|---|---|"]
    for k, v in meta["configuration"].items():
        table.append(f"| {_cell(_label(k))} | {_md_value(v, sink)} |")
    L += ["## Configuration", ""] + table + _legend(table) + [""] + _sections(sink)
    sink = []
    table = ["| Property | Definition |", "|---|---|"]
    for k, v in meta["frame"].items():
        table.append(f"| {_cell(_label(k))} | {_md_value(v, sink)} |")
    for k, v in meta["units"].items():
        table.append(f"| Unit of {NM.m(NM.COLUMN_TEX[k]) if k in NM.COLUMN_TEX else _cell(_label(k).lower())} | {_cell(v)} |")
    L += ["## Frame and units", ""] + table + _legend(table) + [""] + _sections(sink)
    af = meta.get("approach_flow_file")
    L += ["## Reference data", "",
          f"Source in this repository: [`{meta['reference_file']}`]({REPO_URL}/blob/main/{meta['reference_file']})"
          + (f" (approach flow: [`{af}`]({REPO_URL}/blob/main/{af}))" if af else "") + ".", "",
          f"The cleaned table has **{summ['rows']:,} rows** over **{summ['distinct_points']:,} distinct points**; "
          f"columns `{'`, `'.join(summ['columns'])}`.", ""]
    if summ["nulls"]:
        L += ["Unmeasured cells (null): " + ", ".join(f"`{k}` {v}" for k, v in summ["nulls"].items()) + ".", ""]
    rows = []
    for c in configs:
        key = ", ".join(_config_part(k, v) for k, v in c.items() if k not in ("points", "measured", "points_per_direction", "wind_directions"))
        val = c.get("points", c.get("points_per_direction"))
        if "measured" in c:
            val = f"{val} ({c['measured']} measured)"
        if "wind_directions" in c:
            key += ", 16 wind directions"
            val = f"{val} per direction"
        rows.append(f"| {_esc(key)} | {val} |")
    table = ["| Configuration | Points |", "|---|---|"] + rows
    if len(rows) > OPEN_LIST_ROWS:
        L += ['<details markdown="block">', f"  <summary>The {len(rows)} configurations and their points</summary>", ""] + table + ["", "</details>", ""]
    else:
        L += table + [""]
    cols = ["| Column | Symbol | Meaning |", "|---|---|---|"] + [
        f"| `{c}` | {NM.m(NM.COLUMN_TEX[c]) if c in NM.COLUMN_TEX else ''} | {_cell(COLUMN_MEANING.get(c, ''))} |" for c in summ["columns"]]
    L += ["## Columns", "", "The columns of the cleaned table (`points.csv`, `points.json`), in order.", ""]
    if len(cols) - 2 > OPEN_LIST_ROWS:
        L += ['<details markdown="block">', f"  <summary>The {len(cols) - 2} columns and what each holds</summary>", ""] + cols + _legend(cols) + ["", "</details>", ""]
    else:
        L += cols + _legend(cols) + [""]
    inflow = meta.get("inflow_fit")
    if inflow:
        sink = []
        table = ["| Property | Value |", "|---|---|"]
        for k, v in inflow.items():
            if k == "windows":
                for w in v:
                    table.append("| Fit window | " + "; ".join(f"{_cell(_label(a))} {_cell(b)}" for a, b in w.items()) + " |")
            else:
                table.append(f"| {_cell(_label(k))} | {_md_value(v, sink)} |")
        L += ["## Inflow", ""] + table + _legend(table) + [""] + _sections(sink)
    L += ["## Known data issues", ""] + _issue_list(meta["known_issues"])
    L += ["## API", "", "| Resource | Endpoint |", "|---|---|"]
    for name, rel in (("Case", f"cases/{case}.json"), ("Points (JSON)", f"cases/{case}/points.json"),
                      ("Points (CSV)", f"cases/{case}/points.csv"), ("Approach flow (CSV)", f"cases/{case}/approach_flow.csv"),
                      ("Geometry", f"cases/{case}/geometry.json"), ("Geometry (STL)", f"cases/{case}/geometry.stl"),
                      ("Validation", f"cases/{case}/validation.json")):
        L.append(f"| {name} | {_link('`/api/' + rel + '`', '/api/' + rel)} |")
    L += ["", "## Attribution", "", f"- {_collected_by(meta)}",
          f"- Edited and distributed by {_esc(_and_join(meta['people']['editors_distributors']))}."]
    if meta["doi"]:
        L.append(f"- DOI: [{meta['doi']}](https://doi.org/{meta['doi']})")
    elif meta.get("doi_note"):
        L.append(f"- DOI: {_esc(meta['doi_note'])}")
    L += [f"- Citation requested: {_esc(meta['citation_requested'])}", "- Licence: CC BY 4.0", ""]
    return L + C.case_section(case, meta)


def _and_join(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def _collected_by(meta):
    """'Data collected by <names>.' The sources give no year of collection: the year of the requested citation is a publication year."""
    return f"Data collected by {_esc(_and_join(meta['people']['data_collectors']))}."


def _score_table(e):
    """One run's headline scores: a row per score, the metrics across. A bare '|' in a label (|U|) is escaped."""
    L = ["| Score | R | FAC2 | FB | Hit rate | n |", "|---|---|---|---|---|---|"]
    for label, key in e["headline"].items():
        s = e["scores"][key]
        num = lambda m, f: "—" if s.get(m) is None else f"{s[m]:{f}}"  # noqa: E731
        L.append(f"| {_cell(label, lead=True, bare=True)} | {num('R', '+.3f')} | {num('Fac2', '.3f')} | {num('Fb', '+.3f')} | "
                 f"{num('HitRate', '.3f')} | {num('Count', 'd')} |")
    L.append("{: .scores }")
    return L + _legend(L)


REPRODUCE_TAIL = "; scores recomputed"       # in a run's `reproduce`: what comes after is how the scores were made, not how to run it


def _notes(notes):
    """Run notes as a list of the facts, then the collapsed Interpretation sections behind them."""
    L, collapsed = [], []
    for n in notes:
        shown, c = P.split(n)
        if shown:
            L.append(f"- {_tex(shown)}")
        if c:
            collapsed.append(c)
    return L, collapsed


def _case_validation_page(case, meta, p, shared):
    results = p["results"]
    n = D.CASE_IDS.index(case) + 1
    L = _front("Validation", 2, parent=meta["title"], grand_parent="Cases", has_children=False,
               description=f"{meta['title']}: Eddy3D's scores against the measurements, by engine.")
    L += [f"# Case {case}: validation", "{: .no_toc }", ""]
    L += ["Engine status: " + " · ".join(f"{_engine_name(k)} {status_label(v)}" for k, v in ENGINE_STATUS[case].items()), ""]
    if case in CASE_CAVEATS:
        L += [CASE_CAVEATS[case], ""]
    if not results:
        L += [f"**No validation has been run for this case yet.** {QUEUED}", ""]
        return L
    names = {e["id"]: e["name"] for e in ENGINES}
    # What every run of the page has in common is said once, after the runs.
    many = len(results) > 1
    all_quantity = many and len({e["quantity"] for e in results}) == 1 and bool(results[0]["quantity"])
    all_norm = many and len({e["normalisation"] for e in results}) == 1
    all_pairs = many and len({e["pairs"]["path"] for e in results}) == 1
    own_notes = lambda e: [n for n in e["notes"] if n not in CASE_CAVEATS.values()]   # the caveat is printed above  # noqa: E731
    all_notes = [n for n in own_notes(results[0]) if all(n in e["notes"] for e in results[1:])] if many else []
    figures, fig_no, tails = [], 1, []
    for e in results:
        L += [f"## {_esc(names[e['engine']])}" + (f", configuration {_esc(e['configuration'])}" if e["configuration"] else ""), ""]
        if e["quantity"] and not all_quantity:
            L += [f"Quantity: {_tex(e['quantity'])}.", ""]
        if e["recirculation_Lr_over_H"] is not None:
            L += [f"Reattachment length {NM.m('L_r/H')} = {e['recirculation_Lr_over_H']:.2f}.", ""]
        table = _score_table(e)
        if len(e["headline"]) > OPEN_TABLE_ROWS:
            L += ['<details markdown="block">', f"  <summary>All {len(e['headline'])} headline scores</summary>", ""] + table + ["", "</details>", ""]
        else:
            L += table + [""]
        norm, norm_collapsed = [], []
        if not all_norm:
            shown, c = P.split(e["normalisation"])
            norm = [f"- Normalisation: {_tex(shown)}"]
            norm_collapsed = [c] if c else []
        pairs_rel = e["pairs"]["path"]
        head, sep, tail = e["reproduce"].partition(REPRODUCE_TAIL)
        if sep and ("scores recomputed" + tail) not in tails:
            tails.append("scores recomputed" + tail)
        L += norm
        if not all_pairs:
            L.append(f"- Per-point values: {_link('`/api/' + pairs_rel + '`', '/api/' + pairs_rel)}")
        L += [f"- Reproduce: {_tex(head)}", ""]
        facts, collapsed = _notes([n for n in own_notes(e) if n not in all_notes])
        if facts:
            L += ["Notes:", ""] + facts + [""]
        L += _sections(norm_collapsed + collapsed)
        figures += [f for f in e["figures"] if f not in figures]
    if many and (all_quantity or all_norm or all_pairs or all_notes):
        L += ["## All runs", ""]
        if all_quantity:
            L += [f"- Quantity: {_tex(results[0]['quantity'])}"]
        if all_norm:
            shown, c = P.split(results[0]["normalisation"])
            L += [f"- Normalisation: {_tex(shown)}"]
            norm_collapsed = [c] if c else []
        else:
            norm_collapsed = []
        if all_pairs:
            pairs_rel = results[0]["pairs"]["path"]
            L += [f"- Per-point values: {_link('`/api/' + pairs_rel + '`', '/api/' + pairs_rel)}"]
        L.append("")
        facts, collapsed = _notes(all_notes)
        if facts:
            L += ["Notes:", ""] + facts + [""]
        L += _sections(norm_collapsed + collapsed)
    if tails:
        lines = [f"- {_tex(t[0].upper() + t[1:])}." for t in tails]
        if len(" ".join(tails)) < MIN_SECTION:   # a line, not a collapsed fragment
            L += lines + [""]
        else:
            L += ['<details markdown="block">', "  <summary>How the scores are computed</summary>", ""] + lines + ["", "</details>", ""]
    own, elsewhere = [], {}
    for fig in figures:
        name = fig["url"].rsplit("/", 1)[-1]
        if name in FIGURE_HOME:
            elsewhere.setdefault(FIGURE_HOME[name], []).append(fig)
        elif name in shared:
            elsewhere.setdefault(("/validation/", "Validation"), []).append(fig)
        else:
            own.append(fig)
    if own:
        L += ["## Figures", ""]
    for fig in own:
        name = fig["url"].rsplit("/", 1)[-1]
        L += figure(f"/assets/figures/{name}", fig["caption"], f"<strong>Figure {fig_no}.</strong> {_tex(fig['caption'])}", markdown=True)
        fig_no += 1
    if elsewhere:
        L += ["## Figures", ""] if not own else []
        L += ["Figures: " + "; ".join(f"{_link(label, page)}" for (page, label) in elsewhere) + ".", ""]
    return L


def build_pages(percase):
    """The site's generated pages, one set per case in D.CASE_IDS (any id the data has gets its pages): the case page
    (summary, render, status), its Data page and its Validation page, plus the includes the hand-written pages use."""
    shared = _shared_figures(percase)
    build_gallery(percase)
    build_cases_table(percase)
    build_cases_frames()
    build_validation_matrix(percase)
    build_known_issues()
    build_version_label()
    build_nomenclature()
    for case in D.CASE_IDS:
        meta, p = D.CASES[case], percase[case]
        _write(f"cases/{meta['slug']}.md", _case_page(case, meta, p, shared))
        _write(f"cases/{meta['slug']}/data.md", _case_data_page(case, meta, p))
        _write(f"cases/{meta['slug']}/validation.md", _case_validation_page(case, meta, p, shared))
    if P.unused():
        raise SystemExit(f"page_prose entries that match no text (rewritten source string?): {P.unused()}")


# ----------------------------------------------------------------------------- verify

TEMPLATED_URL = re.compile(r"https?://[^\s\"'<>]*\{[^\s\"'<>]*")
API_URL = re.compile(r"https://(?:eddy3d-dev\.github\.io|sustainableurbansystems\.com)/[^\s\"'<>)]*?/api(?:/[^\s\"'<>)]*)?")


def _strings(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)
    elif isinstance(obj, str):
        yield obj


def _read(root, rel):
    with io.open(os.path.join(root, rel), encoding="utf-8") as f:
        return f.read()


def _link_problem(sv, base, root, on_disk, index):
    """Why a URL a tree's document gives is wrong, or None. Inside a tree every URL stays in the tree; the registry
    (versions.json) is the one file outside it, and the latest alias may name its release's frozen copy."""
    if sv == base or "{" in sv or not (sv == LIVE_BASE or sv.startswith(LIVE_BASE + "/")):
        return None
    if sv == f"{LIVE_BASE}/versions.json":
        return None if os.path.isfile(os.path.join(API_ROOT, "versions.json")) else "link to versions.json, which does not exist"
    rel_dir = f"{LIVE_BASE}/{index['versions']['release']}"
    if base == LIVE_BASE and sv in (rel_dir, rel_dir + "/index.json"):   # the root of the frozen copy, and the pinned address a citation gives
        return None if os.path.exists(os.path.join(API_ROOT, sv[len(LIVE_BASE) + 1:])) else f"names {sv}, which does not exist"
    if not sv.startswith(base + "/"):
        return f"link {sv} leaves the tree (it must start with {base}/)"
    rel_t, _, query = sv[len(base) + 1:].partition("?v=")
    if rel_t not in on_disk:
        return f"link to {rel_t}, which does not exist"
    if query and _sha256(rel_t, root)[0][:12] != query:
        return f"link to {rel_t} carries a stale ?v={query}"
    return None


def verify_tree(root, base, strict_assets):
    """One tree (the latest alias or a frozen release), checked on its own: the file list against index.json, every
    document against the schema it names, every link, openapi.json, the data files and the archive."""
    problems = []
    import jsonschema
    from openapi_spec_validator import validate as validate_openapi

    def load(rel):
        return json.loads(_read(root, rel))

    on_disk = tree_files(root)
    index = load("index.json")
    if index["base_url"] != base:
        problems.append(f"index.json base_url is {index['base_url']}, this tree is served at {base}")
    if index.get("tree") is not None and index["tree"] != ("latest" if base == LIVE_BASE else "release"):
        problems.append(f"index.json says tree={index['tree']}")
    if base != LIVE_BASE and index["versions"]["release"] != os.path.basename(root):
        problems.append(f"the tree {os.path.basename(root)}/ holds release {index['versions']['release']}")

    # index.json: lists every other file, with the right size and hash
    listed = {f["path"]: f for f in index["files"]}
    for rel in sorted(on_disk - {"index.json"} - set(listed)):
        problems.append(f"{rel} is served but not listed in index.json")
    for rel, f in listed.items():
        if rel not in on_disk:
            problems.append(f"index.json lists {rel}, which does not exist")
            continue
        sha, n = _sha256(rel, root)
        if (sha, n) != (f["sha256"], f["bytes"]):
            problems.append(f"index.json size/hash of {rel} disagree with the file")

    # schemas: valid themselves, and every document valid against the one it names
    schemas = {}
    for rel in sorted(r for r in on_disk if r.startswith("schemas/")):
        sc = load(rel)
        jsonschema.Draft202012Validator.check_schema(sc)
        schemas[sc["$id"]] = sc
    versions = set()
    for rel in sorted(r for r in on_disk if r.endswith(".json") and not r.startswith("schemas/") and r != "openapi.json"):
        try:
            doc = load(rel)
        except ValueError as e:
            problems.append(f"{rel}: not valid JSON ({str(e)[:80]})")
            continue
        sc = schemas.get(doc.get("$schema"))
        if sc is None:
            problems.append(f"{rel}: $schema {doc.get('$schema')} is not a published schema")
            continue
        for err in jsonschema.Draft202012Validator(sc).iter_errors(doc):
            problems.append(f"{rel}: {'/'.join(str(p) for p in err.absolute_path)}: {err.message[:160]}")
        versions.add((doc.get("schema_version"), doc.get("data_version")))
        # every link into the API resolves inside the tree, and a ?v= is the file's current hash prefix
        for sv in _strings(doc):
            bad = _link_problem(sv, base, root, on_disk, index)
            if bad:
                problems.append(f"{rel}: {bad}")
            # Site assets (figures, renders) are not part of a release's frozen files: only the current build's must exist.
            if strict_assets and sv.startswith(SITE + "/assets/") and not os.path.isfile(os.path.join(DOCS, sv[len(SITE) + 1:])):
                problems.append(f"{rel}: link to site asset {sv[len(SITE) + 1:]}, which does not exist")
    if len(versions) != 1:
        problems.append(f"documents disagree on schema/data version: {sorted(versions)}")

    # A URI template is not a URL; and a text file may not send a reader out of its tree.
    for rel in sorted(r for r in on_disk if r.endswith((".json", ".txt"))):
        text = _read(root, rel)
        for bad in TEMPLATED_URL.findall(text):
            problems.append(f"{rel}: {bad} is a URI template, not a URL to follow")
        if rel.endswith(".txt"):
            for u in sorted(set(API_URL.findall(text))):
                bad = _link_problem(u.rstrip(".,;"), base, root, on_disk, index)
                if bad:
                    problems.append(f"{rel}: {bad}")

    # openapi.json: a valid OpenAPI 3.1 document whose paths exist
    oa = load("openapi.json")
    try:
        validate_openapi(oa)
    except Exception as e:  # noqa: BLE001 — report whatever the validator found
        problems.append(f"openapi.json is not valid OpenAPI: {str(e)[:300]}")
    for p in oa["paths"]:
        pattern = p.lstrip("/")
        if pattern in ROOT_ENDPOINTS:
            if not os.path.isfile(os.path.join(API_ROOT, pattern)):
                problems.append(f"openapi path {p} has no file")
        elif "{" not in pattern:
            if pattern not in on_disk:
                problems.append(f"openapi path {p} has no file")
        else:
            rx = re.compile("^" + re.sub(r"\\\{[a-z]+\\\}", "[^/]+", re.escape(pattern)) + "$")
            if not any(rx.match(r) for r in on_disk):
                problems.append(f"openapi path {p} matches no file")

    # content checks
    for case in index["case_ids"]:
        pj = load(f"cases/{case}/points.json")
        with io.open(os.path.join(root, f"cases/{case}/points.csv"), encoding="utf-8", newline="") as f:
            n_csv = sum(1 for _ in csv.reader(f)) - 1
        if pj["n"] != len(pj["points"]) or pj["n"] != n_csv:
            problems.append(f"case {case}: points.json n={pj['n']} rows={len(pj['points'])} csv={n_csv}")
        gj = load(f"cases/{case}/geometry.json")
        for g in gj["files"]:
            if D.stl_stats(D.read_ascii_stl(os.path.join(root, g["path"])))["triangles"] != g["stats"]["triangles"]:
                problems.append(f"case {case}: {g['path']} triangle count disagrees with geometry.json")
    gall = load("geometry.json")
    with zipfile.ZipFile(os.path.join(root, "geometry.zip")) as z:
        names = set(z.namelist())
        for it in gall["files"]:
            if it["archive_name"] not in names or hashlib.sha256(z.read(it["archive_name"])).hexdigest() != it["sha256"]:
                problems.append(f"geometry.zip lacks {it['archive_name']} or holds different bytes")
        if len(names) != len(gall["files"]):
            problems.append(f"geometry.zip holds {len(names)} files, geometry.json lists {len(gall['files'])}")
    return problems


# Header fields and lines a release tree and the alias legitimately word differently (they name themselves).
TREE_SPECIFIC_INDEX = {"tree", "fallback_note"}
SAME_IN_BOTH_INDEXES = ("release", "release_base_url", "versions_url", "cite")


def _alias_form(text):
    """The text of a release-tree file with its frozen addresses replaced by the alias's."""
    return text.replace(PINNED_BASE, LIVE_BASE).replace(RELEASE_BASE, RAW_BASE)


def _normal(obj):
    """A parsed release-tree document with its addresses in the alias's form."""
    return json.loads(_alias_form(json.dumps(obj, ensure_ascii=False)))


def verify_alias_matches_release():
    """The alias is the newest release: file for file, the same bytes, except that a document names its own tree."""
    problems = []
    rel_root = os.path.join(API_ROOT, RELEASE)
    a_files, r_files = tree_files(API_ROOT), tree_files(rel_root)
    for rel in sorted(a_files ^ r_files):
        problems.append(f"{rel} is in only the {'alias' if rel in a_files else 'release ' + RELEASE + ' tree'}")
    for rel in sorted(a_files & r_files):
        with io.open(os.path.join(API_ROOT, rel), "rb") as f:
            a = f.read()
        with io.open(os.path.join(rel_root, rel), "rb") as f:
            r = f.read()
        if rel.endswith((".csv", ".stl", ".zip")):
            if a != r:
                problems.append(f"{rel} differs between the alias and release {RELEASE}")
        elif rel == "index.json":
            ia, ir = json.loads(a), json.loads(r)
            # the fields that name the release and the registry read the same in both trees; the rest is re-addressed
            for k in SAME_IN_BOTH_INDEXES:
                if ia.get(k) != ir.get(k):
                    problems.append(f"index.json `{k}` differs between the alias and release {RELEASE}")
                ia.pop(k, None), ir.pop(k, None)
            ir = _normal(ir)
            for d in (ia, ir):
                for k in TREE_SPECIFIC_INDEX:
                    d.pop(k, None)
                # a JSON file's hash and size follow its own addresses, so only the other files' entries must agree
                d["files"] = [f for f in d["files"] if not f["path"].endswith((".json", ".txt"))]
            if ia != ir:
                problems.append(f"index.json of the alias and of release {RELEASE} disagree beyond their own addresses: "
                                + ", ".join(k for k in sorted(set(ia) | set(ir)) if ia.get(k) != ir.get(k)))
        elif rel == "openapi.json":
            ia, ir = json.loads(a), _normal(json.loads(r))
            ia.pop("servers"), ir.pop("servers")
            if ia != ir:
                problems.append(f"openapi.json of the alias and of release {RELEASE} disagree beyond their servers")
        elif rel == "llms.txt":
            ta, tr = a.decode("utf-8"), _alias_form(r.decode("utf-8"))
            if ta[ta.index("\n## "):] != tr[tr.index("\n## "):]:
                problems.append(f"llms.txt of the alias and of release {RELEASE} disagree below their headers")
        elif _normal(json.loads(r)) != json.loads(a):
            problems.append(f"{rel} of the alias and of release {RELEASE} differ beyond their addresses")
    return problems


def verify_registry():
    """versions.json against the schema it names, and against a fresh rebuild of it from the trees on disk."""
    import jsonschema
    problems = []
    path = os.path.join(API_ROOT, "versions.json")
    if not os.path.isfile(path):
        return ["versions.json does not exist"]
    text = _read(API_ROOT, "versions.json")
    doc = json.loads(text)
    schema = json.loads(_read(API_ROOT, "schemas/versions.schema.json"))
    for err in jsonschema.Draft202012Validator(schema).iter_errors(doc):
        problems.append(f"versions.json: {'/'.join(str(p) for p in err.absolute_path)}: {err.message[:160]}")
    index = json.loads(_read(API_ROOT, "index.json"))
    if index["versions"]["release"] != RELEASE:
        problems.append(f"the alias holds release {index['versions']['release']}, VERSION is {RELEASE}")
    for v in release_dirs():
        if not R.release_date(v):
            problems.append(f"docs/api/{v}/ is a release tree, but CHANGELOG.md has no dated section for {v}")
    if problems:
        return problems
    try:
        expected = dump(versions_document(index["data_version"]))
    except SystemExit as e:   # an unreleasable state (a tree newer than VERSION): a problem to report, not a crash
        return [str(e)]
    if text != expected:
        problems.append("versions.json is not what the release trees, CHANGELOG.md and LEGACY_RELEASES give; rebuild it")
    return problems


def verify_web():
    """The web copies: each one exists at the size _data/figures.json records, next to its master; the README's figure blocks
    are what the build writes; and no page or README embeds a 1200 dpi master directly."""
    problems = []
    path = os.path.join(DATA_FILES, "figures.json")
    if not os.path.isfile(path):
        return ["docs/_data/figures.json does not exist; run scripts/build_api.py"]
    with io.open(path, encoding="utf-8") as f:
        info = json.load(f)
    for name, rec in info.items():
        web, master = (os.path.join(DOCS, rec[k].lstrip("/")) for k in ("web", "master"))
        if not os.path.isfile(web) or not os.path.isfile(master):
            problems.append(f"{name}: the web copy or the master is missing")
            continue
        if _png_size(web) != (rec["width"], rec["height"]) or os.path.getsize(web) != rec["web_bytes"]:
            problems.append(f"{name}: the web copy is not the size _data/figures.json records")
        if os.path.getsize(master) != rec["master_bytes"] or _png_size(master) != (rec["master_width"], rec["master_height"]):
            problems.append(f"{name}: the master is not the one _data/figures.json describes")
        if rec["width"] > WEB_WIDTH:
            problems.append(f"{name}: the web copy is wider than {WEB_WIDTH} px")
    if set(os.listdir(WEB)) != set(info):
        problems.append("docs/assets/web/ and _data/figures.json list different files")
    with io.open(os.path.join(REPO, "README.md"), encoding="utf-8", newline="") as f:
        text = f.read()
    try:
        if readme_with_figures(text, info) != text:
            problems.append("README.md: a figure block is not what the build writes (sizes, links or labels); run scripts/build_api.py")
    except KeyError as e:
        problems.append(f"README.md: a figure block names {e}, which is not a figure of the site")
    if re.search(r'<img[^>]*src="validation/figures/|!\[[^\]]*\]\(validation/figures/', text):
        problems.append("README.md embeds a 1200 dpi master directly; use a <!--fig ...--> block")
    for path in sorted(glob.glob(os.path.join(DOCS, "**", "*.md"), recursive=True)):
        rel = os.path.relpath(path, DOCS).replace(os.sep, "/")
        if rel.startswith("api/"):
            continue
        with io.open(path, encoding="utf-8") as f:
            page = f.read()
        if re.search(r"<img[^>]*src=\"\{\{ '/assets/(figures|geometry)/|\]\(\{\{ '/assets/(figures|geometry)/", page):
            problems.append(f"docs/{rel} embeds a 1200 dpi master directly; show the web copy (the include figure.html)")
    return problems


LEGACY_SITE = "https://sustainableurbansystems.com/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ"   # where releases up to 3.1.0 were tagged


def release_base(v):
    """The address a frozen release tree names inside itself: the releases up to 3.1.0 were tagged while the site lived at LEGACY_SITE."""
    return f"{LEGACY_SITE}/api/{v}" if tuple(int(x) for x in v.split(".")) <= (3, 1, 0) else f"{LIVE_BASE}/{v}"


def verify():
    """Everything a client relies on, checked against the files on disk: the latest alias, every frozen release tree,
    that the alias is the newest release, and the registry that lists them."""
    try:
        import jsonschema  # noqa: F401
        from openapi_spec_validator import validate as validate_openapi  # noqa: F401
    except ImportError as e:  # the contract is not optional
        return [f"{e.name} is not installed: pip install --require-hashes -r requirements.lock"]
    problems = []
    dirs = release_dirs()
    if RELEASE not in dirs:
        return [f"docs/api/{RELEASE}/, the tree of the current release, does not exist; run scripts/build_api.py"]
    for label, root, base, strict in [("alias", API_ROOT, LIVE_BASE, True)] + [
            (f"release {v}", os.path.join(API_ROOT, v), release_base(v), v == RELEASE) for v in dirs]:
        problems += [f"[{label}] {p}" for p in verify_tree(root, base, strict)]
    problems += [f"[alias vs release] {p}" for p in verify_alias_matches_release()]
    problems += [f"[registry] {p}" for p in verify_registry()]
    problems += [f"[web copies] {p}" for p in verify_web()]
    import check_citation
    problems += [f"[citation] {p}" for p in check_citation.check(REPO)]
    if _read(DOCS, "llms.txt") != _read(API_ROOT, "llms.txt"):
        problems.append("docs/llms.txt and docs/api/llms.txt differ")
    return problems


# ----------------------------------------------------------------------------- main

def build_tree():
    """Write the tree selected by use_tree(): the data files, then the JSON documents, then its index. Returns what
    the site's generated pages need."""
    global DATA_VERSION
    # Phase 1: the data files. Their hashes define data_version, which every JSON document carries.
    data = {case: write_data(case) for case in D.CASE_IDS}
    write_archive(data)
    dv = compute_data_version()
    if DATA_VERSION not in (None, dv):
        raise SystemExit(f"the two trees disagree on data_version ({DATA_VERSION} vs {dv})")
    DATA_VERSION = dv
    # Phase 2: the JSON documents and the index of it all.
    percase = {}
    for case in D.CASE_IDS:
        percase[case] = write_case_documents(case, data[case])
        g = data[case]["geometry"]
        print(f"[{TREE}] case {case}: {percase[case]['summ']['rows']} rows from {data[case]['src']}; geometry "
              f"{[(x['configuration'], x['stats']['triangles'], x['stats']['watertight']) for x in g]}; "
              f"{len(percase[case]['results'])} validation result(s)")
    write_cases_index(percase)
    write_geometry_index(data)
    write_validation_summary(percase)
    write_schemas()
    write_openapi()
    write_text("llms.txt", llms_text(percase))
    write_index()
    remove_stale()
    return percase


def build():
    if RELEASE in LEGACY_RELEASES:
        raise SystemExit(f"VERSION {RELEASE} predates the versioned layout and is not regenerated; set VERSION to the next release")
    os.makedirs(API_ROOT, exist_ok=True)
    check_runs_registry()
    copy_assets()
    sync_readme()
    # The frozen copy of this release first, then the latest alias, which is the same files addressed without the release.
    use_tree("release")
    percase = build_tree()
    write_dataset_jsonld(percase)       # the home page describes this release by its frozen addresses
    write_changelog_include()
    write_citation_files()              # the About include, the README block, CITATION.cff and .zenodo.json
    build_pages(percase)
    use_tree("latest")
    build_tree()
    with io.open(os.path.join(DOCS, "llms.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(_read(API_ROOT, "llms.txt"))
    write_versions(DATA_VERSION)
    print("data_version", DATA_VERSION)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="verify the files on disk; build nothing")
    args = ap.parse_args()
    if not args.check:
        build()
    problems = verify()
    for p in problems:
        print("PROBLEM:", p)
    print("verify:", "OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
