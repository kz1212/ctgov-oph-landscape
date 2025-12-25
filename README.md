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
pip install pandas numpy sqlalchemy psycopg2-binary python-dotenv pyarrow

---------------------------------------------------------------------------
Configuration
---------------------------------------------------------------------------

Request Access: If you do not have an account, register for free at the CTTI AACT website.

Create a .env file in the root directory. Do not commit this file to version control.

AACT_HOST=aact-db.ctti-clinicaltrials.org
AACT_PORT=5432
AACT_DB=aact
AACT_USER=YOUR_USERNAME
AACT_PASSWORD=YOUR_PASSWORD

---------------------------------------------------------------------------
Pipeline Execution Instructions
---------------------------------------------------------------------------

Run the scripts in numerical order to generate the analysis-ready dataset.

Phase I: Connection & Cohort Construction
1) Verify Connection: Ensure database access is active.
   python 00_test_connection.py

2) Build Master Cohort: Extracts trials using the dual MeSH and text-anchor logic.
   python 02_build_oph_master_base.py

Phase II: Classification & Labeling
3) Assign Axis B (Modality): Categorizes interventions and applies "procedural up-ranking"
   (e.g., moving Device trials to Surgical if procedural verbs are present).
   python 03_add_modality_axisB.py

4) Assign & Refine Axis A (Subspecialty): Maps trials to clinical buckets and performs the Retina
   Split (Medical vs. Surgical Retina) based on Axis B results.
   python 07_rebuild_axisA_v2.py

Phase III: Sponsor Analysis & Final Export
5) Attribute Sponsorship: Maps lead sponsors to standardized categories: Industry, NIH, U.S. Fed, or Other.
   python 09_add_sponsor_lead.py

6) Final Export: Cleans and freezes the data for analysis.
   python 977_export_report.py

7) Generate Reproducibility Log: Run this last to record the environment state and file hashes.
   python 13_make_reproducibility_report.py

---------------------------------------------------------------------------
Output Structure
---------------------------------------------------------------------------

All final artifacts are stored in the outputs/ directory.

File: oph_analysis_ready.csv
Description: Primary Export- The final dataset for user-driven analysis.

File: reproducibility_report.txt
Description: Technical log containing AACT freshness and file hashes.

File: axisB_mapping.json
Description: The dictionary used to map raw AACT types to modality buckets.

File: mesh_axisA_mapping.json
Description: The mapping of MeSH terms to clinical subspecialties.

---------------------------------------------------------------------------
Notes
---------------------------------------------------------------------------

Note on Analysis:
This pipeline is designed to provide the definitive aggregate of information as a file. While the code
does NOT generates basic heatmaps and trend tables during the process, users are encouraged to use
oph_analysis_ready.csv for custom visualizations and specific statistical comparisons not explicitly
covered in the scripts.

Note on Data Interpretation:
We recommend using study_first_posted_date for identifying the year of the study. start_date is not
reliable for trend plots as it often contains future placeholder dates (e.g., 2099).

Ethics:
All data are derived from public trial registry records (ClinicalTrials.gov). No IRB approval is required    for this aggregate analysis.
