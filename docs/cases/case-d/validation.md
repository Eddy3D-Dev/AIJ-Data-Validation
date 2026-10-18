---
title: "Validation"
parent: "Case D — high-rise among city blocks"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case D — high-rise among city blocks: Eddy3D's scores against the tunnel data, by engine."
---

# Case D: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-grey status">not comparable</span> · FluidX3D <span class="label label-grey status">not comparable</span> · ML surrogate <span class="label label-green status">scored</span>

*Scored* means a run exists and its scores are below, not that it agrees. How to read them is on [the reading page]({{ '/validation/case-d/' | relative_url }}); the [Validation]({{ '/validation/' | relative_url }}) overview says what each status means and why an engine is *not comparable*.

## OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor)

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| WD 0°, thermistor Vs · √(\|U\|²+2k) | +0.803 | 0.727 | +0.214 | 0.485 | 66 |
| WD 0°, thermistor Vs · \|U\| | +0.811 | 0.667 | +0.362 | 0.394 | 66 |
| WD 0°, split fibre \|U\| | +0.853 | 0.758 | +0.071 | 0.515 | 33 |
| WD 0°, split fibre U | +0.945 | 0.485 | +0.668 | 0.515 | 33 |
| WD 22.5°, thermistor Vs · √(\|U\|²+2k) | +0.803 | 0.924 | +0.050 | 0.667 | 66 |
| WD 22.5°, thermistor Vs · \|U\| | +0.783 | 0.818 | +0.154 | 0.636 | 66 |
| WD 22.5°, rotation sense mirrored (control) | +0.400 | 0.742 | +0.050 | 0.364 | 66 |
| WD 45°, thermistor Vs · √(\|U\|²+2k) | +0.854 | 0.894 | +0.090 | 0.712 | 66 |
| WD 45°, thermistor Vs · \|U\| | +0.844 | 0.818 | +0.170 | 0.697 | 66 |
| WD 45°, rotation sense mirrored (control) | +0.170 | 0.697 | +0.090 | 0.242 | 66 |
{: .scores }

velocities by U\_H, k by U\_H^2 (the benchmark's own convention; Case E by U at 15.9 m, as it is published); hit rate D = 0.25, W = 0.05 in those units. Per-point values: [`/api/cases/D/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/D/pairs/openfoam12-realizableKE.csv' | relative_url }}). Reproduce: Eddy3D fixture TestAijCaseDContainerE2E (EDDY3D\_AIJD\_HEADINGS=0,22.5,45); figure validation/plot\_case\_d\_openfoam.py.

## Eddy3D ML wind surrogate (pedestrian height)

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| Vs, thermistor, 3 WD | +0.325 | 0.343 | +0.673 | 0.167 | 198 |
| \|U\|, split fibre, WD 0 | +0.587 | 0.515 | +0.231 | 0.242 | 33 |
| Vs, WD 0, lattice cut at ±250 m | +0.220 | 0.636 | +0.489 | 0.273 | 66 |
| wind reversed (control) | +0.492 | 0.470 | +0.555 | 0.197 | 66 |
{: .scores }

velocities by U\_H, k by U\_H^2 (the benchmark's own convention; Case E by U at 15.9 m, as it is published); hit rate D = 0.25, W = 0.05 in those units. Per-point values: [`/api/cases/D/pairs/ml-surrogate.csv`]({{ '/api/cases/D/pairs/ml-surrogate.csv' | relative_url }}). Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py.

## Figures

<figure class="figure">
<img src="{{ '/assets/figures/case-d-openfoam-agreement.png' | relative_url }}" alt="Case D, OpenFOAM 12, wind directions 0°, 22.5° and 45°: measured thermistor Vs/U_H against the modelled √(|U|²+2k)/U_H (filled) and |U|/U_H (hollow), and the split-fibre |U| against the modelled |U| at 0°. At 0° the 66 thermistor points are 33 mirror pairs.">
<figcaption><strong>Figure 1.</strong> Case D, OpenFOAM 12, wind directions 0°, 22.5° and 45°: measured thermistor Vs/U_H against the modelled √(|U|²+2k)/U_H (filled) and |U|/U_H (hollow), and the split-fibre |U| against the modelled |U| at 0°. At 0° the 66 thermistor points are 33 mirror pairs.</figcaption>
</figure>

The figure for all cases together (Eddy3D ML surrogate (Yel-2.0)) is on [the ML surrogate page]({{ '/validation/ml-surrogate/' | relative_url }}).
