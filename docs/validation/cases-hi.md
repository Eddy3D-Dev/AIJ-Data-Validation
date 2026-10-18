---
title: "Cases H and I (OpenFOAM)"
parent: Validation
nav_order: 6
summary: "OpenFOAM 12 on the 1:1:2 building with a floor source and the cube with a roof source: velocity, k and tracer concentration"
description: "OpenFOAM 12 against the tunnel for Case H (1:1:2 building, floor point source) and Case I (cube, roof point source): velocity, turbulent kinetic energy and tracer concentration, and three turbulence closures on Case I."
---

# Cases H and I, OpenFOAM 12

The reading of the OpenFOAM 12 runs on the 1:1:2 building with a floor point source (Case H) and on the cube with a roof point source (Case I). They are the two cases with a tracer-gas concentration that Eddy3D has solved so far. Every score of each run, with the per-point files, is on the [Case H]({{ '/cases/case-h/validation/' | relative_url }}) and [Case I]({{ '/cases/case-i/validation/' | relative_url }}) Validation pages.

## How these runs are scored

- Both are Eddy3D production runs, realizable k-ε at numerics level 3 and 3000 iterations, at 1:100 (H) and 1:60 (I), with the probe at the tunnel's own coordinates. Case I was also solved with standard k-ε and with k-ω SST on the same mesh.
- Velocities are divided by U_H, k by U_H². Each side uses its own U_H: the tunnel's (H 3.226 m/s, I 1.7 m/s) for the measurement, the value the solve was driven with (H 3.23 m/s, I 1.7 m/s) for the model.
- Concentration is the cleaned table's C/c₀ (c₀ = 45.18 ppm in H, 39.22 ppm in I) against the model's c\* = c U_H H²/Q. The turbulent Schmidt number is a model parameter, so c\* is scored at 0.3, 0.5 and 0.7; the figures show 0.5.
- The measured values are the cleaned tables', which are the legacy workbooks' numbers at full precision. Eddy3D's own scores were computed against the published CSVs, so they differ from these in the third digit. The scores here are recomputed from the per-point files by `validation/dispersion_metrics.py`, which reproduces Eddy3D's metrics. Concentration is scored with one detection limit, 10⁻³ of the largest measured value.

## Where was it measured?

{% include figure.html name="case-h-layout.png" alt="Measurement lines and planes, Case H" caption="<strong>Figure 1.</strong> Case H, measurement lines and planes: A vertical profiles, y/H = 0; B plane z/H = 0.0625; C plane z/H = 0.25; D plane z/H = 0.5. Positions in multiples of H." %}

{% include figure.html name="case-i-layout.png" alt="Measurement lines and planes, Case I" caption="<strong>Figure 2.</strong> Case I, measurement lines and planes: A concentration, vertical profiles, y/H = 0; B concentration, plane z/H = 0; C velocity, vertical profiles, y/H = 0; D velocity, plane z/H = 0.5. Positions in multiples of H; panels c and d: x/H = -2 to 5." %}

## Does the model agree?

{% include figure.html name="cases-hi-openfoam-agreement.png" alt="Measured vs modelled, Cases H and I" caption="<strong>Figure 3.</strong> Measured vs modelled U, W, k and c*, Cases H (top) and I (bottom), realizable k-ε; the dots take the colour of the line or plane they were measured on, as in Figures 1 and 2. The concentration panels show the positive pairs only." %}

Realizable k-ε, normalised by U_H as above.

| Quantity | R | FAC2 | FB | Hit rate |
|---|---|---|---|---|
| H — U | +0.897 | 0.609 | +0.355 | 0.446 |
| H — V | +0.935 | 0.355 | −0.432 | 0.682 |
| H — W | +0.887 | 0.314 | +2.758 | 0.713 |
| H — k | +0.107 | 0.570 | +0.514 | 0.305 |
| H — c\*, Sct 0.3 | +0.954 | 0.694 | −0.597 | 0.493 |
| H — c\*, Sct 0.5 | +0.951 | 0.615 | −0.825 | 0.507 |
| H — c\*, Sct 0.7 | +0.946 | 0.588 | −0.934 | 0.493 |
| I — U | +0.998 | 0.879 | +0.020 | 0.813 |
| I — V | +0.985 | 0.895 | −2.016 | 1.000 |
| I — W | +0.972 | 0.659 | −0.049 | 0.967 |
| I — k | +0.905 | 0.923 | +0.106 | 0.582 |
| I — c\*, Sct 0.3 | +0.922 | 0.360 | +0.398 | 0.106 |
| I — c\*, Sct 0.5 | +0.940 | 0.475 | +0.083 | 0.284 |
| I — c\*, Sct 0.7 | +0.946 | 0.477 | −0.100 | 0.291 |
{: .scores }

