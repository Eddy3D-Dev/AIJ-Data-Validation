An Eddy3D production run solved on 2026-10-18, realizable k-ε at numerics level 3 and 3000 iterations, on one mesh. The solve ran to the iteration limit with the SIMPLE residual control unmet; the initial residual of epsilon at the last iteration was $$7 \times 10^{-3}$$.

- The tunnel at 1:100 ($$H = 6\thinspace\mathrm{m}$$). Measured and modelled velocities are both divided by the dataset's stated $$U_H$$ = 2.33 m/s, and $$k$$ by $$U_H^2$$. The model is driven by the measured approach profile (3.23 m/s at 0.2 m), which gives 1.97 m/s at $$z = H$$, 0.85 of the stated $$U_H$$.
- The concentration is the measured $$C/c_0$$ ($$c_0$$ = 429.2 ppm) against the model's $$c^\ast = c\thinspace U_H H^2/Q$$ at the turbulent Schmidt numbers 0.3, 0.5 and 0.7, three species on one flow; all three are published.

### Measured against modelled

{% include figure.html name="case-k-openfoam-agreement.png" alt="Case K, measured vs modelled" caption="<strong>Figure 2.</strong> Case K, measured vs modelled $$U$$, $$W$$, $$k$$ and $$c^\ast$$ at three turbulent Schmidt numbers; the dots take the colour of their line in Figure 1. The concentration panels show the positive pairs within five decades; the four points within one cube height of the source are open." %}

| Quantity | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$ | +0.958 | 0.586 | +0.594 | 0.123 | 203 |
| $$V$$ | −0.151 | 0.054 | — | 0.901 | 203 |
| $$W$$ | +0.573 | 0.143 | — | 0.685 | 203 |
| $$k$$ | +0.330 | 0.044 | +1.201 | 0.005 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.953 | 0.793 | −0.690 | 0.458 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.951 | 0.685 | −0.875 | 0.163 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.950 | 0.394 | −0.983 | 0.099 | 203 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, without the 4 near-source points | +0.923 | 0.799 | −0.218 | 0.467 | 199 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, without the 4 near-source points | +0.941 | 0.698 | −0.430 | 0.161 | 199 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, without the 4 near-source points | +0.923 | 0.402 | −0.561 | 0.101 | 199 |
| $$U$$, y-symmetric ceiling (control) | +1.000 | 1.000 | +0.000 | 1.000 | 203 |
| $$c^\ast$$, y-symmetric ceiling (control) | +0.997 | 0.995 | +0.000 | 0.793 | 203 |
{: .scores }

FB is positive when the model is low, and is left out (—) for a signed component whose measured and modelled means are not both positive.

