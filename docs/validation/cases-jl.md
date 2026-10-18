---
title: "Cases J and L (UMF)"
parent: Validation
nav_order: 8
summary: "Eddy3D's buoyant microclimate engine (urbanMicroclimateFoam) on the 1:1:2 building and the 9 x 14 cube array, both on a heated floor with a tracer source"
description: "urbanMicroclimateFoam, an OpenFOAM 12 solver, against the wind tunnel for Case J (1:1:2 building) under two closures and Case L (9 x 14 cube array): velocity, turbulent kinetic energy, temperature and tracer concentration in an unstable boundary layer."
---

# Cases J and L, urbanMicroclimateFoam

Cases J and L are non-isothermal: a floor held at about 45 °C (45.8 °C in J, 45.0 °C in L) under a cooler approach flow (bulk Richardson number −0.086 in J, −0.034 in L), with an ethylene tracer released from the floor. The isothermal OpenFOAM 12 solver Eddy3D uses for the other cases cannot represent them, so Eddy3D solved them with its buoyant microclimate engine, urbanMicroclimateFoam (UMF, the Outdoor+ plugin), which is an OpenFOAM 12 solver developed at ETH Zurich and Empa (its engine ids are on the [Validation]({{ '/validation/' | relative_url }}) overview; Eddy3D owns none of its physics). Every score of each run, with the per-point files and the caveats recorded with the run, is on the [Case J]({{ '/cases/case-j/validation/' | relative_url }}) and [Case L]({{ '/cases/case-l/validation/' | relative_url }}) Validation pages. The isothermal OpenFOAM 12 engine is *pending* on both cases: it was not run.

## How these runs are scored

