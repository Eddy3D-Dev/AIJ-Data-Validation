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
`schema_version`, with its changelog in `index.json` and on the [API page](https://eddy3d-dev.github.io/AIJ-Data-Validation/api-reference/#versioning-and-changes).

## [3.3.1] - 2026-10-20

Field maps: the solved flow on the measurement planes, with the measured points drawn on it.

### Added

- `case-{a,b,h,j,k,l}-*-field-plan.png` and `-field-section.png`, `case-{i,g}-openfoam-field-section.png`,
  `case-{f,m}-openfoam-field-plan.png`: for every Eddy3D run whose solve is at hand (Cases A, B, F, G, H, I, J, K, L, M),
  three panels on one plane: $$u$$; $$u$$ with iso-lines every 0.1 and the edge of the reversed flow ($$u = 0$$) dashed; the
  in-plane speed with streamlines. Each measured point is a dot coloured by its measured value on the same scale, so a dot
  that stands out from the field is a point the model misses. They are listed with each run's figures and on the case pages.
- `validation/extract_planes.py` samples the solves on those planes (`validation/results/planes/`, with the frame, the speed
  and a check against the served pairs: $$r \gt 0.98$$ on every plane, 0.987 at the lowest); `validation/plot_field_maps.py` draws the maps from
  those snapshots in the pinned build. Cases C, D and E have no maps yet: their solves are not on the machine that sampled these.

## [3.3.0] - 2026-10-20

Five more Eddy3D runs, scored and served as submissions: what moves the OpenFOAM 12 scores, and what does not.

### Added

- `submissions/eddy3d-of12-measured-inlet` (Cases A, B, H): the served runs with the tunnel's MEASURED approach profile
  ($$U$$ and $$k$$ of `AF_case*.csv` as fixedProfile tables, epsilon by local equilibrium) at the inlet and the rough floor kept —
  Case A's $$U$$ hit rate 0.586 to 0.624 and $$k$$'s 0.177 to 0.344, Case B's 0.562 to 0.571, Case H unchanged (its log-law $$k$$ is
  within 15 % of the tunnel's). The wake is where the $$U$$ error lives and the inlet does not move it.
- `submissions/eddy3d-of12-sst-urans` (Case A): SST k-omega run transient on the measured inlet, scored on the time
  means ($$k$$ = kMean + the resolved half-trace of UPrime2Mean): the best hit rates of any OpenFOAM run, $$U$$ 0.683 and $$k$$ 0.392,
  with 27 % of the wake's $$k$$ resolved and the reattachment still at $$1.3\thinspace H$$ against the tunnel's $$0.4\text{–}0.75\thinspace H$$.
- `submissions/eddy3d-of12-mesh2x-measured-inlet` (Case A): every snappy level one finer (1,113,756 cells) plus the measured
  inlet, the best steady set-up ($$U$$ hit rate 0.651); the mesh alone changes nothing (grid-converged).
- `submissions/eddy3d-of12-casek-workbook-inflow` (Case K): the served run re-solved at the inflow speed the dataset's
  workbook states, $$U_H$$ = 4.94009 m/s at 0.2 m, instead of the shipped approach-flow file's 3.23 m/s (that file is Case H's,
  cell for cell): $$U$$ hit rate 0.12 to 0.56, the above-roof plane matched to 4 %, $$c^\ast$$ at $$\mathrm{Sc_t}$$ 0.5 off the source FB -0.43 to -0.13.
- `submissions/eddy3d-of12-casee-refined-mesh` (Case E, SW, both states): one snappy level more on the ground and the
  buildings (1,414,688 cells): the thermistor quantity's FB +0.226 to +0.133 and hit rate 0.475 to 0.562 after construction,
  +0.124 to +0.065 before; the construction change's R 0.831 to 0.853 and sign agreement 0.75 to 0.86.
- `/api/submissions/eddy3d-of12-*.json` and `validation/results/submissions/eddy3d-of12-*/` for each.

### Changed