- **Velocity.** $$U$$: $$R = 0.96$$, FAC2 0.59; the mean $$U/U_H$$ is 0.272 modelled against 0.502 measured (FB +0.59). FB by region: +0.35 over the roofs (31 points, FAC2 1.00, R +0.06), +0.79 in the streets along the wind (44 points, R +0.997, FAC2 0.34) and +0.78 in the streets across it (128 points, R +0.95, FAC2 0.57). Both sides are divided by 2.33 m/s; the solved $$U$$ at $$z = H$$ is 0.85 of that.
- **$$k$$.** The mean $$k/U_H^2$$ is 0.027 modelled against 0.107 measured; R is 0.33 and FAC2 0.04.
- **$$V$$ and $$W$$.** $$V$$ has a constant offset in the tunnel and almost no antisymmetric part. A model with $$V$$ = 0 everywhere hits 0.91 of the points ($$\delta_{\mathrm{abs}} = 0.05\thinspace U_H$$); $$V$$'s hit rate is 0.90 and its R is −0.15. $$W$$: $$R = +0.57$$, FAC2 0.14.
- **Concentration.** R is 0.95 at every Schmidt number. FAC2 falls from 0.79 to 0.39 and FB from −0.69 to −0.98 as the Schmidt number rises; the mean $$c^\ast$$ is 0.374 measured against 0.768, 0.956 and 1.097 modelled. The modelled peak at the measured points is 44, 57 and 66 against a measured peak of 8.73. The four points within one cube height of the source (the first point *is* the source location) are 3.7, 4.5 and 5.1 times the measured value on average. Without those four points: FB −0.22, −0.43 and −0.56, FAC2 0.80, 0.70 and 0.40, R 0.92, 0.94 and 0.92. Case H has FB −0.60, −0.83 and −0.93 at the same three Schmidt numbers ([Case H]({{ '/cases/case-h/validation/' | relative_url }})).
- **Symmetry.** The measured plume is not y-symmetric: C at $$-y$$ exceeds C at $$+y$$ at 74 of 74 mirror pairs, and Eddy3D puts the measured plume's lateral centroid 0.011 to 0.017 m toward $$-y$$. The solve is y-symmetric. Scored against the mean of each mirror pair, the measurement has $$R = 1.00$$ for $$U$$ and $$R = 0.997$$, FAC2 0.995 for $$c^\ast$$ (the ceiling-control rows).
- **First ground cell.** 47 of the 203 points (the $$z = 4\thinspace\mathrm{mm}$$ plane) are inside the first ground cell; their modelled values are that cell's, pulled toward the wall's zero by the interpolation.
- **Flow structure.** The air over the roofs outruns the street along the wind, which outruns the cavity across it; the plume is clean 1 to $$1.5\thinspace H$$ ahead of the array, decays through four cavities and is cleaner over the roofs than in them; the solved velocity is y-symmetric to twice the tunnel's own mirror-pair difference.

<details markdown="block">
<summary>Interpretation: Case K velocity, k and concentration</summary>

- The modelled velocity is under the measured mean in every region. Part of the deficit is the inflow.
- $$k$$ is a factor of four low and uncorrelated: the model starts with more $$k$$ than the tunnel (the inlet $$k$$ of the log-law inflow is about 1.7 times the tunnel's) and has less at the points.
- $$V$$ and $$W$$ carry little. $$V$$'s hit rate of 0.90 scores nothing, because a model with $$V$$ = 0 everywhere hits almost as many points.
- The concentration pattern is correlated and the level is high. The excess at the four near-source points follows from the model's source: the four cells (0.75 m across) that a 0.44 m square cuts, where the tunnel's outlet is 5 mm.
- The ceiling scores of a y-symmetric model are far above the model's, so symmetry does not limit the scores. In Eddy3D's own results a lateral shift of the model by +0.01 m raises R of $$c^\ast$$ at $$\mathrm{Sc_t}$$ 0.5 from 0.951 to 0.975 (not recomputed here).

</details>

### Vertical profiles

Where along the height the model meets the measurement, station by station.

{% include figure.html name="case-k-openfoam-profiles.png" alt="Vertical profiles, Case K" caption="<strong>Figure 3.</strong> Case K, vertical profiles of $$U/U_H$$ on the centre plane $$y = 0$$ at four stations along the measured lines, measured points against the modelled line, offset by 1 per station; the dashed line is the roof height." %}

### Field maps

The solved velocity on the measured planes, every point drawn on it as a dot coloured by its measured value on the same scale: a dot that stands out from the colour around it is a point the model misses.

{% include figure.html name="case-k-openfoam-field-plan.png" alt="Solved field and measured points, Case K, plan" caption="<strong>Figure 4.</strong> Case K, the horizontal plane $$z = 0.01\thinspace\mathrm{m}$$: (a) $$u$$ over $$U_H$$; (b) the same with iso-lines every 0.1 and the edge of the reversed flow, $$u = 0$$, dashed; (c) the in-plane speed with streamlines." %}

{% include figure.html name="case-k-openfoam-field-section.png" alt="Solved field and measured points, Case K, section" caption="<strong>Figure 5.</strong> Case K, the centre plane $$y = 0$$: (a) $$u$$ over $$U_H$$; (b) the same with iso-lines every 0.1 and the edge of the reversed flow, $$u = 0$$, dashed; (c) the in-plane speed with streamlines." %}
