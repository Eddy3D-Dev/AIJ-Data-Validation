---
title: "Cases F and M (OpenFOAM)"
parent: Validation
nav_order: 9
summary: "OpenFOAM 12 on the Shinjuku district (Case F, wind from NNW, tunnel and field) and on the tracer release over the TPU Atsugi campus (Case M, WD 180): speed, velocity, k and concentration"
description: "OpenFOAM 12 against the wind tunnel and the field for Case F (Shinjuku sub-centre, one wind direction, two vertical frames) and Case M (tracer release over a campus, three turbulent Schmidt numbers): scalar speed, velocity, turbulent kinetic energy and concentration."
---

# Cases F and M, OpenFOAM 12

The reading of the OpenFOAM 12 runs on the Shinjuku sub-centre of Tokyo (Case F: a 1978 high-rise district, thermistor speed in a 1:800 tunnel and a year of field cup anemometers) and on the tracer release over the Atsugi campus of Tokyo Polytechnic University (Case M: ethylene in a 1:600 tunnel, with 18 field runs). Every score of each run, with the per-point files and the caveats recorded with the run, is on the [Case F]({{ '/cases/case-f/validation/' | relative_url }}) and [Case M]({{ '/cases/case-m/validation/' | relative_url }}) Validation pages. Both are Eddy3D production runs solved on 2026-10-18, realizable k-ε at numerics level 3, **one steady solve each**: Case F for the wind from NNW only (2,143,488 cells, 2000 iterations), Case M for the tunnel's heading WD 180 only (1,394,053 cells, 3000 iterations). Both stopped at the iteration limit with the SIMPLE residual control unmet; the initial residual of epsilon at the last iteration was 1.0 × 10⁻³ in Case F (U<sub>z</sub> 2.6 × 10⁻³) and 1.9 × 10⁻² in Case M. Each case was solved on one mesh only.

## How these runs are scored

- **The measured side** of every pair is the cleaned table, the legacy workbook at full precision. Eddy3D's own scores were computed against the published CSVs, which round the workbooks. The scores here are recomputed from the per-point files by `validation/dispersion_metrics.py`, which reproduces Eddy3D's metrics: fed the published CSVs and Eddy3D's probes it gives the fixtures' own scores to 10⁻⁹ (24 scores of Case F, 84 of Case M). The differences from Eddy3D's results are small: in Case F the tunnel's values are identical to the CSV's, and the field scores differ in the third decimal because point 14's 16 published field values are shifted by one direction in the CSV and realigned with the workbook in the cleaned table (clean/QUESTIONS.md QF1). In Case M the velocities and the concentration lose the CSV's rounding (to 0.01 m/s and 0.1 ppm): U R is 0.7085 here and 0.7081 there, k R 0.4464 and 0.4499, and W, whose values are of the order of the rounding, R 0.1814 and 0.1757 (FAC2 0.27 and 0.20); the field values divide by H<sub>R</sub> = 41 m as the cleaned table states, Eddy3D's by 40.8 m (a 1 % difference in every field c\*). Eddy3D's scores of V and W have a fractional bias (−6.15 and +2.15) that this repository leaves undefined for a signed component whose means are not both positive.
- **Case F** is scored in the benchmark's own ratio, U/U(500 m). The tunnel's thermistor and the field's cup anemometer read a *scalar* speed, so the model is scored as |U| (the lower bound) and as √(|U|² + 2k) (the upper bracket, as in Cases C to E); both are in the tables. The model is divided by **its own** approach speed at 500 m, 9.862 m/s (probed 1100 m upwind of the centre, 0.986 of the imposed 10 m/s); over the imposed 10 m/s the scores are in the files. The tunnel measured at 5, 9 and 20 m above ground at 13 points (7, 13 and 13 of them have a value for NNW) and the field at 13 points, 3 to 11 m up. FB is positive when the model is low.
- **Two vertical frames, neither asserted.** The readme says z is measured from the tunnel floor and the ground is z − 10 m, but the STL's own ground under all 13 points is 5 m. *Literal* probes the model at the published z in the STL's frame, which is 10, 14 and 25 m above the STL's ground for the three planes; *agl* probes the STL's ground plus 5, 9 and 20 m. The files do not say which one the tunnel meant, so both are scored and published side by side, as two runs of one engine (`configuration` literal and agl).
- **Case M** is scored at WD 180 against the wind-tunnel run: U, V, W and k over the tunnel's U<sub>R</sub> = 4.08 m/s on the measurement and over the **solved** speed at the reference mast (4.686 m/s) on the model, because U<sub>R</sub> is defined at the mast. The concentration is the measured C/c₀ (c₀ = 132.5 ppm) against the model's c\* = c U<sub>R</sub> H<sub>R</sub>²/Q with the same solved U<sub>R</sub>, for the turbulent Schmidt numbers 0.3, 0.5 and 0.7: three passive tracers on one flow, **three runs** published side by side (`configuration` sct03, sct05, sct07); the flow scores are the same in all three. A concentration score has one detection limit of 10⁻³ of the largest measured value. The 18 field runs are recorded beside the tunnel and never asserted.

