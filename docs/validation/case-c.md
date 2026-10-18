---
title: "Case C (OpenFOAM)"
parent: Validation
nav_order: 3
summary: "OpenFOAM 12 on the 3 × 3 block array, nine configurations"
description: "OpenFOAM 12 against the tunnel for Case C, the 3 × 3 block array, in all nine configurations."
---

# Case C, OpenFOAM 12

OpenFOAM 12 runs on the 3 × 3 block array. Scores and per-point file: [Case C]({{ '/cases/case-c/validation/' | relative_url }}) Validation page.

All nine configurations (centre block 0D / 1D / 2D × WD 0°, 22.5°, 45°), solved at 1:100 on a cylindrical domain (the tunnel's turntable: the array turns with WD, the domain does not), ~310,000 cells per centre-block height, 3000 iterations per direction, the 120 probes at exactly the tunnel's coordinates.

## Measurement layout

{% include figure.html name="case-c-layout.png" alt="Measurement points, Case C" caption="<strong>Figure 1.</strong> Case C, measurement points: A street x < 0 beside the centre block; B street x > 0 beside the centre block; C street y > 0 beside the centre block; D street y < 0 beside the centre block; E crossings beyond the corners of the centre block. Positions in multiples of D. Centre block absent (0D), D or 2D high; wind directions 0°, 22.5° and 45°." %}

## Measured against modelled

{% include figure.html name="case-c-openfoam-agreement.png" alt="Case C, measured vs modelled" caption="<strong>Figure 2.</strong> Case C, measured vs modelled. The dots take the colour of their street in Figure 1." %}

<details markdown="block">
  <summary>Scores for all nine configurations (R, FAC2, FB, hit rate; |U| alone)</summary>

| centre block | WD | R | FAC2 | FB | hit rate | \|U\| alone: FB / R |
|---|---|---|---|---|---|---|
| 0D | 0° | +0.824 | 0.908 | +0.266 | 0.567 | +0.466 / +0.804 |
| 0D | 22.5° | +0.857 | 0.983 | +0.106 | 0.750 | +0.295 / +0.846 |
| 0D | 45° | +0.831 | 0.942 | +0.121 | 0.783 | +0.307 / +0.801 |
| 1D | 0° | +0.801 | 0.858 | +0.341 | 0.433 | +0.551 / +0.741 |
| 1D | 22.5° | +0.896 | 0.975 | +0.192 | 0.675 | +0.394 / +0.882 |
| 1D | 45° | +0.872 | 0.942 | +0.198 | 0.733 | +0.353 / +0.873 |
| 2D | 0° | +0.857 | 0.850 | +0.251 | 0.492 | +0.443 / +0.848 |
| 2D | 22.5° | +0.906 | 0.983 | +0.091 | 0.875 | +0.240 / +0.894 |
| 2D | 45° | +0.909 | 0.958 | +0.103 | 0.883 | +0.243 / +0.912 |

</details>

{% include figure.html name="case-c-openfoam-bias-map.png" alt="Case C, where the model is slow or fast" caption="<strong>Figure 3.</strong> Case C, where the model is slow or fast." %}

- R 0.80–0.91 and FAC2 0.85–0.98 in every configuration.
- FB +0.25 … +0.34 at WD = 0 (hit rate 0.43–0.57); FB +0.09 … +0.20 at 22.5° and 45° (hit rate 0.68–0.88). FB is positive when the model is low.
- The tunnel's speed is above the model's √(\|U\|² + 2k) at 902 of the 1080 points (84 %); the model's \|U\| alone is lower still.
- Rotation sense mirrored (the paper figure's y mirror), control: R −0.33 … +0.03 at 22.5° and 45°.
- Upwind and downwind swapped, control: R −0.41 … +0.14 in eight of nine configurations.

<details markdown="block">
<summary>Interpretation: Case C pattern and deficit</summary>

- The pattern is right in every configuration.
- The model is slow, worst at WD = 0, and the map puts the deficit in the streets running along the wind.
- The scalar-vs-vector difference does not explain the deficit: the tunnel reads above even √(\|U\|² + 2k) at 902 of the 1080 points, and \|U\| alone is lower still. Where the deficit comes from is not settled.
- Both frame controls above score far below the runs, so the frame is the right one.

</details>

<details markdown="block">
<summary>Data notes: Approach-flow sampling</summary>

The approach flow at the probe height reads 0.83 of the tunnel's; that reading is a sampling artefact. Upstream of the array the probe height lies below the centre of the first cell of the coarse background mesh, where the probes' cell-to-point interpolation runs linearly to zero at the wall: the sampled \|U\| is exactly proportional to z there (1.00 m/s at 1 m, 2.01 m/s at 2 m). At z = D the approach matches the tunnel (0.99). At the measurement points the sampling is sound: none of the 240 checked (2D at 0°, 0D at 45°) has its 2 m sample inside the first cell.

</details>