- `validation/dispersion_metrics.py` sums with `math.fsum` (exact, order-independent) instead of NumPy's pairwise SIMD
  sum, whose rounding depends on the runner's CPU: the geometric mean of one submission flapped in its last digit
  between two CI runs on the same inputs. The served scores are unchanged within the self-test's 1e-9; the
  submissions' scores may move in their last digits.

Every run is an Eddy3D fixture arm (`EDDY3D_VALIDATION_*` knobs; Eddy3D `docs/VALIDATION.md` 3c-ii, 8 and the Case K
note), solved on one Apple M-series laptop on 2026-10-20; the scores here are the site's own evaluator on the submitted
values and reproduce the fixtures' to the printed digit.

## [3.2.3] - 2026-10-19

The site and the API move to <https://aij.eddy3d.com>.

### Changed

- Every address the API, the site, the README and the citation give is `https://aij.eddy3d.com/...` in place of
  `https://eddy3d-dev.github.io/AIJ-Data-Validation/...`; GitHub redirects the old addresses. The frozen copy of 3.2.1 keeps
  the addresses it was released with.

### Added

- Site: `/robots.txt` (rules for AI crawlers, content signals, the sitemap), `/sitemap.xml`, `/.well-known/api-catalog`
  ([RFC 9727](https://www.rfc-editor.org/rfc/rfc9727)) and `/auth.md` (the site and the API need no authentication).

## [3.2.2] - 2026-10-19

Every engine on each case's page, and a leaderboard. API copies are kept from 3.2.1 on.

### Changed

- `/api/cases/{A..E}/validation.json`: the figures that drew several cases together are drawn one per case: every engine on the same
  points, `case-{a,b}-engine-comparison.png`; the ML surrogate, `case-{a..e}-ml-agreement.png`.
- `/api/cases/{G..L}/validation.json`: vertical profiles of $$U/U_H$$ (`case-{g..l}-openfoam-profiles.png`, validation/plot_profiles.py), as
  Cases A and B have.
- Site: each case's Validation page has a table of contents, its measurement locations, then one section per engine (OpenFOAM 12, OpenLB,
  FluidX3D, ML surrogate) with that engine's reading, figures and scores, and ends with a leaderboard: every run on the case, Eddy3D's and
  the community's, scored by one evaluator (validation/score_submissions.py) on the quantities all of them share and ranked by the mean hit
  rate. The Validation overview lists the cases; the OpenLB and FluidX3D and the ML surrogate pages describe the engines and link the cases.
- Site: every table of scores gives $$R^2$$ beside $$R$$. urbanMicroclimateFoam (Cases J and L) is shown as OpenFOAM 12, which it is, not
  as an engine of its own; the engine ids in the API are unchanged.
- Case I: the stacking of its two point sets is described in the table's schema and is no longer listed as a known data issue.
- Wording: "side face" or "side" for "flank", in the notes and in the names of three checks of `clean/checks.json`.

### Removed

- The frozen copies of releases 2.0.0 to 3.2.0 under `/api/<release>/`, and `scripts/host_release.py`. Nobody had pinned to them yet;
  copies are kept from 3.2.1 on, and `/api/versions.json` lists the releases that have one. The unversioned `/api/` serves every file it
  served before. The figures only those copies named are no longer served.

## [3.2.1] - 2026-10-19

One page per case. Each case's Validation page carries its whole reading; no page reads two cases together.

### Changed

- `/api/cases/{A,B,H,I}/validation.json`: the OpenFOAM 12 figures are drawn one per case, `case-{a,b}-openfoam-agreement.png`,
  `case-{a,b}-openfoam-profiles.png` and `case-{h,i}-openfoam-agreement.png`, in place of the figures that drew Cases A and B,
  and Cases H and I, together. The earlier figures stay served at their URLs for the releases that name them.
- Site: the measurement layout, the figures and the interpretation of each case are on its own Validation page
  (`/cases/case-x/validation/`). The pages that read two cases together (Cases A and B, F and M, G and K, H and I, J and L) and
  the separate pages of Cases C, D and E are gone; their addresses redirect to the case's page. The Validation section keeps the
  pages that span cases: the method, the inflow, OpenLB and FluidX3D, and the ML surrogate.

## [3.2.0] - 2026-10-18

Validate your own solver. The benchmark becomes usable by anyone scoring a wind solver or ML model: the points to probe,
the inlet contract and the scoring constants are served per case, `validation/score_submissions.py` scores a folder of values exactly as
the served results are scored, and submissions are scored by the build and served as community results. API schema 2.5.0.

### Added

- `validation/score_submissions.py`: scores a folder of your values at the published points, run from a checkout (nothing beyond
  `requirements.txt`). It scores with `validation/dispersion_metrics.py` as the plot scripts do, and its `--self-test` (run by the build)
  re-scores every served run from its pairs and matches 224 headline scores to $$10^{-9}$$ (Case E to $$10^{-6}$$: its served scores came
  from the published CSV, which rounds the workbook).
- `/api/cases/{id}/probes.csv`: the published points to probe, with the key columns a scored file carries, $$x$$ $$y$$ $$z$$ in the case frame and
  `scored_as` (vector, $$k$$, thermistor_bracket, concentration, theta).
- `/api/cases/{id}.json` `scoring` (the reference speed, the constants of $$\theta$$, the conventions, the metric meanings) and `inflow` (the
  benchmark's approach-flow data; the inlet this repository recommends, a log law with $$k$$ and $$\varepsilon$$ from the neutral ABL relations or
  the tabulated profile where no log law fits; the flow-direction convention; what Eddy3D's runs used, quoted from their snapshots).
- `/api/cases/{id}/inflow_openfoam.txt`: the recommended inlet as OpenFOAM 12 files in one text (`0/U`, `0/k`, `0/epsilon`, `0/nut`, `system/probes`
  with the case's points).
- `/api/submissions.json` and `/api/submissions/{slug}.json`: every folder under `submissions/`, scored by the build with that script from
  the values it gave (served as `/api/submissions/{slug}/{id}.csv`), with the coverage of every score. One example submission, `example-openfoam12`
  (Eddy3D's Case A probes, `example: true`), proves the pipeline.
- Site: [Validate your own solver](https://eddy3d-dev.github.io/AIJ-Data-Validation/byos/) (ten steps, Case A end to end), [Community results](https://eddy3d-dev.github.io/AIJ-Data-Validation/community/)
  (its own matrix, separate from Eddy3D's; self-reported inputs, scored by this repository's CI), the [inlet contract](https://eddy3d-dev.github.io/AIJ-Data-Validation/validation/inflow/)
  page, and a page per submission.
- Repository: `LICENSE` (code, MIT) and `LICENSE-DATA` (data, CC BY 4.0, with the attribution), `CONTRIBUTING.md`, issue templates and a pull
  request template with the release checklist.

### Changed

- `index.json` `license_detail` says what each licence covers: the data CC BY 4.0, the code MIT.
- Documentation since 3.1.3 (no served byte of its own), the LaTeX sweep:
- Every symbol and formula on the site and in the READMEs is LaTeX between `$$ ... $$`, which GitHub and the site's kramdown both read
  (the site loads MathJax): $$c_0 = \dfrac{q}{U_H H^2}$$, $$C/c_0$$, $$\overline{u'u'}$$ instead of `uu`, $$c_{\mathrm{rms}}$$. A column name stays in code font
  where it is an identifier. The served files keep their plain strings.
- Coordinates and positions ($$y/H = 0$$, $$z = 0.019\thinspace H$$, $$x \in \lbrack -0.1,\thinspace 0\rbrack$$, $$H/64$$), powers of ten ($$10^{-3}$$),
  the variances ($$\overline{u'u'} = u_{\mathrm{rms}}^2$$), $$C_\mu$$, $$U_x$$ and the captions of the validation figures are LaTeX too; `scripts/mathtext.py`
  and the `plain-math` rule of `scripts/check_markdown.py` know these forms, so none can come back as plain text.
- One nomenclature (`scripts/nomenclature.py`) says, as bullet points, what each symbol, column and score means: `docs/_includes/nomenclature.md` under every table of
  quantities, `nomenclature-scores.md` under every table of scores ($$n$$, $$R$$, $$\mathrm{FAC2}$$, $$\mathrm{FB}$$, the hit rate), `metrics.md` as the
  Metrics section of the Method page; the READMEs get the same texts between `<!--nomenclature ...-->` markers.
- The hit rate is $$\mathrm{HR}$$ with the tolerances $$\delta_{\mathrm{rel}}$$ and $$\delta_{\mathrm{abs}}$$ (VDI 3783-9: $$q$$, $$D$$, $$W$$), so that $$q$$ is
  the tracer release rate, $$D$$ the block size and $$W$$ the vertical velocity only; tables that headed the hit rate `q` say "hit rate".
- `scripts/check_markdown.py` checks how a formula is written and where it stands, that a table of scores or symbols has its nomenclature, and that no
  symbol comes back as plain text.
- Site: the colour scheme button has a third mode, "system" (the default): the page follows the device's light or dark setting, also while it is open and in
  every open tab. A click goes system, the scheme the page is not in, the scheme it is in, system; the icon (monitor, sun, moon) shows the mode. The math follows
  the scheme without a rule of its own (MathJax's SVG is drawn in the text colour). `theme_toggle.html` holds the one button that the header and the small-screen corner use.

## [3.1.3] - 2026-10-18

Wording; no value changed.

### Changed

- Case L: where the orientation matters, `clean/README.md`, `clean/SCHEMA.md` and `README.md` say "14 rows along x by 9 columns across y", which is what `BD_caseL.stl`
  holds; the name of the array is "9 × 14 cubes" everywhere, as the readme of the case names it (Known data issues).

## [3.1.2] - 2026-10-18

Wording and figures; no value changed.

### Changed

- Case L is "9 × 14 cubes" (nine rows by fourteen columns, as the case's readme says) in `README.md`, `clean/README.md` and `clean/SCHEMA.md`.
- The `notes` of Case F say "The published STL is open along the rim"; the notes of Case G no longer state what is not fitted; `llms.txt` says "Status:";
  the entries of the API changelog in `index.json` lose their "Why MINOR" sentences; the `message` of `CITATION.cff` is the standard one.
  `clean/README.md` states what the building shells of Case E are, not how an earlier build treated them.
- The scores in the panels of the agreement figures of Cases H, I, J and L sit in the corner that hides the fewest points; a box in a fixed corner hid dozens.
  The log axes of Cases J and L start a thousandth above their lowest decade, so two tick labels no longer sit on each other in the corner.
  The letter C of Case L's layout figure sits at the end of its points, not at the end of a long line.

## [3.1.1] - 2026-10-18

Metadata only; no value changed. The repository and the site moved to <https://github.com/Eddy3D-Dev/AIJ-Data-Validation>.

### Changed

- The site is <https://eddy3d-dev.github.io/AIJ-Data-Validation/>: every URL in the served files (`index.json`, `openapi.json`, `llms.txt`, the case and
  validation documents, the Dataset JSON-LD) names it, and the pinned address of a release is
  `https://eddy3d-dev.github.io/AIJ-Data-Validation/api/<release>/index.json`. The frozen trees of 2.0.0 to 3.1.0 keep the addresses they were tagged with.
- The suggested citation of the API (`cite.api` in `index.json`, `CITATION.cff`, `.zenodo.json`, the site and the README) names Ilker Karadag and
  Patrick Kastner as authors and the Sustainable Urban Systems Lab as publisher.

## [3.1.0] - 2026-10-18

Additive: new figures, fields and citation endpoints, and fixes. The API schema is 2.4.0 (additive; its changelog is in `index.json`).

### Added

- A layout figure for each case, A to M (`validation/figures/case-<id>-layout.png`), drawn from the measurement groups in
  `validation/layout.py` (pinned by `validation/test_layout.py`). The dots of the agreement figures take the colour of the line, plane or
  group they were measured in. Each layout figure is the first entry of `figures` in the case's validation results.
- `cite.api` in `index.json` and `citation` in `cases/{id}.json`; suggested citations on the site and in the README; `CITATION.cff` cites this
  dataset (the data paper, the AIJ guidelines and the Zenodo record of each case are its references); `.zenodo.json`.
  `scripts/citation.py` renders all of them and `scripts/check_citation.py` checks them. The pinned address of a release is
  `https://eddy3d-dev.github.io/AIJ-Data-Validation/api/<release>/index.json`.
- `bodies`, `body_contacts`, `inconsistent_triangles` and `min_body_volume` in the `stats` of `geometry.json` and in the geometry index,
  beside `edges_boundary`; `watertight` is true when every body is closed, consistently wound and positive in volume.
  `scripts/check_geometry.py` parses every served and cleaned STL and fails the build on an open, inconsistently wound or inward body, a
  degenerate or repeated triangle, or a stored normal that disagrees with the winding. `clean/build.py` runs four more checks on the cleaned
  tables (293 in all, none failing; 289 before): the closed outward bodies of Cases E, F and M, and the winding and solid of `BD_caseL.stl`.

### Fixed

- Case E: every building of `geometry.stl` and `geometry_bc.stl` is a closed, consistently wound, outward body. 1,563 of the 8,436
  triangles (18.5 %) of the 3dm's building meshes were wound against their neighbours, which the earlier whole-shell flip could not
  repair; they are re-wound. One wall that two buildings share (4 triangles) is removed, which joins the two into one body: 545 bodies
  after construction (8,432 triangles), 542 before (8,396), and 11 edges where two bodies touch.
- Cases F and M: `geometry.stl` is one closed outward body. F is closed with a 1 m base slab (vertical walls from the rim of the 725 m disc
  down to $$z = -1\thinspace\mathrm{m}$$ and a bottom cap, 2,436 added triangles; the zero-area triangles at T-junctions are removed and their neighbours split); M loses 7
  slivers (0.45 m² together) on building roofs and is closed the same way (21 added triangles). The bounding box starts at $$z = -1\thinspace\mathrm{m}$$.
- `BD_caseL.stl`, as published, has the two bottom triangles of each of its 126 cubes wound inward (Known data issues); the served
  `geometry.stl` is the 126 boxes and was never affected.
- Wording of the API descriptions and `llms.txt`, of the `notes` of the runs in `validation.json` (Cases F, G, J, K, L and M), of the wind-direction texts
  (Cases D, E, F and M) and of the known-issue texts (Cases D and F); no value changed. `status_meaning.scored` reads "a validation run exists and its scores are in cases/{id}/validation.json".
- Case M's `notes` state the probe precision: seven significant digits, no $$c^\ast$$ value moved by more than 0.003 against a six-decimal probe. Its controls text says that 14 of the 15 turned points lie in the fluid.

### Changed

- The site title reads "AIJ UWE"; `index.json`, `openapi.json` and `llms.txt` say "AIJ UWE — cleaned data API". The licence note is one line, "Data: Kikumoto et al. (2026), CC BY 4.0. Collectors per case in cases/{id}.json.", and `clean/manifest.json` carries "Data: Kikumoto et al. (2026), CC BY 4.0. Collectors and requested citation per case."

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
  iterations, solved 2026-10-18, scored at the tunnel's 203 points: $$U$$, $$V$$, $$W$$, $$k$$ and the concentration $$c^\ast$$ at turbulent Schmidt numbers 0.3,
  0.5 and 0.7 (three species on one flow, all published), with and without the four points at the source, and the
  y-symmetric ceiling of the measurement. The solve ran to its iteration limit with the residual control unmet.
- Validation of Case G (tree belt, field data): OpenFOAM 12, realizable k-ε, a drag sweep because the canopy's leaf area density and drag
  coefficient are not in the dataset: no belt, three vegetation-library crowns (Cd·LAD 0.30, 0.625 and 0.875 1/m) on a two-dimensional
  slab, and the conifer crown on the real belt as a half domain. Five runs of one engine, each its own `configuration`, none chosen;
  $$U$$ and $$k$$ at the 28 points over the model's own $$U(7\text{ m})$$ and over the imposed $$U_H$$, and the run notes say that the arm nearest the data is a
  calibration and that Eddy3D's trees have no canopy $$k$$ source.
- Validation of Case J (1:1:2 building on a heated floor, floor tracer source) and Case L (9 × 14 cube array on a heated floor, line
  source) on Eddy3D's buoyant microclimate engine, urbanMicroclimateFoam (UMF), at Froude scales 62.5 and 100, solved 2026-10-18 (J:
  236,408 air cells, L: 754,940, the air region stopped at its 1500-iteration cap). J under realizable k-ε and `buoyantKEpsilon`, L under
  realizable k-ε; $$U$$, $$V$$, $$W$$, $$k$$, the floor-referenced temperature $$\theta$$ and the concentration at three Schmidt numbers, in the tunnel's units.
  The API lists UMF as the engines `umf-realizableKE` (J, L) and `umf-buoyantKEpsilon` (J), and each validation result has `notes`.
- Validation of Case F (Shinjuku district: a 1978 high-rise district, thermistor speed in a 1:800 tunnel at 5, 9 and 20 m and a year of field cup
  anemometers): OpenFOAM 12, realizable k-ε, numerics level 3, 2,143,488 cells, 2000 iterations, solved 2026-10-18 for the wind from NNW only
  (the other eleven tunnel directions were not run). The tunnel's 33 points and the field's 13 are scored as $$\lvert\mathbf{U}\rvert$$ and $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ over the model's own
  $$U(500\text{ m})$$, in two vertical frames that are two runs of one engine (`configuration` `literal`: the published z in the STL's frame; `agl`: the STL's
  ground plus the instrument height; the files do not say which the tunnel meant, so neither is asserted), with the tunnel's 9 m column as a model of
  the field and the solved field's correlation with the tunnel's column for the opposite wind (SSE) as controls. That control corroborates the
  compass reading of the wind directions at NNW: the direction table of `clean/` marks the NNW rows `corroborated by a solved field`, the other
  directions stay `unverified`.
- Validation of Case M (TPU Atsugi campus, tracer release over real terrain): OpenFOAM 12, realizable k-ε, numerics level 3, 1,394,053 cells, 3000
  iterations, solved 2026-10-18 for the tunnel's heading WD 180 only, scored at the 15 points: $$c^\ast$$ at turbulent Schmidt numbers 0.3, 0.5 and 0.7 (three
  runs on one flow, `configuration` `sct03`, `sct05`, `sct07`, none chosen) and $$U$$, $$V$$, $$W$$ and $$k$$ over the solved speed at the reference mast, with the
  fixture's two controls (the points turned 180° about the source and mirrored across the plume axis), the tunnel's own WD 175 and WD 185 scored
  against its WD 180, and the 18 field runs recorded beside the tunnel. The ordering the fixture first asserted (the points nearest the source carry
  more than the far ones) is recorded and stated in the run notes as a model finding.
- Every score of the runs of Cases F, G, K, J, L and M is recomputed from the per-point pairs by `validation/dispersion_metrics.py`, never copied
  from Eddy3D's log; fed the published CSVs and the fixtures' own probes it reproduces the fixtures' scores to $$10^{-9}$$ (the script fails
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
- Every figure is drawn in one colour-blind-safe style (UltraPlot).

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
- Units of Case G's approach flow: `cases/G.json` `approach_flow.units` said m/s and m²/s², but the table holds $$U/U_b$$ and $$k/U_b^2$$, which are
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
- The site pages and the README embed a 1600 px copy of each figure (`docs/assets/web/`, written by `scripts/build_api.py`,
  byte-identical on every build) with `width`, `height` and `loading="lazy"`, and link it to the full-size figure
  (`docs/assets/figures/`, `docs/assets/geometry/`; the API's `figures` and `render` entries point there).
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
