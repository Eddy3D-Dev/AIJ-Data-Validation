---
title: "Case D (OpenFOAM)"
parent: Validation
nav_order: 4
summary: "OpenFOAM 12 on the high-rise among city blocks, wind directions 0°, 22.5° and 45°"
description: "OpenFOAM 12 against the tunnel for Case D, the high-rise among city blocks, at wind directions 0°, 22.5° and 45°."
---

# Case D, OpenFOAM 12

OpenFOAM 12 runs on the high-rise among city blocks. Scores and per-point file: [Case D]({{ '/cases/case-d/validation/' | relative_url }}) Validation page.

All three headings: 3.6 million cells at 1:400 on a cylinder domain, 3000 iterations, the 66 measured thermistor points and the 33 split-fibre points at z/H = 0.02.

{% include figure.html name="case-d-openfoam-agreement.png" alt="Case D, measured vs modelled" caption="<strong>Figure 1.</strong> Case D, wind directions 0°, 22.5° and 45°: measured against modelled speed on the thermistor plane, and at the split-fibre points (0° only)." %}

<details markdown="block">
  <summary>Scores for all three headings and both instruments</summary>

| | n | FAC2 | FB | q | R |
|---|---|---|---|---|---|
| WD 0° · thermistor Vs · √(\|U\|²+2k) | 66 | 0.73 | +0.21 | 0.48 | 0.80 |
| WD 0° · thermistor Vs · \|U\| | 66 | 0.67 | +0.36 | 0.39 | 0.81 |
| WD 22.5° · thermistor Vs · √(\|U\|²+2k) | 66 | 0.92 | +0.05 | 0.67 | 0.80 |
| WD 22.5° · thermistor Vs · \|U\| | 66 | 0.82 | +0.15 | 0.64 | 0.78 |
| WD 22.5° · the same, rotation sense mirrored (control) | 66 | 0.74 | +0.05 | 0.36 | 0.40 |
| WD 45° · thermistor Vs · √(\|U\|²+2k) | 66 | 0.89 | +0.09 | 0.71 | 0.85 |
| WD 45° · thermistor Vs · \|U\| | 66 | 0.82 | +0.17 | 0.70 | 0.84 |
| WD 45° · the same, rotation sense mirrored (control) | 66 | 0.70 | +0.09 | 0.24 | 0.17 |
| WD 0° · split fibre \|U\| · \|U\| | 33 | 0.76 | +0.07 | 0.52 | 0.85 |
| WD 0° · split fibre U · U | 33 | 0.48 | +0.67 | 0.52 | 0.95 |

</details>

- Thermistor plane: R 0.80–0.85 at all three headings. Split-fibre \|U\|: R 0.85.
- Split-fibre points (33): \|U\| FB +0.07. Thermistor (66): FB +0.21 with √(\|U\|²+2k) and +0.36 with \|U\|. In the tunnel the thermistor reads 1.34 times the split-fibre \|U\| over the same 33 points.
- Split-fibre streamwise U: FB +0.67, R 0.95.
- Rotation sense at 22.5° and 45°: the array is symmetric about y = 0, so a wind turned toward +y and one turned toward −y give mirror-image fields. The data paper's Figure 4 draws +y.
  - Figure 4's sense: R 0.80 and FAC2 0.92 at 22.5°; R 0.85 and FAC2 0.89 at 45°.
  - Mirrored sense (control): R 0.40 at 22.5°, 0.17 at 45°.
  - FB against the thermistor with √(\|U\|²+2k): +0.05 and +0.09.
- At 0° the 66 thermistor values are 33 mirror pairs (33 independent values); the mirror control is equal to the score there.
- FB is positive when the model is low.

<details markdown="block">
<summary>Interpretation: Case D pattern, instruments and rotation sense</summary>

- The pattern is right. The frame check (R above 0.5 at 0°) passes with room to spare; a prior Eddy3D attempt at this case scored R 0.10 ([Known data issues]({{ '/known-data-issues/' | relative_url }})).
- Against the instrument that measures what RANS computes, the model is nearly unbiased (split-fibre \|U\|, FB +0.07).
- Most of the thermistor gap is the instrument: the thermistor reads 1.34 times the split-fibre \|U\| in the tunnel itself.
- The model's streamwise component is low (U FB +0.67, R 0.95) while its \|U\| is not: more of the model's near-ground speed is in the lateral and vertical components than the tunnel's.
- At 22.5° and 45° the solved fields corroborate the rotation sense that the measurements alone cannot decide. At both headings the model is also nearly unbiased against the thermistor (FB +0.05 and +0.09 with √(\|U\|²+2k)).

</details>