FB is positive when the model is low. Reading these honestly:

- **Case H: the mean flow is reproduced, k is not.** R is 0.90, 0.94 and 0.89 for U, V and W. FAC2 on V and W is low by construction, because those components change sign (see [Cases A and B]({{ '/validation/cases-ab/' | relative_url }})); W's FB of +2.76 is a near-zero mean, so read R and the hit rate. k has R = 0.11 and the model is low (FB +0.51): the pattern of the tunnel's turbulence at the measured points is not followed.
- **Case H: the concentration is well correlated and over-predicted.** R is 0.95 at every Schmidt number, FB is −0.83 at 0.5, and the modelled c\* at the measured points peaks at 238 against a measured peak of 66. A higher turbulent Schmidt number raises the modelled concentration further (FB −0.60, −0.83, −0.93 for 0.3, 0.5, 0.7) and lowers FAC2 from 0.69 to 0.59.
- **Case I: velocity and k agree closely.** U has R = 1.00 and FAC2 0.88, W has R = 0.97, k has R = 0.91 and FAC2 0.92. V is scored at the 38 points off the y = 0 plane: on the plane the workbook holds numerical zeros, which are not a measurement, so those points are left out. Its FB of −2.0 is the near-zero mean again; its R is 0.99.
- **Case I: the concentration is well correlated, with a wide scatter.** R is 0.92 to 0.95, but FAC2 stays below 0.5, and the scatter at low concentration is visible in panel h. The bias changes sign with the Schmidt number: the model is low at 0.3 (FB +0.40), nearly unbiased at 0.5 (+0.08) and high at 0.7 (−0.10). Case H over-predicts at all three, so the Schmidt number that suits one case does not suit the other.

## Does the turbulence closure matter?

{% include figure.html name="case-i-openfoam-closures.png" alt="Case I under three turbulence closures" caption="<strong>Figure 4.</strong> Case I under standard k-ε, realizable k-ε and k-ω SST on one mesh, dots coloured as in Figure 2: measured vs modelled U, k and c* (Sct 0.5)." %}

| Closure | U R | U FAC2 | k R | k FAC2 | k FB | c\* (Sct 0.5) R | c\* FAC2 | c\* FB |
|---|---|---|---|---|---|---|---|---|
| standard k-ε | +0.990 | 0.846 | +0.870 | 0.912 | −0.037 | +0.955 | 0.519 | −0.035 |
| realizable k-ε | +0.998 | 0.879 | +0.905 | 0.923 | +0.106 | +0.940 | 0.475 | +0.083 |
| k-ω SST | +0.992 | 0.879 | +0.880 | 0.396 | +0.495 | +0.466 | 0.403 | −0.153 |
{: .scores }

- **The mean velocity does not tell the closures apart.** R is 0.99 to 1.00 and FAC2 0.85 to 0.88 under all three.
- **k and the concentration do.** The two k-ε closures keep k within a factor of two at more than 90 % of the points and give a concentration with R of 0.94 to 0.96. Under k-ω SST FAC2 for k falls to 0.40, with the model low (FB +0.49), and the concentration's R falls to 0.47. The mean k/U_H² of that run's approach profile is 0.0006, against 0.0075 under both k-ε closures, so its turbulence is lower from the inlet on.
- **The reattachment length differs too:** L_r/H is 2.23 (standard k-ε), 2.51 (realizable k-ε) and 2.68 (k-ω SST).

This ranks three closures on one cube, one mesh and this release's numerics. It is not a claim about the closures in general.
