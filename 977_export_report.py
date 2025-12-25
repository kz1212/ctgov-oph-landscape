import pandas as pd
import os

df = pd.read_parquet("oph_primary_with_lead_sponsor.parquet")

# Ensure Year column is derived for analysis
df["year"] = pd.to_datetime(df["study_first_posted_date"], errors='coerce').dt.year

keep_cols = [
    "nct_id", "included_by", "brief_title", "overall_status", "phase",
    "axisA_final", "axisB_primary", "funder4", "tag_ai", "year"
]

# Export final outputs
os.makedirs("outputs", exist_ok=True)
df[keep_cols].to_csv("outputs/oph_analysis_ready.csv", index=False)
df[keep_cols].to_parquet("outputs/oph_analysis_ready.parquet", index=False)

# Reproducibility Snapshot (Simplified 13)
with open("outputs/reproducibility_report.txt", "w") as f:
    f.write(f"Export Date: {pd.Timestamp.now()}\n")
    f.write(f"Total Trials: {len(df)}\n")
    f.write(f"Columns Exported: {', '.join(keep_cols)}\n")