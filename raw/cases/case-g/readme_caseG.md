# AIJ UWE Benchmark Dataset – Case G (Tree): Field Observation for Flow behind Tree Belt

## Investigators

### Data Collectors

- Yasuo Kurotani (Shimane University, Japan)  
- Nobuyoshi Kiyota (Hiroshima Institute of Technology, Japan)

### Dataset Editors and Distributors

- Yoshihide Tominaga (Niigata Institute of Technology, Japan)  
- Hideki Kikumoto (The University of Tokyo, Japan)  
- Tsubasa Okaze (Institute of Science Tokyo, Japan)

### Contact for Questions

Yoshihide Tominaga
E-mail: [tominaga@abe.niit.ac.jp](mailto:tominaga@abe.niit.ac.jp)

---

## Overview

The wind velocity behind a tree belt was measured (Kurotani et al, 2001). The tree belt is a traditional windbreak forest in Izumo plain, Japan called Tsuiji-matsu, which is trimmed into a rectangular shape, and mainly consists of Japanese black pine. The tree height is 7m and the depth is 2m with a bottom gap of 1.2 m high. 

## Dataset Contents

### File List

- **AF_caseG.csv**  
  Vertical profile of the approaching flow. Wind speed and turbulence kinetic energy are normalized with mean wind velocity of approath flow at 9.0 m high, Ub.  
  **Columns:**  
  
  - `Z` (m): Height  
  - `U/Ub` (-): Normalized mean scalar velocity (wind speed)
  - `k/Ub^2` (-): Normalized turbulent kinetic energy  

- **RS_caseG.csv**  
  Measurements results. Wind speed and turbulence kinetic energy are normalized with mean wind speed at the tree height of 7.0 m, which are interpolated with a power low of the approach flow, UH. 
  **Columns:**  
  
  - `X`,  `Z` (m): Coordinates  
  - `U/UH` (-): Normalized mean scalar velocity (wind speed)
  - `k/UH^2` (-): Normalized turbulent kinetic energy  

- **MP_caseG.png**  
  Measurement points

- **LF_caseG.xlsx**  
  Legacy Excel version of the measurement dataset, provided as per the AIJ guidelines. Also available via: Guidebook for CFD Predictions of Urban Wind Environment [https://www.aij.or.jp/jpn/publish/cfdguide/index_e.htm](https://www.aij.or.jp/jpn/publish/cfdguide/index_e.htm)

---

## Experimental Methodology

The dimension of the tree is 7m (height), 74 m (width) and 2 m (depth) with a bottom gap of 1.2 m high. The wind velocity was measured at the vertical section of the center of the tree belt. The approach flow approximately obeys the power law with the index of 0.22. A movable observation tower with ultrasonic anemometers at 4 heights was shifted in the streamwise direction and wind velocities behind the tree belt were measured at each line. The wind velocities at each line were normalized with the mean approach wind speed at a height of 7 m, corresponding to the tree height, during the measurement period.

### Approach flow

- Date: 28 Dec 2000
- Equipment: 3 dimentional ultra sonic anemometer, DA-600 with TR-90Tx (KAIJO)
- Measurement height: 1.5 m, 3.0 m, 6.0 m, 9.0 m
- Sampling rate: 5 Hz
- Sampling period: 120 min

### Wind behind tree belt

- Date: 26 Dec 2000  
- Equipment: 3 dimentional ultra sonic anemometer, DA-600 with TR-90Tx (KAIJO)
- Measurement line: 0.25H, 0.5H, 1.0H, 2.0H, 3.0H, 4.0H, 5.0H behind tree (H: Tree height, 7 m)
- Measurement height: 1.5 m, 3.0 m, 6.0 m, 9.0 m
- Sampling rate: 5 Hz
- Sampling period: 10min or more

---

## Location

Taisha-machi, Hikawa-gun, Simane, Japan

---

## Metadata

- **Units:**  
  - Length: meters (m)  
  - Wind speed: meters per second (m/s)  
- **File creation date:** 4 July, 2025  
- **Format:** CSV, PNG, XLSX  
- **License:** CC BY 4.0  
- **Version:** 1.0  
- **Citation requested:** Kurotani Yasuo, Kiyota Nobuyoshi, Kobayashi Sadanori (2001). Windbreak effect of Tsuijimatsu in Izumo Part. 2, Summaries of technical papers of Annual Meeting Architectural Institute of Japan. D-2, Environmental engineering II, 745-746. (in Japanese)

---

## Data Accessibility

- **Repository name:** Zenodo  
- **DOI:** 10.5281/zenodo.15589666
- **URL:** https://zenodo.org/records/15589666

---

## Related Articles

- Kurotani Y., Kiyota N., Kobayashi S. (2001). Windbreak effect of Tsuijimatsu in Izumo Part. 2, Summaries of technical papers of Annual Meeting Architectural Institute of Japan. D-2, Environmental engineering II, 745-746. (in Japanese)
- Mochida A., Tabata Y., Iwata T., Yoshino H. (2008). Examining tree canopy models for CFD prediction of wind environment at pedestrian level. J. Wind Eng. Ind. Aerodyn. 96, 1667-1677. https://doi.org/10.1016/j.jweia.2008.02.055

---

*Note: Note: This dataset is part of the AIJ urban wind environment benchmark project, which aims to support the development and validation of urban flow simulations.*
