---
title: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12"
parent: "Community results"
nav_order: 1
has_children: false
generated: true
description: "OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12: a community submission scored against the AIJ cases by this repository's build."
---

# OpenFOAM simpleFoam (Eddy3D Outdoor case writer) 12

{: .note }
This is the repository's own worked example (Eddy3D's Case A OpenFOAM probes, copied from the served pairs). It shows the pipeline; it is not a community result.

Self-reported inputs, scored by this repository's build ([method]({{ '/validation/method/' | relative_url }})). The submitted values are under [`submissions/example-openfoam12/`](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/tree/main/submissions/example-openfoam12) and served as [`/api/submissions/example-openfoam12.json`]({{ '/api/submissions/example-openfoam12.json' | relative_url }}).

| Field | Value |
|---|---|
| solver | OpenFOAM simpleFoam (Eddy3D Outdoor case writer) |
| version | 12 |
| url | <https://openfoam.org> |
| author | Sustainable Urban Systems Lab |
| licence | CC-BY-4.0 |
| contact | <https://github.com/Eddy3D-Dev/AIJ-Data-Validation/discussions> |
| inlet | log law fitted to AF\_caseA.csv ($$u_\ast$$ = 0.343 m/s, $$z_0$$ = 0.668 mm, kappa 0.41), the inlet cases/A.json recommends |
| mesh | snappyHexMesh, 1:100 scale, numerics level 3 (Eddy3D fixture TestAijCaseAContainerE2E) |
| turbulence\_model | realizable k-epsilon |
| compute | 3000 iterations, steady, one workstation |
| units | normalised |
| notes | the values are the served pairs of Eddy3D\'s run, so the scores equal validation.json\'s for Case A |

{% include nomenclature.md %}

## Case A — 1:1:2 building

| Score | R | FAC2 | FB | Hit rate | n | coverage |
|---|---|---|---|---|---|---|
| $$U$$ | +0.955 | 0.817 | +0.185 | 0.586 | 186 | 186/186 |
| $$V$$ | +0.961 | 0.349 | — | 0.892 | 186 | 186/186 |
| $$W$$ | +0.708 | 0.398 | -1.501 | 0.801 | 186 | 186/186 |
| $$\lvert\mathbf{U}\rvert$$ | +0.940 | 0.876 | +0.144 | 0.634 | 186 | 186/186 |
{: .scores }

{% include nomenclature-scores.md %}
