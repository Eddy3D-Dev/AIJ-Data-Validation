# Open questions for the data collectors (Ilker / Patrick to forward)

Things the published files, readmes and the data paper (Kikumoto et al. 2026, JAR 9(1) e70083)
cannot settle, each with what was measured and what one line from the collector would close.
Contacts are in `manifest.json → cases.<id>.contact`. Numbers below are in `checks.json`.

## Q1 — Case C: which way does the turntable turn? (Nonomura)

In `RS_caseC.csv`'s own frame (+x = the WD = 0 flow, confirmed three ways on the data) the WD = 45°
field is mirror-symmetric about the line **y = −x**: mean |ΔVs| over the 57 mirror pairs is
0.108 / 0.103 / 0.130 m/s for 0D / 1D / 2D — the experiment's own repeatability floor — while the
mirror about y = +x gives 0.52 / 0.77 / 0.80 m/s. So in the CSV the wind rotates from +x **toward
−y** as WD grows. Figure 3 of the data paper draws the 0 / 22.5 / 45° arrows fanning toward **+y**.
The two differ by a sign of y, which is invisible at WD = 0.

This release keeps the CSV frame (`directions.csv`: flow_dir = (cos WD, −sin WD)) because the point
coordinates live in it. **Question:** is the y axis of `RS_caseC.csv` the one in Figure 3, or its
mirror? Equivalently: for WD = 45°, does the wind come from the (−x, +y) quadrant or the (−x, −y)
quadrant of the CSV coordinates?

*Update 2026-10-14 — a second, independent line of evidence.* Eddy3D solved all nine configurations
(OpenFOAM 12, realizable k-ε) and scored the 120 points both ways on the same solutions: in the CSV's
sense R = 0.83–0.91 at 22.5° and 45°; in Figure 3's sense (the y mirror) R = −0.33 … +0.03. A RANS
solution knows nothing about the CSV's convention, so the data's own symmetry and the physics now agree;
the question stays open only for the collector's word on Figure 3.

## Q2 — Case D: rotation sense for 22.5° and 45° (Tominaga)

The 83-block array is exactly symmetric under y → −y, so a wind at +θ and one at −θ give exact mirror
fields and **no measurement can distinguish them**; the 0° thermistor column is itself an exact
y-mirror (33 pairs with ΔVs = 0, i.e. half of it was measured and mirrored). The sense used here
(flow_dir = (cos WD, +sin WD), status `unverified`) is a reading of Figure 4 of the data paper, and
it is the OPPOSITE of what Case C's data show for Case C. The Zenodo readme (now in
`clean/sources/zenodo_caseD/`) does not state it either.

**Question:** at WD = 22.5° and 45°, is the wind turned from +x toward +y or toward −y, in the
coordinates of `RS-T_caseD.csv` / `MP_caseD.png`? (Also: which half of the 0° plane was actually
measured, +y or −y?)

*Update 2026-10-15 — the solved field decides 22.5°.* No measurement alone can, but a solution can: Eddy3D
solved the array at 22.5° (OpenFOAM 12, realizable k-ε, 3.6 million cells) and scored the 66 measured
points in this release's sense and in its y mirror on the same solution. In Figure 4's sense (+x toward
+y) R = 0.80, FAC2 0.92; mirrored R = 0.40, FAC2 0.74. A RANS solution knows nothing about the figure, so
22.5° is corroborated in Figure 4's sense (`directions.csv` says so); 45° stays unverified until it is
solved. The question stays open for the collector's word, and for 45°.

*Update 2026-10-16 — and 45°.* Solved the same way (3000 iterations, the same residual plateau as 0° and
22.5°): in Figure 4's sense R = 0.85, FAC2 0.89; mirrored R = 0.17, FAC2 0.70 — a wider margin than at 22.5°.
Both rotated headings are now corroborated in Figure 4's sense. The question stays open only for the
collector's own word, and for which half of the 0° plane was measured.

## Q3 — Case E: the sensor frame against the two geometries (Tominaga)

1. Point 50 at (−45.5, −45.0) m lies **0.17 m inside a building wall of the official `BD_caseE.stl`**
   (roof at 6.75 m) and 2.06 m clear of the nearest wall in `case-e.3dm`. The other 79 points
   are in open space in both files (median 4.9 m from the nearest vertex). The two files are
   different triangulations of the district (official: 227 shells, 60,101 triangles, 5,253 open
   edges, bbox ±198 m after ×250; the 3dm: 5,015 meshes, bbox −201.5…203 m). Which is the
   measured model, and is point 50 really in the street?
