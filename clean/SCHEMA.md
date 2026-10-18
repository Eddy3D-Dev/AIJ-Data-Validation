# clean/ — schema of the cleaned AIJ UWE release (Cases A–M)

Schema `2.0.0` (release `3.0.0`; schema 1.0.0 had 18 columns, 2.0.0 adds the 18 below the line, appended, so every old column keeps its position). Built by `clean/build.py` from the published Zenodo files; every
transform is listed in `build.log`, every validity check in `checks.json`, every source file with its
SHA-256 in `manifest.json`. **The headers carry no units.** Units live in `units.json` (and in each
Parquet file's schema metadata under the keys `units` and `column_meaning`).

## 1. One table, long format

`points.csv` / `points.parquet` hold every measured value of every case as one row per
*(case, configuration, instrument, point, wind direction)*. Per-case copies are `cases/<id>/points.*`
(identical rows, identical column order). The per-case CSV is what `scripts/aijdata.py` reads for the
site API (`clean/manifest.json` → `cases.<id>.files.points_csv`).

| column | type | unit | meaning |
|---|---|---|---|
| `case_id` | text | — | `A` … `M` |
| `config` | text | — | `default` (A, B, D) · C: centre building `0D` / `1D` / `2D` · E: `bc` before / `ac` after construction |
| `instrument` | text | — | `split_fibre` (hot-wire split-fibre probe: vector components) · `thermistor` (omnidirectional scalar speed) |
| `point_id` | int | — | the tunnel's own point number (`No.`); shared by every configuration and direction of a case |
| `wind_direction_deg` | float | deg | A–D: the AIJ turntable angle WD (0 = flow along +x). E: meteorological FROM-direction, clockwise from north (N = 0, E = 90). **Do not turn this into a vector yourself — read `flow_dir_x/y` from `directions.csv`.** |
| `wind_direction` | text | — | compass name (E only; empty elsewhere) |
| `x` `y` `z` | float | m | case frame, section 2. Model-scale metres for A–D, FULL-scale metres for E |
| `U` `V` `W` | float | m/s | mean velocity along +x, +y, +z. **V is positive toward +y in every case** (B's published sign is flipped) |
| `uu` `vv` `ww` | float | m²/s² | velocity variances ⟨u′u′⟩ … (A publishes rms; squared here) |
| `k` | float | m²/s² | turbulent kinetic energy as published (= ½(uu+vv+ww) wherever all three exist — checked) |
| `Vs` | float | m/s | mean omnidirectional scalar speed from a thermistor. Never a vector magnitude |
| `velocity_ratio` | float | — | mean speed over the case's reference speed: E: Vs / U_ref, U_ref = approach-flow speed at z = 15.9 m full scale (3.935 m/s, section 5); F, G: see the case's `normalisation` in `manifest.json` |
| `campaign` | text | — | `wind_tunnel` (model scale) or `field` (a full-scale observation: F, G, M) |
| `run` | text | — | replicate label where the dataset publishes individual runs (M); empty elsewhere |
| `uv` `uw` `vw` | float | m²/s² | Reynolds shear stresses as published |
| `C` `c_rms` | float | ppm | mean and rms tracer-gas concentration as published |
| `concentration_ratio` | float | — | C / c0, c0 = q / (U_ref L_ref²) as the benchmark defines it for the case (`manifest.json`, `cases.<id>.normalisation`) |
| `T` `T_rms` | float | °C, K | mean air temperature and its rms (J, L) |
| `uc` `vc` `wc` | float | ppm·m/s | turbulent concentration fluxes |
| `uT` `vT` `wT` | float | K·m/s | turbulent heat fluxes |
| `velocity_ratio_sd` | float | — | standard deviation of `velocity_ratio` over the observations behind a field value (F) |
| `k_ratio` | float | — | k / U_ref² where only normalised values are published (G) |

Rules:

- **Not measured = NaN** (empty cell in CSV, null in Parquet). The sources' `-999.9`, `-` and blank
  cells all become NaN. A column a case never measures is NaN for that whole case.
- The key `(case_id, config, instrument, point_id, wind_direction_deg)` is unique. Case B's seven
  repeat measurements keep their own point numbers (README, B).
- Rows are sorted by `(config, instrument, wind_direction_deg, point_id)` within a case; cases in
  order A–E. Floats are written with `%.10g`; coordinates and variances are rounded to 1e-9.
- A *derived* quantity the source publishes beside measured ones is dropped, not carried: Case D's
  split-fibre "Vs" / "Scalar Vel." (= √(U²+V²+W²), checked to 1e-15) and "Vs/UH"; Case B's
  "1/4 power" fit column. Everything else published is here.

## 2. Frames — one per case

All five: right-handed, +z up from the ground plane, origin on the ground. Lengths in metres.

| case | origin | +x | +y | scale of the coordinates | transform from the published files |
|---|---|---|---|---|---|
| A | building centre | streamwise at WD = 0 | lateral; points on the y ≤ 0 half | model (b = 0.08 m; no model:full ratio is stated) | none (metres as published); rms → variance |
| B | slab centre | streamwise | lateral; points on y ≤ 0 | model (H = 0.20 m; ratio not stated) | x, y, z **mm → m** (×0.001); **V → −V** |
| C | array centre (= centre block centre) | streamwise at WD = 0 | lateral | model (D = 0.20 m; ratio not stated) | none; `CB` text → `config` |
| D | tower centre | streamwise at WD = 0 | lateral | model, **1:400** (H = 0.25 m = 100 m) | none (Zenodo CSVs are in metres; the workbook's mm are cross-checked) |
| E | centre of the reproduced area | **east** | **north** | **full scale**, model 1:250 | none for points; official STL ×250 (it is model scale) |

Why the sign flip on B: just outside the y < 0 flank the flow must deflect away from the centreline,
i.e. toward −y. Case A reads V = −2.893 m/s there ((−0.040, −0.050, 0.010)); Case B reads
**+3.630** at the same place ((−0.025, −0.110, 0.0125)); Case D's split fibre reads +2.055 on its +y
flank. So B's published V is positive toward −y and is flipped so that V is positive toward +y
everywhere (`checks.json`: `lateral_sign_*`). For a y-symmetric building "flip V" and "flip y" are
the same transform; V is flipped so the coordinates stay the drawing's.

Why E keeps a geographic frame: the district is real, its points and its STL are published in
east/north coordinates, and its 16 directions are compass names. "+x along the wind" is a property
of A–D only.

### Wind direction → flow vector (`directions.csv`)

`directions.csv` has one row per `(case_id, config, instrument, wind_direction_deg)` with
`flow_dir_x`, `flow_dir_y` = the unit vector the mean wind **blows toward** in the case frame, the
row and measured counts, and `sense_basis` / `status` saying what fixes the rotation sense:

| case | flow_dir(WD) | how the sense is known |
|---|---|---|
| A, B | (1, 0) | definition |
| C | (cos WD, **−sin WD**) | measured from the data: the WD = 45° field is mirror-symmetric about y = −x (mean |ΔVs| 0.10–0.13 m/s, the experiment's repeatability) and not about y = +x (0.52–0.80). Figure 3 of the data paper draws the opposite sense — QUESTIONS Q1 |
| D | (cos WD, **+sin WD**) for 22.5°, 45° | **corroborated by solved fields**: the array is exactly y-mirror symmetric, so the sense cannot be settled from the data; it is taken from Figure 4 of the data paper, and Eddy3D's solved fields score R 0.80 / 0.85 in this sense against 0.40 / 0.17 mirrored (22.5° / 45°) — QUESTIONS Q2 |
| E | (−sin WD, −cos WD) | definition: FROM-direction, +y north (compass rose in `MP_caseE.png`); frame verified by all 80 points lying in open space and a 10° rotation control putting 26 inside buildings |

Note C and D disagree in sense. That is what the sources say today; it is the first question to
put to the data collectors.

## 3. Approach flow (`approach_flow.csv` / `.parquet`)

One row per published height: `case_id, z, U, uu, vv, ww, k` in the same units as section 1.
A: 24 heights (rms squared); B: 12; C: 16 (U and uu only); D: 13 (U and k); E: 12 heights
de-normalised from `z/ZR, U/UR, k/UR²` with ZR = 250 m (1 m model), UR = 7.8 m/s, in full-scale
metres. `manifest.json → cases.<id>.inflow` carries the measured U_H, the log-law fit(s)
(κ = 0.41, least squares on the published points, window stated, residual and errors at the heights
that matter) and a power-law fit — reproduced in `build.py`, never typed in.

## 4. Geometry (`cases/<id>/geometry*.stl`, `geometry.json`)

ASCII STL, LF line endings, outward normals, **metres in the same frame as the points** (so the E
files are full-scale and ~400 m across). `geometry.json` lists each file, its provenance, triangle
count, bounding box, watertightness, and — for A–D — the axis-aligned boxes it is made of, so a
consumer need not parse an STL at all.

| case | files | made from |
|---|---|---|
| A, B | `geometry.stl` | the readme's stated dimensions, centred (the MP drawings) |
| C | `geometry_0D/1D/2D.stl` | nine 0.20 m cubes on a 0.40 m pitch; the pitch is verified against the 120-point grid (the 49 absent nodes of the 13 × 13 lattice are exactly the nine footprints) and read from `MP-z-caseC.png` |
| D | `geometry.stl` | the 83 closed shells of the published `BD_caseD.stl`, each reduced to its box (the published file has 576 duplicate facets and every roof wound inward; the rebuild is watertight with the analytic volume 0.0214766 m³) |
| E | `geometry_ac.stl` | the official `BD_caseE.stl` scaled ×250 (after construction; 60,101 triangles; NOT watertight as published, 5,253 open edges) |
| E | `geometry_ac_3dm.stl`, `geometry_bc_3dm.stl` | Eddy3D-side reconstructions from `case-e.3dm` (layers `buildings` + `buildings_new_construction`); **the before-construction state has no published source** — provisional |

## 5. Case E normalisation

All 2,560 published ratios are integer multiples of one quantum q = 0.0198204 (55 distinct levels):
the sheet holds U/UR quantised at 0.01 and re-normalised by UR / U_ref, so
U_ref = 0.01 · UR / q = **3.935 m/s** at z = 15.9 m. Log-interpolating the published profile at
15.9 m gives 3.973 m/s (+1 %); the data paper says "4.0 m/s". The data's own resolution is ±q/2 =
±0.0099 — 3 % of the median ratio and 10 % of the smallest (5 quanta). Zenodo's `RS_caseE.csv` is
the workbook rounded to 2 dp; this release carries the workbook's full values.

## 6. Provenance and determinism

`manifest.json → cases.<id>.provenance` lists every source file read, with SHA-256 and byte size.
For D and E the official Zenodo files the repository clone lacks were downloaded into
`clean/sources/zenodo_case{D,E}/` (checksums in `SHA256SUMS.txt` beside them); the clone's
workbooks are byte-identical in content to Zenodo's `LF_*.xls` and are used as cross-checks. Two
consecutive builds produce byte-identical files (49 outputs hashed), so a changed hash means a
changed input or a changed `build.py`.

## 7. Site API

`scripts/aijdata.py` reads `clean/manifest.json`, finds each case's `points_csv`, maps the columns
by name and serves them unchanged through `docs/api/cases/<id>/points.{json,csv}`
(`points_source` in each file says so). Column `case_id` is deliberately not named `case`, which
that adapter would read as the configuration.

## Cases F and M

The two cases that bring the schema-2.0.0 columns `campaign`, `run`, `C`, `c_rms`, `concentration_ratio`,
`velocity_ratio_sd` into use. Both are real sites measured in a wind tunnel and in the field, both are in
**full-scale metres**, both come from a legacy workbook as well as from the Zenodo CSVs. Modules:
`clean/case_f.py`, `clean/case_m.py`.

### Rows: what one row is

`instrument` takes three values beyond `split_fibre` and `thermistor`: `cup_anemometer` (F, field),
`hydrocarbon_analyser` (M, tunnel concentration) and `sorbent_gc_ecd` (M, field concentration: sorbent tubes read
by gas chromatography with an electron-capture detector). A row carries only what its instrument measured; the
rest is NaN.

| case | `campaign` | `instrument` | `config` | one row is | filled columns |
|---|---|---|---|---|---|
| F | `wind_tunnel` | `thermistor` | `default` (9 m plane), `h5`, `h20` | a point at one wind direction on one plane | `velocity_ratio` |
| F | `field` | `cup_anemometer` | `default` | a point at one wind direction, the year's mean | `velocity_ratio`, `velocity_ratio_sd` |
| M | `wind_tunnel` | `split_fibre` | `default` | a point at 180° | `U V W`, `uu vv ww`, `k` |
| M | `wind_tunnel` | `hydrocarbon_analyser` | `default` | a point at 175°, 180° or 185° | `C`, `c_rms`, `concentration_ratio` |
| M | `field` | `sorbent_gc_ecd` | `default` | a point in one of the 18 runs (`run` = "1" … "18") | `C`, `concentration_ratio` |

F's `config` is the tunnel plane's height above ground by the readme's rule (z − 10 m): 9 m is `default` because
it is the benchmark plane, complete at 13 points × 12 directions, and the plane the field values are compared with;
the 5 m and 20 m planes exist at some points only. M's wind direction in a field row is the run's mean direction
at the reference point (`WD_R`), which differs from run to run, so the row key stays unique. M's per-run
reference speed `U_R`, tracer flow `q` and `c0` have no column; they are in `manifest.json → cases.M.extra_measurements.field_runs`.

### Frames

| case | origin | +x | +y | scale of the coordinates | transform from the published files |
|---|---|---|---|---|---|
| F | centre of the reproduced district, on the tunnel floor | **east** | **north** | **full scale**, model 1:800 | tunnel x, y, z × 800 (the field's are published in full scale); STL × 800 and re-wound outward |
| M | centre of the tunnel turntable, on the floor | **north** | **west** | **full scale**, model 1:600 | tunnel x, y, z × 600 (the field uses the tunnel's 15 points); STL × 600 and re-wound outward |

`z` is the height above the **tunnel floor**, not above the ground. F: the readme's rule is ground = z − 10 m
(planes at z = 15, 19 and 30 m are 5, 9 and 20 m above ground); the STL's terrain under the 13 points is at
z = 5 m, so the rule and the STL disagree by 5 m (`QUESTIONS.md` QF4). M: the campus ground lies at z ≈ 32 m and
every point is 3 m above the local ground (verified against the STL to ±0.06 m). Velocities and concentrations are
**not** scaled: U, V, W are the tunnel's m/s, `C` the tunnel's ppm.

### Normalisations

- **F, `velocity_ratio`**: U / U_ref, U_ref the approaching mean speed at 500 m (the boundary-layer height), full
  scale. The legacy workbook normalises by the roof anemometers instead (SMB, G.L.+237 m, for NW–NE; KDD,
  G.L.+187 m, for the other directions); the CSVs re-normalise it, and the factor is recovered from the data:
  CSV = workbook × 0.9397 (SMB sector) or × 0.9629 (KDD sector), to within [0.93947, 0.94000] and [0.96250, 0.96324].
  U_ref itself in m/s is 10 (data paper) or 10.65 (implied by the approach-flow profile): `QUESTIONS.md` QF8.
  `velocity_ratio_sd` is the standard deviation of the 10-minute means behind a field value; it moves in steps of
  f/100 = 0.0094 or 0.0096 because the workbook's S.D. is rounded to 0.01.
- **M, `concentration_ratio`**: C / c0, c0 = q / (U_R H_R²) (data paper 3.13.1). Tunnel: q = 2.5 × 10⁻⁶ m³/s,
  U_R = 4.08 m/s, H_R = 0.068 m, c0 = **132.514 ppm** (the paper rounds to 1.33 × 10² ppm). Field: each run's own
  q and U_R with H_R = 41 m, c0 = 1,444 … 7,379 ppq. Field concentrations are **parts per quadrillion** (10⁻¹⁵) in
  the sources; `C` holds ppm, so `C_ppm = C_ppq × 10⁻⁹`.

### Wind direction → flow vector

| case | flow_dir(WD) | how the sense is known |
|---|---|---|
| F | (−sin WD, −cos WD) | compass FROM-direction, +y north (`MP_caseF.png`); the readme does not define it. Supported by the reference-building choice and by upwind roughness: status `unverified` (`QUESTIONS.md` QF9) |
| M | (−cos WD, +sin WD) | measured: the plume's lateral centroid moves toward −y as WD grows, in the tunnel (175° → 185°) and across the 18 field runs; the compass rose of `MP_caseM.png` (N at +x, W at +y) agrees |

### Geometry

| case | file | made from |
|---|---|---|
| F | `geometry.stl` | the published `BD_caseF.stl` × 800 (it is model scale: 0.90625 m = 725 m), every triangle reversed (all 21,537 horizontal ground and roof facets faced down); one shell, open only along the rim of the disc (812 boundary edges), 3 zero-area facets kept |
| M | `geometry.stl` | the published `BD_caseM.stl` × 600 (model scale: 1.8 m × 1.2 m = 1080 m × 720 m), every triangle reversed (3,118 of 3,152 horizontal facets faced down); one shell with 21 boundary and 7 non-manifold edges, kept |

### Approach flow

F: the 18 published heights (10 … 400 m full scale), `uu` = u_rms²; no `vv`, `ww`, `k`. M: the workbook's 40
heights at x = −0.498 m model (−299 m full scale), z = 3 … 360 m full scale, `uu vv ww` = σ², `k` = half their sum. M's heights are above the
**empty tunnel floor**: at the profile station the model's taper is already 0.052 m high, above the 10 lowest heights.
