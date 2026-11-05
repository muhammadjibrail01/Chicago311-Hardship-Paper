# Replication package: Neighborhood Hardship and 311 Service Delivery in Chicago, 2019–2024

This package reproduces every analysis, table input, and figure in the paper from the public Chicago Data Portal files.
**Tested end to end on 29 September 2026** from the raw Chicago Data Portal files in an empty folder (Python 3.12, Linux, 4 GB RAM,
one CPU). All 23 steps ran in about 26 minutes; `check_results.py` reported 40 of 40 key numbers matching the paper, and all
1,889 table cells in the 16 tables were identical to the paper.

## 1. Install
1. Install Python 3.10 or newer (python.org). On Windows, tick "Add Python to PATH" during installation.
2. Open a terminal (Windows: "Command Prompt") in this folder and run:
   `pip install -r requirements.txt`
   (`pyfixest` is only used by the optional step 19; if it fails to install, delete that line and continue.)

## 2. Put the data in `raw_data/`
Create a folder named `raw_data` inside this package and place these downloads from https://data.cityofchicago.org in it.
File names can differ slightly; the scripts find files by pattern.

| Dataset (portal name) | Export | File name pattern |
|---|---|---|
| 311 Service Requests | CSV, filtered to created date 2019-01-01 – 2024-12-31 (or the .7z archive) | `311_Service_Requests*.csv` or `*311*Service*Requests*.7z` |
| Crimes – 2001 to Present | CSV covering 2019–2024 (several overlapping files are fine; duplicates are removed) | `Crimes*2001_to_Present*.csv` |
| Building Violations | CSV covering 2019–2024 (one or more files) | `Building_Violations*.csv` |
| Census Data – Selected socioeconomic indicators in Chicago, 2008 – 2012 | CSV | `Census_Data*Selected_socioeconomic*.csv` |
| ACS 5 Year Data by Community Area | CSV (2023 release, i.e., 2019–2023) | `ACS_5_Year_Data_by_Community_Area*.csv` |
| Boundaries – Community Areas | CSV (with `the_geom` column) | `Boundaries*Community*Areas*.csv` |

To keep data elsewhere, edit `RAW_DIR` in `config.py` (or set the `RAW_DIR` environment variable). Outputs go to `work/` (`WORK_DIR`).

## 3. Run
`python run_all.py`  — runs all steps in order and prints OK/FAIL with the time for each.
Resume after an error with `python run_all.py --from 7`; run one step with `python run_all.py --only 12`.
Each step writes a log to `work/logs/`. Expect roughly 25–60 minutes in total and about 6 GB of temporary disk space
if you start from the .7z archive (you can delete `work/311_csv/` after step 1).

**Memory.** The scripts are designed to run in about 3–4 GB of RAM. If a step stops with a message that the system stopped it,
the computer ran out of memory: close other programs and resume with `python run_all.py --from <step>`.

## 4. Check your results against the paper
`python check_results.py` compares 40 key numbers (sample sizes, main estimates, robustness checks, audits) with the paper,
then compares every cell of all 16 tables with `expected/tables_in_paper.json`. Every line should read PASS, and all table
cells should be identical. The global Moran's I permutation p-values are not seeded and can vary slightly between runs;
all other random steps (samples, bootstraps, local Moran) use fixed seeds.

## 5. What each step does
| Step | Script | Produces | Paper |
|---|---|---|---|
| 00 | `00_extract_311.py` | Extracts the 311 archive if needed | §4.1 |
| 01 | `01_convert_311.py` | Compact Parquet copies of the 311 CSVs | §4.1 |
| 02 | `02_build_requests.py` | Exclusions: info-only calls, aircraft noise, invalid areas | §4.1, Table 1 |
| 03 | `03_type_profile.py` | Profile of all request types | Appendix Table A1 |
| 04 | `04_build_community_areas.py` | Hardship, ACS, crime, building violations, geography | §4.3, Table 2 |
| 05 | `05_build_core_sample.py` | 49 core types, channels, speed/quality/re-report measures, workload | §4.2 |
| 06 | `06_descriptives.py` | Outcomes by hardship quartile | Tables 2–3 |
| 07 | `07_speed_models.py` | Main fixed-effects speed models | Table 4 |
| 08 | `08_quality_models.py` | Quality models | Table 5 |
| 09 | `09_heterogeneity.py` | By type, department, year, channel | Table 6, Figs. 5–7 |
| 10 | `10_robustness.py` | Race vs. class, components, robustness battery | Tables 7–8, Fig. 11 |
| 11 | `11_survival_decomposition_spatial_equity.py` | Survival, decomposition, spatial models, concentration indices, Poisson | Tables 9–13, Figs. 2, 8–10 |
| 12 | `12_extra_robustness.py` | Ward-by-month FE; pooling city-generated records | §6.11, §7.1 |
| 13–15 | `13_audit_models.py`, `14_audit_recurrence.py`, `15_audit_ph_test.py` | Leave-one-out, ambiguous origins, re-report check, PH test | §6.11, App. B |
| 16–18 | `16_raw_data_audit.py`, `17_channel_audit.py`, `18_geo_validation.py` | Data audits | App. B.9 |
| 19 | `19_validate_estimator.py` | Custom estimator vs. pyfixest (optional) | App. B.2 |
| 20 | `20_multiple_testing.py` | Benjamini–Hochberg / Bonferroni | §6.4 |
| 21 | `21_figures.py` | Figures 1–11 → `work/figs/` | Figures |
| 22 | `22_tables.py` | All table values → `work/tables.json` | Tables |

Helper modules: `common.py` (loading), `prep.py` (analysis variables), `fe.py` (the fixed-effects estimator with
community-area-clustered standard errors; see Appendix B.1).

## 6. Disclosure
The code in this package was drafted with an AI assistant (Claude, Anthropic). Describe this accurately in the paper's
AI-use statement, along with the checks and extensions you carried out yourself.