2. The official STL is **model scale** (z max 0.24 m = 60 m / 250) while the readme calls the
   coordinates "actual scale"; the ×250 is this release's inference from the 60 m high-rise. Please
   confirm, and whether a watertight STL exists.
3. The dataset publishes **only the after-construction geometry**. The before-construction state
   used here (`geometry_bc_3dm.stl`) is the 3dm's `buildings` layer with the three sites empty. Is
   that what stood in the tunnel for the "bc" runs, or were there earlier buildings on the sites?
4. `RS_caseE.csv` on Zenodo is the workbook rounded to 2 dp (max |Δ| 0.00497); the workbook's values
   are exact multiples of 0.0198204 (= U/UR at 0.01 resolution re-normalised by UR / U(15.9 m), which
   gives U(15.9 m) = 3.935 m/s; the paper says 4.0). Which U_ref was used, and is the workbook the
   authoritative precision?

## Q4 — Case B: lateral sign and the seven repeated points (Tominaga)

1. The published V appears positive toward −y: V = +3.630 m/s at (−25, −110, 12.5) mm, just outside
   the y = −100 mm flank where the flow must deflect away from the centreline. Case A (V = −2.893 at
   the equivalent point) and Case D (V = +2.055 on the +y flank) both read positive toward +y. This
   release flips B's V. Please confirm the sign convention of V in `RS_caseB.csv` (or whether the
   published points are on the +y half rather than the −y half of the drawing).
2. Seven locations appear twice with different values: the foot of each vertical-section profile
   (z = 12.5 mm, y = 0; points 12, 43, 56, 69, 82, 95, 108) and the horizontal-plane centreline
   (points 110, 147, 160, 173, 186, 199, 212). |ΔU| = 0.05–0.14 m/s (mean 0.105). Two runs? Which
   is canonical, or should both be kept (as here) as a repeatability estimate?

## Q5 — Case C: what reference speed did the legacy workbook use? (Nonomura)

`LF-caseC.xls` publishes velocity ratios "normalized by the inflow velocity at the same height".
Multiplying by U(0.02 m) = 2.434 m/s from `AF_caseC.csv` reproduces the CSV's Vs only to 0.3 %:
Vs / ratio spans 2.4145–2.4525 m/s across the 1,080 values, so the ratios seem to use a per-run
reference. Is that so, and are the CSV's 2-dp Vs values the raw measurements?

## Q6 — Case D: the split-fibre "Scalar Vel." column (Tominaga)

`RS-S_caseD.csv`'s `Vs` and the workbook's `Scalar Vel.` equal √(U²+V²+W²) to 1e-15 at all 33
points, so they are the vector magnitude, not a thermistor reading, and are dropped here. Is that
right? (The thermistor readings at the same 33 points are in `RS-T_caseD.csv`; their ratio to the
magnitude averages 1.34.)

## Q7 — Cases A, B, C: model scale (Ishihara / Tominaga / Nonomura)

No model:full-scale ratio is stated for A, B or C (D says 1:400, E 1:250). Eddy3D solves them at
1:100 with the tunnel velocities, which only matters for how results are labelled. Is a nominal
scale on record?

## Q8 — Case C: data paper Table 2 vs the CSV point numbering (Nonomura)

The readme lists 1, 2, 3, 34, 35, 36, 37, 46, 55, 100, 101, 102 as missing point numbers and the CSV
agrees (4…132 with those gaps). Were points 1–3 and the nine interior gaps never measured, or
measured and withheld (e.g. inside buildings for one configuration)?

## QJ1 — Case J: the w′θ′ uncertainty at z/H = 0.25 (Yoshie)

In `LF_caseJ.xlsx`, sheet `xy-plane2(Unstable state)`, the "Expanded Uncertainty" column of ⟨w′θ′⟩/(U_H Δθ) (column AH) reads
0.00374 in row 31 and then 1.0037, 2.0037, 3.0037 … 193.0037 down to row 234: the cell was dragged with the fill handle
(+1 per row), 193 cells. Only the 11 rows on y = 0 (the locations the `xz-plane` sheet shares) hold a real value (5·10⁻⁵ – 5.5·10⁻⁴); row 31, the seed, is 0.00374. What are the original
uncertainties of w′θ′ on the z/H = 0.25 plane? (The mean-concentration uncertainty has no such problem; it is about 1 ppm.)

