---
title: "Validation"
parent: "Case J — 1:1:2 building, non-isothermal"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case J — 1:1:2 building, non-isothermal: Eddy3D's scores against the measurements, by engine."
---

# Case J: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-yellow status">pending</span> · UMF <span class="label label-green status">scored</span> · UMF buoyantKEpsilon <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

## urbanMicroclimateFoam, realizable k-epsilon (Eddy3D Outdoor+)

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$ | +0.921 | 0.731 | +0.193 | 0.573 | 443 |
| $$V$$ | +0.866 | 0.449 | — | 0.526 | 443 |
| $$W$$ | +0.840 | 0.289 | — | 0.596 | 443 |
| $$k$$ | +0.322 | 0.558 | -0.034 | 0.178 | 443 |
| $$\theta$$, floor-referenced temperature | +0.922 | 1.000 | +0.120 | 0.817 | 443 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.919 | 0.858 | +0.065 | 0.716 | 443 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.905 | 0.847 | -0.162 | 0.709 | 443 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.896 | 0.828 | -0.256 | 0.686 | 443 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, without the near-source points | +0.874 | 0.760 | +0.240 | 0.570 | 416 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, without the near-source points | +0.860 | 0.752 | +0.067 | 0.567 | 416 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, without the near-source points | +0.848 | 0.728 | +0.025 | 0.565 | 416 |
| $$U$$, y-symmetric ceiling (control) | +0.993 | 0.971 | +0.000 | 0.925 | 346 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/J/pairs/umf-realizableKE.csv`]({{ '/api/cases/J/pairs/umf-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture MetaFOAM.Lib.Tests/TestAijCaseJUmfContainerE2E (1:1:2 building, heated floor, floor point source; urbanMicroclimateFoam, realizable k-ε, 236,408 air cells at Froude scale 62.5, 1500 air iterations, solved 2026-10-18); figures validation/plot\_cases\_jl\_umf.py

Notes:

- The tracer is solved steady beside the flow, as three species of one flow. The outlet carried 0.89, 0.75 and 0.62 of the emission for $$\mathrm{Sc_t}$$ 0.3, 0.5 and 0.7, within the factor of two accepted as a check on the wiring.
- The air region ended at its 1500-iteration cap with the residualControl unmet (no \'solution converged\' line); at the last iteration the initial residuals were 1.3e-2 ($$U_y$$), 1.5e-2 (`p_rgh`) and 1.1e-3 to 1.7e-3 (the tracers).
- The steady closure gives a longer recirculation than the tunnel: reattachment at $$z/H = 0.25\text{ and }0.025$$ is $$1.35\thinspace H$$ and $$1.35\thinspace H$$, against the measured $$0.68\thinspace H$$ and $$0.80\thinspace H$$.

## urbanMicroclimateFoam, buoyantKEpsilon (Eddy3D Outdoor+)

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$ | +0.924 | 0.761 | +0.167 | 0.607 | 443 |
| $$V$$ | +0.901 | 0.442 | — | 0.540 | 443 |
| $$W$$ | +0.849 | 0.289 | — | 0.587 | 443 |
| $$k$$ | +0.360 | 0.582 | -0.088 | 0.208 | 443 |
| $$\theta$$, floor-referenced temperature | +0.920 | 0.998 | +0.127 | 0.806 | 443 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.894 | 0.869 | -0.050 | 0.698 | 443 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.869 | 0.840 | -0.274 | 0.675 | 443 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.852 | 0.806 | -0.380 | 0.641 | 443 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, without the near-source points | +0.829 | 0.757 | +0.052 | 0.541 | 416 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, without the near-source points | +0.788 | 0.731 | -0.193 | 0.538 | 416 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, without the near-source points | +0.755 | 0.709 | -0.292 | 0.519 | 416 |
| $$U$$, y-symmetric ceiling (control) | +0.993 | 0.971 | +0.000 | 0.925 | 346 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/J/pairs/umf-buoyantKEpsilon.csv`]({{ '/api/cases/J/pairs/umf-buoyantKEpsilon.csv' | relative_url }})
- Reproduce: Eddy3D fixture MetaFOAM.Lib.Tests/TestAijCaseJUmfContainerE2E (1:1:2 building, heated floor, floor point source; urbanMicroclimateFoam, buoyantKEpsilon, 236,408 air cells at Froude scale 62.5, 1500 air iterations, solved 2026-10-18); figures validation/plot\_cases\_jl\_umf.py

