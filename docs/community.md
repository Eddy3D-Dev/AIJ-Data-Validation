---
title: "Community results"
nav_order: 7
permalink: /community/
has_children: true
description: "Solvers and models submitted by their authors, scored against the AIJ cases by this repository's build."
---

# Community results

Solvers and models that others validated against the benchmark ([Validate your own solver]({{ '/byos/' | relative_url }})).
Each row is **self-reported, scored by this repository's CI**: the author gave the values at the published points, and
the pinned build scored them with the same metrics and conventions as Eddy3D's results on the
[Validation]({{ '/validation/' | relative_url }}) page, which are kept apart from this table on purpose. The scoring is
checked; the solve is not.

{% include community-matrix.md %}

{% include nomenclature-scores.md %}

R and FAC2: the range over the submission's scores for the case; `n/N` points: the points it gave over the points the
benchmark measured (a partial submission scores its points only). A dash: the case was not submitted. The row marked
*example* is the repository's own worked example (Eddy3D's Case A probes), there to prove the pipeline. Every value and
every score is served at [`/api/submissions.json`]({{ '/api/submissions.json' | relative_url }}).

To add yours: [Validate your own solver]({{ '/byos/' | relative_url }}), step 10.
