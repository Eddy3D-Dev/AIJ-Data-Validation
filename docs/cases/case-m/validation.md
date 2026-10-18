---
title: "Validation"
parent: "Case M — TPU Atsugi campus"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case M — TPU Atsugi campus: Eddy3D's scores against the tunnel data, by engine."
---

# Case M: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

*Scored* means a run exists and its scores are below, not that it agrees. How to read them is on [the reading page]({{ '/validation/cases-fm/' | relative_url }}); the [Validation]({{ '/validation/' | relative_url }}) overview says what each status means and why an engine is *not comparable*.

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration sct03

Quantity: U, V, W and k at the 15 points of the tunnel\'s WD 180 run over the tunnel\'s U\_R = 4.08 m/s (measured) and over the solved speed at the reference mast (modelled; U\_R is defined at the mast), and the dimensionless concentration c\* = C/c0 (c0 = q/(U\_R H\_R^2) = 132.5 ppm) against the model\'s c U\_R H\_R^2/Q for turbulent Schmidt number 0.3; the field campaign (18 runs) is recorded beside it.

<details markdown="block">
  <summary>All 16 headline scores</summary>

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| c\* | +0.412 | 0.200 | +1.396 | 0.133 | 15 |
| c\*, over the imposed speed at the mast\'s height (3.934 m/s) | +0.412 | 0.200 | +1.480 | 0.067 | 15 |
| c\*, over the tunnel\'s U\_R = 4.08 m/s | +0.412 | 0.200 | +1.464 | 0.067 | 15 |
| c\*, points turned 180° about the source (control) | -0.050 | 0.071 | +2.000 | 0.071 | 14 |
| c\*, points mirrored across the plume axis (control) | +0.675 | 0.467 | +0.321 | 0.133 | 15 |
| c\*, tunnel WD 175 as a model of its WD 180 (control) | +0.932 | 0.733 | +0.401 | 0.267 | 15 |
| c\*, tunnel WD 185 as a model of its WD 180 (control) | +0.976 | 0.800 | -0.117 | 0.533 | 15 |
| c\*, mean of the tunnel\'s WD 175 and WD 185 as a model of its WD 180 (control) | +0.998 | 1.000 | +0.111 | 0.867 | 15 |
| c\* against the field\'s geometric mean (10 runs) | +0.464 | 0.067 | +1.012 | 0.000 | 15 |
| c\*, tunnel WD 180 as a model of the field\'s geometric mean (control) | +0.984 | 0.600 | -0.593 | 0.000 | 15 |
| U | +0.708 | 0.267 | +1.460 | 0.267 | 15 |
| V | +0.731 | 0.333 | — | 0.133 | 15 |
| V, sign flipped (control) | -0.731 | 0.067 | -0.616 | 0.133 | 15 |
| W | +0.181 | 0.267 | — | 0.733 | 15 |
| \|U\| | +0.601 | 0.733 | +0.185 | 0.400 | 15 |
| k | +0.446 | 0.133 | +1.131 | 0.067 | 15 |
{: .scores }

</details>

Recorded with this run:

