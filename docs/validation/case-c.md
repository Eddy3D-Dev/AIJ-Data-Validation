---
title: "Case C (OpenFOAM)"
parent: Validation
nav_order: 3
summary: "OpenFOAM 12 on the 3 × 3 block array, nine configurations"
description: "OpenFOAM 12 against the tunnel for Case C, the 3 × 3 block array, in all nine configurations."
---

# Case C, OpenFOAM 12

The reading of the OpenFOAM 12 runs on the 3 × 3 block array. Every score, with the per-point file, is on the [Case C]({{ '/cases/case-c/validation/' | relative_url }}) Validation page.

All nine configurations (centre block 0D / 1D / 2D × WD 0°, 22.5°, 45°), solved at 1:100 on a cylindrical domain —
the tunnel's turntable: the array turns with WD, the domain does not — ~310,000 cells per centre-block height,
3000 iterations per direction, the 120 probes at exactly the tunnel's coordinates.

## Where was it measured?

{% include figure.html name="case-c-layout.png" alt="Measurement points, Case C" caption="<strong>Figure 1.</strong> Case C, measurement points: A street x < 0 beside the centre block; B street x > 0 beside the centre block; C street y > 0 beside the centre block; D street y < 0 beside the centre block; E crossings beyond the corners of the centre block. Positions in multiples of D. Centre block absent (0D), D or 2D high; wind directions 0°, 22.5° and 45°." %}

## Does the model agree?

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

- **The pattern is right in every configuration** — R 0.80–0.91, FAC2 0.85–0.98.
- **The model is slow, worst at WD = 0** (FB +0.25 … +0.34, hit rate 0.43–0.57; at 22.5° and 45° FB +0.09 … +0.20,
  hit rate 0.68–0.88). The map puts the deficit in the streets running along the wind.
- **It is not the scalar-vs-vector question.** The tunnel reads above even √(\|U\|² + 2k) at 902 of the 1080 points
  (84 %); \|U\| alone is lower still.
- **Where the deficit comes from is not settled.** An earlier version of this page put it on the inflow, reading the
  approach flow at the probe height as 0.83 of the tunnel's. That reading was a sampling artefact: upstream of the
  array the probe height lies below the centre of the first cell of the coarse background mesh, where the probes'
  cell-to-point interpolation runs linearly to zero at the wall (the sampled |U| is exactly proportional to z there:
  1.00 m/s at 1 m, 2.01 m/s at 2 m). At z = D the approach matches the tunnel (0.99). At the measurement points the
  sampling is sound: none of the 240 checked (2D at 0°, 0D at 45°) has its 2 m sample inside the first cell.
- **The frame is checked by the scores.** Scored with the paper figure's rotation sense (the y mirror) R falls to
  −0.33 … +0.03 at 22.5° and 45°; with upwind and downwind swapped to −0.41 … +0.14 in eight of nine configurations.
- An independent re-scoring from the probe files and the original `RS_caseC.csv` reproduces every number (largest
  difference 9 × 10⁻¹⁶).
