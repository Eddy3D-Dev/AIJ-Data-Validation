---
title: "Validation"
parent: "Case K — 9 x 9 cube array, point source"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case K — 9 x 9 cube array, point source: Eddy3D's scores against the tunnel data, by engine."
---

# Case K: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

*Scored* means a run exists and its scores are below, not that it agrees. How to read them is on [the reading page]({{ '/validation/cases-gk/' | relative_url }}); the [Validation]({{ '/validation/' | relative_url }}) overview says what each status means and why an engine is *not comparable*.

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor)

Quantity: U, V, W over the stated U\_H = 2.33 m/s and k over U\_H^2 (split fibre, 203 points); c\* = C/c0 (c0 = q/(U\_H H^2) = 429.2 ppm) against the model\'s c U\_H H^2/Q for turbulent Schmidt numbers 0.3, 0.5 and 0.7; the four points within one cube height of the source are scored with and without.

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| U | +0.958 | 0.586 | +0.594 | 0.123 | 203 |
| V | -0.151 | 0.054 | — | 0.901 | 203 |
| W | +0.573 | 0.143 | — | 0.685 | 203 |
| k | +0.330 | 0.044 | +1.201 | 0.005 | 203 |
| c\*, Sct 0.3 | +0.953 | 0.793 | -0.690 | 0.458 | 203 |
| c\*, Sct 0.5 | +0.951 | 0.685 | -0.875 | 0.163 | 203 |
| c\*, Sct 0.7 | +0.950 | 0.394 | -0.983 | 0.099 | 203 |
| c\*, Sct 0.3, without the 4 near-source points | +0.923 | 0.799 | -0.218 | 0.467 | 199 |
| c\*, Sct 0.5, without the 4 near-source points | +0.941 | 0.698 | -0.430 | 0.161 | 199 |
| c\*, Sct 0.7, without the 4 near-source points | +0.923 | 0.402 | -0.561 | 0.101 | 199 |
| U, y-symmetric ceiling (control) | +1.000 | 1.000 | +0.000 | 1.000 | 203 |
| c\*, y-symmetric ceiling (control) | +0.997 | 0.995 | +0.000 | 0.793 | 203 |
{: .scores }

Recorded with this run:

- The inflow is the measured approach profile (3.23 m/s at 0.2 m, z0 fitted to 13.5 mm), not the stated U\_H = 2.33 m/s, which is not on that profile: the solved U at z = H is 1.97 m/s, 0.85 of the stated U\_H (the fixture\'s inflow.U.modelAtH). Measured and modelled velocities are both divided by 2.33 m/s, so the modelled velocity sits under the measured mean.
- The inlet k from that log law, u\*^2/sqrt(Cmu) = 0.77 m^2/s^2, is about 1.7 times the tunnel\'s 0.33 to 0.45 (the fixture\'s own remark).
- The first measurement point is the source location: the four points within one cube height of the floor outlet hold the four largest c\* (8.73, 5.31, 3.02 and 2.86 against 1.03 for the next), and the model\'s source is the 4 cells (0.75 m across) that a 0.44 m square cuts, not the 5 mm outlet. Those four points are scored with and without.
- 47 of the 203 points (the z = 4 mm plane, 0.4 m at 1:100) lie inside the first ground cell (0.735 m): their modelled values are that cell\'s, pulled toward the wall\'s zero by the point interpolation.
- The measured plume is not y-symmetric (C at -y exceeds C at +y at 74 of 74 mirror pairs; the fixture puts its lateral centroid 0.011 to 0.017 m toward -y at every station) and the solve is. The \'y-symmetric ceiling\' controls score the measurement against the mean of each mirror pair, the best a y-symmetric model can do on this file.
- V has a constant offset and almost no antisymmetric part, so it does not score the flow\'s divergence; a model with V = 0 everywhere hits 0.91 of the points at W = 0.05 U\_H, so V\'s hit rate says nothing.
- The solve stopped at the 3000-iteration limit with the residualControl unmet (no \'solution converged\' line); the epsilon initial residual at the last iteration was 7e-3.
- The fixture\'s structure checks passed. The air over the roofs outruns the street along the wind, which outruns the cavity across it; the plume leaves the source, is clean 1 to 1.5 H ahead of the array, decays through four cavities and is cleaner over the roofs than in them; the solved velocity is y-symmetric to twice the tunnel\'s own mirror-pair difference. They set no band on the statistics.

U, V, W by the stated U\_H = 2.33 m/s and k by U\_H^2, the same divisor on both sides; c\* is the measured C/c0 (c0 = q/(U\_H H^2) = 429.2 ppm) against the modelled c U\_H H^2/Q (full scale, Q = 1 kg/s) for turbulent Schmidt numbers 0.3, 0.5 and 0.7, with one detection limit of 10^-3 of the largest measured value; hit rate D = 0.25, W = 0.05 in U\_H. Per-point values: [`/api/cases/K/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/K/pairs/openfoam12-realizableKE.csv' | relative_url }}). Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseKContainerE2E (9 x 9 cubes, floor point source, 1:100; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 972,637 cells, solved 2026-10-18); figures validation/plot\_cases\_gk\_openfoam.py; scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

## Figures

The figures for these runs are shown once, beside their reading: [Cases G and K (OpenFOAM)]({{ '/validation/cases-gk/' | relative_url }}).
