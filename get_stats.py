import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

try:
    df = pd.read_csv('outputs/oph_master_final_rebuild.csv')
    
    print("=" * 50)
    print("       FINAL MANUSCRIPT STATISTICS")
    print("=" * 50)

    #COHORT COUNTS
    print(f"\n[1] COHORT TOTALS")
    print(f"Total Trials:       {len(df)}")
    print(f"MeSH Capture:       {df['source_mesh'].sum()}")
    print(f"Text-Only Capture:  {len(df[df['source_mesh'] == False])}")
    print(f"Hybrid Intersection:{len(df[(df['source_mesh'] == True) & (df['source_text'] == True)])}")

    #ME-SH TERMS HIT COUNTS
    print(f"\n[2] TOP 20 MeSH TERMS (Aggregate Hits)")
    # We need to query the browse_conditions table again for this cohort
    db_url = f"postgresql://{os.getenv('AACT_USER')}:{os.getenv('AACT_PASSWORD')}@{os.getenv('AACT_HOST')}:{os.getenv('AACT_PORT')}/{os.getenv('AACT_DB')}"
    engine = create_engine(db_url)
    all_ids_tuple = tuple(df['nct_id'].tolist())
    q_mesh = f"SELECT mesh_term, count(*) as c FROM browse_conditions WHERE nct_id IN {all_ids_tuple} GROUP BY mesh_term ORDER BY c DESC LIMIT 20"
    df_mesh_counts = pd.read_sql(q_mesh, engine)
    print(df_mesh_counts.to_string(index=False))

    #UP-RANKING AUDIT
    print(f"\n[3] SURGICAL UP-RANKING AUDIT")
    uprank_count = df['is_upranked'].sum()
    print(f"Trials Up-Ranked to Surgical by Regex: {uprank_count}")
    print(f"Percentage of Total Cohort:            {(uprank_count/len(df))*100:.2f}%")

    #SPONSORSHIP
    print(f"\n[4] SPONSORSHIP (Big 4)")
    print(df['sponsor_class'].value_counts())

    #PHASES
    print(f"\n[5] PHASE DISTRIBUTION")
    print(df['phase'].value_counts(dropna=False).head(10))

    #GEOGRAPHY
    print(f"\n[6] TOP 10 COUNTRIES")
    all_countries = df['countries'].str.split('|').explode()
    print(all_countries.value_counts().head(10))

    #AI ANALYSIS
    print(f"\n[7] AI SUB-ANALYSIS")
    ai_trials = df[df['tag_ai'] == True]
    print(f"Total AI Trials: {len(ai_trials)} ({len(ai_trials)/len(df)*100:.2f}%)")
    
    print("\n   > AI by Subspecialty:")
    print(ai_trials['axisA_subspecialty'].value_counts().head(5))
    
    print("\n   > AI by Sponsor:")
    print(ai_trials['sponsor_class'].value_counts())

    #SUBSPECIALTY & RETINA
    print(f"\n[8] FINAL CLASSIFICATION COUNTS")
    print("--- Top Subspecialties ---")
    print(df['axisA_subspecialty'].value_counts())
    print("\n--- Retina Split ---")
    print(df['final_category'].value_counts().loc[['Medical Retina', 'Surgical Retina', 'Retina (Other/Unclear)']])

except Exception as e:
    print(f"Error: {e}")