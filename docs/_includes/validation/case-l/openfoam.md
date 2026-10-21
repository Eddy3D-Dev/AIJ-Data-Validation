Case L is non-isothermal: a floor held at 45.0 °C under a cooler approach flow (bulk Richardson number −0.034), with an ethylene tracer released from the floor. Eddy3D solved it with its buoyant microclimate engine, urbanMicroclimateFoam (UMF, the Outdoor+ plugin), an OpenFOAM 12 solver developed at ETH Zurich and Empa (its engine ids are on the [Validation]({{ '/validation/' | relative_url }}) overview; Eddy3D owns none of its physics). The isothermal OpenFOAM 12 solver was not run on this case.

- **What the run is.** Solved on 2026-10-18. 126 cubes (14 rows × 9 columns), 754,940 air cells, realizable k-ε. The air region stopped at its 1500-iteration cap with the residual control unmet; at the last iteration the initial residuals of $$U_y$$ and `p_rgh` were of the order of $$10^{-2}$$ and those of the tracers $$10^{-3}$$. Solved on one mesh, with a steady tracer solved beside the flow as three species (turbulent Schmidt numbers 0.3, 0.5 and 0.7, all published).
- **Froude scale.** The production case writer cannot mesh the tunnel model, so the scene is the tunnel scaled by 100: lengths times the scale, velocities times its square root, temperatures unchanged. The Richardson number, Pr and the Kelvin values are kept; the Reynolds number is not. Every pair is in the tunnel's units: coordinates divided by the scale, velocities by the scene's $$U_H$$, $$k$$ by its square.
- **Temperature** is scored as the floor-referenced fraction $$\theta = (T_f - T)/(T_f - T_H)$$, 0 at the floor and 1 in the approach air at the building height (the workbook's own normalisation). $$\theta$$ lies between 0.4 and 1.1. The temperature errors in kelvin are in the files (`temperature.all`).
- **Concentration** is the measured $$C/c_0$$ ($$c_0$$ = 1728 ppm) against the model's ethylene mass fraction as ppm over the same $$c_0$$, with one detection limit of $$10^{-3}$$ of the largest measured value.
- **Tracer mass balance.** The outlet carried 0.86, 0.73 and 0.70 (for $$\mathrm{Sc_t}$$ 0.3, 0.5 and 0.7) of the emission.
- FB is positive when the model is low, and is left out (—) for a signed component whose measured and modelled means are not both positive.

<details markdown="block">
<summary>Interpretation: Engine, scale and temperature scoring</summary>

- The isothermal OpenFOAM 12 solver Eddy3D uses for the other cases cannot represent a heated floor, which is why this case was solved with UMF.
- Temperature FAC2 is 1.00 almost everywhere because $$\theta$$ lies between 0.4 and 1.1, so R and the hit rate carry the comparison.
- The Froude scale keeps the Richardson number, Pr and the Kelvin values and changes the Reynolds number, so the wall-function regime of the model differs from the tunnel's.

</details>

### Measured against modelled

{% include figure.html name="case-l-umf-agreement.png" alt="Case L, measured vs modelled" caption="<strong>Figure 2.</strong> Case L under realizable k-ε: measured vs modelled $$U$$, $$W$$, $$k$$, $$\theta$$, $$V$$ and $$c^\ast$$ at three turbulent Schmidt numbers, in the tunnel's units; the dots take the colour of their class in Figure 1." %}

| Quantity | R | FAC2 | FB | Hit rate | n |
|---|---|---|---|---|---|
| $$U$$ | +0.918 | 0.608 | +0.268 | 0.506 | 344 |
| $$V$$ | −0.037 | 0.291 | −0.795 | 0.747 | 344 |
| $$W$$ | −0.027 | 0.183 | — | 0.762 | 344 |
| $$\lvert\mathbf{U}\rvert$$ | +0.898 | 0.674 | +0.206 | 0.515 | 344 |
| $$k$$ | +0.145 | 0.584 | +0.635 | 0.244 | 344 |
| $$\theta$$ | +0.936 | 1.000 | +0.049 | 0.985 | 344 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.798 | 0.759 | −0.498 | 0.468 | 344 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.766 | 0.683 | −0.649 | 0.387 | 344 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.746 | 0.602 | −0.731 | 0.358 | 344 |
| $$U$$, points at or above 30 mm | +0.902 | 0.798 | +0.147 | 0.669 | 242 |
| $$k$$, points at or above 30 mm | +0.468 | 0.802 | +0.364 | 0.343 | 242 |
| $$\theta$$, points at or above 30 mm | +0.944 | 1.000 | +0.041 | 1.000 | 242 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, points at or above 30 mm | +0.814 | 0.715 | −0.495 | 0.430 | 242 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, points at or above 30 mm | +0.821 | 0.636 | −0.583 | 0.351 | 242 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, points at or above 30 mm | +0.816 | 0.541 | −0.624 | 0.302 | 242 |
| $$V$$, lateral sign flipped (control) | +0.037 | 0.110 | — | 0.695 | 344 |
| $$U$$, approach column alone (control) | +0.861 | 0.846 | −0.205 | 0.599 | 344 |
| $$\theta$$, approach column alone (control) | +0.925 | 1.000 | −0.117 | 0.837 | 344 |
| $$U$$, y-symmetric ceiling (control) | +0.984 | 0.986 | +0.000 | 0.860 | 292 |
{: .scores }

{% include nomenclature-scores.md %}

The 51 points at $$z = 4\thinspace\mathrm{mm}$$ lie inside the model's first fine cell (0.75 m, 0.4 m at 1:100), a wall-function cell; the 242 points at or above 30 mm are scored separately.

- **Flow.** $$U$$: $$R = 0.92$$, and the mean $$U/U_H$$ is 0.499 modelled against 0.654 measured; at or above 30 mm R is 0.90 and FAC2 0.80. Against the undisturbed approach column, the model's R is higher ($$U$$: 0.918 against 0.861; $$\theta$$: 0.936 against 0.925). The model's mean $$U/U_H$$ in the streets is 0.045 below 30 mm and 1.11 above 110 mm, against the tunnel's 0.297 and 1.068. $$V$$ and $$W$$: R is −0.04 and −0.03, and with the sign of $$V$$ flipped it is +0.04.
- **$$k$$.** $$R = 0.15$$ (0.47 at or above 30 mm), FB +0.64.
- **Temperature.** $$\theta$$: $$R = 0.94$$, hit rate 0.99. The mean bias is +1.17 K, the mean absolute error 1.59 K and the root-mean-square error 2.11 K.
- **Tracer.** R is 0.80, 0.77 and 0.75 from $$\mathrm{Sc_t}$$ 0.3 to 0.7 (0.81 to 0.82 at or above 30 mm); FAC2 falls from 0.76 to 0.60 and FB from −0.50 to −0.73. The largest modelled $$c^\ast$$ is 3.3, 4.0 and 5.0 (at $$y = -0.12,\thinspace +0.18\text{ and }+0.18\thinspace\mathrm{m}$$, in the source street) against the tunnel's 1.93 at (−0.15, −0.12, 0.004).

<details markdown="block">
<summary>Interpretation: Case L flow, temperature and tracer</summary>

- The streamwise flow and the temperature follow the tunnel; the streets do not. The model beats the undisturbed approach column on R, which is the number a model of the array has to beat. The street air is nearly stagnant in the model. $$V$$ and $$W$$ carry no pattern.
- $$k$$ is low and weakly correlated.
- The model is warmer by 1.2 K on average.
- The tracer is over-predicted and the pattern is correlated.

</details>

### Vertical profiles

Where along the height the model meets the measurement, station by station.

{% include figure.html name="case-l-openfoam-profiles.png" alt="Vertical profiles, Case L" caption="<strong>Figure 3.</strong> Case L, vertical profiles of $$U/U_H$$ on the centre plane $$y = 0$$ at four stations along the measured lines, measured points against the modelled line, offset by 1 per station; the dashed line is the roof height." %}

### Field maps

The solved velocity on the measured planes, every point drawn on it as a dot coloured by its measured value on the same scale: a dot that stands out from the colour around it is a point the model misses.

{% include figure.html name="case-l-umf-field-plan.png" alt="Solved field and measured points, Case L, plan" caption="<strong>Figure 4.</strong> Case L, the horizontal plane $$z = 0.01\thinspace\mathrm{m}$$: (a) $$u$$ over $$U_H$$; (b) the same with iso-lines every 0.1 and the edge of the reversed flow, $$u = 0$$, dashed; (c) the in-plane speed with streamlines." %}

{% include figure.html name="case-l-umf-field-section.png" alt="Solved field and measured points, Case L, section" caption="<strong>Figure 5.</strong> Case L, the centre plane $$y = 0$$: (a) $$u$$ over $$U_H$$; (b) the same with iso-lines every 0.1 and the edge of the reversed flow, $$u = 0$$, dashed; (c) the in-plane speed with streamlines." %}