## QJ2 — Case J: the reference concentration (Yoshie)

The workbook's c0 = 12.283 ppm equals 0.05 · q / (U_H H²) with U_H = 1.4581 m/s (to 1e-15): the 5 % ethylene fraction of the
released gas is in it. The data paper gives c0 for Cases H (45.2 ppm, pure ethylene) and I (39.2 ppm, 10 % ethane, fraction
included) but not for J, and the readme gives q = 9.17·10⁻⁶ m³/s of "5 % concentration". Confirm: are the published C
values ppm of ethylene itself (not of the 5 % mixture), and is 12.283 ppm the intended c0? (Without the fraction c0 would be
245.7 ppm and every concentration ratio 20 times smaller.)

## QJ3 — Case J: the readme's Reynolds number (Yoshie)

The readme says the Reynolds number is "approx. 43,000 (based on U_H and H)". With U_H = 1.46 m/s and H = 0.16 m it is
1.6·10⁴, which is what the data paper states; 43,000 is Case H's (3.23 m/s × 0.2 m). A copy from Case H's readme?

## QJ4 — Case J: σ against ⟨u′²⟩ (Yoshie)

The workbook's ⟨u′²⟩/U_H² columns are not the squares of its σ_u/U_H columns: up to 3.2 % in u, 2.2 % in v, 1.7 % in w
(47 of 443 locations differ by more than 1 % in a component; the largest absolute difference is at (−0.06, −0.05, 0.04): σ_u² =
0.1294, ⟨u′²⟩ = 0.1316 in units of U_H²). k is the half-sum of the ⟨u′²⟩ columns to 9·10⁻⁵. This release carries the variance columns.
Is that the right one, and why do the two differ (different sensor of the split-fibre probe, detrending)? The published CSV has
only the rms.

## QJ5 — Case J: which empty-tunnel profile is the inflow? (Yoshie)

`AF_caseJ.csv` is the workbook's profile at x/H = −2.5 (x = −0.4 m). The workbook also has the empty-tunnel profiles at
x/H = 0 and +2.5, which differ near the ground: U/U_H at z/H = 0.019 is 0.33, 0.58 and 0.50 (and 1.00, 1.03, 1.04 at z = H).
Was the boundary layer still developing over the heated floor, and which profile should a model reproduce at the
building's position? Also: `RS_caseJ.csv` lists (−0.16, 0, 0.004) twice (No. 1 and 153, identical); a duplicate or two
runs?

## QK1 — Case K: the reference height, velocity and concentration (Yoshie, Tachibana)

The readme and the data paper give the cube H = 0.06 m and U_H = 2.33 m/s, from which c0 = q / (U_H H²) = 429.18 ppm for
q = 3.6·10⁻⁶ m³/s of pure ethylene. `LF_caseK.xlsx` ('Measurement data', cells R7:R11) normalises with H = 0.2 m (Case H's
building), a "reference velocity" UH = 4.94009 m/s and C0 = 18.218 ppm; every normalised column (X/H, ⟨u⟩/UH, k/UH²,
⟨c⟩/C0) reproduces its dimensional column exactly with those, so the workbook's concentration ratios are 23.56 times smaller
than the cube's. The approach-flow file (Case H's) gives U = 2.24 m/s at z = 0.06 m (log-interpolated), 4 % below 2.33, and
4.94 m/s is not on it (U = 4.32 at z = 0.6 m). Which H, U_H and c0 are meant for Case K, and what is UH = 4.94 m/s? This
release uses the cube's (c0 = 429.18 ppm) and gives the factor to the workbook's in the manifest.

## QK2 — Cases K and L: the workbook's mean scalar speed (Yoshie)

K's workbook has `<usc>` and σ_usc ("Velocity magnitute") beside ⟨u⟩, ⟨v⟩, ⟨w⟩: it is never below |U| (1.03 – 3.9 × |U|,
median 1.19) and is not √(|U|² + 2k) (0.67 – 0.98 of it). L's workbook has `Usc`, which equals √(⟨u⟩² + ⟨v⟩² + ⟨w⟩²) to
1e-16. Is K's `<usc>` the mean of the instantaneous speed (a scalar, like a thermistor's)? If so it is the quantity a RANS |U|
should be compared with, and the table has no column for it; if not, what is it?

## QK3 — Case K: point numbers (Yoshie)

