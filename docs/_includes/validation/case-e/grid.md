OpenFOAM on four meshes (edge ratio $$\sqrt{2}$$, 0.45 to 5.1 million cells per state), eddy-viscosity cap lifted as in [eddy3d-of12-nutcap-lifted]({{ '/community/eddy3d-of12-nutcap-lifted/' | relative_url }}). The served run keeps the cap.

{% include figure.html name="case-e-openfoam-grid.png" alt="Grid uncertainty, OpenFOAM, Case E" caption="<strong>Figure 5.</strong> Case E, second mesh of four: measured vs modelled $$\sqrt{\lvert\mathbf{U}\rvert^2 + 2k}$$, bar = grid uncertainty. Hollow: no band." %}

- Median band: 0.032 before, 0.026 after construction (p90 0.12, 0.10). Most points oscillate between meshes. 46 and 45 of 80 points within the hit rate's 0.05.
- Across the meshes: $$\lvert\mathbf{U}\rvert$$ FAC2 after construction 0.66–0.78; hit rates move up to 0.10. The construction change keeps $$R$$ 0.82–0.84.
- Point 74 is inside a building on the coarsest mesh: no band.
- Bands: [`grid/openfoam12-realizableKE.csv`]({{ '/api/cases/E/grid/openfoam12-realizableKE.csv' | relative_url }}). Method: [Grid uncertainty]({{ '/validation/method/' | relative_url }}#grid-uncertainty).
