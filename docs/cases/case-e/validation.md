---
title: "Validation"
parent: "Case E — Niigata district"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case E — Niigata district: Eddy3D's scores against the measurements, by engine."
redirect_from:
  - /validation/case-e/
---

# Case E: validation
{: .no_toc }

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-grey status">not comparable</span> · FluidX3D <span class="label label-grey status">not comparable</span> · ML surrogate <span class="label label-green status">scored</span>

{% include validation/case-e.md %}

## Scores, run by run

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor), configuration SW

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| before, $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.688 | 0.950 | +0.124 | 0.613 | 80 |
| before, $$\lvert\mathbf{U}\rvert$$ | +0.692 | 0.787 | +0.266 | 0.412 | 80 |
| after, $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.845 | 0.887 | +0.226 | 0.475 | 80 |
| after, $$\lvert\mathbf{U}\rvert$$ | +0.835 | 0.738 | +0.341 | 0.300 | 80 |
| no-construction ceiling control | +0.099 | 0.787 | +0.368 | 0.350 | 80 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/E/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/E/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseEContainerE2E (EDDY3D\_AIJ\_E\_DIRECTIONS=SW, tabulated inlet); figures validation/plot\_case\_e\_openfoam.py

### Eddy3D ML wind surrogate (pedestrian height)

| Score | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$V_{\mathrm{s}}/U(15.9\text{ m})$$, 16 WD, bc + ac | +0.433 | 0.225 | +0.996 | 0.082 | 2560 |
| after construction | +0.425 | 0.284 | +0.853 | 0.105 | 1280 |
| after − before | +0.399 | 0.234 | +0.077 | 0.312 | 1280 |
| after, lattice cut at ±250 m | +0.230 | 0.836 | +0.053 | 0.388 | 1280 |
| wind reversed (control) | +0.425 | 0.284 | +0.853 | 0.105 | 1280 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/E/pairs/ml-surrogate.csv`]({{ '/api/cases/E/pairs/ml-surrogate.csv' | relative_url }})
- Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py

### All runs

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units

## Figures

Figures: [ML surrogate]({{ '/validation/ml-surrogate/' | relative_url }}).
