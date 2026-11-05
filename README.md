# Chicago 311 Hardship Paper: Replication Package

This repository contains the replication code and documentation for the paper: 
**"Slower, Not Worse: Neighborhood Hardship and the Speed, Quality, and Equity of 311 Service Delivery in Chicago, 2019-2024"**

## Overview
This project uses 11.1 million Chicago 311 service records from 2019 to 2024 to examine how neighborhood socioeconomic hardship relates to the speed, quality, and equity of city services. 

## Data Availability
The raw data used in this paper are publicly available from the [City of Chicago Data Portal](https://data.cityofchicago.org/). The analysis relies on the following public datasets:
* 311 Service Requests (2019–2024)
* Building Violations
* Crimes - 2001 to Present
* Census Data (Selected Socioeconomic Indicators in Chicago, 2008–2012)
* ACS 5-Year Data by Community Area
* Boundaries - Community Areas

## Repository Structure
* `00_extract_311.py` to `05_build_core_sample.py`: Data extraction, conversion, and sample construction scripts.
* `06_descriptives.py` to `12_extra_robustness.py`: Main estimation, robustness checks, and spatial/survival analyses.
* `13_audit_models.py` to `20_multiple_testing.py`: Data audits, validation, and multiple testing corrections.
* `21_figures.py` and `22_tables.py`: Scripts to generate the final figures and tables for the manuscript.
* `prep.py`, `fe.py`, `common.py`: Foundational helper scripts for data preparation, high-dimensional fixed effects, and shared utilities.
* `requirements.txt`: Required Python packages.

## Instructions for Replication
1. Download the raw data from the City of Chicago Data Portal and place it in a local `data/` directory (not included in this repo due to size).
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt 
