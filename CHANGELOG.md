# Changelog

Every release of this repository's data and API, newest first. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the version follows [Semantic Versioning](https://semver.org/)
with the rules of the [Data Package version recipe](https://datapackage.org/recipes/data-package-version/), applied to
what this repository serves (the API under `docs/api/` and the cleaned tables under `clean/`):

- **MAJOR**: an incompatible change. A served file, endpoint, field or column renamed or removed; a CSV column added,
  removed or reordered; a unit, frame or normalisation changed; a major change of the API schema.
- **MINOR**: a backward-compatible addition. A new case, configuration, run, endpoint, field or file.
- **PATCH**: a backward-compatible fix. A corrected value, score, caption or metadata text.

Documentation, figures and tooling that change no served byte need no release. `VERSION` holds the number;
CI fails a change to the served files that does not move it by at least the level the change needs, and tags
`vX.Y.Z` with a GitHub Release when it moves on `main`. The API's own contract has a separate version,
`schema_version`, with its changelog in `index.json` and on the [API page](https://sustainableurbansystems.com/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ/api-reference/#versioning-and-changes).

## [3.1.0] - 2026-10-18

Additive: new figures, fields and citation endpoints, and fixes. The API schema is 2.4.0 (additive; its changelog is in `index.json`).

### Added

- A layout figure for each case, A to M (`validation/figures/case-<id>-layout.png`), drawn from the measurement groups in
  `validation/layout.py` (pinned by `validation/test_layout.py`). The dots of the agreement figures take the colour of the line, plane or
  group they were measured in. Each layout figure is the first entry of `figures` in the case's validation results.
- `cite.api` in `index.json` and `citation` in `cases/{id}.json`; suggested citations on the site and in the README; `CITATION.cff` cites this
  dataset (the data paper, the AIJ guidelines and the Zenodo record of each case are its references); `.zenodo.json`.
  `scripts/citation.py` renders all of them and `scripts/check_citation.py` checks them. The pinned address of a release is
  `https://sustainableurbansystems.com/CFD-Test-Cases-Architectural-Institute-of-Japan-AIJ/api/<release>/index.json`.
- `bodies`, `body_contacts`, `inconsistent_triangles` and `min_body_volume` in the `stats` of `geometry.json` and in the geometry index,
  beside `edges_boundary`; `watertight` is true when every body is closed, consistently wound and positive in volume.
  `scripts/check_geometry.py` parses every served and cleaned STL and fails the build on an open, inconsistently wound or inward body, a
  degenerate or repeated triangle, or a stored normal that disagrees with the winding.

### Fixed

- Case E: every building of `geometry.stl` and `geometry_bc.stl` is a closed, consistently wound, outward body. 1,563 of the 8,436
  triangles (18.5 %) of the 3dm's building meshes were wound against their neighbours, which the earlier whole-shell flip could not
  repair; they are re-wound. One wall that two buildings share (4 triangles) is removed, which joins the two into one body: 545 bodies
  after construction (8,432 triangles), 542 before (8,396), and 11 edges where two bodies touch.
- Cases F and M: `geometry.stl` is one closed outward body. F is closed with a 1 m base slab (vertical walls from the rim of the 725 m disc
  down to z = −1 m and a bottom cap, 2,436 added triangles; the zero-area triangles at T-junctions are removed and their neighbours split); M loses 7
  slivers (0.45 m² together) on building roofs and is closed the same way (21 added triangles). The bounding box starts at z = −1 m.
- `BD_caseL.stl`, as published, has the two bottom triangles of each of its 126 cubes wound inward (Known data issues); the served
  `geometry.stl` is the 126 boxes and was never affected.
- Removed boilerplate wording from the API descriptions and from `llms.txt`.
- `status_meaning.scored` reads "a validation run exists and its scores are in cases/{id}/validation.json"; the site and the README carry the same definition.
- The `notes` of the runs in `validation.json` of Cases F, G, J, K, L and M state their facts directly. Case G's notes begin with the calibration statement (LAD and Cd are not in the dataset); Case M's notes keep the probe precision (seven significant digits; no c\* value moved by more than 0.003 against a six-decimal probe) and drop the account of a first solve killed for memory (exit 137). The controls text of Case M says that 14 of the 15 turned points lie in the fluid.
- The wind-direction texts of Cases D, E, F and M and the known-issue texts of Cases D and F read as plain statements; no value changed.
- `clean/manifest.json`: the Case E log-law note reads "appropriate choice". The geometry index no longer says the STL files are "deliberately" not one scene.

### Changed

- The title reads "AIJ UWE" in `index.json`, `openapi.json`, `llms.txt` and the Dataset JSON-LD. The licence note is one line, "Data: Kikumoto et al. (2026), CC BY 4.0. Collectors per case in cases/{id}.json.", and `clean/manifest.json` carries "Data: Kikumoto et al. (2026), CC BY 4.0. Collectors and requested citation per case."
- Run history moved out of the pages into this line: Eddy3D's test of Case M asserted the near/far ordering of c\* before the first solve and now records it; Case B's first OpenLB run crashed on the STL reader fault described on the OpenLB page, and a regression test fails without the lattice move.

## [3.0.0] - 2026-10-18

Eight more cases of the benchmark, F to M, join A to E: the cleaned tables, the API and the site now cover all thirteen.
The point table gained columns, which is why this release is MAJOR.

### Changed (incompatible)

- The point table is schema 2.0.0 of the cleaned release: 18 columns are appended after the 18 of 2.0.0 (`campaign`, `run`,
  `uv`, `uw`, `vw`, `C`, `c_rms`, `concentration_ratio`, `T`, `T_rms`, `uc`, `vc`, `wc`, `uT`, `vT`, `wT`,
  `velocity_ratio_sd`, `k_ratio`), in `clean/points.*`, and every `clean/cases/<id>/points.*`, and in the API's `points.csv`
  and `points.json`, which list the columns a case has. For Cases A to E the one new column is
  `campaign` (`wind_tunnel`); the values of the 2.0.0 columns are unchanged. See `clean/SCHEMA.md`.

### Added

- Cases F to M, cleaned from their Zenodo records with the same checks as A to E (289 checks in all, none failing; the
  documented warnings are in `clean/checks.json`), one `clean/cases/<id>/` folder each, and served by the API
  (`cases/{id}.json`, points, approach flow, geometry and validation documents) and the site. Rows: F 472 (tunnel
  thermistor at 5, 9 and 20 m and field cup anemometers), G 28 (field sonic anemometers behind a tree belt), H 1,652 and I 630
  (building and cube with a tracer source), J 444 and L 344 (non-isothermal building and cube array), K 203 (cube array,
  point source), M 330 (campus, tunnel and field). Geometry is rebuilt from the published model or generated from its stated
  dimensions: boxes for G to L, an STL for F and M. Each case has a geometry render.
- `instrument` takes the new values `cup_anemometer`, `sonic_anemometer`, `ldv`, `hydrocarbon_analyser` and
  `sorbent_gc_ecd`; `campaign` separates the tunnel from the field in Cases F, G and M.
- Validation runs, each with its scores and per-point pairs: OpenFOAM 12 on Case H (realizable k-ε) and on Case I under
  realizable k-ε, standard k-ε and k-ω SST. The API lists the two closures as the engines `openfoam12-kEpsilon` and
  `openfoam12-kOmegaSST`, for Case I only.
- Validation of Case K (9 × 9 cube array, floor point source): OpenFOAM 12, realizable k-ε, numerics level 3, 972,637 cells, 3000
  iterations, solved 2026-10-18, scored at the tunnel's 203 points: U, V, W, k and the concentration c\* at turbulent Schmidt numbers 0.3,
  0.5 and 0.7 (three species on one flow, all published), with and without the four points at the source, and the
  y-symmetric ceiling of the measurement. The solve ran to its iteration limit with the residual control unmet.
- Validation of Case G (tree belt, field data): OpenFOAM 12, realizable k-ε, a drag sweep because the canopy's leaf area density and drag
  coefficient are not in the dataset: no belt, three vegetation-library crowns (Cd·LAD 0.30, 0.625 and 0.875 1/m) on a two-dimensional
  slab, and the conifer crown on the real belt as a half domain. Five runs of one engine, each its own `configuration`, none chosen;
  U and k at the 28 points over the model's own U(7 m) and over the imposed U_H, and the run notes say that the arm nearest the data is a
  calibration and that Eddy3D's trees have no canopy k source.
- Validation of Case J (1:1:2 building on a heated floor, floor tracer source) and Case L (9 × 14 cube array on a heated floor, line
  source) on Eddy3D's buoyant microclimate engine, urbanMicroclimateFoam (UMF), at Froude scales 62.5 and 100, solved 2026-10-18 (J:
  236,408 air cells, L: 754,940, the air region stopped at its 1500-iteration cap). J under realizable k-ε and `buoyantKEpsilon`, L under
  realizable k-ε; U, V, W, k, the floor-referenced temperature θ and the concentration at three Schmidt numbers, in the tunnel's units.
  The API lists UMF as the engines `umf-realizableKE` (J, L) and `umf-buoyantKEpsilon` (J), and each validation result has `notes`.
- Validation of Case F (Shinjuku district: a 1978 high-rise district, thermistor speed in a 1:800 tunnel at 5, 9 and 20 m and a year of field cup
  anemometers): OpenFOAM 12, realizable k-ε, numerics level 3, 2,143,488 cells, 2000 iterations, solved 2026-10-18 for the wind from NNW only
  (the other eleven tunnel directions were not run). The tunnel's 33 points and the field's 13 are scored as |U| and √(|U|²+2k) over the model's own
  U(500 m), in two vertical frames that are two runs of one engine (`configuration` `literal`: the published z in the STL's frame; `agl`: the STL's
  ground plus the instrument height; the files do not say which the tunnel meant, so neither is asserted), with the tunnel's 9 m column as a model of
  the field and the solved field's correlation with the tunnel's column for the opposite wind (SSE) as controls. That control corroborates the
  compass reading of the wind directions at NNW: the direction table of `clean/` marks the NNW rows `corroborated by a solved field`, the other
  directions stay `unverified`.
- Validation of Case M (TPU Atsugi campus, tracer release over real terrain): OpenFOAM 12, realizable k-ε, numerics level 3, 1,394,053 cells, 3000
  iterations, solved 2026-10-18 for the tunnel's heading WD 180 only, scored at the 15 points: c\* at turbulent Schmidt numbers 0.3, 0.5 and 0.7 (three
  runs on one flow, `configuration` `sct03`, `sct05`, `sct07`, none chosen) and U, V, W and k over the solved speed at the reference mast, with the
  fixture's two controls (the points turned 180° about the source and mirrored across the plume axis), the tunnel's own WD 175 and WD 185 scored
  against its WD 180, and the 18 field runs recorded beside the tunnel. The ordering the fixture first asserted (the points nearest the source carry
  more than the far ones) is recorded and stated in the run notes as a model finding.
