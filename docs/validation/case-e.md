---
title: "Case E (OpenFOAM)"
parent: Validation
nav_order: 5
summary: "OpenFOAM 12 on the Niigata district, wind from SW, before and after construction"
description: "OpenFOAM 12 against the tunnel for Case E, the Niigata district, with the wind from SW, before and after construction."
---

# Case E, OpenFOAM 12

OpenFOAM 12 runs on the Niigata district, wind from SW. Scores and per-point file: [Case E]({{ '/cases/case-e/validation/' | relative_url }}) Validation page.

Before and after the construction of a 60 m tower and two 18 m blocks, each state on a 504 m-radius cylinder (about one million cells, 2 m at the buildings), the tunnel's own profile imposed as a table (`wind.inlet: "manual"`), the model's speed over its own solved $$U(15.9\text{ m})$$.

## Measurement layout

{% include figure.html name="case-e-layout.png" alt="Measurement points, Case E" caption="<strong>Figure 1.</strong> Case E, measurement points: A within 30 m of the 60 m building; B within 30 m of the two 18 m buildings; C elsewhere. Positions in metres, full scale. Dark footprints: the three buildings added in the after state." %}

## Measured against modelled

{% include figure.html name="case-e-openfoam-agreement.png" alt="Case E, measured vs modelled, before, after and the change" caption="<strong>Figure 2.</strong> Case E, measured vs modelled, before, after and the change. The dots take the colour of their group in Figure 1." %}

| | FAC2 | FB | hit rate | R |
|---|---|---|---|---|
| before · $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | 0.95 | +0.12 | 0.61 | 0.69 |
| before · $$\lvert\mathbf{U}\rvert$$ | 0.79 | +0.27 | 0.41 | 0.69 |
| after · $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | 0.89 | +0.23 | 0.47 | 0.85 |
| after · $$\lvert\mathbf{U}\rvert$$ | 0.74 | +0.34 | 0.30 | 0.84 |
| ceiling control: the tunnel's *before*, scored as a model of its *after* | 0.79 | +0.37 | 0.35 | 0.10 |

{% include nomenclature-scores.md %}

{% include figure.html name="case-e-openfoam-bias-map.png" alt="Case E, where the model is slow or fast" caption="<strong>Figure 3.</strong> Case E, where the model is slow or fast." %}

- Construction change (after − before): R = 0.84; the sign is right at 75 % of the points where the tunnel resolved a change; the modelled change is about 60 % of the measured size.
- Control that ignores the construction (the tunnel's *before* as a model of its *after*): R = 0.10.
- FB is positive when the model is low.

<details markdown="block">
<summary>Interpretation: Case E absolute ratios and the construction change</summary>

- In the change after − before, inflow, closure and instrument biases largely cancel. R = 0.84 is far above the control that ignores the construction.
- The absolute ratios are low and the cause is not established.

</details>

<details markdown="block">
<summary>Data notes: Approach-flow sampling</summary>

The approach flow reads 0.41 and 0.79 of the imposed table at 1.25 m and 2.5 m. Those readings were taken inside the first cell of the coarse upstream mesh, where the sampling interpolates to zero at the wall (see [Inflow]({{ '/validation/method/' | relative_url }}#inflow)).

</details>
