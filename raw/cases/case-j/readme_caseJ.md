# AIJ UWE Benchmark Dataset – Case J (112CT): Wind Tunnel Experiment for Flow and Dispersion Around a 1:1:2 Shape Building Model under Non-isothermal Conditions

## Investigators

### Data Collectors

- Ryuichiro Yoshie (Tokyo Polytechnic University, Japan)
- Hideyuki Tanaka (Takenaka Corporation, Japan)
- Tsuyoshi Kobayashi (Tokyo Polytechnic University, Japan)

### Dataset Editors and Distributors

- Yoshihide Tominaga (Niigata Institute of Technology, Japan)  
- Hideki Kikumoto (The University of Tokyo, Japan)  
- Tsubasa Okaze (Institute of Science Tokyo, Japan)

### Contact for Questions

Ryuichiro Yoshie  
Email: yoshie@arch.t-kougei.ac.jp

---

## Overview

This dataset provides wind tunnel measurement results of wind velocity, gas concentration and air temperature around a 1:1:2 shaped building model with a near-ground point source. The experiment was conducted under an unstable stratified condition.

---

## Dataset Contents

### File List

- **AF_caseJ.csv**  
  Vertical profile of the approaching flow.  
  **Columns:**  
  
  - `x`, `y`, `z` (m): Coordinates  
  - `U`, `V`, `W` (m/s): Mean wind velocity components  
  - `u_rms`, `v_rms`, `w_rms` (m/s): Root mean square (RMS) of each component of wind velocity fluctuation
  - `uv`, `uw` (m²/s²): Reynolds shear stresses  
  - `k` (m²/s²): Turbulent kinetic energy
  - `T` (K): Mean air temperature
  - `t_rms` (K): RMS of temperature fluctuation
  - `ut`, `vt`, `wt` (m/s K): Each component of turbulent temerature flux

- **BD-ST_caseJ.csv**  
  Detail temperature of building model surface.  
  **Columns:**  
  
  - `x`, `y`, `z` (m): Coordinates  
  - `Building_surface_temperature` (K): Building surface temperature  

- **RS_caseJ.csv**  
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

- **MP-y_caseJ.png**  
  Measurement points on the center vertical plane (`y/H = 0`).

- **MP-z_caseJ.png**  
  Measurement points on two horizontal planes (`z/H = 0.025`, `0.25`).

- **LF_caseJ.xlsx**  
  Legacy Excel version of the measurement dataset, provided as per the AIJ guidelines. Also available via: [Guidebook for CFD Predictions of Urban Wind Environment](https://www.aij.or.jp/jpn/publish/cfdguide/index_e.htm)

---

## Experimental Methodology

### Experimental Setup

- Model dimensions: 0.08 m (width, depth), H = 0.16 m (height)  
- Mean wind speed of approach flow at building heigh: U_H = 1.46 (m/s)
- Mean floor surface temperature: T_f = 318.95 (K)
- Mean temperature of approach flow at building height: T_b = 285.32 (K)
- Reynolds number: approx. 43,000 (based on  U_H and H)
- Bulk Rechardson number: approx. -0.086 (based on U_H, H, T_f, T_b and mean temperature of approach flow from floor to building height)
- Tracer source: 5 mm diameter hole on floor, 0.25H from the leeward wall  
- Gas: Ethylene (C2H4), 5% concentration with 303.55 (K) 
- Flow rate: 9.17E-6 m3/s

### Instrumentation

- Wind velocity:  
  
  - Constant temperature anemometer (DANTEC 90C10)  
  - Split-fiber probe (DANTEC 55R55, 55R56, 55R57)  
  - Sampling rate: 1000 Hz, Duration: 120 s

- Temperature
  
  - Cold wire

- Gas concentration:  
  
  - High-speed total hydrocarbon analyzer  
  - Sampling rate: 1000 Hz, Duration: 120 s

### Location

Tokyo Polytechnic University, Atsugi, Japan

---

## Metadata

- **Units:**  
  - Length: meters (m)  
  - Wind speed: meters per second (m/s)  
  - Temperature: Kelvin (K)
  - Concentration: parts per million (ppm)  
- **File creation date:** 21 April, 2025  
- **Format:** CSV, PNG, XLSX  
- **Missing values:** None  
- **License:** CC BY 4.0  
- **Version:** 1.0  
- **Citation requested:** Yoshie, R. (2016). *Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer*. Adv Environ Wind Eng, 167–196. https://doi.org/10.1007/978-4-431-55912-2_9

---

## Data Accessibility

- **Repository name:** Zenodo  
- **DOI:** 10.5281/zenodo.15447887
- **URL:** https://zenodo.org/records/15447887

---

## Related Articles

- Yoshie, R. (2016). *Wind Tunnel Experiment and Large Eddy Simulation of Pollutant/Thermal Dispersion in Non-isothermal Turbulent Boundary Layer*. Adv Environ Wind Eng, 167–196. https://doi.org/10.1007/978-4-431-55912-2_9
- Tokyo Polytechnic University, Wind Tunnel Experimental Database of Air Pollution around a Building: Database on Indoor / Outdoor Air Pollution. http://www.wind.arch.t-kougei.ac.jp/info_center/pollution/pollution.html

---

*Note: This dataset is part of the AIJ urban wind environment benchmark project, which aims to support the verification and validation of CFD simulation for urban flow simulations.*