- Every score of the runs of Cases F, G, K, J, L and M is recomputed from the per-point pairs by `validation/dispersion_metrics.py`, never copied
  from Eddy3D's log; fed the published CSVs and the fixtures' own probes it reproduces the fixtures' scores to 10⁻⁹ (the script fails
  otherwise), and the scores here differ from the logged ones where the measured side moved from the rounded CSVs to the workbooks.
  The SHA-256 of every file a snapshot was read from is in its results file under `sources`.
- Release-numbered API paths: every release is a frozen copy of the whole API under `/api/<release>/` (for example
  `/api/3.0.0/index.json`), the unversioned `/api/` paths always equal the newest release, and `/api/versions.json`
  lists every release. API schema 2.3.0 (a minor change: nothing renamed or removed; thirteen cases, the new
  columns, instruments and engines are additions). Release 2.0.0 predates the layout; `/api/2.0.0/` holds the
  files of its tag with only their addresses rewritten (`scripts/host_release.py`).
- The site is rebuilt on Just the Docs: search, a navigation hierarchy, and three pages per case (the case, its reference
  data, its validation). `scripts/check_markdown.py` checks that every Markdown file of the repository and every generated
  page renders the same on GitHub and in Jekyll, and runs in the build.
- Every figure is drawn in one colour-blind-safe style (UltraPlot) and written at 1200 dpi.

