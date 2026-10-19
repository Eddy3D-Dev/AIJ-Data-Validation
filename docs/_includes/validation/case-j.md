**urbanMicroclimateFoam.** Case J is non-isothermal: a floor held at 45.8 °C under a cooler approach flow (bulk Richardson number −0.086), with an ethylene tracer released from the floor. Eddy3D solved it with its buoyant microclimate engine, urbanMicroclimateFoam (UMF, the Outdoor+ plugin), an OpenFOAM 12 solver developed at ETH Zurich and Empa (its engine ids are on the [Validation]({{ '/validation/' | relative_url }}) overview; Eddy3D owns none of its physics). The isothermal OpenFOAM 12 engine is *pending* on this case: it was not run.

- **What each run is.** Solved on 2026-10-18. The 1:1:2 building on a floor 33.6 K warmer than the approach air at building height, 236,408 air cells, under UMF's two closures, realizable k-ε (the shipped one) and `buoyantKEpsilon` (which carries the buoyancy production the neutral closure lacks); two engine ids, `umf-realizableKE` and `umf-buoyantKEpsilon`. The air region stopped at its 1500-iteration cap with the residual control unmet; at the last iteration the initial residuals of $$U_y$$ and `p_rgh` were of the order of $$10^{-2}$$ and those of the tracers $$10^{-3}$$. Solved on one mesh, with a steady tracer solved beside the flow as three species (turbulent Schmidt numbers 0.3, 0.5 and 0.7, all published).
- **Froude scale.** The production case writer cannot mesh the tunnel model, so the scene is the tunnel scaled by 62.5: lengths times the scale, velocities times its square root, temperatures unchanged. The Richardson number, Pr and the Kelvin values are kept; the Reynolds number is not ($$1.6 \times 10^{4}$$ in the tunnel, $$8 \times 10^{6}$$ in the scene). Every pair is in the tunnel's units: coordinates divided by the scale, velocities by the scene's $$U_H$$, $$k$$ by its square.
- **Temperature** is scored as the floor-referenced fraction $$\theta = (T_f - T)/(T_f - T_H)$$, 0 at the floor and 1 in the approach air at the building height (the workbook's own normalisation). $$\theta$$ lies between 0.4 and 1.1. The temperature errors in kelvin are in the files (`temperature.all`).
- **Concentration** is the measured $$C/c_0$$ ($$c_0$$ = 12.28 ppm) against the model's ethylene mass fraction as ppm over the same $$c_0$$, with one detection limit of $$10^{-3}$$ of the largest measured value.
- **Measured side.** Point 153 repeats point 1 (the crossing of two planes, identical values) and is left out: 443 points.
- **Tracer mass balance.** The outlet carried 0.62 to 0.95 (0.89, 0.75 and 0.62 under rk-ε; 0.95, 0.84 and 0.73 under bKε, for $$\mathrm{Sc_t}$$ 0.3, 0.5 and 0.7) of the emission.
- FB is positive when the model is low, and is left out (—) for a signed component whose measured and modelled means are not both positive.

<details markdown="block">
<summary>Interpretation: Engine, scale and temperature scoring</summary>

- The isothermal OpenFOAM 12 solver Eddy3D uses for the other cases cannot represent a heated floor, which is why this case was solved with UMF.
- Temperature FAC2 is 1.00 almost everywhere because $$\theta$$ lies between 0.4 and 1.1, so R and the hit rate carry the comparison.
- The Froude scale keeps the Richardson number, Pr and the Kelvin values and changes the Reynolds number, so the wall-function regime of the model differs from the tunnel's.

</details>

## Measurement layout

{% include figure.html name="case-j-layout.png" alt="Measurement lines and planes, Case J" caption="<strong>Figure 1.</strong> Case J, measurement lines and planes: A vertical profiles, $$y/H = 0$$; B plane $$z/H = 0.025$$; C plane $$z/H = 0.25$$. Positions in multiples of $$H$$." %}

## UMF: measured against modelled

{% include figure.html name="case-j-umf-agreement.png" alt="Case J, measured vs modelled velocity, k and temperature" caption="<strong>Figure 2.</strong> Case J under realizable k-ε (top) and buoyantKEpsilon (bottom): measured vs modelled $$U$$, $$W$$, $$k$$ and the floor-referenced temperature $$\theta$$; the dots take the colour of the line or plane they were measured on, as in Figure 1." %}

| Quantity | R (rk-ε) | FAC2 | FB | R (bKε) | FAC2 | FB |
|---|---|---|---|---|---|---|
| $$U$$ | +0.921 | 0.731 | +0.193 | +0.924 | 0.761 | +0.167 |
| $$V$$ | +0.866 | 0.449 | — | +0.901 | 0.442 | — |
| $$W$$ | +0.840 | 0.289 | — | +0.849 | 0.289 | — |
| $$k$$ | +0.322 | 0.558 | −0.034 | +0.360 | 0.582 | −0.088 |
| $$\theta$$ | +0.922 | 1.000 | +0.120 | +0.920 | 0.998 | +0.127 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3 | +0.919 | 0.858 | +0.065 | +0.894 | 0.869 | −0.050 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5 | +0.905 | 0.847 | −0.162 | +0.869 | 0.840 | −0.274 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7 | +0.896 | 0.828 | −0.256 | +0.852 | 0.806 | −0.380 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.3, without the near-source points | +0.874 | 0.760 | +0.240 | +0.829 | 0.757 | +0.052 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.5, without the near-source points | +0.860 | 0.752 | +0.067 | +0.788 | 0.731 | −0.193 |
| $$c^\ast$$, $$\mathrm{Sc_t}$$ 0.7, without the near-source points | +0.848 | 0.728 | +0.025 | +0.755 | 0.709 | −0.292 |
{: .scores }

{% include nomenclature-scores.md %}

n is 443 (416 without the 27 points within a quarter of a building height of the source); rk-ε is realizable k-ε and bKε is buoyantKEpsilon.

- **Flow.** $$U$$: $$R = 0.92$$ under both closures, FAC2 0.73 and 0.76; the mean $$U/U_H$$ is 0.465 and 0.477 modelled against 0.564 measured. FB in the wake (rk-ε and bKε): +0.36 and +0.29 in the near wake, +0.48 and +0.43 in the far wake. Reattachment at $$z/H = 0.25\text{ and }0.025$$ is $$1.35\thinspace H$$ and $$1.35\thinspace H$$ (rk-ε) or $$1.35\thinspace H$$ and $$1.56\thinspace H$$ (bKε), against the measured $$0.68\thinspace H$$ and $$0.80\thinspace H$$. Scored against the mean of each mirror pair, the measurement has $$R = 0.99$$ for $$U$$; the $$+y$$ half of the $$z/H = 0.25$$ plane is 11 % slower than the $$-y$$ half (97 pairs, R 0.955).
- **$$k$$.** R is 0.32 and 0.36; the means are 0.030 and 0.031 modelled, 0.029 measured.
- **Temperature.** $$\theta$$: $$R = 0.92$$ and hit rate 0.82 and 0.81. In kelvin the mean bias is +3.46 K (rk-ε) and +3.63 K (bKε), the root-mean-square error 4.53 K and 4.80 K, $$R = 0.92$$. The model's first cell is 12 mm at tunnel scale; the tunnel's 24 K drop between the floor and the first measurement at 3 mm lies inside it.
- **Tracer.** R is 0.92 to 0.90 (rk-ε) and 0.89 to 0.85 (bKε) from $$\mathrm{Sc_t}$$ 0.3 to 0.7. Under rk-ε the model is low at $$\mathrm{Sc_t}$$ 0.3 (FB +0.065) and high at 0.5 and 0.7 (−0.162, −0.256). The modelled peak at the measured points is 275, 339 and 373 against a measured peak of 437. By region at $$\mathrm{Sc_t}$$ 0.5 under rk-ε (R, FAC2): above the roof +0.78 and 0.33 (75 points), beside the building +0.82 and 0.40 (60), the near wake +0.90 and 0.75 (168), the far wake +0.89 and 0.82 (56), upstream −0.18 and 0.05 (84). Upstream the tunnel measures a background of 0.018 $$c_0$$ on average (about 0.2 ppm, below the workbook's expanded uncertainty noted in the known data issues) and the model has a mean of $$4 \times 10^{-5}$$ $$c_0$$ and a largest value of $$1.4 \times 10^{-3}$$ at $$\mathrm{Sc_t}$$ 0.5 under rk-ε.
- **Closures compared.** buoyantKEpsilon against realizable k-ε: $$U$$'s R 0.924 against 0.921, $$U$$'s FAC2 0.761 against 0.731, $$k$$'s R 0.36 against 0.32. The tracer's R is lower by 0.025 to 0.044 and FB lower by 0.11 to 0.12.

<details markdown="block">
<summary>Interpretation: Case J flow, temperature and tracer</summary>

- The flow is reproduced in pattern and low in level. The deficit is largest in the wake. The steady closures give a recirculation that is too long.
- The tunnel's mirror-pair ceiling ($$R = 0.99$$) is above the model's R of 0.92.
- $$k$$ is not reproduced. The means are close, so the agreement in FB is not agreement in pattern.
- The model is warmer than the tunnel. Near-floor temperature is a wall-function result, because the tunnel's 24 K drop lies inside the model's first cell.
- The tracer pattern is correlated at every Schmidt number, and the bias changes sign. The near-source points are low; in Cases H and K they are high.
- Upstream, FAC2 is small whatever the model does, because the tunnel measures a background the model has almost none of.
- The two closures differ little in the flow and more in the tracer: the modelled concentration is higher under buoyantKEpsilon. This ranks two closures on one building, one mesh and a run capped at 1500 iterations.

</details>

{% include figure.html name="case-j-umf-tracer.png" alt="Case J, measured vs modelled tracer concentration" caption="<strong>Figure 3.</strong> Case J, dots coloured as in Figure 1: measured vs modelled $$c^\ast$$ at three turbulent Schmidt numbers under both closures. The concentration panels show the positive pairs within seven decades; the points within a quarter of a building height of the source are open." %}

## Not run and not modelled

- A second mesh, a longer iteration count and a transient run.
- OpenLB, FluidX3D and the ML surrogate.
- Not represented in the model (Eddy3D's list): the release momentum and the gas's own heat; the tunnel's side walls and ceiling (slip here); radiation (emissivity 0.01, effectively off); the measured 4 K gradient up the building's walls.

<details markdown="block">
<summary>Interpretation: Limits of these runs</summary>

- The air region reached its cap with residuals near $$10^{-2}$$, so these numbers are those of an unconverged steady solve on one mesh.
- The tracer balance closes within a factor of two; why part of the emission is missing at the outlet was not investigated.

</details>
