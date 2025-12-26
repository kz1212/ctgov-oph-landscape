import pandas as pd
import os

df = pd.read_csv('outputs/oph_master_final_rebuild.csv')

clean_df = df[[
    'nct_id', 
    'brief_title', 
    'official_title', 
    'start_date', 
    'year', 
    'overall_status', 
    'phase', 
    'enrollment', 
    'enrollment_type', 
    'sponsor_class', 
    'countries', 
    'axisA_subspecialty',    # (Retina, Glaucoma)
    'final_category',        # (Medical Retina vs Surgical Retina)
    'axisB_modality',        # Intervention (e.g., Pharmacologic)
    'tag_ai',                # AI Flag
    'is_upranked',           # Surgical Up-Rank
    'source_mesh',           # via MeSH
    'source_text'            # via Text
]]

clean_df.columns = [
    'NCT_ID', 'Brief_Title', 'Official_Title', 'Start_Date', 'Year', 
    'Status', 'Phase', 'Enrollment', 'Enrollment_Type', 'Sponsor_Class', 
    'Countries', 'Subspecialty', 'Retina_Subtype', 'Modality', 
    'AI_Tag', 'Was_UpRanked', 'Source_MeSH', 'Source_Text'
]

if not os.path.exists('outputs'):
    os.makedirs('outputs')

clean_df.to_csv('outputs/Ocular_Landscape_Frozen_Dataset.csv', index=False)
print(f"Frozen dataset created: 'outputs/Ocular_Landscape_Frozen_Dataset.csv' with {len(clean_df)} rows.")