---
title: "Validation"
parent: "Case F — Shinjuku district"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case F — Shinjuku district: Eddy3D's scores against the measurements, by engine."
---

# Case F: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration literal

Quantity: the thermistor\'s (tunnel) and the cup anemometer\'s (field) mean speed over U(500 m) against the model\'s \|U\| and sqrt(\|U\|^2 + 2k) over its own approach U(500 m) = 9.862 m/s (probed 1100 m upwind of the centre; the imposed U(500 m) is 10 m/s), at the 33 tunnel points (planes at 5, 9 and 20 m) and the 13 field observations of wind from NNW; frame literal.

<details markdown="block">
  <summary>All 13 headline scores</summary>

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| Tunnel, 9 m plane, √(\|U\|²+2k) | +0.935 | 1.000 | +0.036 | 0.846 | 13 |
| Tunnel, 5 m plane, √(\|U\|²+2k) | +0.995 | 1.000 | +0.127 | 1.000 | 7 |
| Tunnel, 20 m plane, √(\|U\|²+2k) | +0.796 | 0.923 | +0.071 | 0.769 | 13 |
| Tunnel, all 33 points, √(\|U\|²+2k) | +0.912 | 0.970 | +0.067 | 0.848 | 33 |
| Tunnel, 9 m plane, \|U\| | +0.928 | 1.000 | +0.134 | 0.615 | 13 |
| Tunnel, 5 m plane, \|U\| | +0.988 | 0.857 | +0.307 | 0.571 | 7 |
| Tunnel, 20 m plane, \|U\| | +0.788 | 0.923 | +0.112 | 0.692 | 13 |
| Tunnel, all 33 points, \|U\| | +0.906 | 0.939 | +0.149 | 0.636 | 33 |
| Field, √(\|U\|²+2k) | +0.873 | 1.000 | +0.027 | 0.769 | 13 |
| Field, \|U\| | +0.860 | 1.000 | +0.126 | 0.308 | 13 |
| Tunnel, 9 m plane, √(\|U\|²+2k) over the imposed U(500 m) = 10 m/s | +0.935 | 1.000 | +0.050 | 0.846 | 13 |
| Tunnel\'s 9 m column as a model of the field (ceiling control) | +0.933 | 1.000 | -0.015 | 0.692 | 13 |
| Tunnel\'s SSE column, the opposite wind, against the solved NNW field (compass control) | +0.077 | 0.615 | +0.327 | 0.077 | 13 |
{: .scores }

</details>

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseFContainerE2E (EDDY3D\_AIJ\_F\_DIRECTIONS=NNW, the default) (Shinjuku district, 1:800, wind from NNW, frame literal; OpenFOAM 12 realizable k-ε, numerics level 3, 2000 iterations, 2,143,488 cells, solved 2026-10-18); figures validation/plot\_cases\_fm\_openfoam.py

Notes:

- Frame \'literal\': the model is probed at the published z in the STL\'s frame. The readme says z is measured from the tunnel floor and the ground is z - 10 m, but the STL\'s own ground under all 13 points is 5 m, so the 5, 9 and 20 m planes are probed 10, 14 and 25 m above the STL\'s ground (height\_above\_stl\_ground in the pairs). The other frame, \'agl\' (the STL\'s ground plus 5, 9 and 20 m), is the other run of this case. The files do not say which frame the tunnel meant: the 9 m plane\'s √(\|U\|²+2k) scores R 0.93 and FB +0.04 in the literal frame and R 0.94 and FB +0.13 in the agl frame.
- Both sides are U/U(500 m): the tunnel\'s ratio is as published, the model\'s is over its own approach U(500 m) = 9.862 m/s, probed 1100 m upwind of the centre (0.986 of the imposed 10 m/s). Over the imposed 10 m/s the 9 m plane\'s √(\|U\|²+2k) scores R 0.93 and FB +0.05.

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration agl