## Case F: does the model agree?

{% include figure.html name="case-f-openfoam-agreement.png" alt="Case F, measured vs modelled speed over U(500 m)" caption="<strong>Figure 1.</strong> Case F, wind from NNW: the tunnel's and the field's U/U(500 m) against the modelled √(|U|²+2k) (filled) and |U| (hollow), in the published-z frame (top) and the STL-ground frame (bottom). The bars are the standard deviation of the field's 10-minute means." %}

The scalar-speed bracket, √(|U|² + 2k) over U(500 m):

| Points | Frame | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| Tunnel, 9 m plane | literal | +0.935 | 1.000 | +0.036 | 0.846 | 13 |
| Tunnel, 9 m plane | agl | +0.945 | 1.000 | +0.126 | 0.769 | 13 |
| Tunnel, 5 m plane | literal | +0.995 | 1.000 | +0.127 | 1.000 | 7 |
| Tunnel, 5 m plane | agl | +0.918 | 1.000 | +0.128 | 0.571 | 7 |
| Tunnel, 20 m plane | literal | +0.796 | 0.923 | +0.071 | 0.769 | 13 |
| Tunnel, 20 m plane | agl | +0.807 | 1.000 | +0.208 | 0.462 | 13 |
| Tunnel, all points | literal | +0.912 | 0.970 | +0.067 | 0.848 | 33 |
| Tunnel, all points | agl | +0.898 | 1.000 | +0.165 | 0.606 | 33 |
| Field | literal | +0.873 | 1.000 | +0.027 | 0.769 | 13 |
| Field | agl | +0.889 | 1.000 | +0.147 | 0.692 | 13 |
{: .scores }

And |U| alone:

| Points | Frame | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| Tunnel, 9 m plane | literal | +0.928 | 1.000 | +0.134 | 0.615 | 13 |
| Tunnel, 9 m plane | agl | +0.935 | 0.923 | +0.242 | 0.538 | 13 |
| Tunnel, 5 m plane | literal | +0.988 | 0.857 | +0.307 | 0.571 | 7 |
| Tunnel, 5 m plane | agl | +0.923 | 0.857 | +0.259 | 0.571 | 7 |
| Tunnel, 20 m plane | literal | +0.788 | 0.923 | +0.112 | 0.692 | 13 |
| Tunnel, 20 m plane | agl | +0.801 | 0.846 | +0.269 | 0.308 | 13 |
| Tunnel, all points | literal | +0.906 | 0.939 | +0.149 | 0.636 | 33 |
| Tunnel, all points | agl | +0.894 | 0.879 | +0.258 | 0.455 | 33 |
| Field | literal | +0.860 | 1.000 | +0.126 | 0.308 | 13 |
| Field | agl | +0.866 | 0.846 | +0.266 | 0.308 | 13 |
{: .scores }

The controls:

| Control | Frame | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| 9 m plane over the imposed U(500 m) | literal | +0.935 | 1.000 | +0.050 | 0.846 | 13 |
| 9 m plane over the imposed U(500 m) | agl | +0.945 | 1.000 | +0.139 | 0.692 | 13 |
| Tunnel's SSE column (opposite wind) | literal | +0.077 | 0.615 | +0.327 | 0.077 | 13 |
| Tunnel's SSE column (opposite wind) | agl | +0.102 | 0.385 | +0.413 | 0.000 | 13 |
| Tunnel's 9 m column as a model of the field | literal | +0.933 | 1.000 | −0.015 | 0.692 | 13 |
| Tunnel's 9 m column as a model of the field | agl | +0.933 | 1.000 | −0.015 | 0.692 | 13 |
{: .scores }

