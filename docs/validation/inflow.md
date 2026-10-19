---
title: "Inlet contract"
parent: Validation
nav_order: 2
summary: "the approach flow a submission should use, per case: the measured profile, and the inlet this repository recommends"
description: "The inlet for a comparable solve of each AIJ case: the benchmark's measured profile, and the log-law inlet with k and epsilon that this repository recommends."
---

# Inlet contract

Two solvers are comparable on a case only when they see the same approach flow. Per case, `/api/cases/{id}.json`
carries an `inflow` block with two parts, and `/api/cases/{id}/inflow_openfoam.txt` holds the recommended inlet as OpenFOAM files.

## The benchmark's data

`inflow.benchmark_data`: the measured approach-flow profile, `approach_flow.csv` ($$z$$, $$U$$, and $$k$$ or
$$u_{\mathrm{rms}}$$ where published), and `inflow_fit`, the fit of it made during cleaning. That is the data; use the
profile itself wherever your solver takes a tabulated inlet.

## What this repository recommends

`inflow.recommended` is this repository's choice, not the benchmark's, and says so in its `status`:

- Where a log law fits the profile (Cases A, B, C, D, H, I, J, K, L): $$U(z) = \dfrac{u_\ast}{\kappa}\ln\dfrac{z + z_0}{z_0}$$
  with the fitted $$u_\ast$$ and $$z_0$$ and $$\kappa = 0.41$$, and the neutral ABL relations
  $$k = u_\ast^2/\sqrt{C_\mu}$$, $$\varepsilon = \dfrac{u_\ast^3}{\kappa (z + z_0)}$$ with $$C_\mu = 0.09$$. These are
  the inlets of OpenFOAM's `atmBoundaryLayerInletVelocity`, `atmBoundaryLayerInletK` and `atmBoundaryLayerInletEpsilon`,
  and the ground takes `nutkAtmRoughWallFunction` with the same $$z_0$$, so the profile holds along an empty fetch. Cases
  C and D have two fitting windows; the first is used.
- Where no log law fits (Cases E, F, G, M, which publish power-law or tabulated profiles): the measured profile as a
  table (`fixedProfile` in OpenFOAM 12), with $$\varepsilon = C_\mu^{1/2}\thinspace k\thinspace \mathrm{d}U/\mathrm{d}z$$
  from the tabulated $$U$$ and $$k$$ where $$k$$ is published.

The recommendation exists so that inlets are comparable, not because the benchmark prescribes one: Eddy3D's own runs of
Cases A and B used this log law (the [method]({{ '/validation/method/' | relative_url }}) page gives the fits), and its
runs of Cases E, F and M used the tabulated profiles. Any inlet may be submitted; `submission.yaml` records which.

## Flow direction

`inflow.flow_direction` says how a wind direction becomes a vector in the case's frame: along $$+x$$ at WD 0 for the
model-scale cases and Case G, the meteorological from-direction in the geographic frames of Cases E and F, and Case M's
$$+x$$ north, $$+y$$ west frame. `inflow_openfoam.txt` sets `flowDir` for the case's first direction; rotate it for another.

## What Eddy3D's runs used

`inflow.eddy3d_runs` quotes, per run, what the fixture's snapshot records: the inlet, the scale, the roughness lengths
and the mesh size, under the keys the fixture wrote. The domain extents and blockage of those runs are not in the
snapshots and are not stated: `inflow.domain` says so rather than guessing.

## OpenFOAM

[`/api/cases/A/inflow_openfoam.txt`]({{ '/api/cases/A/inflow_openfoam.txt' | relative_url }}) (one per case) holds `0/U`,
`0/k`, `0/epsilon`, `0/nut` and `system/probes` (the case's points as a probes function object, to include from
`controlDict`), each after a `==== <path>` line: split it into those files. The files are OpenFOAM 12 (openfoam.org) syntax; in ESI OpenFOAM v2xxx the three
`atmBoundaryLayerInlet*` conditions and `nutkAtmRoughWallFunction` take the same entries, while `fixedProfile` is
openfoam.org only (use `timeVaryingMappedFixedValue` or `codedFixedValue` there). Patch names (`inlet`, `outlet`,
`ground`, `buildings`, `top`, `sides`) are placeholders for yours.

{% include nomenclature.md %}