- One heading and one steady solve: WD 180, the only heading with measured velocities. The tunnel\'s own neighbouring headings are the noise floor of a single heading: its WD 175 scored as a model of its WD 180 gives R +0.93, FAC2 0.73, FB +0.40, its WD 185 R +0.98, FAC2 0.80, FB -0.12, and the mean of the two R +1.00, FAC2 1.00, FB +0.11; 8 of the 15 points change by more than a factor of two between WD 175 and WD 185 (computed from the pairs).
- The turbulent Schmidt number does not change the flow: the three runs of this case are one solve with three passive tracers, so U, V, W and k are the same in all three and only c\* differs.
- U\_R is the solved speed at the reference mast, 4.686 m/s, which is 1.19 of the tabulated inlet\'s speed at the mast\'s elevation (3.934 m/s) and 1.15 of the tunnel\'s 4.08 m/s. Over the imposed speed c\* scores FB +1.48 and over 4.08 m/s FB +1.46, against +1.40 over the solved speed.
- The model is not the tunnel: a cylinder of 540 m radius and 240 m height on the terrain sheet, the tabulated approach profile over a smooth floor, none of the tunnel\'s side walls (at ±360 m) and 600 m ceiling (blockage 5 % in the fixture\'s count); the 6 mm outlet is 3.6 m at 1:600, and the source here is a 4 m cube on the ground (a zone of 20 cells, 2 m surface cells), 1 kg/s as a volume source with no exit momentum. The 15 points are 3 m above the ground.
- The structure the fixture first asserted is recorded: the three points nearest the source carry more than the two far downwind ones in this run (0.26 against 0.11), where the tunnel\'s are 2.52 against 0.21. The tunnel obeys it by a factor of about twelve and the model by less (Sct 0.7 reverses it), which Eddy3D reads as a finding about where the model puts the plume and not as a wrong bar: a probe repeated at full precision moved no c\* value by more than 0.003. The peak c\* is 1.27 against 3.04 measured, and 3 of the five highest points are shared.
- Controls on the same solution: the 15 points turned 180° about the source score R -0.05, FAC2 0.07, FB +2.00 (n 14; the model\'s mean over those points is 7.3e-06 against 0.186 at the real ones: the tracer goes downwind), and the points mirrored across the plume axis score R +0.68, FAC2 0.47, FB +0.32, better than the real points\' R +0.41, FAC2 0.20, FB +1.40: the modelled plume is displaced sideways against the tunnel\'s.
- The field campaign (18 runs) is recorded beside the tunnel, not asserted: the 10 runs within 10° of 180 at 3 m/s or more, each with its own U\_R and q and H\_R = 41 m as the cleaned table states (the fixture divides by 40.8 m, a 1 % difference). The model against the field\'s geometric mean scores R +0.46, FAC2 0.07, FB +1.01, and lies inside the field\'s minimum-maximum range at 2 of 15 points; the tunnel\'s WD 180 against the same mean scores R +0.98, FAC2 0.60, FB -0.59; the spread of the field at point 1 is a factor of 4.5.
- The velocity at the 15 points: the mean U/U\_R is 0.026 modelled against 0.164 measured. FB is not defined for V and W (their means are not both positive); V correlates at R +0.73 and flipping its sign gives -0.73.
- The solve ran to its 3000-iteration limit with the residualControl unmet (no \'solution converged\' line); the initial residuals at the last iteration were U\_x 6.1e-04, U\_z 6.9e-04, p 1.0e-04, epsilon 1.9e-02, k 1.6e-04 and the tracers 8.1e-06 to 1.1e-05. checkMesh: Mesh OK. 1,394,053 cells. The first solve of this case was killed by the container runtime for memory (exit 137) and the solve was run again alone; the scores are of the second. Its tracer probe, which printed six decimals, was replaced by a probe of the same solved study at seven significant digits (no c\* value moved by more than 0.003, Eddy3D\'s account).

U, V, W and k at the 15 points over the tunnel\'s U\_R = 4.08 m/s on the measurement and over the solved speed at the reference mast on the model (U\_R is defined at the mast), k over U\_R^2; c\* = C/c0 (c0 = q/(U\_R H\_R^2) = 132.5 ppm) against the model\'s c U\_R H\_R^2/Q (H\_R = 0.068 m x 600, Q = 1 kg/s) for turbulent Schmidt number 0.3, with one detection limit of 10^-3 of the largest measured value; hit rate D = 0.25, W = 0.05 in those units; the Schmidt numbers are three runs on one flow, published side by side. Per-point values: [`/api/cases/M/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/M/pairs/openfoam12-realizableKE.csv' | relative_url }}). Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseMContainerE2E (WD 180, the default) (TPU Atsugi campus, 1:600, tunnel WD 180, turbulent Schmidt number 0.3; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 1,394,053 cells, solved 2026-10-18); figures validation/plot\_cases\_fm\_openfoam.py; scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration sct05

Quantity: U, V, W and k at the 15 points of the tunnel\'s WD 180 run over the tunnel\'s U\_R = 4.08 m/s (measured) and over the solved speed at the reference mast (modelled; U\_R is defined at the mast), and the dimensionless concentration c\* = C/c0 (c0 = q/(U\_R H\_R^2) = 132.5 ppm) against the model\'s c U\_R H\_R^2/Q for turbulent Schmidt number 0.5; the field campaign (18 runs) is recorded beside it.

