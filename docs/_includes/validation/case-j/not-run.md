- A second mesh, a longer iteration count and a transient run.
- OpenLB, FluidX3D and the ML surrogate.
- Not represented in the model (Eddy3D's list): the release momentum and the gas's own heat; the tunnel's side walls and ceiling (slip here); radiation (emissivity 0.01, effectively off); the measured 4 K gradient up the building's walls.

<details markdown="block">
<summary>Interpretation: Limits of these runs</summary>

- The air region reached its cap with residuals near $$10^{-2}$$, so these numbers are those of an unconverged steady solve on one mesh.
- The tracer balance closes within a factor of two; why part of the emission is missing at the outlet was not investigated.

</details>
