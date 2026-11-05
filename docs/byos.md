---
title: "Validate your own solver"
nav_order: 6
permalink: /byos/
description: "Score your own wind solver or ML model against the AIJ cases, the way Eddy3D's results are scored, and submit the result."
---

# Validate your own solver
{: .no_toc }

The benchmark's points, the inlet, the scoring conventions and the metrics that score Eddy3D's results are all served
by the API, and one script in the repository applies them to your values. Ten steps, Case A end to end; the same walk
scores every case. Your result can then be submitted and shown on the [Community results]({{ '/community/' | relative_url }}) page.
{: .fs-5 .fw-300 .lede }

<details open markdown="block">
  <summary>
    Contents
  </summary>
  {: .text-delta }
1. TOC
{:toc}
</details>

## 1. Get a checkout

```bash
git clone https://github.com/Eddy3D-Dev/AIJ-Data-Validation
```

Nothing to install beyond [uv](https://docs.astral.sh/uv/) (`uv sync` reads `pyproject.toml` and `uv.lock`; NumPy is all the scorer needs). The scorer,
`validation/score_submissions.py`, uses `validation/dispersion_metrics.py`, the transcription of Eddy3D's metrics that
scores every served result; its self-test re-scores every served run from its pairs and matches the headline scores to
$$10^{-9}$$. The API itself needs no checkout: every file below is a plain GET.

## 2. Pick a case

[`GET /api/cases.json`]({{ '/api/cases.json' | relative_url }}): every case with its rows, points and which engines Eddy3D
has scored. Pin a release (`/api/3.2.0/...`) when the numbers must stay reproducible.

## 3. Read the case

[`GET /api/cases/A.json`]({{ '/api/cases/A.json' | relative_url }}). Read `frame`, `units` and `known_issues` before
anything else: they differ per case. `scoring` says what the measured side is divided by (`U_ref_m_s`, Case A's
$$U_H = 4.491$$ m/s) and how each instrument is scored; `inflow` is the inlet contract (step 5).

## 4. Fetch the points to probe

[`GET /api/cases/A/probes.csv`]({{ '/api/cases/A/probes.csv' | relative_url }}): one row per measured row of the point
table: the key columns (`point_id`, `config`, `campaign`, `instrument`, `run`, `wind_direction_deg`), `x y z` in the case
frame and units, and `scored_as`, the families the row is scored in. Probe your field at exactly these coordinates; do not
interpolate the reference. For Case A that is 186 points. Cases C, D, E and F have several configurations and wind
directions in one file: keep the rows of the ones you solve, and each is scored as its own group.

## 5. Set the inlet

[`GET /api/cases/A/inflow_openfoam.txt`]({{ '/api/cases/A/inflow_openfoam.txt' | relative_url }}) holds `0/U`, `0/k`,
`0/epsilon` (the `atmBoundaryLayerInlet*` conditions of OpenFOAM 12), `0/nut` with the `nutkAtmRoughWallFunction` ground
patch, and `system/probes`, a probes function object with the case's points, each after a `==== <path>` line. The
[inlet contract]({{ '/validation/inflow/' | relative_url }}) page says what is the benchmark's data (the measured
profile, `approach_flow.csv`) and what is this repository's recommendation (the log-law fit, $$k$$ and $$\varepsilon$$
from the ABL relations). Any inlet is allowed; a submission records which one it used.

## 6. Run your solver and probe

Solve the case in its own frame and units (Case A is model scale: $$H = 0.16$$ m, the tunnel's own speeds). Probe at the
points of step 4. Write your values into new columns of your copy of `probes.csv`:

| column | what | units (`units: normalised`, the default) |
|---|---|---|
| `U`, `V`, `W` | the mean velocity components in the case frame | over $$U_H$$ |
| `speed` | the speed $$\lvert\mathbf{U}\rvert$$ (computed from the components when absent) | over $$U_H$$ |
| `k` | turbulent kinetic energy | over $$U_H^2$$ |
| `cstar` | the dimensionless concentration $$c^\ast = c\thinspace U_H H^2/Q$$ (the case's `normalisation`) | — |
| `theta` or `T` | the floor-referenced temperature fraction, or the temperature in °C (Cases J and L) | — or °C |

{% include nomenclature.md %}

With `units: si` in `submission.yaml` you give m/s and m²/s², and the script divides by the case's `U_ref_m_s`. Cases
E, F and G publish ratios and have no reference speed: give ratios over your own approach flow, as their
`scoring.U_ref_meaning` says.

## 7. Score

Put the file in a submission folder (step 10 shows the layout; `submission.yaml` is ten lines about your solver) and run,
from the checkout:

```bash
uv run python validation/score_submissions.py submissions/my-solver
```

It checks the folder, prints one line per score, and with `--out results/` writes `<case>.json` (the same shape as the
served results: every metric, the `headline` map, the `coverage` of each score). Case A scores $$U$$, $$V$$, $$W$$ as signed
velocities (FAC2's ratio keeps the sign; hit rate $$\delta_{\mathrm{rel}} = 0.25$$, $$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$),
and $$k$$ by the plain definitions, exactly as the [method]({{ '/validation/method/' | relative_url }}) page defines
them. If you give the served pairs of Eddy3D's Case A run as your file, you get the served scores back: that is the
example submission.

## 8. The thermistor bracket

Cases C, D, E and F (and G's sonic anemometer) measured a mean *scalar* speed, which a RANS mean velocity cannot
reproduce. Give `U`, `V`, `W` (or `speed`) and `k`, and the script scores the measurement twice: against
$$\lvert\mathbf{U}\rvert$$ (`vs.vector`) and against $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$ (`vs.scalar`), the two ends
of the bracket the thermistor reading has to fall in. Quote both.

## 9. Partial coverage

You may score a subset: one configuration, one wind direction, a few quantities. Each score then carries its coverage,
the points scored over the points the benchmark measured in that group, and the community page shows it as `n/N`, so a
partial submission cannot pass for a full one. A row that matches no published point is counted and reported, not
silently dropped.

## 10. Submit

Make the folder `submissions/<your-slug>/` in a fork of the repository:

```text
submissions/my-solver/
  submission.yaml           solver, version, url, author, licence, contact, inlet, mesh, turbulence_model (or ml_description), compute
  cases/A/probes.csv        the probe keys plus your value columns (step 6)
  cases/C/probes.csv        more cases, each in its own folder
```

Run step 7 once more, then open a pull request that adds the folder. CI scores it again in the pinned build (the result
is a file under `validation/results/submissions/`), the API serves it as `/api/submissions/<slug>.json`, and the
[Community results]({{ '/community/' | relative_url }}) page gets a row, labelled *self-reported, scored by this
repository's CI*. Eddy3D's own results stay on the [Validation]({{ '/validation/' | relative_url }}) page: a submission
is scored by the same code but is not one of them. See [CONTRIBUTING.md](https://github.com/Eddy3D-Dev/AIJ-Data-Validation/blob/main/CONTRIBUTING.md)
for the rules of a pull request; the example `submissions/example-openfoam12/` is the layout to copy.

## What is not scored

Controls (sign flips, mirrored frames, ceilings), subsets (points above two cells, far from the source) and the ML
surrogate's runs are Eddy3D's own analyses; the script scores the plain quantities at the published points. Case M's
field campaign and Case F's field observations are groups like any other: give values for them and they are scored.