<details markdown="block">
  <summary>All 16 headline scores</summary>

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| c\* | +0.251 | 0.200 | +1.524 | 0.133 | 15 |
| c\*, over the imposed speed at the mast\'s height (3.934 m/s) | +0.251 | 0.133 | +1.592 | 0.067 | 15 |
| c\*, over the tunnel\'s U\_R = 4.08 m/s | +0.251 | 0.200 | +1.579 | 0.133 | 15 |
| c\*, points turned 180° about the source (control) | -0.058 | 0.071 | +2.000 | 0.071 | 14 |
| c\*, points mirrored across the plume axis (control) | +0.655 | 0.400 | +0.220 | 0.333 | 15 |
| c\*, tunnel WD 175 as a model of its WD 180 (control) | +0.932 | 0.733 | +0.401 | 0.267 | 15 |
| c\*, tunnel WD 185 as a model of its WD 180 (control) | +0.976 | 0.800 | -0.117 | 0.533 | 15 |
| c\*, mean of the tunnel\'s WD 175 and WD 185 as a model of its WD 180 (control) | +0.998 | 1.000 | +0.111 | 0.867 | 15 |
| c\* against the field\'s geometric mean (10 runs) | +0.285 | 0.067 | +1.202 | 0.000 | 15 |
| c\*, tunnel WD 180 as a model of the field\'s geometric mean (control) | +0.984 | 0.600 | -0.593 | 0.000 | 15 |
| U | +0.708 | 0.267 | +1.460 | 0.267 | 15 |
| V | +0.731 | 0.333 | — | 0.133 | 15 |
| V, sign flipped (control) | -0.731 | 0.067 | -0.616 | 0.133 | 15 |
| W | +0.181 | 0.267 | — | 0.733 | 15 |
| \|U\| | +0.601 | 0.733 | +0.185 | 0.400 | 15 |
| k | +0.446 | 0.133 | +1.131 | 0.067 | 15 |
{: .scores }

</details>

Recorded with this run:

- One heading and one steady solve: WD 180, the only heading with measured velocities. The tunnel\'s own neighbouring headings are the noise floor of a single heading: its WD 175 scored as a model of its WD 180 gives R +0.93, FAC2 0.73, FB +0.40, its WD 185 R +0.98, FAC2 0.80, FB -0.12, and the mean of the two R +1.00, FAC2 1.00, FB +0.11; 8 of the 15 points change by more than a factor of two between WD 175 and WD 185 (computed from the pairs).
- The turbulent Schmidt number does not change the flow: the three runs of this case are one solve with three passive tracers, so U, V, W and k are the same in all three and only c\* differs.
- U\_R is the solved speed at the reference mast, 4.686 m/s, which is 1.19 of the tabulated inlet\'s speed at the mast\'s elevation (3.934 m/s) and 1.15 of the tunnel\'s 4.08 m/s. Over the imposed speed c\* scores FB +1.59 and over 4.08 m/s FB +1.58, against +1.52 over the solved speed.
- The model is not the tunnel: a cylinder of 540 m radius and 240 m height on the terrain sheet, the tabulated approach profile over a smooth floor, none of the tunnel\'s side walls (at ±360 m) and 600 m ceiling (blockage 5 % in the fixture\'s count); the 6 mm outlet is 3.6 m at 1:600, and the source here is a 4 m cube on the ground (a zone of 20 cells, 2 m surface cells), 1 kg/s as a volume source with no exit momentum. The 15 points are 3 m above the ground.
- The structure the fixture first asserted is recorded: the three points nearest the source carry more than the two far downwind ones in this run (0.11 against 0.10), where the tunnel\'s are 2.52 against 0.21. The tunnel obeys it by a factor of about twelve and the model by less (Sct 0.7 reverses it), which Eddy3D reads as a finding about where the model puts the plume and not as a wrong bar: a probe repeated at full precision moved no c\* value by more than 0.003. The peak c\* is 1.37 against 3.04 measured, and 3 of the five highest points are shared.
- Controls on the same solution: the 15 points turned 180° about the source score R -0.06, FAC2 0.07, FB +2.00 (n 14; the model\'s mean over those points is 9.2e-06 against 0.143 at the real ones: the tracer goes downwind), and the points mirrored across the plume axis score R +0.65, FAC2 0.40, FB +0.22, better than the real points\' R +0.25, FAC2 0.20, FB +1.52: the modelled plume is displaced sideways against the tunnel\'s.
- The field campaign (18 runs) is recorded beside the tunnel, not asserted: the 10 runs within 10° of 180 at 3 m/s or more, each with its own U\_R and q and H\_R = 41 m as the cleaned table states (the fixture divides by 40.8 m, a 1 % difference). The model against the field\'s geometric mean scores R +0.28, FAC2 0.07, FB +1.20, and lies inside the field\'s minimum-maximum range at 2 of 15 points; the tunnel\'s WD 180 against the same mean scores R +0.98, FAC2 0.60, FB -0.59; the spread of the field at point 1 is a factor of 4.5.
- The velocity at the 15 points: the mean U/U\_R is 0.026 modelled against 0.164 measured. FB is not defined for V and W (their means are not both positive); V correlates at R +0.73 and flipping its sign gives -0.73.
- The solve ran to its 3000-iteration limit with the residualControl unmet (no \'solution converged\' line); the initial residuals at the last iteration were U\_x 6.1e-04, U\_z 6.9e-04, p 1.0e-04, epsilon 1.9e-02, k 1.6e-04 and the tracers 8.1e-06 to 1.1e-05. checkMesh: Mesh OK. 1,394,053 cells. The first solve of this case was killed by the container runtime for memory (exit 137) and the solve was run again alone; the scores are of the second. Its tracer probe, which printed six decimals, was replaced by a probe of the same solved study at seven significant digits (no c\* value moved by more than 0.003, Eddy3D\'s account).

U, V, W and k at the 15 points over the tunnel\'s U\_R = 4.08 m/s on the measurement and over the solved speed at the reference mast on the model (U\_R is defined at the mast), k over U\_R^2; c\* = C/c0 (c0 = q/(U\_R H\_R^2) = 132.5 ppm) against the model\'s c U\_R H\_R^2/Q (H\_R = 0.068 m x 600, Q = 1 kg/s) for turbulent Schmidt number 0.5, with one detection limit of 10^-3 of the largest measured value; hit rate D = 0.25, W = 0.05 in those units; the Schmidt numbers are three runs on one flow, published side by side. Per-point values: [`/api/cases/M/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/M/pairs/openfoam12-realizableKE.csv' | relative_url }}). Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseMContainerE2E (WD 180, the default) (TPU Atsugi campus, 1:600, tunnel WD 180, turbulent Schmidt number 0.5; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 1,394,053 cells, solved 2026-10-18); figures validation/plot\_cases\_fm\_openfoam.py; scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration sct07

