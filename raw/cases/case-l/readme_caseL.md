# AIJ UWE Benchmark Dataset – Case L (ArraysCT): Wind Tunnel Experiment for Flow and Dispersion around Cube Arrays with a Line-source under Non-isothermal Conditions

## Investigators

### Data Collectors

- Ryuichiro Yoshie (Tokyo Polytechnic University, Japan)
- Koudai Katada (Tokyo Polytechnic University, Japan)  

### Dataset Editors and Distributors

- Yoshihide Tominaga (Niigata Institute of Technology, Japan)  
- Hideki Kikumoto (The University of Tokyo, Japan)  
- Tsubasa Okaze (Institute of Science Tokyo, Japan)

### Contact for Questions

Ryuichiro Yoshie  
Email: [yoshie@arch.t-kougei.ac.jp](mailto:yoshie@arch.t-kougei.ac.jp)

---

## Overview

The wind velocity, air temperature and gas concentration were measured in an urban block model formed by a group of cubes placed in an unstable boundary layer with emission gas released from a line source placed on the floor. The cube blocks were placed at equal intervals of 9 rows by 14 columns (126 cubes in total). The gas source is located between the seventh and eighth rows. 

---

## Dataset Contents

### File List

- **AF_caseK.csv**  
  Vertical profile of the approaching flow.  
  **Columns:**  
  
  - `x`, `y`, `z` (m): Coordinates
  - `U`, `V`, `W` (m/s): Mean wind velocity components
  - `u_rms`, `v_rms`, `w_rms` (m/s): Root-mean-square (RMS) of each component of wind velocity fluctuation
  - `uv`, `uw` (m²/s²): Reynolds shear stresses
  - `k` (m²/s²): Turbulent kinetic energy
  - `T` (K): Mean air temperature
  - `t_rms` (K): RMS of temperature fluctuation
  - `ut`, `vt`, `wt` (m/s K): Each component of turbulent temerature flux

- **RS_caseK.csv**  
  Wind and concentration measurements around the building.  
  **Columns:**  
  
  - `No.`: Measurement point number
  - `x`, `y`, `z` (m): Coordinates
  - `U`, `V`, `W` (m/s): Mean wind velocity components
  - `u_rms`, `v_rms`, `w_rms` (m/s): RMS of each component of wind velocity fluctuation
  - `k` (m2/s2): turbulence kinetic energy
  - `T` (K): Mean air temperature
  - `t_rms` (K): RMS of temperature fluctuation
  - `ut`, `vt`, `wt` (m/s K): Each component of turbulent temerature flux
  - `C` (ppm): Mean gas concentration
  - `c_rms` (ppm): RMS of concentration fluctuations
  - `uc`, `vc`, `wc` (m/s ppm): Each component of turbulent consentration flux
  - `uv`, `uw` (m2/s2): Reynolds stresses
  - `tc` (K ppm): Correlation of temperature and consentration fluctuations

- **MP-y_caseL.png**  
  Measurement points on vertical planes (`y/H = 0, 0.5, 1, 2, 3`).

- **MP-z_caseL.png**  
  Measurement points on two horizontal sctions (`z/H =< 1/2` and `z/H>1/2`).

- **BD_caseL.stl**
  
  Geometry of building and source with stl format.

- **LF_caseL.xlsx** 
  Legacy Excel version of the measurement dataset, provided as per the AIJ guidelines. Also available via: [Guidebook for CFD Predictions of Urban Wind Environment](https://www.aij.or.jp/jpn/publish/cfdguide/index_e.htm)

---

## Experimental Methodology

### Experimental Setup

- One side of the cube: H = 0.06 m
- Mean wind velocity and temperature of the approaching flow at H: U_H = 1.34 m/s, T_0 = 14.8 ˚C
- Reynolds number: approx. 5600 (defined with H and U_H)
- Bulk Richardson number: approx. -0.04 (defiend with H, U_H, T_0, T_b - T_f and g: gravity acceleration)
- Origin: Bottom center of the windward wall of the nineth row of the central building
- Floor surface temperature: T_f = 45.0 ˚C
- Building suraface temperature: T_b = 14.8 ˚C
- Source: Line source on the ground surface located at 0.15 m windward from the origin.
- Dimension of source area: 0.037 m (x) x 1.2 m (y)
- Tracer gas: 100% ethylene (C2H4) at a flow rate of 500 cc/min and at 35˚C
- Cross section of wind tunnel: 1.2 m (y) x 1.0 m (z)

### Instrumentation

- Wind velocity:  
  
  - Constant temperature anemometer (DANTEC 90C10)  
  - Split-fiber probe (DANTEC 55R55, 55R56, 55R57)  
  - The sampling frequency was 1000 Hz with 200 Hz cutoff frequency of low-pass filter. The measurements are taken for 60 sec to obtain statistics.

- Air temperature
  
  - Cold wire

- Gas concentration:  
  
  - High-speed total hydrocarbon analyzer  
  - The sampling frequency was 1000 Hz with 200 Hz cutoff frequency of low-pass filter. The measurements are taken for 60 sec to obtain statistics.

### Location

Tokyo Polytechnic University, Atsugi, Japan

---

## Metadata

- **Units:**  
  
  - Length: meters (m)  
  - Wind speed: meters per second (m/s)  
  - Concentration: parts per million (ppm)  

- **File creation date:** 21 April, 2025  

- **Format:** CSV, PNG, STL, XLSX  

- **Missing values:** None  

- **License:** CC BY 4.0  

- **Version:** 1.0  

- **Citation requested:** Yoshie, R., Nomura, K., Katada, K., Jiang, G., 2012. Non-isothermal large eddy simulation of pollutant and thermal dispersion in urban street canyons. 22nd Proceedings of National Symposium on Wind Engineering, 61-66. (in Japanese)   https://doi.org/10.14887/kazekosymp.22.0.61.0
  
  Jiang, G., Yoshie, R. (2018). Large-eddy simulation of flow and pollutant dispersion in a 3D urban street model located in an unstable boundary layer. Build. Environ. 142, 47–57. https://doi.org/10.1016/j.buildenv.2018.06.015

---

## Data Accessibility

- **Repository name:** Zenodo  
- **DOI:** 10.5281/zenodo.15487637
- **URL:** https://zenodo.org/records/15487637

---

## Related Articles

- Yoshie, R., Nomura, K., Katada, K., Jiang, G., 2012. Non-isothermal large eddy simulation of pollutant and thermal dispersion in urban street canyons. 22nd Proceedings of National Symposium on Wind Engineering, 61-66. (in Japanese)   https://doi.org/10.14887/kazekosymp.22.0.61.0
- Yoshie, R. (2016). *Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer*. Adv Environ Wind Eng, 167–196. https://doi.org/10.1007/978-4-431-55912-2_9
- Jiang, G., Yoshie, R. (2018). Large-eddy simulation of flow and pollutant dispersion in a 3D urban street model located in an unstable boundary layer. Build. Environ. 142, 47–57. https://doi.org/10.1016/j.buildenv.2018.06.015

---

*Note: This dataset is part of the AIJ urban wind environment benchmark project, which aims to support the verification and validation of CFD simulation for urban flow simulations.*