`RS_caseK.csv` and the workbook's `Measurement data` sheet have no point numbers (Cases A–E and J, L do). Are the 203 rows in
the order of measurement, and is there a numbering to use? This release numbers them 1 … 203 in file order.

## QK4 — Case K: the data paper's description (Kikumoto, Okaze)

Section 3.11 ends: "The measurements were taken at approximately 30 points at eight different heights downwind of the line
source." Case K has a point source and 203 points at five heights (0.004, 0.01, 0.03, 0.05, 0.07 m); the sentence matches
Case L (27 locations at 8 heights). A text slip?

## QK5 — Case K: the approach flow (Yoshie)

`AF_caseK.csv` equals `AF_caseH.csv` row for row (17 heights at x = −0.493 m, U = 3.23 m/s at z = 0.2 m). The data paper says
the approach flows were the same. Was Case K's own profile measured, or is Case H's the record? (The workbook's `Inflow`
sheet divides by 3.23 m/s and H = 0.2 m, and its ratios imply 3.21 – 3.27 m/s for U, not exactly 3.23.)

## QK6 — Cases K and L: the lateral velocity (Yoshie)

In the y-symmetric arrays V should be odd in y. K's even part is 0.057 m/s against an odd part of 0.017 m/s (74 mirror pairs;
the empty-tunnel profile has V ≈ +0.04 m/s), L's comparable: a cross-flow offset of about 2° (probe yaw or tunnel swirl) that
hides the lateral structure and the sign of V. Is V corrected for it, and does +V point toward +y of the published
coordinates?

## QL1 — Case L: the unit of the temperature column (Yoshie, Katada)

`RS_caseL.csv`'s column is headed `T(K)` but holds 12.85 … 29.86, equal to the workbook's ⟨θ⟩ (deg.) to 0.005, i.e. degrees
Celsius; `AF_caseL.csv`'s `T(K)` (283.11 … 295.31) is kelvin. Confirm. This release carries °C for both.

## QL2 — Case L: the building surface temperature (Yoshie, Katada)

The readme lists "Building surface temperature: T_b = 14.8 °C", the same number as its T_0 = 14.8 °C and as the workbook's
⟨θ_H⟩ = 14.75 °C (the air at z = H); the bulk Richardson number uses T_b − T_f = θ_H − θ_f. The workbook gives
⟨θ_build⟩ = 42.2 °C (floor 45.0 °C). Which is the building surface in the experiment? (Case J's readme calls θ_H "T_b" as
well, and its measured surface is 24.5 °C.) A model needs the surface temperature, and no per-point values are published for L.

## QL3 — Case L: the source geometry (Yoshie, Katada)

The readme and data paper give the source area as 0.037 m (x) × 1.2 m (y), the tunnel width; `BD_caseL.stl`'s `line_source`
solid is a flat patch 0.04 m × 1.02 m (x from −0.17 to −0.13, y ±0.51: the width of the cube array), centred at x = −0.15 m.
Which is the physical outlet? The tracer flux through four cross-sections is 0.86 – 1.0 of q / 1.2 m and 0.73 – 0.85 of q / 1.02 m,
so the data favour the 1.2 m width only weakly.

## QL4 — Case L: the lateral asymmetry (Yoshie, Katada)

The array and the source are y-symmetric, yet the same point at +y and −y differs in U by 26 %, in k by 23 %, in C by 36 % on
average (110 mirror pairs), and at z = 0.15 m (0.09 m above the roofs) U is 0.11 m/s lower and T 1.3 K higher at +y. Is the
heated floor or the stratification non-uniform across the tunnel, were the two halves measured in different runs, and which
half is representative of a symmetric simulation?

## QL5 — Case L: the readme (Yoshie, Katada)

The readme's file list names `AF_caseK.csv` and `RS_caseK.csv` (the files are `AF_caseL.csv`, `RS_caseL.csv`), lists `tc`
(⟨θ′c′⟩, K·ppm) which has no counterpart in the other cases, and says "9 rows by 14 columns" where `BD_caseL.stl` has 14 rows
along the flow by 9 across. Please confirm the rows and columns are 14 along x and 9 across y, and that `tc` is the
covariance of the temperature and concentration fluctuations.

## QL6 — Case L: what is the model floor's height? (Yoshie, Katada)

The data paper raises the block model's floor 10 mm above the tunnel floor and joins it with a 1/7 taper; the lowest points
are at z = 4 mm. Are the heights measured from the model floor (as assumed here, so cube tops are at 0.06 m) or from the
tunnel floor?