Quantity: U, V, W and k at the 15 points of the tunnel\'s WD 180 run over the tunnel\'s U\_R = 4.08 m/s (measured) and over the solved speed at the reference mast (modelled; U\_R is defined at the mast), and the dimensionless concentration c\* = C/c0 (c0 = q/(U\_R H\_R^2) = 132.5 ppm) against the model\'s c U\_R H\_R^2/Q for turbulent Schmidt number 0.7; the field campaign (18 runs) is recorded beside it.

<details markdown="block">
  <summary>All 16 headline scores</summary>

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| c\* | +0.198 | 0.133 | +1.579 | 0.133 | 15 |
| c\*, over the imposed speed at the mast\'s height (3.934 m/s) | +0.198 | 0.133 | +1.640 | 0.067 | 15 |
| c\*, over the tunnel\'s U\_R = 4.08 m/s | +0.198 | 0.133 | +1.628 | 0.133 | 15 |
| c\*, points turned 180° about the source (control) | -0.058 | 0.071 | +2.000 | 0.071 | 14 |
| c\*, points mirrored across the plume axis (control) | +0.650 | 0.400 | +0.180 | 0.333 | 15 |
| c\*, tunnel WD 175 as a model of its WD 180 (control) | +0.932 | 0.733 | +0.401 | 0.267 | 15 |
| c\*, tunnel WD 185 as a model of its WD 180 (control) | +0.976 | 0.800 | -0.117 | 0.533 | 15 |
| c\*, mean of the tunnel\'s WD 175 and WD 185 as a model of its WD 180 (control) | +0.998 | 1.000 | +0.111 | 0.867 | 15 |
| c\* against the field\'s geometric mean (10 runs) | +0.224 | 0.067 | +1.287 | 0.000 | 15 |
| c\*, tunnel WD 180 as a model of the field\'s geometric mean (control) | +0.984 | 0.600 | -0.593 | 0.000 | 15 |
| U | +0.708 | 0.267 | +1.460 | 0.267 | 15 |
| V | +0.731 | 0.333 | — | 0.133 | 15 |
| V, sign flipped (control) | -0.731 | 0.067 | -0.616 | 0.133 | 15 |
| W | +0.181 | 0.267 | — | 0.733 | 15 |
| \|U\| | +0.601 | 0.733 | +0.185 | 0.400 | 15 |
| k | +0.446 | 0.133 | +1.131 | 0.067 | 15 |
{: .scores }

</details>

Recorded with this run:

