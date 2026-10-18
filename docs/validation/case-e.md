---
title: "Case E (OpenFOAM)"
parent: Validation
nav_order: 5
summary: "OpenFOAM 12 on the Niigata district, wind from SW, before and after construction"
description: "OpenFOAM 12 against the tunnel for Case E, the Niigata district, with the wind from SW, before and after construction."
---

# Case E, OpenFOAM 12

The reading of the OpenFOAM 12 runs on the Niigata district, wind from SW. Every score, with the per-point file, is on the [Case E]({{ '/cases/case-e/validation/' | relative_url }}) Validation page.

Before and after the construction of a 60 m tower and two 18 m blocks, each state on a 504 m-radius cylinder
(about one million cells, 2 m at the buildings), the tunnel's own profile imposed as a table
(`wind.inlet: "manual"`), the model's speed over its own solved U(15.9 m).

## Where was it measured?

{% include figure.html name="case-e-layout.png" alt="Measurement points, Case E" caption="<strong>Figure 1.</strong> Case E, measurement points: A within 30 m of the 60 m building; B within 30 m of the two 18 m buildings; C elsewhere. Positions in metres, full scale. Dark footprints: the three buildings added in the after state." %}

## Does the model agree?

{% include figure.html name="case-e-openfoam-agreement.png" alt="Case E, measured vs modelled, before, after and the change" caption="<strong>Figure 2.</strong> Case E, measured vs modelled, before, after and the change. The dots take the colour of their group in Figure 1." %}

| | FAC2 | FB | q | R |
|---|---|---|---|---|
| before · √(\|U\|²+2k) | 0.95 | +0.12 | 0.61 | 0.69 |
| before · \|U\| | 0.79 | +0.27 | 0.41 | 0.69 |
| after · √(\|U\|²+2k) | 0.89 | +0.23 | 0.47 | 0.85 |
| after · \|U\| | 0.74 | +0.34 | 0.30 | 0.84 |
| ceiling control: the tunnel's *before*, scored as a model of its *after* | 0.79 | +0.37 | 0.35 | 0.10 |

{% include figure.html name="case-e-openfoam-bias-map.png" alt="Case E, where the model is slow or fast" caption="<strong>Figure 3.</strong> Case E, where the model is slow or fast." %}

The construction change (after − before), in which inflow, closure and instrument biases largely cancel, has
R = 0.84, the sign right at 75 % of the points where the tunnel resolved a change, and about 60 % of the measured
size — far above the control that ignores the construction. The absolute ratios are low, and the cause is not
established: an earlier version of this page blamed an approach flow decaying near the ground, but those readings
(0.41 and 0.79 of the imposed table at 1.25 m and 2.5 m) were taken inside the first cell of the coarse upstream
mesh, where the sampling interpolates to zero at the wall (see [Inflow]({{ '/validation/method/' | relative_url }}#inflow)).
