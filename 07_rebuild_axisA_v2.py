import pandas as pd
import re

df = pd.read_parquet("oph_master_with_axisB.parquet")

# Subspecialty Mapping (MeSH & Regex Stems)
MESH_TO_BUCKET = {
    "Retinal Diseases": "Retina", "Macular Degeneration": "Retina", "Glaucoma": "Glaucoma",
    "Corneal Diseases": "Cornea & Ocular Surface", "Cataract": "Cataract & Lens",
    "Uveitis": "Uveitis & Inflammation", "Optic Nerve Diseases": "Neuro-Ophthalmology",
    "Strabismus": "Pediatrics & Strabismus", "Orbital Diseases": "Oculoplastics & Orbit",
    "Eye Neoplasms": "Ocular Oncology", "Refractive Errors": "Refractive Surgery"
}

# Weighted Regex Patterns
PRIORITY = ["Ocular Oncology", "Glaucoma", "Uveitis & Inflammation", "Retina", "Cornea & Ocular Surface", 
            "Cataract & Lens", "Oculoplastics & Orbit", "Neuro-Ophthalmology", "Refractive Surgery", 
            "Pediatrics & Strabismus", "Comprehensive & Public Health"]

def get_axisA(row):
    text = f"{row['brief_title']} {row['official_title']} {row['conditions_text']}".lower()
    # Simple example of the regex fallback logic (can be expanded with MASTER_REGEX from script 07)
    if "glaucoma" in text or "iop" in text: return "Glaucoma", "regex"
    if "retina" in text or "amd" in text or "vegf" in text: return "Retina", "regex"
    return "General/Other", "unclassified"

df[['axisA_primary', 'axisA_source']] = df.apply(lambda r: pd.Series(get_axisA(r)), axis=1)

# Retina Split logic
def refine_retina(row):
    if row["axisA_primary"] == "Retina":
        if row["axisB_primary"] == "Pharmacologic": return "Medical Retina"
        if row["axisB_primary"] == "Surgical/Interventional": return "Surgical Retina"
    return row["axisA_primary"]

df["axisA_final"] = df.apply(refine_retina, axis=1)
df.to_parquet("oph_master_FINAL_v2.parquet", index=False)