- One heading and one steady solve: WD 180, the only heading with measured velocities. The tunnel\'s own neighbouring headings are the noise floor of a single heading: its WD 175 scored as a model of its WD 180 gives R +0.93, FAC2 0.73, FB +0.40, its WD 185 R +0.98, FAC2 0.80, FB -0.12, and the mean of the two R +1.00, FAC2 1.00, FB +0.11; 8 of the 15 points change by more than a factor of two between WD 175 and WD 185 (computed from the pairs).
- The turbulent Schmidt number does not change the flow: the three runs of this case are one solve with three passive tracers, so U, V, W and k are the same in all three and only c\* differs.
- U\_R is the solved speed at the reference mast, 4.686 m/s, which is 1.19 of the tabulated inlet\'s speed at the mast\'s elevation (3.934 m/s) and 1.15 of the tunnel\'s 4.08 m/s. Over the imposed speed c\* scores FB +1.64 and over 4.08 m/s FB +1.63, against +1.58 over the solved speed.
- The model is not the tunnel: a cylinder of 540 m radius and 240 m height on the terrain sheet, the tabulated approach profile over a smooth floor, none of the tunnel\'s side walls (at ±360 m) and 600 m ceiling (blockage 5 % in the fixture\'s count); the 6 mm outlet is 3.6 m at 1:600, and the source here is a 4 m cube on the ground (a zone of 20 cells, 2 m surface cells), 1 kg/s as a volume source with no exit momentum. The 15 points are 3 m above the ground.
- The structure the fixture first asserted is recorded: the three points nearest the source carry less than the two far downwind ones in this run (0.05 against 0.09), where the tunnel\'s are 2.52 against 0.21. The tunnel obeys it by a factor of about twelve and the model by less (Sct 0.7 reverses it), which Eddy3D reads as a finding about where the model puts the plume and not as a wrong bar: a probe repeated at full precision moved no c\* value by more than 0.003. The peak c\* is 1.38 against 3.04 measured, and 3 of the five highest points are shared.
- Controls on the same solution: the 15 points turned 180° about the source score R -0.06, FAC2 0.07, FB +2.00 (n 14; the model\'s mean over those points is 1.0e-05 against 0.125 at the real ones: the tracer goes downwind), and the points mirrored across the plume axis score R +0.65, FAC2 0.40, FB +0.18, better than the real points\' R +0.20, FAC2 0.13, FB +1.58: the modelled plume is displaced sideways against the tunnel\'s.
- The field campaign (18 runs) is recorded beside the tunnel, not asserted: the 10 runs within 10° of 180 at 3 m/s or more, each with its own U\_R and q and H\_R = 41 m as the cleaned table states (the fixture divides by 40.8 m, a 1 % difference). The model against the field\'s geometric mean scores R +0.22, FAC2 0.07, FB +1.29, and lies inside the field\'s minimum-maximum range at 2 of 15 points; the tunnel\'s WD 180 against the same mean scores R +0.98, FAC2 0.60, FB -0.59; the spread of the field at point 1 is a factor of 4.5.
- The velocity at the 15 points: the mean U/U\_R is 0.026 modelled against 0.164 measured. FB is not defined for V and W (their means are not both positive); V correlates at R +0.73 and flipping its sign gives -0.73.
- The solve ran to its 3000-iteration limit with the residualControl unmet (no \'solution converged\' line); the initial residuals at the last iteration were U\_x 6.1e-04, U\_z 6.9e-04, p 1.0e-04, epsilon 1.9e-02, k 1.6e-04 and the tracers 8.1e-06 to 1.1e-05. checkMesh: Mesh OK. 1,394,053 cells. The first solve of this case was killed by the container runtime for memory (exit 137) and the solve was run again alone; the scores are of the second. Its tracer probe, which printed six decimals, was replaced by a probe of the same solved study at seven significant digits (no c\* value moved by more than 0.003, Eddy3D\'s account).

U, V, W and k at the 15 points over the tunnel\'s U\_R = 4.08 m/s on the measurement and over the solved speed at the reference mast on the model (U\_R is defined at the mast), k over U\_R^2; c\* = C/c0 (c0 = q/(U\_R H\_R^2) = 132.5 ppm) against the model\'s c U\_R H\_R^2/Q (H\_R = 0.068 m x 600, Q = 1 kg/s) for turbulent Schmidt number 0.7, with one detection limit of 10^-3 of the largest measured value; hit rate D = 0.25, W = 0.05 in those units; the Schmidt numbers are three runs on one flow, published side by side. Per-point values: [`/api/cases/M/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/M/pairs/openfoam12-realizableKE.csv' | relative_url }}). Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseMContainerE2E (WD 180, the default) (TPU Atsugi campus, 1:600, tunnel WD 180, turbulent Schmidt number 0.7; OpenFOAM 12 realizable k-ε, numerics level 3, 3000 iterations, 1,394,053 cells, solved 2026-10-18); figures validation/plot\_cases\_fm\_openfoam.py; scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

## Figures

The figures for these runs are shown once, beside their reading: [Cases F and M (OpenFOAM)]({{ '/validation/cases-fm/' | relative_url }}).
