---
title: "Validation"
parent: "Case I — cube with a roof point source"
grand_parent: "Cases"
nav_order: 2
has_children: false
generated: true
description: "Case I — cube with a roof point source: Eddy3D's scores against the measurements, engine by engine."
---

# Case I: validation
{: .no_toc }

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

Engine status: OpenFOAM 12 <span class="label label-green status">scored</span> · OpenFOAM 12 k-ε <span class="label label-green status">scored</span> · OpenFOAM 12 k-ω SST <span class="label label-green status">scored</span> · OpenLB <span class="label label-yellow status">pending</span> · FluidX3D <span class="label label-yellow status">pending</span> · ML surrogate <span class="label label-yellow status">pending</span>

## Measurement locations

{% include validation/case-i/layout.md %}

## OpenFOAM 12

Status: <span class="label label-green status">scored</span>

{% include validation/case-i/openfoam.md %}

### OpenFOAM 12, realizable k-epsilon (Eddy3D Outdoor)

Reattachment length $$L_r/H$$ = 2.51.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$ | +0.998 | 0.997 | 0.879 | +0.020 | 0.813 | 91 |
| $$V$$ | +0.985 | 0.970 | 0.895 | — | 1.000 | 38 |
| $$W$$ | +0.972 | 0.945 | 0.659 | -0.049 | 0.967 | 91 |
| $$k$$ | +0.905 | 0.818 | 0.923 | +0.106 | 0.582 | 91 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.922 | 0.850 | 0.360 | +0.398 | 0.106 | 539 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.940 | 0.884 | 0.475 | +0.083 | 0.284 | 539 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.946 | 0.896 | 0.477 | -0.100 | 0.291 | 539 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/I/pairs/openfoam12-realizableKE.csv`]({{ '/api/cases/I/pairs/openfoam12-realizableKE.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCubeContainerE2E (realizable k-ε, 1:60) (numerics level 3, 3000 iterations); figures validation/plot\_cases\_hi\_openfoam.py

### OpenFOAM 12, standard k-epsilon (Eddy3D Outdoor)

Reattachment length $$L_r/H$$ = 2.23.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$ | +0.990 | 0.981 | 0.846 | -0.003 | 0.769 | 91 |
| $$V$$ | +0.966 | 0.934 | 0.789 | — | 0.895 | 38 |
| $$W$$ | +0.943 | 0.889 | 0.615 | +0.080 | 0.901 | 91 |
| $$k$$ | +0.870 | 0.757 | 0.912 | -0.037 | 0.637 | 91 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.938 | 0.879 | 0.442 | +0.308 | 0.134 | 539 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.955 | 0.913 | 0.519 | -0.035 | 0.378 | 539 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.954 | 0.909 | 0.519 | -0.248 | 0.288 | 539 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/I/pairs/openfoam12-kEpsilon.csv`]({{ '/api/cases/I/pairs/openfoam12-kEpsilon.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCubeContainerE2E (standard k-ε, 1:60) (numerics level 3, 3000 iterations); figures validation/plot\_cases\_hi\_openfoam.py

### OpenFOAM 12, k-omega SST (Eddy3D Outdoor)

Reattachment length $$L_r/H$$ = 2.68.

| Score | R | $$R^2$$ | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|---|
| $$U$$ | +0.992 | 0.983 | 0.879 | +0.091 | 0.802 | 91 |
| $$V$$ | +0.968 | 0.937 | 0.789 | -2.000 | 0.921 | 38 |
| $$W$$ | +0.922 | 0.850 | 0.615 | -0.214 | 0.868 | 91 |
| $$k$$ | +0.880 | 0.775 | 0.396 | +0.495 | 0.264 | 91 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.514 | 0.265 | 0.432 | -0.047 | 0.236 | 539 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.466 | 0.217 | 0.403 | -0.153 | 0.202 | 539 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.439 | 0.193 | 0.380 | -0.221 | 0.195 | 539 |
{: .scores }

{% include nomenclature-scores.md %}

- Per-point values: [`/api/cases/I/pairs/openfoam12-kOmegaSST.csv`]({{ '/api/cases/I/pairs/openfoam12-kOmegaSST.csv' | relative_url }})
- Reproduce: Eddy3D fixture TestAijCubeContainerE2E (k-ω SST, 1:60) (numerics level 3, 3000 iterations); figures validation/plot\_cases\_hi\_openfoam.py

## Not run

{% include validation/case-i/not-run.md %}

## Notes on every run

- Normalisation: velocities by $$U_H$$, $$k$$ by $$U_H^2$$ (the benchmark\'s own convention; Case E by $$U$$ at 15.9 m, as it is published); hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05$$ in those units

- Scores recomputed from the pairs by validation/dispersion\_metrics.py.

## Leaderboard

| Rank | Run | Source | Hit rate, $$U$$ | Hit rate, $$V$$ | Hit rate, $$W$$ | Hit rate, $$\lvert\mathbf{U}\rvert$$ | Hit rate, $$k$$ | Hit rate, $$c^\ast$$ | Hit rate | FAC2 | R | $$R^2$$ | Points scored |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.7 | Eddy3D | **0.813** | **1.000** | **0.967** | 0.789 | 0.582 | 0.291 | **0.741** | **0.797** | **+0.967** | **0.936** | 89 % |
| 2 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.5 | Eddy3D | **0.813** | **1.000** | **0.967** | 0.789 | 0.582 | 0.284 | 0.739 | **0.796** | +0.966 | 0.934 | 89 % |
| 3 | OpenFOAM 12 k-ε · $$\mathrm{Sc_t}$$ 0.5 | Eddy3D | 0.769 | 0.895 | 0.901 | 0.789 | **0.637** | **0.378** | 0.728 | 0.763 | +0.952 | 0.909 | 89 % |
| 4 | OpenFOAM 12 k-ε · $$\mathrm{Sc_t}$$ 0.7 | Eddy3D | 0.769 | 0.895 | 0.901 | 0.789 | **0.637** | 0.288 | 0.713 | 0.763 | +0.952 | 0.908 | 89 % |
| 5 | OpenFOAM 12 · $$\mathrm{Sc_t}$$ 0.3 | Eddy3D | **0.813** | **1.000** | **0.967** | 0.789 | 0.582 | 0.106 | 0.710 | 0.777 | +0.963 | 0.929 | 89 % |
| 6 | OpenFOAM 12 k-ε · $$\mathrm{Sc_t}$$ 0.3 | Eddy3D | 0.769 | 0.895 | 0.901 | 0.789 | **0.637** | 0.134 | 0.688 | 0.750 | +0.950 | 0.903 | 89 % |
| 7 | OpenFOAM 12 k-ω SST · $$\mathrm{Sc_t}$$ 0.3 | Eddy3D | 0.802 | 0.921 | 0.868 | **0.816** | 0.264 | 0.236 | 0.651 | 0.685 | +0.878 | 0.799 | 89 % |
| 8 | OpenFOAM 12 k-ω SST · $$\mathrm{Sc_t}$$ 0.5 | Eddy3D | 0.802 | 0.921 | 0.868 | **0.816** | 0.264 | 0.202 | 0.646 | 0.680 | +0.870 | 0.791 | 89 % |
| 9 | OpenFOAM 12 k-ω SST · $$\mathrm{Sc_t}$$ 0.7 | Eddy3D | 0.802 | 0.921 | 0.868 | **0.816** | 0.264 | 0.195 | 0.644 | 0.677 | +0.865 | 0.787 | 89 % |
{: .scores }

{% include nomenclature-scores.md %}

Every run on the case, scored by one evaluator, `validation/score_submissions.py`, the way a submission is scored: Eddy3D's runs from their served values at the measured points, the community's from theirs. The tasks are the quantities every run here was scored on, averaged over the case's configurations and wind directions; runs are ranked by the mean hit rate over them, the measure the VDI 3783 guideline validates wind models with, and the best value of each column is in bold; the hit rate, FAC2, R and $$R^2$$ columns are means over the tasks. *Points scored* is the share of the measured points a run gave values at. The ML surrogate is not on the board: its values carry no point ids, so this evaluator cannot score them; its scores are in its section. Negative controls are not runs and are left out. Community rows are self-reported values ([Validate your own solver]({{ '/byos/' | relative_url }})).
