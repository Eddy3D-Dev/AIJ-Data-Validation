**OpenFOAM 12.** Eddy3D production runs solved on 2026-10-18, realizable k-ε at numerics level 3 and 3000 iterations, on one mesh. The solves ran to the iteration limit with the SIMPLE residual control unmet; the initial residual of epsilon at the last iteration was $$2.7 \times 10^{-2}$$ to $$3.6 \times 10^{-2}$$.

- A field observation at full scale. The measurement is $$U/U_H$$ and $$k/U_H^2$$ at 28 points, $$U_H$$ the wind at the tree height (7 m) during each period.
- Eddy3D models trees as a Darcy-Forchheimer momentum sink only. The leaf area density (LAD) and drag coefficient (Cd) of the belt are not in the dataset (only its shading rate, 81 %); the drag values are crowns of the Eddy3D vegetation library.
- Eddy3D solved a **sweep**: no belt, and three crowns from its vegetation library of rising Cd·LAD (0.30, 0.625 and 0.875 1/m), on a two-dimensional slab, and the conifer crown on the real 74 m belt as a half domain. Each arm is a separate run.
- The model is divided by its own $$U(7\text{ m})$$ at $$x = -35\thinspace\mathrm{m}$$, because the tabulated inlet has a smooth floor and the approach does not stay the imposed profile; scores over the imposed $$U_H$$ = 5.299 m/s are in the files too.

## Measurement layout

{% include figure.html name="case-g-layout.png" alt="Measurement lines and planes, Case G" caption="<strong>Figure 1.</strong> Case G, measurement lines and planes: A to G vertical profiles, $$x/H = 0.25,\thinspace 0.5,\thinspace 1,\thinspace 2,\thinspace 3,\thinspace 4,\thinspace 5$$. Positions in multiples of $$H$$." %}

## OpenFOAM 12: measured against modelled

{% include figure.html name="case-g-openfoam-sweep.png" alt="Case G, measured vs modelled, drag sweep" caption="<strong>Figure 2.</strong> Case G, the field's $$U/U_H$$ and $$k/U_H^2$$ against the modelled $$\lvert\mathbf{U}\rvert$$ and $$k$$ over the model's own $$U(7\text{ m})$$, one column per arm of the drag sweep; the dots take the colour of their line in Figure 1." %}

| Arm | Cd·LAD [1/m] | $$U$$ R | $$U$$ FAC2 | $$U$$ FB | $$U$$ hit rate | mean $$U/U_H$$ | RMSE of $$U$$ |
|---|---|---|---|---|---|---|---|
| no belt (control) | 0 | +0.300 | 0.464 | −0.659 | 0.000 | 0.948 | 0.474 |
| pine | 0.30 | +0.503 | 1.000 | −0.425 | 0.036 | 0.735 | 0.262 |
| conifer | 0.625 | +0.489 | 1.000 | −0.248 | 0.286 | 0.613 | 0.145 |
| screen | 0.875 | +0.459 | 1.000 | −0.148 | 0.857 | 0.554 | 0.097 |
| conifer, real belt (half domain) | 0.625 | +0.468 | 1.000 | −0.202 | 0.607 | 0.585 | 0.120 |
{: .scores }

{% include nomenclature-scores.md %}

The field's mean $$U/U_H$$ over the 28 points is 0.478. The model is $$\lvert\mathbf{U}\rvert$$ over its own $$U(7\text{ m})$$; the same scores over the imposed $$U_H$$, and for $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$, are in the files. The same arms for $$k$$:

| Arm | $$k$$ R | $$k$$ FAC2 | $$k$$ FB | mean $$k/U_H^2$$ |
|---|---|---|---|---|
| no belt (control) | −0.087 | 0.714 | +0.300 | 0.023 |
| pine | +0.213 | 0.714 | +0.138 | 0.027 |
| conifer | +0.278 | 0.750 | −0.090 | 0.034 |
| screen | +0.234 | 0.679 | −0.206 | 0.038 |
| conifer, real belt (half domain) | +0.228 | 0.750 | −0.081 | 0.034 |
{: .scores }

{% include nomenclature-scores.md %}

The field's mean $$k/U_H^2$$ is 0.031.

{% include figure.html name="case-g-openfoam-stations.png" alt="Case G, by station" caption="<strong>Figure 3.</strong> Case G, the letters A to G mark the seven lines of Figure 1; the mean $$U/U_H$$ and the mean $$k/U_H^2$$ over the four heights at each station behind the belt, the field against each arm of the drag sweep." %}

- **Drag.** The mean $$U/U_H$$ falls from 0.948 with no belt to 0.735, 0.613 and 0.554 as Cd·LAD rises, and the RMSE of $$U$$ from 0.474 to 0.097. $$U$$ R stays between +0.46 and +0.50 in every arm with trees (+0.30 with none). The densest crown has mean $$U/U_H$$ 0.554 against 0.478 measured.
- **Factor of two.** In every arm with trees, all 28 points are within a factor of two (FAC2 1.000); with no belt FAC2 is 0.464. For $$U$$, FB is negative in every arm (the model is high).
- **Stations.** The field's station-mean speed is lowest at $$x/H = 1$$ (0.435) and recovers to 0.51 at $$4\thinspace H$$; the conifer arm has its minimum at the same station (0.586) and recovers to 0.661 at $$5\thinspace H$$. The field's mean $$k/U_H^2$$ rises from 0.018 at $$1\thinspace H$$ to 0.053 at $$5\thinspace H$$; in every arm it falls (conifer 0.036 to 0.030). Eddy3D's trees have no canopy $$k$$ or ε source terms.
- **Two dimensions against the real belt.** The real belt on a half domain is slower than the infinite slab by 0.028 of $$U/U(7\text{ m})$$ on average (at most 0.042 over the 28 points; R between the two 0.99). Between the pine and the conifer crown of the sweep the difference is 0.12.
- **Flow structure.** In every arm with trees: a velocity deficit directly behind the belt against the open field, recovery with distance, a speed-up through the 1.2 m gap, and more drag slowing the lee more and pushing more wind through the gap.

<details markdown="block">
<summary>Interpretation: Case G drag sweep</summary>

- Drag changes the level of the mean speed and leaves the pattern (R) where it was.
- The arm nearest the data is the densest one and the edge of the sweep, so the sweep does not bracket the field.
- The streamwise shape is present only in part. For $$k$$ the trend is the other way, and the modelled $$k$$ behind the belt is what the inflow and the shear layer over the belt produce.
- The two-dimensional idealisation costs 0.028 of $$U/U(7\text{ m})$$, against 0.12 between the pine and the conifer crown.

</details>

## Not run

- A second mesh or iteration count.
- LAD or Cd other than the three library crowns. The wind direction relative to the belt normal is not published.
- OpenLB, FluidX3D and the ML surrogate.

<details markdown="block">
<summary>Interpretation: Limits of these runs</summary>

- With one mesh and the residual control unmet, none of these numbers is mesh- or iteration-independent.
- The two-dimensional slab is an assumption, and the half belt is the only check on it.

</details>