FB is positive when the model is low. What the numbers say:

- **The pattern follows the tunnel in both frames, and the level depends on the frame.** For √(|U|²+2k) at the 9 m plane R is 0.935 (literal) and 0.945 (agl) with FAC2 1.00; over all 33 tunnel points R is 0.912 and 0.898, FAC2 0.970 and 1.00. The 20 m plane has the lowest R (0.796 and 0.807) and the 5 m plane, 7 points, the highest in the literal frame (0.995) and 0.918 in the agl frame. The mean of the modelled scalar speed at the 9 m plane is 0.252 (literal) and 0.230 (agl) against 0.261 measured, FB +0.04 and +0.13; for |U| alone FB is +0.13 and +0.24, the model's mean 0.228 and 0.205.
- **The frame moves the level, not the pattern.** The published z sits 5 m higher above the STL's ground than the instrument heights, and the literal frame scores the smaller bias (FB +0.04 against +0.13 at 9 m, +0.07 against +0.21 at 20 m) with R within 0.02 at the 9 m and 20 m planes. That is a statement about the datum and not about the model: nothing in the files says which one the tunnel meant. At the fixture's 4 m surface cells the lowest probes of the agl frame (the 7 points of the 5 m plane, 1.25 cells up, and the field's point at 3 m) sit in the first cell, where the point interpolation is pulled toward the wall's zero.
- **Point by point.** At the 9 m plane, literal frame, the model-to-tunnel ratio of √(|U|²+2k) runs from 0.70 (point 8) to 1.51 (point 3): the model is faster than the tunnel at points 3, 5, 10 and 14 and slower at points 1, 2, 8, 9 and 13, within 5 % at points 6, 7, 11 and 15; in the agl frame the ratio runs from 0.65 (point 1) to 1.31 (point 3), slower at points 1, 2, 6, 8, 9 and 13 (0.65 to 0.80) and faster at points 3, 5, 10 and 14 (1.08 to 1.31). Over all 33 tunnel points one is outside a factor of two in the literal frame (FAC2 0.970), none in the agl frame. The plan is in Figure 2.
- **The field is scored and not asserted.** R is 0.873 and 0.889 and FAC2 1.00 for √(|U|²+2k) (|U|: R 0.860 and 0.866, FB +0.13 and +0.27). The standard deviation of the 10-minute means behind a field value is 0.075 to 0.15 of U(500 m), 0.20 to 0.78 of the value itself, and a steady solve is one state for one direction while a field value averages a sector 22.5° wide over a year of strong winds. The tunnel's own 9 m column scored as a model of the field gives R 0.933, FAC2 1.00, FB −0.015: that, not 1, is what a model of the tunnel can be expected to reach, and the model's R against the field is 0.04 to 0.06 under it.
- **The compass sense is corroborated at this direction.** The solved field correlates R 0.935 with the tunnel's 9 m column for the wind from NNW and R 0.077 with its column for the opposite wind, SSE (agl frame 0.945 and 0.102). A RANS solution knows no compass, so this supports the reading of the direction labels as the direction the wind comes from, which the cleaned release had marked unverified. The cleaned release's direction table now marks its NNW rows *corroborated by a solved field*; the other directions stay *unverified* until one is solved (clean/QUESTIONS.md QF9).

{% include figure.html name="case-f-openfoam-bias-map.png" alt="Case F, where the model is slow or fast" caption="<strong>Figure 2.</strong> Case F, wind from NNW: log₂(model / tunnel) of √(|U|²+2k) at the 13 points of the 9 m plane on the plan of the district, in the two vertical frames; the arrow is the wind." %}

## Case M: does the model agree?

{% include figure.html name="case-m-openfoam-agreement.png" alt="Case M, measured vs modelled velocity, k and concentration" caption="<strong>Figure 3.</strong> Case M, WD 180: measured vs modelled U, V, W, k and c\* at three turbulent Schmidt numbers (log axes show the positive pairs within eight decades). The last panel is the tunnel's own WD 175 and WD 185 against its WD 180." %}

| Quantity | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| c\*, Sct 0.3 | +0.412 | 0.200 | +1.396 | 0.133 | 15 |
| c\*, Sct 0.5 | +0.251 | 0.200 | +1.524 | 0.133 | 15 |
| c\*, Sct 0.7 | +0.198 | 0.133 | +1.579 | 0.133 | 15 |
| c\*, Sct 0.3, points turned 180° about the source (control) | −0.050 | 0.071 | +2.000 | 0.071 | 14 |
| c\*, Sct 0.5, points turned 180° about the source (control) | −0.058 | 0.071 | +2.000 | 0.071 | 14 |
| c\*, Sct 0.7, points turned 180° about the source (control) | −0.058 | 0.071 | +2.000 | 0.071 | 14 |
| c\*, Sct 0.3, points mirrored across the plume axis (control) | +0.675 | 0.467 | +0.321 | 0.133 | 15 |
| c\*, Sct 0.5, points mirrored across the plume axis (control) | +0.655 | 0.400 | +0.220 | 0.333 | 15 |
| c\*, Sct 0.7, points mirrored across the plume axis (control) | +0.650 | 0.400 | +0.180 | 0.333 | 15 |
| c\*, tunnel WD 175 as a model of WD 180 (control) | +0.932 | 0.733 | +0.401 | 0.267 | 15 |
| c\*, tunnel WD 185 as a model of WD 180 (control) | +0.976 | 0.800 | −0.117 | 0.533 | 15 |
| c\*, mean of WD 175 and WD 185 as a model of WD 180 (control) | +0.998 | 1.000 | +0.111 | 0.867 | 15 |
| c\*, Sct 0.3, against the field's geometric mean | +0.464 | 0.067 | +1.012 | 0.000 | 15 |
| c\*, Sct 0.5, against the field's geometric mean | +0.285 | 0.067 | +1.202 | 0.000 | 15 |
| c\*, Sct 0.7, against the field's geometric mean | +0.224 | 0.067 | +1.287 | 0.000 | 15 |
| c\*, tunnel WD 180 as a model of the field's geometric mean (control) | +0.984 | 0.600 | −0.593 | 0.000 | 15 |
| U | +0.708 | 0.267 | +1.460 | 0.267 | 15 |
| V | +0.731 | 0.333 | — | 0.133 | 15 |
| V, sign flipped (control) | −0.731 | 0.067 | −0.616 | 0.133 | 15 |
| W | +0.181 | 0.267 | — | 0.733 | 15 |
| \|U\| | +0.601 | 0.733 | +0.185 | 0.400 | 15 |
| k | +0.446 | 0.133 | +1.131 | 0.067 | 15 |
{: .scores }

FB is positive when the model is low, and left out (—) for a signed component whose measured and modelled means are not both positive. How the concentration and its controls compare:

| Run | c\* over the imposed speed at the mast: FB | over 4.08 m/s: FB | mean c\* tunnel | mean c\* model | peak tunnel | peak model | top five shared | near three, tunnel | model | far two, tunnel | model |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Sct 0.3 | +1.480 | +1.464 | 0.998 | 0.177 | 3.04 | 1.27 | 3 of 5 | 2.52 | 0.26 | 0.21 | 0.11 |
| Sct 0.5 | +1.592 | +1.579 | 0.998 | 0.135 | 3.04 | 1.37 | 3 of 5 | 2.52 | 0.11 | 0.21 | 0.10 |
| Sct 0.7 | +1.640 | +1.628 | 0.998 | 0.117 | 3.04 | 1.38 | 3 of 5 | 2.52 | 0.05 | 0.21 | 0.09 |

What the numbers say:

- **The tracer is under-predicted at every Schmidt number, and the pattern is weakly correlated.** R is 0.41, 0.25 and 0.20 and FAC2 0.20, 0.20 and 0.13 from Sct 0.3 to 0.7; the mean c\* is 0.18, 0.13 and 0.12 against the tunnel's 1.00 (FB +1.40 to +1.58), the peak 1.27 to 1.38 against 3.04, and three of the five highest points are shared. A higher Schmidt number lowers c\* further here. The choice of normalising speed does not change this: over the imposed speed at the mast's height (3.934 m/s) or the tunnel's 4.08 m/s FB is +1.48 and +1.46 at Sct 0.3 (the solved speed at the mast is 4.686 m/s, 1.19 of the imposed one).
- **Where the plume is.** The three points nearest the source carry c\* 2.52 in the tunnel and 0.26, 0.11 and 0.05 in the model; the two far downwind ones 0.21 in the tunnel and 0.11, 0.10 and 0.09 in the model. The tunnel's near points exceed its far ones by a factor of about twelve; the model's by 2.3 and 1.1 at Sct 0.3 and 0.5, and at Sct 0.7 they carry *less* (0.055 against 0.087). Eddy3D's fixture asserted this ordering before the solve and now only records it, because a first run can only fail an assertion about the very thing the case measures (Eddy3D's account).
- **The tracer goes downwind, and sideways differently from the tunnel.** The 15 points turned 180° about the source score R −0.05 to −0.06 (the model's mean over them is 7 × 10⁻⁶ against 0.19 at the real points, Sct 0.3): the model carries the tracer downwind. The points **mirrored across the plume axis** score R +0.65 to +0.68, FAC2 0.40 to 0.47, better than the real points' +0.20 to +0.41: the modelled plume is displaced sideways against the tunnel's.
- **A single heading cannot be read against 1.** The tunnel's own WD 175 and WD 185 scored as models of its WD 180 reach FAC2 0.73 and 0.80 (R 0.93 and 0.98), and the mean of the two 1.00 (R 0.998); 8 of the 15 points change by more than a factor of two between WD 175 and WD 185 (up to 11 at point 14). The model's FAC2 of 0.13 to 0.20 is under what the tunnel's own neighbouring headings score against its WD 180, and a steady solve at one heading is not a mean over them.
- **The field campaign is recorded and not asserted.** The 10 of 18 runs within 10° of 180 at 3 m/s or more, each with its own U<sub>R</sub> and tracer flow, give a geometric-mean c\* at each point; the spread of the field at point 1 is a factor of 4.5. The model against that mean scores R 0.46, 0.29 and 0.22, FAC2 0.07 and FB +1.01 to +1.29, and lies inside the field's minimum–maximum range at 2 of the 15 points. The tunnel's WD 180 against the same mean scores R 0.98, FAC2 0.60 and FB −0.59: the tunnel is higher than the field's geometric mean at the same points (mean c\* 1.00 against 0.54).
- **The velocity.** The magnitude of the velocity is close (|U| R 0.60, FAC2 0.73, FB +0.19, means 0.206 modelled against 0.247 measured) and the streamwise component is not: U R 0.71, FAC2 0.27, FB +1.46, the mean U/U<sub>R</sub> 0.026 modelled against 0.164 measured. V correlates (R 0.73; flipping its sign gives −0.73, so its sign agrees with the tunnel's) and W does not (R 0.18). k has R 0.45, FAC2 0.13 and FB +1.13 (mean k/U<sub>R</sub>² 0.008 against 0.029).

{% include figure.html name="case-m-openfoam-plan.png" alt="Case M, the tracer on the plan of the campus" caption="<strong>Figure 4.</strong> Case M, WD 180: log₁₀ of c\* at the 15 points on the plan of the campus, the tunnel and the three Schmidt numbers on one scale (open: below 10⁻³ or zero). The star is the gas source and the square the reference mast; the arrow is the wind." %}

## What was not checked

- No second mesh or iteration count was run for either case, and the residual control was not met, so none of these numbers is mesh- or iteration-independent.
- **Case F** was solved for one of the tunnel's twelve directions; the other eleven, and the field's other fifteen, were not run. Which vertical datum the tunnel meant was not settled (the two frames are both published). The STL is open along the rim of its disc (812 boundary edges) and the mesh fails one checkMesh check (43 highly skew faces, maximum skewness 14.8), so the solve ran on Eddy3D's hardened numerics; nothing was run to see how much either matters. The rooftop anemometers' modelled speeds are in the results file and are not scored.
- **Case M** was solved at WD 180 only: WD 175 and WD 185, which the tunnel also measured, were not. The model is not the tunnel (a cylinder on the terrain sheet, none of the tunnel's side walls and ceiling, a smooth floor under the tabulated inflow) and its source is a 4 m cube of 20 cells where the tunnel's outlet is 6 mm (3.6 m at 1:600); a finer source or a finer surface mesh was not tried. The first solve of the case was killed by the container runtime for memory and the solve was run again alone; the scores are of the second.
- OpenLB, FluidX3D, UMF and the ML surrogate have not been run on either case.