Notes:

- The tracer is solved steady beside the flow, as three species of one flow. The outlet carried 0.95, 0.84 and 0.73 of the emission for $$\mathrm{Sc_t}$$ 0.3, 0.5 and 0.7, within the factor of two accepted as a check on the wiring.
- The air region ended at its 1500-iteration cap with the residualControl unmet (no \'solution converged\' line); at the last iteration the initial residuals were 1.3e-2 ($$U_y$$), 1.1e-2 (`p_rgh`) and 1.2e-3 to 1.6e-3 (the tracers).
- The steady closure gives a longer recirculation than the tunnel: reattachment at $$z/H = 0.25\text{ and }0.025$$ is $$1.35\thinspace H$$ and $$1.56\thinspace H$$, against the measured $$0.68\thinspace H$$ and $$0.80\thinspace H$$.

## All runs

- Quantity: $$U$$, $$V$$, $$W$$ over $$U_H$$ = 1.4581 m/s and $$k$$ over $$U_H^2$$ (the tunnel\'s units, 443 distinct points); theta = ($$T_f - T$$)/($$T_f - T_H$$) with $$T_f$$ = 318.95 K and $$T_H$$ = 285.32 K; $$c^\ast = C/c_0$$ ($$c_0$$ = 12.28 ppm) against the model\'s ethylene mass fraction as ppm over the same $$c_0$$, for turbulent Schmidt numbers 0.3, 0.5 and 0.7; the 27 points within a quarter of a building height of the source are scored with and without. The scene is the tunnel at Froude scale 62.5
- Normalisation: the tunnel\'s units: velocities by $$U_H$$ (1.4581 m/s measured, the Froude-scaled 11.53 m/s modelled), $$k$$ by $$U_H^2$$, temperature as theta = ($$T_f - T$$)/($$T_f - T_H$$) ($$T_f$$ = 45.8 degC, $$T_f - T_H$$ = 33.63 K), $$c^\ast = C/c_0$$ ($$c_0$$ = 12.28 ppm) against the modelled ethylene mass fraction as ppm over the same $$c_0$$; hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units, concentration with one detection limit of $$10^{-3}$$ of the largest measured value; 443 points (point 153 repeats point 1)

Notes:

- The scene is the tunnel at Froude scale 62.5 (the production case writer cannot mesh a 0.16 m building): lengths times 62.5, velocities times 7.9, temperatures unchanged. That keeps the bulk Richardson number (-0.0856), Pr, the tunnel\'s Kelvin values and the dimensionless tracer, and does not keep Re (1.6e4 in the tunnel, 8e6 here).
- UMF\'s first cell is 0.75 m, 12 mm at tunnel scale: the tunnel\'s 24 K drop in air temperature between the floor and the first measurement at 3 mm lies inside it. The source is a mass rate into one pair of cells, with no release momentum and no heat from the 30.4 degC gas. The 27 points within a quarter of a building height of the source are scored with and without.
- The building is not adiabatic here: its walls are held at the measured mean surface temperature, 297.62 K, and the measured 4 K vertical gradient up the walls is not modelled. There is no sun, and the radiation exchange is at the least the view-factor model accepts (air-side emissivity 0.01).
- The measured $$+y$$ half of the $$z/H = 0.25$$ plane runs 11 % slower than the -y half (97 mirror pairs, R 0.955, recomputed from the cleaned table): the y-symmetric ceiling control scores the measurement against the mean of each mirror pair.
- The wake recirculates behind the leeward face and reattaches within $$3\thinspace H$$; the approach layer is unstable and the first cell above the heated floor is warmer than the air that entered it; every species is emitted, with clean air 25 m ahead of the building and its maximum at the source, and leaves through the outlet at 0.5 to 2 times the emission.

<details markdown="block">
<summary>Interpretation: Case J wall functions</summary>

At the model\'s Re, UMF\'s wall functions belong and the tunnel\'s laminar-sublayer heat transfer does not exist. Near-floor temperature is a wall-function result, and the data\'s tracer peak 4 mm above the 5 mm hole is a source-cell-limited number.

</details>

<details markdown="block">
  <summary>How the scores are computed</summary>

- Scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

</details>

## Figures

Figures: [Cases J and L (UMF)]({{ '/validation/cases-jl/' | relative_url }}).
