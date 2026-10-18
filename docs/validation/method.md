---
title: "Method and metrics"
parent: Validation
nav_order: 1
summary: "how each case is scored, the metrics, the inflow, the two systematic differences"
description: "How Eddy3D's solvers are scored against the AIJ tunnel data: the method, the metrics, the fitted inflow and the figures' sources."
---

# Method and metrics

The method every score on this site follows. The overview of what is scored is on the [Validation]({{ '/validation/' | relative_url }}) page.

## How each case is scored

Each case is solved through Eddy3D's production case writer (`build-case → run → probe`), not a hand-built
OpenFOAM case, so what is validated is what a user gets. The probe sits at **exactly the tunnel's own measurement
coordinates**, so no interpolation enters the comparison.

- Cases C–E measure an omnidirectional *scalar* speed with thermistors, so the model is scored as √(\|U\|² + 2k) and
  as \|U\| — the two ends of the bracket the measurement has to fall in.
- The tunnel's model-scale geometry is solved at 1:100 (Cases A, B) with the tunnel's own velocities; the log-law
  inlet is fitted to each case's own approach-flow file over z = 0.02 … 2H (`u*`, `z₀` below), and the profile
  shape is scale-invariant for a log law, so U/U_H values carry over unchanged.
- Everything is normalised by U_H (k by U_H²), the benchmark's own convention.
- Metrics per quantity: Pearson **R**; **FAC2**, the fraction of points within a factor of two; **FB**, the fractional
  bias 2(ō − p̄)/(ō + p̄), positive when the model is low; and the **hit rate**, the fraction within D = 0.25 relative
  or W = 0.05 U_H absolute. NMSE, NAD, MG, VG are in the API's `validation.json`.
- Cases H, I, J, K and L add a tracer concentration. The measured C/c₀ is scored against the model's c\* = c U_H H²/Q at three turbulent Schmidt numbers, with one detection limit (10⁻³ of the largest measured value); see [Cases H and I]({{ '/validation/cases-hi/' | relative_url }}), [Cases G and K]({{ '/validation/cases-gk/' | relative_url }}) and [Cases J and L]({{ '/validation/cases-jl/' | relative_url }}).
- Cases J and L add a temperature, scored as the floor-referenced fraction θ = (T<sub>f</sub> − T)/(T<sub>f</sub> − T<sub>H</sub>) (the workbook's normalisation; 0 at the floor, 1 in the approach air at the building height), and are solved at a Froude scale on Eddy3D's buoyant engine. Case G is field data with an unknown canopy drag, solved as a sweep of arms that are each their own run.
- Case B's lateral velocity is sign-corrected before scoring (see [Known data issues]({{ '/known-data-issues/' | relative_url }})).
- The reattachment length L_r behind the building is read from a wake line at ground level.

## Two systematic differences between the tunnels and the solvers

Both were measured on the data rather than assumed, and both shape the validations of Cases C, D and E.

- **Scalar vs vector speed.** C, D and E measure with thermistor anemometers, which report a mean *omnidirectional
  scalar* speed; steady RANS gives the magnitude of the mean velocity, which is lower by construction. Case D is the
  only case where both instruments overlap: over its 33 shared points the thermistor reads 1.34× |U| (ratio of means),
  and √(|U|² + 2k) from the split-fibre data matches the thermistor to FB +0.058 where |U| alone gives +0.292. A
  Case C/D/E score is therefore reported at both ends of the bracket \|U\| ≤ Vs ≤ √(\|U\|² + 2k).
- **The inlet is a log law, the tunnels' profiles are not.** Fitted power-law exponents are 0.19 (C, D) and 0.16–0.20
  (E) against the papers' 0.28 / 0.25; a log-law fit misses the single measurement height by −4 … −11 % depending on
  the fitting window, and sets the inlet k 26–48 % below the tunnel's (Case D). These are declared systematics, and
  the first thing to quote if the scores come back worse than A and B.

## Inflow

Fitted to each case's own approach-flow file over z = 0.02 … 2H, rather than assumed:

| Case | u\* (m/s) | z₀ (mm) | U_H measured (m/s) | log-law error |
|---|---|---|---|---|
| A | 0.343 | 0.668 | 4.491 | +2.0 % |
| B | 0.399 | 0.882 | 5.133 | +2.9 % |

Cases C, D and E carry their own fitted profiles on their pages — and a caveat each: their tunnels' profiles are
closer to a power law than a log law, and C, D and E all score at a single near-ground height, which is where a
log-law inlet is least right. The fits are in `/api/cases/{id}.json` under `inflow_fit`.

## Reproducing the figures

`validation/plot_cases_ab_openfoam.py` (Cases A and B), `validation/plot_case_c_openfoam.py`, `validation/plot_cases_hi_openfoam.py`
(Cases H and I), `validation/plot_cases_gk_openfoam.py` (Cases G and K), `validation/plot_cases_jl_umf.py` (Cases J and L) and
`validation/plot_ml_surrogate.py` (UltraPlot) build the figures. The Eddy3D fixtures are
`TestAijCaseAContainerE2E`, `TestAijCaseBContainerE2E`, `TestAijCaseC{0D,1D,2D}ContainerE2E`, `TestAijCaseGContainerE2E`, `TestAijCaseHContainerE2E`,
`TestAijCubeContainerE2E`, `TestAijCaseKContainerE2E`, `TestAijCaseJUmfContainerE2E`, `TestAijCaseLUmfContainerE2E` and `Outdoor.ML.Tests/TestAijSurrogateE2E`. The scores they wrote are
snapshotted in `validation/results/` with the per-point pairs beside them, and served unchanged by
`/api/cases/{id}/validation.json`. For Cases G, K, J and L (as for H and I) the scores served are recomputed from the pairs, the SHA-256 of every file a snapshot was read from is in its
results file under `sources`, and the script fails if the metrics, fed the published CSVs and the fixture's probes, do not give the fixture's own scores to 10⁻⁹.
