An Eddy3D production run, realizable k-ε at numerics level 3 and 3000 iterations, at 1:60, with the probe at the tunnel's own coordinates. Case I was also solved with standard k-ε and with k-ω SST on the same mesh.

- Velocities are divided by $$U_H$$, $$k$$ by $$U_H^2$$, with $$U_H$$ = 1.7 m/s for the measurement and for the model.
- Concentration: the cleaned table's $$C/c_0$$ ($$c_0$$ = 39.22 ppm) against the model's $$c^\ast = c\thinspace U_H H^2/Q$$, scored at the turbulent Schmidt numbers 0.3, 0.5 and 0.7 (the figures show 0.5). One detection limit, $$10^{-3}$$ of the largest measured value.

### Measured against modelled

{% include figure.html name="case-i-openfoam-agreement.png" alt="Measured vs modelled, Case I" caption="<strong>Figure 2.</strong> Case I, measured vs modelled $$U$$, $$W$$, $$k$$ and $$c^\ast$$, realizable k-ε; the dots take the colour of the line or plane they were measured on, as in Figure 1. The concentration panel shows the positive pairs only." %}

FB is positive when the model is low.

- **Flow.** $$U$$: R 1.00, FAC2 0.88. $$W$$: R 0.97. $$k$$: R 0.91, FAC2 0.92. $$V$$ is scored at the 38 points off the $$y = 0$$ plane; on the plane the workbook holds numerical zeros, which are left out. $$V$$: FB −2.0 on a near-zero mean, R 0.99.
- **Concentration.** R is 0.92 to 0.95 and FAC2 stays below 0.5. FB +0.40 at 0.3, +0.08 at 0.5 and −0.10 at 0.7. [Case H]({{ '/cases/case-h/validation/' | relative_url }}) has a negative FB (model high) at all three.

<details markdown="block">
<summary>Interpretation: Case I scores</summary>

- Velocity and $$k$$ agree closely. $$V$$'s FB of −2.0 comes from a near-zero mean.
- The concentration is well correlated, with a wide scatter at low concentration (visible in panel d). The bias changes sign with the Schmidt number: the model is low at 0.3, nearly unbiased at 0.5 and high at 0.7. Case H over-predicts at all three, so the Schmidt number that suits one case does not suit the other.

</details>

### Turbulence closures

{% include figure.html name="case-i-openfoam-closures.png" alt="Case I under three turbulence closures" caption="<strong>Figure 3.</strong> Case I under standard k-ε, realizable k-ε and k-ω SST on one mesh, dots coloured as in Figure 1: measured vs modelled $$U$$, $$k$$ and $$c^\ast$$ ($$\mathrm{Sc_t}$$ 0.5)." %}

| Closure | $$U$$ R | $$U$$ FAC2 | $$k$$ R | $$k$$ FAC2 | $$k$$ FB | $$c^\ast$$ ($$\mathrm{Sc_t}$$ 0.5) R | $$c^\ast$$ FAC2 | $$c^\ast$$ FB |
|---|---|---|---|---|---|---|---|---|
| standard k-ε | +0.990 | 0.846 | +0.870 | 0.912 | −0.037 | +0.955 | 0.519 | −0.035 |
| realizable k-ε | +0.998 | 0.879 | +0.905 | 0.923 | +0.106 | +0.940 | 0.475 | +0.083 |
| k-ω SST | +0.992 | 0.879 | +0.880 | 0.396 | +0.495 | +0.466 | 0.403 | −0.153 |
{: .scores }

{% include nomenclature-scores.md %}

- $$U$$: R is 0.99 to 1.00 and FAC2 0.85 to 0.88 under all three.
- The two k-ε closures keep $$k$$ within a factor of two at more than 90 % of the points (FAC2 0.912 and 0.923) and give a concentration with R of 0.94 to 0.96. Under k-ω SST, $$k$$ FAC2 is 0.40 (FB +0.49, model low) and the concentration's R is 0.47.
- Mean $$k/U_H^2$$ of the approach profile: 0.0006 under k-ω SST, 0.0075 under both k-ε closures.
- Reattachment length $$L_r/H$$: 2.23 (standard k-ε), 2.51 (realizable k-ε), 2.68 (k-ω SST).

<details markdown="block">
<summary>Interpretation: Case I turbulence closures</summary>

- The mean velocity does not tell the closures apart. $$k$$ and the concentration do.
- Under k-ω SST the turbulence is lower from the inlet on.
- This ranks three closures on one cube, one mesh and this release's numerics.

</details>

### Vertical profiles

Where along the height the model meets the measurement, station by station.

{% include figure.html name="case-i-openfoam-profiles.png" alt="Vertical profiles, Case I" caption="<strong>Figure 4.</strong> Case I, vertical profiles of $$U/U_H$$ on the centre plane $$y = 0$$ at four stations along the measured lines, measured points against the modelled line, offset by 1 per station; the dashed line is the roof height." %}

### Field maps

The solved velocity on the measured planes, every point drawn on it as a dot coloured by its measured value on the same scale: a dot that stands out from the colour around it is a point the model misses.

{% include figure.html name="case-i-openfoam-field-section.png" alt="Solved field and measured points, Case I, section" caption="<strong>Figure 5.</strong> Case I, the centre plane $$y = 0$$, realizable k-ε: (a) $$u$$ over $$U_H$$; (b) the same with iso-lines every 0.1 and the edge of the reversed flow, $$u = 0$$, dashed; (c) the in-plane speed with streamlines." %}
