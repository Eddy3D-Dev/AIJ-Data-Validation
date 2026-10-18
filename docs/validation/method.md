---
title: "Method and metrics"
parent: Validation
nav_order: 1
summary: "how each case is scored, the metrics, the inflow, the two systematic differences"
description: "How Eddy3D's solvers are scored against the AIJ tunnel data: the method, the metrics, the fitted inflow and the figures' sources."
---

# Method and metrics

Scores: [Validation]({{ '/validation/' | relative_url }}).

## How the scores are computed

- Each case is solved through Eddy3D's production case writer (`build-case → run → probe`). The probe sits at the tunnel's own measurement coordinates; no interpolation enters the comparison.
- The measured side of every pair is the cleaned table (the legacy workbook at full precision). Eddy3D's fixtures score against the published CSVs, which round the workbooks; their scores differ from the scores on these pages in the third digit.
- Normalisation (the benchmark's convention): velocities by U_H, k by U_H².
- Cases A and B are solved at 1:100 with the tunnel's own velocities. The log-law inlet is fitted to each case's own approach-flow file over z = 0.02 … 2H (`u*`, `z₀` below).
- Cases C–E measure an omnidirectional *scalar* speed with thermistors; the model is scored as √(\|U\|² + 2k) and as \|U\|. Case F (thermistor and field, scalar speed over U(500 m)) is scored the same way.
- Cases H, I, J, K, L and M add a tracer concentration. The measured C/c₀ is scored against the model's c\* = c U_H H²/Q (Case M: c U_R H_R²/Q) at three turbulent Schmidt numbers, 0.3, 0.5 and 0.7. See [Cases H and I]({{ '/validation/cases-hi/' | relative_url }}), [Cases G and K]({{ '/validation/cases-gk/' | relative_url }}), [Cases J and L]({{ '/validation/cases-jl/' | relative_url }}) and [Cases F and M]({{ '/validation/cases-fm/' | relative_url }}).
- Cases J and L add a temperature, scored as the floor-referenced fraction θ = (T<sub>f</sub> − T)/(T<sub>f</sub> − T<sub>H</sub>) (the workbook's normalisation; 0 at the floor, 1 in the approach air at the building height). They are solved at a Froude scale on Eddy3D's buoyant engine.
- Case G is field data with an unknown canopy drag, solved as a sweep of arms that are each their own run.
- Case F is solved for one wind direction in two vertical frames that are each their own run. Case M (tracer over a real campus) is solved at one heading with the three Schmidt numbers as three runs on one flow.
- Case B's lateral velocity is sign-corrected before scoring (see [Known data issues]({{ '/known-data-issues/' | relative_url }})).
- The reattachment length L_r behind the building is read from a wake line at ground level.
- Fixture structure checks (ordering of regions, plume decay, symmetry): passed for every run.

### Metrics

- **R**: Pearson correlation of measured and modelled values.
- **FAC2**: fraction of pairs with 0.5 ≤ p/o ≤ 2 (o measured, p modelled; the ratio carries the sign for a signed component). For concentration, a pair with both values at or below the detection limit also counts.
- **FB**: fractional bias 2(ō − p̄)/(ō + p̄), positive when the model is low. Undefined (shown as —) for a signed component unless the measured and modelled means are both positive; R, FAC2, the hit rate and the counts stay.
- **Hit rate**: fraction of pairs with \|p − o\| ≤ W or \|p − o\|/\|o\| ≤ D, with D = 0.25. W is 0.05 U_H for a velocity component and the detection limit for concentration; k has no W.
- **NMSE** = mean((o − p)²)/(ō p̄); **NAD** = mean(\|o − p\|)/(ō + p̄); **MG** = exp(mean(ln o − ln p)); **VG** = exp(mean((ln o − ln p)²)). They are in the API's `validation.json`, with the FB, NMSE and NAD rule above.
- **Detection limit** (concentration): one limit, 10⁻³ of the largest measured value. It sets W of the hit rate and the both-below rule of FAC2, and floors the values in MG and VG.
- FB, FAC2, NMSE, NAD, MG and VG follow Chang & Hanna (2004); the hit rate follows VDI 3783-9.

### Controls

A control is scored with the same metrics as the run.

- **Frame:** the rotation sense mirrored (Cases C and D); upwind and downwind swapped (Case C); the lateral sign of V flipped (Cases L and M, OpenLB, FluidX3D); the points turned 180° about the source or mirrored across the plume axis (Case M); the tunnel's column for the opposite wind (Case F, SSE); U scrambled across the points (OpenLB).
- **Ceiling:** one measurement scored as a model of another: the tunnel's *before* as a model of its *after* (Case E); the measurement against the mean of each mirror pair (Cases K and L); the tunnel's WD 175, WD 185 and their mean as models of its WD 180 (Case M); the tunnel's WD 180 or 9 m column as a model of the field (Cases M and F).
- **Reference runs:** no belt (Case G); the approach column alone (Case L); the empty-domain flow (FluidX3D); the 9 m plane over the imposed U(500 m) (Case F); the reversed wind (ML surrogate).

### How the scores were checked against the solvers' own output

- Case C: a re-scoring from the probe files and the original `RS_caseC.csv` reproduces every number (largest difference 9 × 10⁻¹⁶).
- Case D: the numbers were reproduced from the solver's probe output against the cleaned table, with the frame mapped independently and separate metric code.
- OpenLB: reproduced from the solver's probe output against the original Zenodo CSVs (largest difference 1 × 10⁻¹⁵).
- FluidX3D: reproduced from the solver's probe output against the cleaned tables, with the comparable set derived independently (largest difference 3 × 10⁻¹²).
- Cases F, G, H, I, J, K, L and M: the scores served are recomputed from the per-point pairs by `validation/dispersion_metrics.py`, a transcription of Eddy3D's `MetaFOAM.DispersionMetrics`. Fed the published CSVs and the probes of Eddy3D's test, it gives that test's own scores to 10⁻⁹ (24 scores of Case F, 43 of Case K, five per arm of Case G, 80 per run of Case J, 48 of Case L, 84 of Case M). The SHA-256 of every file a snapshot was read from is in its results file under `sources`, and the script fails if the check is not met.

<details markdown="block">
<summary>Interpretation: Scoring choices</summary>

- The scalar-speed pair √(\|U\|² + 2k) and \|U\| are the two ends of the bracket the thermistor measurement has to fall in.
- The profile shape of a log law is scale-invariant, so the U/U_H values of the 1:100 solves of Cases A and B carry over unchanged.

</details>

## Two systematic differences between the tunnels and the solvers

These shape the validations of Cases C, D and E.

- **Scalar vs vector speed.** C, D and E measure with thermistor anemometers, which report a mean *omnidirectional scalar* speed; steady RANS gives the magnitude of the mean velocity. Case D is the only case where both instruments overlap: over its 33 shared points the thermistor reads 1.34× \|U\| (ratio of means), and √(\|U\|² + 2k) from the split-fibre data matches the thermistor to FB +0.058 where \|U\| alone gives +0.292. A Case C/D/E score is reported at both ends of the bracket \|U\| ≤ Vs ≤ √(\|U\|² + 2k).
- **Inflow profile.** The inlet is a log law. Fitted power-law exponents of the tunnels' profiles are 0.19 (C, D) and 0.16–0.20 (E) against the papers' 0.28 / 0.25. A log-law fit misses the single measurement height by −4 … −11 % depending on the fitting window, and sets the inlet k 26–48 % below the tunnel's (Case D).

<details markdown="block">
<summary>Interpretation: The two differences</summary>

- Steady RANS gives a mean velocity magnitude that is lower than the thermistor's scalar speed by construction.
- Both differences lower the model against Cases C, D and E relative to Cases A and B.
- The tunnels' profiles of Cases C, D and E are closer to a power law than a log law, and a single near-ground height is where a log-law inlet is least right.

</details>

## Inflow

Fitted to each case's own approach-flow file over z = 0.02 … 2H:

| Case | u\* (m/s) | z₀ (mm) | U_H measured (m/s) | log-law error |
|---|---|---|---|---|
| A | 0.343 | 0.668 | 4.491 | +2.0 % |
| B | 0.399 | 0.882 | 5.133 | +2.9 % |

- Cases C, D and E carry their own fitted profiles on their pages. All three score at a single near-ground height.
- The fits are in `/api/cases/{id}.json` under `inflow_fit`.

## Reproducing the figures

`validation/plot_cases_ab_openfoam.py` (Cases A and B), `validation/plot_case_c_openfoam.py`, `validation/plot_cases_hi_openfoam.py`
(Cases H and I), `validation/plot_cases_gk_openfoam.py` (Cases G and K), `validation/plot_cases_jl_umf.py` (Cases J and L), `validation/plot_cases_fm_openfoam.py` (Cases F and M) and
`validation/plot_ml_surrogate.py` (UltraPlot) build the figures; `validation/plot_layout.py` draws where each case was measured, from the groups of lines and planes in `validation/layout.py`, which also colour the dots of the agreement figures (`validation/test_layout.py` pins them). The Eddy3D fixtures are
`TestAijCaseAContainerE2E`, `TestAijCaseBContainerE2E`, `TestAijCaseC{0D,1D,2D}ContainerE2E`, `TestAijCaseFContainerE2E`, `TestAijCaseGContainerE2E`, `TestAijCaseHContainerE2E`,
`TestAijCubeContainerE2E`, `TestAijCaseKContainerE2E`, `TestAijCaseJUmfContainerE2E`, `TestAijCaseLUmfContainerE2E`, `TestAijCaseMContainerE2E` and `Outdoor.ML.Tests/TestAijSurrogateE2E`. The scores they wrote are
snapshotted in `validation/results/` with the per-point pairs beside them, and served unchanged by
`/api/cases/{id}/validation.json`.
