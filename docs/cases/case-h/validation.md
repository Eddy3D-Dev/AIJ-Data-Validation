---
title: "Validation"
parent: "Case H"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case H — 1:1:2 building with a floor point source: Eddy3D's scores against the measurements, engine by engine."
redirect_from:
  - /validation/cases-hi/
---

# Case H: validation
{: .no_toc }

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

## Measurement locations

{% include validation/case-h/layout.md %}

## Explore the points

{% include explorer.html case="H" %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-h/openfoam.md %}

### Scores

Reattachment length $$L_r/H$$ = 1.36.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$ | +0.897 | 0.805 | 0.609 | +0.355 | 0.446 | 826 |
| $$V$$ | +0.935 | 0.874 | 0.355 | -0.432 | 0.682 | 826 |
| $$W$$ | +0.887 | 0.786 | 0.314 | — | 0.713 | 826 |
| $$k$$ | +0.107 | 0.012 | 0.570 | +0.514 | 0.305 | 826 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.954 | 0.910 | 0.694 | -0.597 | 0.493 | 826 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.951 | 0.905 | 0.615 | -0.825 | 0.507 | 826 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.946 | 0.895 | 0.588 | -0.934 | 0.493 | 826 |
{: .scores }

{% include nomenclature-scores.md %}

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units
- Per-point values: [`/api/cases/H/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/H/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCaseHContainerE2E (realizable k-ε, 1:100) (numerics level 3, 3000 iterations); figures validation/plot\_cases\_hi\_openfoam.py

## Not run

{% include validation/case-h/not-run.md %}

- Scores recomputed from the pairs by validation/dispersion\_metrics.py.

## Leaderboard

| Rank | Run | Source | Hit rate, $$U$$ | Hit rate, $$V$$ | Hit rate, $$W$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate, $$k$$ | Hit rate, $$c^\ast$$ | Hit rate | FAC2 | R | $$R^2$$ | Points scored |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.5 | Eddy3D | **0.446** | **0.682** | **0.713** | **0.441** | **0.305** | **0.507** | **0.516** | 0.519 | **+0.777** | 0.694 | 100 % |
| 2 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.3 | Eddy3D | **0.446** | **0.682** | **0.713** | **0.441** | **0.305** | 0.493 | 0.513 | **0.532** | **+0.778** | **0.695** | 100 % |
| 3 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.7 | Eddy3D | **0.446** | **0.682** | **0.713** | **0.441** | **0.305** | 0.493 | 0.513 | 0.515 | +0.776 | 0.693 | 100 % |
{: .scores }

{% include nomenclature-scores.md %}

Every run on the case, scored by one evaluator, `validation/score_submissions.py`, the way a submission is scored: Eddy3D's runs from their served values at the measured points, the community's from theirs. The tasks are the quantities every run here was scored on, averaged over the case's configurations and wind directions; runs are ranked by the mean hit rate over them, the measure the VDI 3783 guideline validates wind models with, and the best value of each column is in bold; the hit rate, FAC2, R and $$R^2$$ columns are means over the tasks. *Points scored* is the share of the measured points a run gave values at. The ML surrogate is not on the board: its values carry no point ids, so this evaluator cannot score them; its scores are in its section. Negative controls are not runs and are left out. Community rows are self-reported values ([Validate your own solver]({{ '/byos/' | relative_url }})).