- **What each run is.** Solved on 2026-10-18. Case J: the 1:1:2 building on a floor 33.6 K warmer than the approach air at building height, 236,408 air cells, under UMF's two closures, realizable k-ε (the shipped one) and `buoyantKEpsilon` (which carries the buoyancy production the neutral closure lacks); two engine ids, `umf-realizableKE` and `umf-buoyantKEpsilon`. Case L: 126 cubes (14 rows × 9 columns), 754,940 air cells, realizable k-ε. The air region of every run stopped at its 1500-iteration cap with the residual control unmet; at the last iteration the initial residuals of U<sub>y</sub> and p\_rgh were of the order of 10⁻² and those of the tracers 10⁻³. Each case was solved on one mesh, with a steady tracer solved beside the flow as three species (turbulent Schmidt numbers 0.3, 0.5 and 0.7, all published).
- **Froude scale.** The production case writer cannot mesh a 0.16 m building, so each scene is the tunnel scaled by 62.5 (J) or 100 (L): lengths times the scale, velocities times its square root, temperatures unchanged. That keeps the Richardson number, Pr and the Kelvin values and not the Reynolds number. Every pair is in the tunnel's units: coordinates divided by the scale, velocities by the scene's U<sub>H</sub>, k by its square.
- **Temperature** is scored as the floor-referenced fraction θ = (T<sub>f</sub> − T)/(T<sub>f</sub> − T<sub>H</sub>), 0 at the floor and 1 in the approach air at the building height (the workbook's own normalisation); its FAC2 is 1.00 almost everywhere because θ lies between 0.4 and 1.1, so read R and the hit rate. The temperature errors in kelvin are in the files (`temperature.all`).
- **Concentration** is the measured C/c₀ (c₀ = 12.28 ppm in J, 1728 ppm in L) against the model's ethylene mass fraction as ppm over the same c₀, with one detection limit of 10⁻³ of the largest measured value.
- **The measured side** is the cleaned table. Case J's point 153 repeats point 1 (the crossing of two planes, identical values) and is left out, as Eddy3D's fixture does: 443 points. Eddy3D's scores were computed against the rounded CSVs; the scores here are recomputed from the per-point files, and the fixture's own scores are reproduced to 10⁻⁹ from the CSVs and its probes (80 scores of each J run, 48 of Case L).

## Case J: does the model agree?

{% include figure.html name="case-j-umf-agreement.png" alt="Case J, measured vs modelled velocity, k and temperature" caption="<strong>Figure 1.</strong> Case J under realizable k-ε (top) and buoyantKEpsilon (bottom): measured vs modelled U, W, k and the floor-referenced temperature θ." %}

| Quantity | R (rk-ε) | FAC2 | FB | R (bKε) | FAC2 | FB |
|---|---|---|---|---|---|---|
| U | +0.921 | 0.731 | +0.193 | +0.924 | 0.761 | +0.167 |
| V | +0.866 | 0.449 | — | +0.901 | 0.442 | — |
| W | +0.840 | 0.289 | — | +0.849 | 0.289 | — |
| k | +0.322 | 0.558 | −0.034 | +0.360 | 0.582 | −0.088 |
| θ | +0.922 | 1.000 | +0.120 | +0.920 | 0.998 | +0.127 |
| c\*, Sct 0.3 | +0.919 | 0.858 | +0.065 | +0.894 | 0.869 | −0.050 |
| c\*, Sct 0.5 | +0.905 | 0.847 | −0.162 | +0.869 | 0.840 | −0.274 |
| c\*, Sct 0.7 | +0.896 | 0.828 | −0.256 | +0.852 | 0.806 | −0.380 |
| c\*, Sct 0.3, without the near-source points | +0.874 | 0.760 | +0.240 | +0.829 | 0.757 | +0.052 |
| c\*, Sct 0.5, without the near-source points | +0.860 | 0.752 | +0.067 | +0.788 | 0.731 | −0.193 |
| c\*, Sct 0.7, without the near-source points | +0.848 | 0.728 | +0.025 | +0.755 | 0.709 | −0.292 |
{: .scores }

n is 443 (416 without the 27 points within a quarter of a building height of the source); rk-ε is realizable k-ε and bKε is buoyantKEpsilon. FB is positive when the model is low, and is left out (—) for a signed component whose measured and modelled means are not both positive.

- **The flow is reproduced in pattern and low in level.** U has R = 0.92 under both closures, FAC2 0.73 and 0.76, and the model is low (mean U/U<sub>H</sub> 0.465 and 0.477 against 0.564 measured). The deficit is largest in the wake (FB +0.36 and +0.29 in the near wake, +0.48 and +0.43 in the far wake, under rk-ε and bKε). The steady closures give a recirculation that is too long: reattachment at z/H = 0.25 and 0.025 is 1.35 H and 1.35 H (rk-ε) or 1.35 H and 1.56 H (bKε), against the measured 0.68 H and 0.80 H. Scored against the mean of each mirror pair, the measurement has R = 0.99 for U, so the tunnel's lack of y-symmetry is not what holds the model's R at 0.92; the +y half of the z/H = 0.25 plane is 11 % slower than the −y half (97 pairs, R 0.955).
- **k is not reproduced.** R is 0.32 and 0.36; the means are close (0.030 and 0.031 modelled, 0.029 measured), so the agreement in FB is not agreement in pattern.
- **The model is warmer than the tunnel.** θ has R = 0.92 and a hit rate of 0.82 and 0.81; in kelvin the mean bias is +3.46 K (rk-ε) and +3.63 K (bKε) with a root-mean-square error of 4.53 K and 4.80 K and R = 0.92. The model's first cell is 12 mm at tunnel scale, so the tunnel's 24 K drop between the floor and the first measurement at 3 mm lies inside it: near-floor temperature is a wall-function result.
- **The tracer pattern is correlated at every Schmidt number, and the bias changes sign.** R is 0.92 to 0.90 (rk-ε) and 0.89 to 0.85 (bKε) from Sct 0.3 to 0.7. Under rk-ε the model is low at Sct 0.3 (FB +0.065) and high at 0.5 and 0.7 (−0.162, −0.256); the modelled peak at the measured points is 275, 339 and 373 against a measured peak of 437, so the near-source points are low, not high as in Cases H and K. By region at Sct 0.5 under rk-ε: above the roof R = +0.78 and FAC2 0.33 (75 points), beside the building +0.82 and 0.40 (60), the near wake +0.90 and 0.75 (168), the far wake +0.89 and 0.82 (56). The 84 points upstream have R = −0.18 and FAC2 0.05: the tunnel measures a background of 0.018 c₀ on average (about 0.2 ppm, below the workbook's expanded uncertainty noted in the known data issues) where the model has almost none (a mean of 4 × 10⁻⁵ c₀ and a largest value of 1.4 × 10⁻³ at Sct 0.5 under rk-ε), so FAC2 there is small whatever the model does.
- **The two closures differ little in the flow and more in the tracer.** buoyantKEpsilon raises U's R from 0.921 to 0.924 and its FAC2 from 0.731 to 0.761, and k's R from 0.32 to 0.36. It lowers the tracer's R by 0.025 to 0.044 and moves FB down by 0.11 to 0.12: the modelled concentration is higher. This ranks two closures on one building, one mesh and a run capped at 1500 iterations; it is not a claim about the closures in general.

{% include figure.html name="case-j-umf-tracer.png" alt="Case J, measured vs modelled tracer concentration" caption="<strong>Figure 2.</strong> Case J, measured vs modelled c* at three turbulent Schmidt numbers under both closures. The concentration panels show the positive pairs within seven decades; the points within a quarter of a building height of the source are open." %}

## Case L: does the model agree?

{% include figure.html name="case-l-umf-agreement.png" alt="Case L, measured vs modelled" caption="<strong>Figure 3.</strong> Case L under realizable k-ε: measured vs modelled U, W, k, θ, V and c* at three turbulent Schmidt numbers, in the tunnel's units." %}

| Quantity | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| U | +0.918 | 0.608 | +0.268 | 0.506 | 344 |
| V | −0.037 | 0.291 | −0.795 | 0.747 | 344 |
| W | −0.027 | 0.183 | — | 0.762 | 344 |
| \|U\| | +0.898 | 0.674 | +0.206 | 0.515 | 344 |
| k | +0.145 | 0.584 | +0.635 | 0.244 | 344 |
| θ | +0.936 | 1.000 | +0.049 | 0.985 | 344 |
| c\*, Sct 0.3 | +0.798 | 0.759 | −0.498 | 0.468 | 344 |
| c\*, Sct 0.5 | +0.766 | 0.683 | −0.649 | 0.387 | 344 |
| c\*, Sct 0.7 | +0.746 | 0.602 | −0.731 | 0.358 | 344 |
| U, points at or above 30 mm | +0.902 | 0.798 | +0.147 | 0.669 | 242 |
| k, points at or above 30 mm | +0.468 | 0.802 | +0.364 | 0.343 | 242 |
| θ, points at or above 30 mm | +0.944 | 1.000 | +0.041 | 1.000 | 242 |
| c\*, Sct 0.3, points at or above 30 mm | +0.814 | 0.715 | −0.495 | 0.430 | 242 |
| c\*, Sct 0.5, points at or above 30 mm | +0.821 | 0.636 | −0.583 | 0.351 | 242 |
| c\*, Sct 0.7, points at or above 30 mm | +0.816 | 0.541 | −0.624 | 0.302 | 242 |
| V, lateral sign flipped (control) | +0.037 | 0.110 | — | 0.695 | 344 |
| U, approach column alone (control) | +0.861 | 0.846 | −0.205 | 0.599 | 344 |
| θ, approach column alone (control) | +0.925 | 1.000 | −0.117 | 0.837 | 344 |
| U, y-symmetric ceiling (control) | +0.984 | 0.986 | +0.000 | 0.860 | 292 |
{: .scores }

The 51 points at z = 4 mm lie inside the model's first fine cell (0.75 m, 0.4 m at 1:100), a wall-function cell; the 242 points at or above 30 mm are scored separately. FB is positive when the model is low.

- **The streamwise flow and the temperature follow the tunnel; the streets do not.** U has R = 0.92 and the model is low (mean U/U<sub>H</sub> 0.499 against 0.654 measured); at or above 30 mm R is 0.90 and FAC2 0.80. The model beats the undisturbed approach column on R (U: 0.918 against 0.861; θ: 0.936 against 0.925), the number a model of the array has to beat. But the street air is nearly stagnant: the model's mean U/U<sub>H</sub> in the streets is 0.045 below 30 mm and 1.11 above 110 mm, against the tunnel's 0.297 and 1.068 (as Eddy3D's fixture quotes them). V and W carry no pattern: R is −0.04 and −0.03, and with the sign of V flipped it is +0.04.
- **k is low and weakly correlated:** R = 0.15 (0.47 at or above 30 mm), FB +0.64.
- **The model is warmer by 1.2 K on average:** θ has R = 0.94 and a hit rate of 0.99; the mean bias is +1.17 K, the mean absolute error 1.59 K and the root-mean-square error 2.11 K.
- **The tracer is over-predicted and the pattern is correlated.** R is 0.80, 0.77 and 0.75 from Sct 0.3 to 0.7 (0.81 to 0.82 at or above 30 mm), FAC2 falls from 0.76 to 0.60 and FB from −0.50 to −0.73. The largest modelled c\* is 3.3, 4.0 and 5.0 (at y = −0.12, +0.18 and +0.18 m, in the source street) against the tunnel's 1.93 at (−0.15, −0.12, 0.004).

## What was not checked

- No second mesh, no longer iteration count and no transient run: the air region reached its cap with residuals near 10⁻², so these numbers are those of an unconverged steady solve on one mesh.
- The tracer's mass balance does not close: the outlet carried 0.62 to 0.95 of the emission in Case J (0.89, 0.75 and 0.62 under rk-ε; 0.95, 0.84 and 0.73 under bKε, for Sct 0.3, 0.5 and 0.7) and 0.86, 0.73 and 0.70 in Case L. Eddy3D's fixture accepts a factor of two, a wiring detector and not a convergence claim; why a part of the emission is not at the outlet was not investigated here.
- The Froude-scaled scenes do not keep the Reynolds number (1.6 × 10⁴ in the tunnel of Case J, 8 × 10⁶ in the scene), so the wall-function regime of the model is not the tunnel's.
- Not represented (Eddy3D's list): the release momentum and the gas's own heat, the tunnel's side walls and ceiling (slip here), radiation (emissivity 0.01, effectively off), and in Case L the 10 mm raised block floor and the measured velocity profile (UMF's inlet is a log law; the model's approach column differs from the tunnel's by up to 39 % above 30 mm). In Case J the measured 4 K gradient up the building's walls is not modelled.
- OpenLB, FluidX3D and the ML surrogate have not been run on either case.
