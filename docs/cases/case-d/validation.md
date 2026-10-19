---
title: "Validation"
parent: "Case D — high-rise among city blocks"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case D — high-rise among city blocks: Eddy3D's scores against the measurements, engine by engine."
redirect_from:
  - /validation/case-d/
---

# Case D: validation
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

{% include validation/case-d/layout.md %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-d/openfoam.md %}

### Scores

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| WD 0°, thermistor $$V_{\mathrm{s}}$$ · $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.803 | 0.644 | 0.727 | +0.214 | 0.485 | 66 |
| WD 0°, thermistor $$V_{\mathrm{s}}$$ · $$\lvert\mathbf{U}\rvert$$ | +0.811 | 0.658 | 0.667 | +0.362 | 0.394 | 66 |
| WD 0°, split fibre $$\lvert\mathbf{U}\rvert$$ | +0.853 | 0.728 | 0.758 | +0.071 | 0.515 | 33 |
| WD 0°, split fibre $$U$$ | +0.945 | 0.894 | 0.485 | +0.668 | 0.515 | 33 |
| WD 22.5°, thermistor $$V_{\mathrm{s}}$$ · $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.803 | 0.646 | 0.924 | +0.050 | 0.667 | 66 |
| WD 22.5°, thermistor $$V_{\mathrm{s}}$$ · $$\lvert\mathbf{U}\rvert$$ | +0.783 | 0.613 | 0.818 | +0.154 | 0.636 | 66 |
| WD 22.5°, rotation sense mirrored (control) | +0.400 | 0.160 | 0.742 | +0.050 | 0.364 | 66 |
| WD 45°, thermistor $$V_{\mathrm{s}}$$ · $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | +0.854 | 0.730 | 0.894 | +0.090 | 0.712 | 66 |
| WD 45°, thermistor $$V_{\mathrm{s}}$$ · $$\lvert\mathbf{U}\rvert$$ | +0.844 | 0.712 | 0.818 | +0.170 | 0.697 | 66 |
| WD 45°, rotation sense mirrored (control) | +0.170 | 0.029 | 0.697 | +0.090 | 0.242 | 66 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/D/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/D/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseDContainerE2E (EDDY3D\_AIJD\_HEADINGS=0,22.5,45); figure validation/plot\_case\_d\_openfoam.py

## OpenLB

Status: <span class="label label-grey status">not comparable</span>

{% include validation/case-d/openlb.md %}

## FluidX3D

Status: <span class="label label-grey status">not comparable</span>

{% include validation/case-d/fluidx3d.md %}

## ML surrogate

Status: <span class="label label-green status">scored</span>

{% include validation/case-d/ml-surrogate.md %}

### Scores

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$V_{\mathrm{s}}$$, thermistor, 3 WD | +0.325 | 0.106 | 0.343 | +0.673 | 0.167 | 198 |
| $$\lvert\mathbf{U}\rvert$$, split fibre, WD 0 | +0.587 | 0.344 | 0.515 | +0.231 | 0.242 | 33 |
| $$V_{\mathrm{s}}$$, WD 0, lattice cut at ±250 m | +0.220 | 0.048 | 0.636 | +0.489 | 0.273 | 66 |
| wind reversed (control) | +0.492 | 0.242 | 0.470 | +0.555 | 0.197 | 66 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/D/pairs/ml-surrogate.csv`]({{ '/api/cases/D/pairs/ml-surrogate.csv' | relative_url }})
- Reproduce: Eddy3D fixture Outdoor.ML.Tests/TestAijSurrogateE2E; figure validation/plot\_ml\_surrogate.py

## Notes on every run

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units

## Leaderboard

| Rank | Run | Source | Hit rate, $$U$$ | Hit rate, $$V$$ | Hit rate, $$W$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate, $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate | FAC2 | R | $$R^2$$ | Points scored |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM 12 | Eddy3D | 0.515 | 0.424 | 0.939 | 0.515 | 0.621 | 0.576 | 0.598 | 0.638 | +0.840 | 0.713 | 100 % |
{: .scores }

{% include nomenclature-scores.md %}

Every run on the case, scored by one evaluator, `validation/score_submissions.py`, the way a submission is scored: Eddy3D's runs from their served values at the measured points, the community's from theirs. The tasks are the quantities every run here was scored on, averaged over the case's configurations and wind directions; runs are ranked by the mean hit rate over them, the measure the VDI 3783 guideline validates wind models with, and the best value of each column is in bold; the hit rate, FAC2, R and $$R^2$$ columns are means over the tasks. *Points scored* is the share of the measured points a run gave values at. The ML surrogate is not on the board: its values carry no point ids, so this evaluator cannot score them; its scores are in its section. Negative controls are not runs and are left out. Community rows are self-reported values ([Validate your own solver]({{ '/byos/' | relative_url }})).
