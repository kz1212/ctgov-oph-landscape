import os
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(f"postgresql+psycopg2://{os.environ.get('AACT_USER')}:{os.environ.get('AACT_PASSWORD')}@{os.environ.get('AACT_HOST')}:5432/{os.environ.get('AACT_DB')}?sslmode=require")

# Handle AACT schema variability for sponsors
q = """
SELECT s.nct_id, sp.agency_class
FROM studies s
LEFT JOIN sponsors sp ON (sp.nct_id = s.nct_id AND sp.lead_or_collaborator = 'lead');
"""
sponsor = pd.read_sql(q, engine)

df = pd.read_parquet("oph_master_FINAL_v2.parquet")
df = df.merge(sponsor, on="nct_id", how="left")

def funder4(x):
    x = str(x).upper()
    if "NIH" in x: return "NIH"
    if "FED" in x: return "U.S. Fed"
    if "INDUSTRY" in x: return "Industry"
    return "Other"

df["funder4"] = df["agency_class"].apply(funder4)
df.to_parquet("oph_primary_with_lead_sponsor.parquet", index=False)