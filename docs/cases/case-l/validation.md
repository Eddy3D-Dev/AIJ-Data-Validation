---
title: "Validation"
parent: "Case L — 9 x 14 cube array, line source, non-isothermal"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case L — 9 x 14 cube array, line source, non-isothermal: Eddy3D's scores against the measurements, by engine."
---

# Case L: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-yellow status">pending</span> · UMF <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

## urbanMicroclimateFoam, realizable k-epsilon (Eddy3D Outdoor+)

Quantity: $$U$$, $$V$$, $$W$$, the speed $$\lvert\mathbf{U}\rvert$$ over $$U_H$$ = 1.3394 m/s and $$k$$ over $$U_H^2$$ (the tunnel\'s units, 344 points); theta = ($$T_f - T$$)/($$T_f - T_H$$) with $$T_f$$ = 45.01 degC and $$T_f - T_H$$ = 30.26 K; $$c^\ast = C/c_0$$ ($$c_0$$ = 1728 ppm) against the model\'s ethylene mass fraction as ppm over the same $$c_0$$, for turbulent Schmidt numbers 0.3, 0.5 and 0.7; also the 242 points at or above 30 mm, the first four fine cells above the floor. The scene is the tunnel at Froude scale 100.

<details markdown="block">
  <summary>All 19 headline scores</summary>

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$ | +0.918 | 0.608 | +0.268 | 0.506 | 344 |
| $$V$$ | -0.037 | 0.291 | -0.795 | 0.747 | 344 |
| $$W$$ | -0.027 | 0.183 | — | 0.762 | 344 |
| $$\lvert\mathbf{U}\rvert$$ | +0.898 | 0.674 | +0.206 | 0.515 | 344 |
| $$k$$ | +0.145 | 0.584 | +0.635 | 0.244 | 344 |
| $$\theta$$, floor-referenced temperature | +0.936 | 1.000 | +0.049 | 0.985 | 344 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.798 | 0.759 | -0.498 | 0.468 | 344 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.766 | 0.683 | -0.649 | 0.387 | 344 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.746 | 0.602 | -0.731 | 0.358 | 344 |
| $$U$$, points at or above 30 mm | +0.902 | 0.798 | +0.147 | 0.669 | 242 |
| $$k$$, points at or above 30 mm | +0.468 | 0.802 | +0.364 | 0.343 | 242 |
| $$\theta$$, points at or above 30 mm | +0.944 | 1.000 | +0.041 | 1.000 | 242 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, points at or above 30 mm | +0.814 | 0.715 | -0.495 | 0.430 | 242 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, points at or above 30 mm | +0.821 | 0.636 | -0.583 | 0.351 | 242 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, points at or above 30 mm | +0.816 | 0.541 | -0.624 | 0.302 | 242 |
| $$V$$, lateral sign flipped (control) | +0.037 | 0.110 | — | 0.695 | 344 |
| $$U$$, approach column alone (control) | +0.861 | 0.846 | -0.205 | 0.599 | 344 |
| $$\theta$$, approach column alone (control) | +0.925 | 1.000 | -0.117 | 0.837 | 344 |
| $$U$$, y-symmetric ceiling (control) | +0.984 | 0.986 | +0.000 | 0.860 | 292 |
{: .scores }

{% include nomenclature-scores.md %}

</details>

- Normalisation: the tunnel\'s units: velocities by $$U_H$$ (1.3394 m/s measured, the Froude-scaled 13.39 m/s modelled), $$k$$ by $$U_H^2$$, temperature as theta = ($$T_f - T$$)/($$T_f - T_H$$) ($$T_f$$ = 45.01 degC, $$T_f - T_H$$ = 30.26 K), $$c^\ast = C/c_0$$ ($$c_0$$ = 1728 ppm) against the modelled ethylene mass fraction as ppm over the same $$c_0$$; hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units, concentration with one detection limit of $$10^{-3}$$ of the largest measured value
- Per-point values: [`/api/cases/L/pairs/umf-realizableKE.csv`]({{ '/api/cases/L/pairs/umf-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture MetaFOAM.Lib.Tests/TestAijCaseLUmfContainerE2E (9 x 14 cubes, heated floor, floor line source; urbanMicroclimateFoam, realizable k-ε, 754,940 air cells at Froude scale 100, 1500 air iterations, solved 2026-10-18); figures validation/plot\_cases\_jl\_umf.py

Notes:

- The scene is the tunnel at Froude scale 100 (lengths times 100, velocities times 10, temperatures unchanged), which keeps the bulk Richardson number (-0.034) and the tunnel\'s Kelvin values and does not keep Re.
- What the model does not represent: the gas\'s own heat and the buried slot (a mass rate into 624 whole cells, a strip 3 m wide), the tunnel\'s near-floor temperature drop (below the first cell), the measured velocity profile (UMF\'s inlet is a log law), the tunnel\'s no-slip side walls and ceiling (slip here), radiation (emissivity 0.01, effectively off) and the 10 mm raised block floor.
- 51 of the 344 points ($$z = 4\thinspace\mathrm{mm}$$, 0.4 m here) lie inside the first fine cell (0.75 m), a wall-function cell. The 242 points at or above 30 mm are scored separately.
- The street air is nearly stagnant in the model: the mean $$U/U_H$$ in the streets is 0.045 below 30 mm and 1.11 above 110 mm, against the tunnel\'s 0.297 and 1.068; the model\'s approach column differs from the tunnel\'s AF profile by up to 39 % above 30 mm (UMF\'s inlet is a log law, the tunnel\'s profile is not).
- The tracer is solved steady beside the flow, as three species of one flow. The outlet carried 0.86, 0.73 and 0.70 of the emission for $$\mathrm{Sc_t}$$ 0.3, 0.5 and 0.7, within the factor of two accepted as a check on the wiring. The largest modelled $$c^\ast$$ over the 344 points is in the source street for every species, at $$y = -0.12\thinspace\mathrm{m}$$ ($$\mathrm{Sc_t}$$ 0.3) and $$y = +0.18\thinspace\mathrm{m}$$ ($$\mathrm{Sc_t}$$ 0.5 and 0.7), against the tunnel\'s 1.929 at (-0.15, -0.12, 0.004).
- The air region ended at its 1500-iteration cap with the residualControl unmet (no \'solution converged\' line); at the last iteration the initial residuals were 2.6e-2 ($$U_y$$), 3.0e-2 (`p_rgh`) and 1.1e-3 to 2.0e-3 (the tracers).
- The tunnel is not y-symmetric although the array is: over 110 mirror pairs the mean \|U(y) - $$U$$(-y)\| is 0.143 $$U_H$$ in the tunnel and 0.058 $$U_H$$ in the model. $$V$$ is barely antisymmetric in the tunnel, so it cannot be scored as a pattern; the sign-flipped control shows what a wrong sign scores.
- The inlet\'s $$U_H$$ reaches the array within 20 %; the approach air is warmest at the floor; the street air near the floor is warmer than the approach air at H and cools with height; the street flow is slower than the flow above the array; every species emits and its largest value is in the source street.

<details markdown="block">
  <summary>How the scores are computed</summary>

- Scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

</details>

## Figures

Figures: [Cases J and L (UMF)]({{ '/validation/cases-jl/' | relative_url }}).