### Changed (compatible)

- API `cases.json` and `validation.json` list thirteen cases; an engine is listed for a case only where it applies.
- README, the site and `CITATION.cff` cover Cases A to M; `CITATION.cff` lists the dataset of each case.
- `clean/checks.json`: each of the 16 documented warnings (`"pass": false`, severity `warning`) also carries `"warning": true`, and the
  note says that `failed` counts errors only.
- `clean/manifest.json`: every provenance entry gained `eol`. `lf-normalised` means the SHA-256 and the byte count are those of
  the text file with CRLF folded to LF, so a fresh clone and a Windows checkout record the same numbers; `as-is` means
  the file was hashed as stored (binary files and the byte-exact mirrors in `clean/sources/`).

### Fixed

- Markdown that rendered differently in Jekyll and on GitHub: lists and tables not preceded by a blank line, a table row
  with an unescaped pipe in `clean/SCHEMA.md`, bare URLs, and the API changelog include, whose text with `<word>`
  was read as an HTML tag.
- Units of Case G's approach flow: `cases/G.json` `approach_flow.units` said m/s and m^2/s^2, but the table holds U/Ub and k/Ub^2, which are
  dimensionless; the API now takes the units of each case's approach flow from its registry entry (`approach_flow_units`), and the
  `U` and `k` entries of `clean/units.json` name Case G as the exception. The meanings of `config`, `instrument`, `wind_direction`,
  `wind_direction_deg`, `x`, `y`, `z`, `V`, `velocity_ratio` and `C` in `clean/units.json` and the manifest now cover Cases F to M.