Quantity: the thermistor\'s (tunnel) and the cup anemometer\'s (field) mean speed over U(500 m) against the model\'s \|U\| and sqrt(\|U\|^2 + 2k) over its own approach U(500 m) = 9.862 m/s (probed 1100 m upwind of the centre; the imposed U(500 m) is 10 m/s), at the 33 tunnel points (planes at 5, 9 and 20 m) and the 13 field observations of wind from NNW; frame agl.

<details markdown="block">
  <summary>All 13 headline scores</summary>

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| Tunnel, 9 m plane, √(\|U\|²+2k) | +0.945 | 1.000 | +0.126 | 0.769 | 13 |
| Tunnel, 5 m plane, √(\|U\|²+2k) | +0.918 | 1.000 | +0.128 | 0.571 | 7 |
| Tunnel, 20 m plane, √(\|U\|²+2k) | +0.807 | 1.000 | +0.208 | 0.462 | 13 |
| Tunnel, all 33 points, √(\|U\|²+2k) | +0.898 | 1.000 | +0.165 | 0.606 | 33 |
| Tunnel, 9 m plane, \|U\| | +0.935 | 0.923 | +0.242 | 0.538 | 13 |
| Tunnel, 5 m plane, \|U\| | +0.923 | 0.857 | +0.259 | 0.571 | 7 |
| Tunnel, 20 m plane, \|U\| | +0.801 | 0.846 | +0.269 | 0.308 | 13 |
| Tunnel, all 33 points, \|U\| | +0.894 | 0.879 | +0.258 | 0.455 | 33 |
| Field, √(\|U\|²+2k) | +0.889 | 1.000 | +0.147 | 0.692 | 13 |
| Field, \|U\| | +0.866 | 0.846 | +0.266 | 0.308 | 13 |
| Tunnel, 9 m plane, √(\|U\|²+2k) over the imposed U(500 m) = 10 m/s | +0.945 | 1.000 | +0.139 | 0.692 | 13 |
| Tunnel\'s 9 m column as a model of the field (ceiling control) | +0.933 | 1.000 | -0.015 | 0.692 | 13 |
| Tunnel\'s SSE column, the opposite wind, against the solved NNW field (compass control) | +0.102 | 0.385 | +0.413 | 0.000 | 13 |
{: .scores }

</details>

- Reproduce: Eddy3D fixture Eddy3DCli.Tests/Validation/TestAijCaseFContainerE2E (EDDY3D\_AIJ\_F\_DIRECTIONS=NNW, the default) (Shinjuku district, 1:800, wind from NNW, frame agl; OpenFOAM 12 realizable k-ε, numerics level 3, 2000 iterations, 2,143,488 cells, solved 2026-10-18); figures validation/plot\_cases\_fm\_openfoam.py

Notes:

- Frame \'agl\': the model is probed at the STL\'s own ground under each point plus the instrument height (5, 9 and 20 m for the tunnel, 3 to 11 m for the field). The readme says z is measured from the tunnel floor and the ground is z - 10 m, but the STL\'s ground under all 13 points is 5 m, so the published z would sit 5 m higher; that frame is the other run of this case, \'literal\'. The files do not say which frame the tunnel meant: the 9 m plane\'s √(\|U\|²+2k) scores R 0.93 and FB +0.04 in the literal frame and R 0.94 and FB +0.13 in the agl frame.
- At the 4 m surface cells of the mesh the lowest probes of this frame (the 7 points of the 5 m plane, 1.25 cells above the ground, and the field\'s point at 3 m) sit in the first cell, where the point interpolation is pulled toward the wall\'s zero.
- Both sides are U/U(500 m): the tunnel\'s ratio is as published, the model\'s is over its own approach U(500 m) = 9.862 m/s, probed 1100 m upwind of the centre (0.986 of the imposed 10 m/s). Over the imposed 10 m/s the 9 m plane\'s √(\|U\|²+2k) scores R 0.94 and FB +0.14.

## All runs

- Normalisation: the thermistor\'s (tunnel) and the cup anemometer\'s (field) mean speed over U(500 m), the benchmark\'s own ratio, against the model\'s \|U\| and sqrt(\|U\|^2 + 2k) over its own approach U(500 m) = 9.862 m/s (the imposed U(500 m) is 10 m/s); hit rate D = 0.25, W = 0.05 in those units; 33 tunnel points and 13 field observations of wind from NNW; FB is positive when the model is low
- Per-point values: [`/api/cases/F/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/F/pairs/openfoam12-realizableKE.csv' | relative_url }})

Notes:

- One direction of the tunnel\'s twelve was solved: wind from NNW, which with ENE has the most tunnel rows (33). The other eleven tunnel directions and the field\'s other fifteen were not run.
- The thermistor reads a scalar speed and so does the cup anemometer: the model is scored as \|U\|, and as √(\|U\|²+2k), the speed of a velocity with the modelled turbulent kinetic energy in all three components.
- The field is a year of 10-minute means above 5 m/s at a rooftop reference, over a sector 22.5° wide, at 3 to 11 m above ground; the standard deviation of the means behind each value is 0.075 to 0.15 of U(500 m), 0.20 to 0.78 of the value itself (the horizontal bars of the figure). The tunnel\'s 9 m column scored as a model of the field, point for point, gives R 0.93, FAC2 1.00, FB -0.01.
- The field values of point 14 are the cleaned table\'s, realigned with the workbook: the published RS-FO\_caseF.csv holds them shifted by one direction (clean/QUESTIONS.md QF1). The field scores here therefore differ from Eddy3D\'s own results file in the third decimal (√(\|U\|²+2k) in the literal frame: R 0.8729 here, 0.8731 there; in the agl frame 0.8893 and 0.8872); the tunnel scores are identical to it.
- The published STL is open along the rim of its 725 m disc (812 boundary edges, one shell, wound inward), which the canvas\'s pre-meshing pass cannot close (it removed 3 degenerate faces). The mesh has 2,143,488 cells and checkMesh fails one check (43 highly skew faces, maximum skewness 14.8, maximum non-orthogonality 64.8°), so the solve started on the hardened numerics of Eddy3D\'s mesh-quality tier.
- The solve ran to its 2000-iteration limit with the residualControl unmet (no \'solution converged\' line); the initial residuals at the last iteration were U\_x 1.0e-04, U\_y 5.9e-05, U\_z 2.6e-03, p 3.0e-05, epsilon 1.0e-03 and k 1.4e-04, and the log has 1,988 \'bounding k\' lines.
- The solved field correlates R 0.93 with the tunnel\'s 9 m column for the wind from NNW and R 0.08 with its column for the opposite wind, SSE (agl frame: 0.94 and 0.10). A RANS field knows no compass, so this supports reading the direction labels as the direction the wind comes from (clean/QUESTIONS.md QF9), at this one direction.
- The model\'s U/U(500 m) at the workbook\'s two rooftop anemometers (SMB 0.85 for \|U\|, KDD 0.45) is in the results file and not scored: the tunnel\'s anchors for them exist for the north and south tests only.

<details markdown="block">
<summary>Interpretation: Case F scalar speed and field data</summary>

The modelled \|U\| is the lower bound. √(\|U\|²+2k) is the upper bracket (as in Cases C to E). A RANS field is one steady state for one exact direction. The tunnel\'s 9 m column as a model of the field is the bar a model of the tunnel is not expected to clear.

</details>

<details markdown="block">
  <summary>How the scores are computed</summary>

- Scores recomputed from the pairs by validation/dispersion\_metrics.py; the SHA-256 of every file the snapshot was read from is in its results file, under `sources`.

</details>

## Figures

Figures: [Cases F and M (OpenFOAM)]({{ '/validation/cases-fm/' | relative_url }}).
