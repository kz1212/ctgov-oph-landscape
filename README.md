README.md

This repository contains a streamlined pipeline to generate a reproducible 'landscape' map of ophthalmology clinical trials. The data is extracted from the AACT (Aggregate Analysis of ClinicalTrials.gov) database.

The pipeline constructs a trial cohort using a dual-anchor approach and classifies trials across two primary axes to facilitate independent analysis:

Axis A (Subspecialty):
- Retina (Medical/Surgical)
- Glaucoma
- Cornea
- Cataract
- Uveitis
- etc.

Axis B (Modality):
- Pharmacologic
- Device/Hardware
- Surgical/Interventional
- Imaging
- etc.

---------------------------------------------------------------------------
Methodology & Data Integrity
---------------------------------------------------------------------------

Cohort Identification
- MeSH-Anchor: Trials linked to "Eye Diseases" via MeSH ancestor mapping.
- Text-Anchor: High-precision regex search across titles, conditions, keywords, and summaries.

Reproducibility
To ensure the pipeline reproduciblility despite daily AACT updates, the scripts include:
- Freshness Proxies: Record the MAX date of key columns to 'timestamp' the database state.
- Environment Logging: Capture Python + package versions (e.g., Pandas, SQLAlchemy).
- Artifact Hashing: Storing SHA-256 hashes for final file exports.

---------------------------------------------------------------------------
Prerequisites
---------------------------------------------------------------------------

Python:
- 3.9+

AACT Credentials:
- A valid username and password from the CTTI AACT website.

---------------------------------------------------------------------------
Dependencies
---------------------------------------------------------------------------

Install the required packages:
pip install pandas numpy sqlalchemy psycopg2-binary python-dotenv pyarrow seaborn matplotlib

---------------------------------------------------------------------------
Configuration
---------------------------------------------------------------------------

Request Access: If you do not have an account, register for free at the [CTTI AACT website](https://aact-db.ctti-clinicaltrials.org/users/sign_up).

Create a .env file in the root directory. Do not commit this file to version control.

AACT_HOST=aact-db.ctti-clinicaltrials.org
AACT_PORT=5432
AACT_DB=aact
AACT_USER=YOUR_USERNAME
AACT_PASSWORD=YOUR_PASSWORD

---------------------------------------------------------------------------
Execution Instructions
---------------------------------------------------------------------------

## Setup ### Environment Variables Create a file named .env in the root directory to store your database credentials (Do not commit this file).

ini
AACT_USER=your_username
AACT_PASSWORD=your_password
AACT_HOST=aact-db.ctti-clinicaltrials.org
AACT_PORT=5432
AACT_DB=aact

##Install Dependencies ##
pip install pandas sqlalchemy psycopg2-binary seaborn matplotlib python-dotenv


---------------------------------------------------------------------------
Pipeline Steps
---------------------------------------------------------------------------
Usage: The Pipeline
The analysis is consolidated into four sequential steps. Run them in order:

##1. Build the Cohort (run_pipeline.py)##
Extracts IDs using MeSH ("Eye Diseases") and Regex Text Search. Merges them, fetches metadata (Title, Phase, Sponsor, Enrollment), and applies the hierarchical classification logic and Procedural Up-Rank Rule. 

Key Logic: MeSH > Regex > General.

Refinement: Auto-detects AI trials and "Up-Ranks" device/imaging trials to "Surgical" only if specific procedural keywords are found.

Output: outputs/oph_master_final_rebuild.csv

##2. Generate Figures (make_figures.py)##
Produces the visualizations used in the manuscript.

Figure 1: Subspecialty vs. Modality Heatmap (Multiple accessibility styles).

Figure 2: Industry Sponsorship Share (Bar Graph).

Figure 3: Longitudinal Retina Research Trends (Line Plot).

Output: outputs/Figure_*.png

##3. Generate Manuscript Tables (make_manuscript_tables.py)##
Calculates aggregate statistics and exports definition dictionaries for the Supplement, excluding the pediatric analysis (included as an optional step below).

Tables: AI Prevalence, Phase Distribution, Cohort Flow, Unclassified Analysis.

Output: tables/*.csv

##4. Final Export & Reproducibility (99_finalize_data.py & make_reproducibility_log.py)##
Creates the clean, "frozen" dataset for public sharing and generates a cryptographic hash log of the outputs.

---------------------------------------------------------------------------
Output Structure
---------------------------------------------------------------------------

Primary cohort file: outputs/oph_master_final_rebuild.csv

Figures: outputs/Figure_*.png

Tables: tables/*.csv

Frozen dataset: outputs/Ocular_Landscape_Frozen_Dataset.csv

Reproducibility log: outputs/reproducibility_report.txt

---------------------------------------------------------------------------
Notes
---------------------------------------------------------------------------

Note on Analysis:
This pipeline is designed to provide the definitive aggregate of information as a file. While the code
does NOT perform every analysis explored, users are encouraged to use
oph_analysis_ready.csv for custom visualizations and specific statistical comparisons not explicitly
covered in the scripts. All interpretation can be performed directly from the frozen data set within the software of their choosing. 

Optional Step: 
Please note that, *after* this pipeline has been run, the optional pediatric_keyword_screen.py may be run for replication of the specific sensitivity analysis that was performed. This will require you rename the (oph_master_final_rebuild) to match the file name / path on your device. 

Note on Data Interpretation:
We recommend using study_first_posted_date for identifying the year of the study. start_date is not
reliable for trend plots as it often contains future placeholder dates (e.g., 2099).

Ethics:
All data are derived from public trial registry records (ClinicalTrials.gov). No IRB approval was required for this aggregate analysis.

---------------------------------------------------------------------------
Citation & Contact
---------------------------------------------------------------------------

If you use this pipeline or dataset in your research, please cite:
Khan, Z. et al. (2026). Ocular Clinical Trial Variability: An AACT Landscape Analysis (1999-2025). 
GitHub Repository: https://github.com/kz1212/ctgov-oph-landscape.git

For inquiries: khanzs@odu.edu