- Validation scores of Cases H and I: FB, NMSE and NAD are `null` for a signed velocity component whose observed and predicted
  means differ in sign or are not both positive (H `velocity.W`: NMSE was -91; I `velocity.V`: -4.5e6 under realizable k-ε and
  -2.8e6 under standard k-ε), where they were numbers that mean nothing; R, FAC2, the hit rate and the counts are unchanged. The scores
  of Cases A to E are the Eddy3D fixtures' own and are served as written.
- `docs/api/versions.json`: the fallback of release 2.0.0 is the raw files at tag `v2.0.0` (frozen), not the copy on `main`.
- The figure build is deterministic: `scripts/build_all.sh` pins the numerical libraries to one thread. With several, the Case D
  agreement figure came out as one of two layouts, a pixel apart, from run to run on the same machine. Pinning the threads did not
  settle the Case E agreement figure, which still alternated between two files: ultraplot solves every layout with kiwisolver, whose
  result differs in the last digits from build to build, and `validation/plotstyle.py` now selects ultraplot's legacy solver, which does not.

### Repository notes

These change no served byte.

- The raw case folders moved from `case-a/` … `case-e/` to `raw/cases/case-a/` …; Cases F to M are added there from their
  Zenodo records (CC BY 4.0). Their text files are stored with LF line endings, like those of Cases A to E
  (`.gitattributes`): 23 of the Zenodo originals (22 CSV files and the STL of Case L) use CRLF, and the MD5 check against the
  records was made on those CRLF originals, so a stored copy matches its record only after converting back to CRLF.
