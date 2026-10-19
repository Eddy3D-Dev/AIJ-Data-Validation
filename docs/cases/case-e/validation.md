---
title: "Validation"
parent: "Case E — Niigata district"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case E — Niigata district: Eddy3D's scores against the measurements, engine by engine."
redirect_from:
  - /validation/case-e/
---

# Case E: validation
{: .no_toc }

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-grey status">not comparable</span> · FluidX3D <span class="label label-grey status">not comparable</span> · ML surrogate <span class="label label-green status">scored</span>

## Measurement locations

{% include validation/case-e/layout.md %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-e/openfoam.md %}

### Scores

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| before, $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.688 | 0.474 | 0.950 | +0.124 | 0.613 | 80 |
| before, $$\lvert\mathbf{U}\rvert$$ | +0.692 | 0.478 | 0.787 | +0.266 | 0.412 | 80 |
| after, $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.845 | 0.714 | 0.887 | +0.226 | 0.475 | 80 |
| after, $$\lvert\mathbf{U}\rvert$$ | +0.835 | 0.698 | 0.738 | +0.341 | 0.300 | 80 |
| no-construction ceiling control | +0.099 | 0.010 | 0.787 | +0.368 | 0.350 | 80 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/E/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/E/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseEContainerE2E (EDDY3D\_AIJ\_E\_DIRECTIONS=SW, tabulated inlet); figures validation/plot\_case\_e\_openfoam.py

## OpenLB

Status: <span class="label label-grey status">not comparable</span>

{% include validation/case-e/openlb.md %}

## FluidX3D

Status: <span class="label label-grey status">not comparable</span>

{% include validation/case-e/fluidx3d.md %}

## ML surrogate

Status: <span class="label label-green status">scored</span>

{% include validation/case-e/ml-surrogate.md %}

### Scores

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$V_{\mathrm{s}}/U(15.9\text{ m})$$, 16 WD, bc + ac | +0.433 | 0.187 | 0.225 | +0.996 | 0.082 | 2560 |
| after construction | +0.425 | 0.181 | 0.284 | +0.853 | 0.105 | 1280 |
| after − before | +0.399 | 0.159 | 0.234 | +0.077 | 0.312 | 1280 |
| after, lattice cut at ±250 m | +0.230 | 0.053 | 0.836 | +0.053 | 0.388 | 1280 |
| wind reversed (control) | +0.425 | 0.181 | 0.284 | +0.853 | 0.105 | 1280 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/E/pairs/ml-surrogate.csv`]({{ '/api/cases/E/pairs/ml-surrogate.csv' | relative_url }})
- Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py

## Notes on every run

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units

## Leaderboard

| Rank | Run | Source | Hit rate, $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate | FAC2 | R | $$R^2$$ | Points scored |
|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM 12 · SW | Eddy3D | 0.544 | 0.356 | 0.450 | 0.841 | +0.765 | 0.591 | 100 % |
{: .scores }

{% include nomenclature-scores.md %}

Every run on the case, scored by one evaluator, `validation/score_submissions.py`, the way a submission is scored: Eddy3D's runs from their served values at the measured points, the community's from theirs. The tasks are the quantities every run here was scored on, averaged over the case's configurations and wind directions; runs are ranked by the mean hit rate over them, the measure the VDI 3783 guideline validates wind models with, and the best value of each column is in bold; the hit rate, FAC2, R and $$R^2$$ columns are means over the tasks. *Points scored* is the share of the measured points a run gave values at. The ML surrogate is not on the board: its values carry no point ids, so this evaluator cannot score them; its scores are in its section. Negative controls are not runs and are left out. Community rows are self-reported values ([Validate your own solver]({{ '/byos/' | relative_url }})).