- Every figure and geometry render is still drawn and served at 1200 dpi (`docs/assets/figures/`, `docs/assets/geometry/`; the API's `figures`
  and `render` entries point there). The site pages and the README now embed a 1600 px copy (`docs/assets/web/`, written by
  `scripts/build_api.py`, byte-identical on every build) with `width`, `height` and `loading="lazy"`, and link it to the 1200 dpi
  original, named with its size. Image bytes on the home page: 18.9 MB before, 2.1 MB after; distinct images in the README: 66.7 MB
  before, 8.6 MB after.
- No PDFs are stored: the data paper (Kikumoto et al. 2026) and the AIJ guidelines paper (Tominaga et al. 2008) are cited
  and linked by DOI in `papers/README.md`. The Elsevier PDF of the guidelines paper (all rights reserved, removed from the tree in
  2.0.0) was also purged from the repository's git history, which rewrote the commits up to the 2.0.0 tag: a clone made
  before the rewrite does not share history with `main` and has to be cloned again.

## [2.0.0] - 2026-10-18

The first tagged release. Every number from here on identifies exactly one content of the served files, and
the release rebuilds byte for byte from its tag (see *Reproduce a release* in the README).

### Changed (incompatible)

- Folders and files renamed to one scheme: `case-a/` … `case-e/` for the cases, `case-x-description.ext` for the
  repository's own files, `author-year-title.pdf` for papers. The README's *Repository layout and file names*
  lists every old and new name.
- API schema 2.0.0: `gotchas` is `known_issues`; `licence` is `license` (SPDX `CC-BY-4.0`); `generated_from` and
  `generated_at` are gone (`data_version` replaces them); links are named `url`, and downloads are objects with
  `url`, `path`, `media_type`, `bytes` and `sha256`; a result's `figures` is a list of `{url, caption}`.

### Added

- Validation runs, each with its scores and per-point pairs: OpenFOAM 12 on Case C (nine configurations), Case D
  (wind directions 0°, 22.5° and 45°) and Case E (wind from SW, before and after construction); OpenLB on Cases A
  and B; FluidX3D on Cases A and B; the Eddy3D ML surrogate on Cases A–E.
- API: `validation.json`; `cases/{id}/pairs/{engine}.csv`; `cases/{id}/approach_flow.csv`; JSON Schemas for every
  document; the geometry index and archive; `llms.txt`; schema.org Dataset metadata. Schema 2.1.0 lists the files
  of templated endpoints; schema 2.2.0 adds the release (`versions.release`, `release`).
- Versioning: `VERSION`, this changelog, the version in `CITATION.cff`, release tags and archives, one pinned
  build environment (`requirements.lock` with hashes, Python 3.12.12, a container image pinned by digest), and the
  CI check that the version moves with the change.

### Fixed

- Withdrawn: the reading that the Case C model's approach flow ran at 0.83 of the tunnel's and Case E's at 0.41/0.79
  near the ground. Upstream of the arrays the probe height sits below the first cell's centre, where the sampling
  falls linearly to zero; at the measurement points the sampling is sound.
- Case D: the 22.5° and 45° rotation sense, read from Figure 4 of the data paper, is corroborated by solved fields
  (`directions.csv` status, `QUESTIONS.md` Q2).
- `clean/manifest.json`: the fitted roughness lengths `z0_m` are written to 12 significant digits, so the file is
  byte-identical on every platform.

### Removed

- The PDF of the AIJ guidelines paper (Tominaga et al. 2008, Elsevier, all rights reserved); `papers/README.md`
  cites it by DOI.

## [1.0.0] - 2026-10-14

The first release of the cleaned tables (`clean/`) and the API. It was never tagged, and the served content
changed under this number afterwards; that is why tagged releases begin at 2.0.0.
