import pandas as pd
import os
import re
from collections import Counter


if not os.path.exists('tables'):
    os.makedirs('tables')

print("Loading dataset...")
try:
    df = pd.read_csv('outputs/oph_master_final_rebuild.csv')
except FileNotFoundError:
    print("Error: Could not find 'outputs/oph_master_final_rebuild.csv'. Please run run_pipeline.py first.")
    exit()

print("Generating Manuscript Tables...")

# =========================================================
# TABLE 1: Prevalence of AI (Subspecialty x AI_Tag)
# =========================================================

df['tag_ai'] = df['tag_ai'].astype(bool)


tab1 = df.groupby(['axisA_subspecialty', 'tag_ai']).size().unstack(fill_value=0)


if False not in tab1.columns: tab1[False] = 0
if True not in tab1.columns: tab1[True] = 0


tab1 = tab1.rename(columns={False: 'Non_AI', True: 'AI_Related'})

# Calculate Stats
tab1['Total'] = tab1['Non_AI'] + tab1['AI_Related']
tab1['AI_Prevalence_Percent'] = (tab1['AI_Related'] / tab1['Total']) * 100


tab1 = tab1.sort_values('AI_Related', ascending=False)

tab1.to_csv('tables/Table_1_AI_Prevalence.csv')
print("  > Generated Table 1 (AI Prevalence)")

# =========================================================
# TABLE 2: Phase Distribution
# =========================================================

tab2 = df['phase'].value_counts(dropna=False).reset_index()
tab2.columns = ['Phase', 'Count']
tab2['Percentage'] = (tab2['Count'] / len(df)) * 100
tab2.to_csv('tables/Table_2_Phase_Distribution.csv', index=False)
print("  > Generated Table 2 (Phases)")

# =========================================================
# TABLE S6.1: Cohort Flow & Stage Counts
# =========================================================

mesh_only = len(df[(df['source_mesh'] == True) & (df['source_text'] == False)])
text_only = len(df[(df['source_mesh'] == False) & (df['source_text'] == True)])
hybrid = len(df[(df['source_mesh'] == True) & (df['source_text'] == True)])
total = len(df)

s6_1_data = {
    'Stage': ['Identified via MeSH', 'Identified via Text Search', 'Intersection (Hybrid)', 'MeSH Only', 'Text Only', 'Total Unique Trials'],
    'Count': [df['source_mesh'].sum(), df['source_text'].sum(), hybrid, mesh_only, text_only, total]
}
pd.DataFrame(s6_1_data).to_csv('tables/Table_S6_1_Cohort_Flow.csv', index=False)
print("  > Generated Table S6.1 (Cohort Flow)")

# =========================================================
# TABLE S6.2: Yearly Classification Breakdown
# =========================================================

s6_2 = df.groupby('year').agg(
    MeSH_Anchor_Count=('source_mesh', 'sum'),
    Text_Anchor_Count=('source_text', 'sum'), 
    Text_Only_Unique=('source_mesh', lambda x: (~x).sum()),
    Total_Trials=('nct_id', 'count')
).reset_index()

s6_2['Percent_Text_Only'] = (s6_2['Text_Only_Unique'] / s6_2['Total_Trials']) * 100
s6_2 = s6_2[(s6_2['year'] >= 1999) & (s6_2['year'] <= 2025)]
s6_2.to_csv('tables/Table_S6_2_Yearly_Classification.csv', index=False)
print("  > Generated Table S6.2 (Yearly Stats)")

# =========================================================
# TABLE S5: Unclassified Analysis (General/Other)
# =========================================================

unclassified = df[df['axisA_subspecialty'] == 'General/Other'].copy()

if len(unclassified) > 0:
    titles = unclassified['official_title'].fillna('').astype(str)
    summaries = unclassified['brief_title'].fillna('').astype(str)
    
  
    combined_series = titles + " " + summaries

    all_text = " ".join(combined_series).lower()

    stop_words = set(['the', 'of', 'and', 'in', 'to', 'a', 'with', 'for', 'study', 'evaluation', 'clinical', 'trial', 'safety', 'efficacy', 'patients', 'on', 'by', 'comparison', 'analysis', 'assessment', 'using', 'associated', 'after', 'following', 'treatment', 'ocular', 'eye', 'ophthalmic'])
    words = re.findall(r'\b[a-z]{4,}\b', all_text)
    words = [w for w in words if w not in stop_words]
    
    top_words = Counter(words).most_common(20)
    pd.DataFrame(top_words, columns=['Word', 'Frequency']).to_csv('tables/Table_S5_Unclassified_Top_Words.csv', index=False)
    print("  > Generated Table S5 (Unclassified Word Frequency)")
else:
    print("  > Table S5 skipped (No Unclassified trials found).")

# =========================================================
# STATIC DICTIONARY TABLES (Supplement)
# =========================================================

MESH_TO_BUCKET = {
    "Retinal Diseases": "Retina", "Macular Degeneration": "Retina", "Diabetic Retinopathy": "Retina", "Choroid Diseases": "Retina", "Retinal Neovascularization": "Retina", "Retinal Vein Occlusion": "Retina", "Retinal Detachment": "Retina", "Retinitis": "Retina",
    "Glaucoma": "Glaucoma", "Ocular Hypertension": "Glaucoma", "Hydrophthalmos": "Glaucoma",
    "Corneal Diseases": "Cornea & Ocular Surface", "Keratitis": "Cornea & Ocular Surface", "Dry Eye Syndromes": "Cornea & Ocular Surface", "Keratoconus": "Cornea & Ocular Surface", "Conjunctival Diseases": "Cornea & Ocular Surface", "Conjunctivitis": "Cornea & Ocular Surface", "Conjunctivitis, Allergic": "Cornea & Ocular Surface", "Allergic Conjunctivitis": "Cornea & Ocular Surface", "Rhinitis, Allergic, Seasonal": "Cornea & Ocular Surface", "Trachoma": "Cornea & Ocular Surface",
    "Cataract": "Cataract & Lens", "Lens Diseases": "Cataract & Lens", "Lens, Crystalline": "Cataract & Lens", "Aphakia": "Cataract & Lens",
    "Uveitis": "Uveitis & Inflammation", "Uveal Diseases": "Uveitis & Inflammation", "Choroiditis": "Uveitis & Inflammation", "Endophthalmitis": "Uveitis & Inflammation", "Scleritis": "Uveitis & Inflammation", "Iritis": "Uveitis & Inflammation", "Panuveitis": "Uveitis & Inflammation",
    "Optic Nerve Diseases": "Neuro-Ophthalmology", "Optic Neuritis": "Neuro-Ophthalmology", "Papilledema": "Neuro-Ophthalmology", "Intracranial Hypertension": "Neuro-Ophthalmology", "Visual Field Defects": "Neuro-Ophthalmology", "Cranial Nerve Diseases": "Neuro-Ophthalmology", "Ocular Motility Disorders": "Neuro-Ophthalmology", "Ophthalmoplegia": "Neuro-Ophthalmology",
    "Strabismus": "Pediatrics & Strabismus", "Amblyopia": "Pediatrics & Strabismus", "Retinopathy of Prematurity": "Pediatrics & Strabismus", "Esotropia": "Pediatrics & Strabismus", "Exotropia": "Pediatrics & Strabismus",
    "Orbital Diseases": "Oculoplastics & Orbit", "Eyelid Diseases": "Oculoplastics & Orbit", "Lacrimal Apparatus Diseases": "Oculoplastics & Orbit", "Blepharitis": "Oculoplastics & Orbit", "Blepharoptosis": "Oculoplastics & Orbit",
    "Eye Neoplasms": "Ocular Oncology", "Uveal Neoplasms": "Ocular Oncology", "Retinoblastoma": "Ocular Oncology", "Melanoma": "Ocular Oncology", "Melanoma, Uveal": "Ocular Oncology",
    "Refractive Errors": "Refractive Surgery", "Myopia": "Refractive Surgery", "Hyperopia": "Refractive Surgery", "Astigmatism": "Refractive Surgery", "Presbyopia": "Refractive Surgery",
    "Vision Disorders": "Comprehensive & Public Health", "Blindness": "Comprehensive & Public Health", "Visual Impairment": "Comprehensive & Public Health"
}
pd.DataFrame(list(MESH_TO_BUCKET.items()), columns=['MeSH_Term', 'Bucket']).to_csv('tables/Table_S1_1_MeSH_Dictionary.csv', index=False)

# S2.1 MASTER REGEX
MASTER_REGEX = {
    "Ocular Oncology": [r"retinoblastoma", r"uveal melanoma", r"choroidal melanoma", r"intraocular lymphoma", r"ocular.*lymphoma", r"conjunctival melanoma", r"tebentafusp", r"\beye neoplasm"],
    "Refractive Surgery": [r"\blasik\b", r"\bprk\b", r"\bsmile\b", r"keratomileusis", r"\bphakic iol\b", r"\bicl\b", r"\bmyopia\b", r"\bhyperopia\b", r"\bastigmatism\b", r"\bpresbyopia\b", r"\brefractive error\b", r"\borthokeratology\b", r"\bcontact lens\b", r"\bcontact lenses\b", r"\bscleral lens\b"],
    "Pediatrics & Strabismus": [r"\bamblyopia\b", r"\bstrabismus\b", r"\besotropia\b", r"\bexotropia\b", r"\bhypertropia\b", r"retinopathy of prematurity", r"\bpediatric ophthalm"],
    "Glaucoma": [r"\bglaucoma\b", r"ocular hypertension", r"intraocular pressure", r"\biop\b", r"trabeculect", r"\bmigs\b", r"\bistent\b", r"\bhydrus\b", r"\bxen\b", r"tube shunt", r"preserflo", r"iridotomy", r"pseudoexfoliation"],
    "Uveitis & Inflammation": [r"\buveitis\b", r"\bscleritis\b", r"pars planitis", r"\bchoroiditis\b", r"\biridocyclitis\b", r"\bendophthalmitis\b", r"\bbehcet\b", r"\bsarcoidosis\b", r"\bvkh\b", r"sympathetic ophthalmia"],
    "Cornea & Ocular Surface": [r"\bdry eye\b", r"\bmeibom", r"\bmgd\b", r"\bblepharitis\b", r"\bcornea\b", r"\bcorneal\b", r"\bkeratitis\b", r"\bkeratoconus\b", r"crosslink", r"\bpterygium\b", r"ocular surface", r"\bsjogren\b", r"sjögren", r"limbal stem.*cell", r"\bfuchs\b", r"\bconjunctiv", r"\bconjunctivitis\b", r"allergic conjunctivitis", r"rhinoconjunctivitis"],
    "Oculoplastics & Orbit": [r"\bptosis\b", r"\beyelid\b", r"blepharoplasty", r"\borbital\b", r"thyroid eye", r"\bgraves\b", r"\blacrimal\b", r"dacryo", r"\bchalazion\b", r"\bectropion\b", r"\bentropion\b", r"\benucleat", r"\beviscerat", r"anophthalmic", r"prosthesis", r"artificial eye"],
    "Neuro-Ophthalmology": [r"\boptic neuritis\b", r"\boptic neuropathy\b", r"\boptic atrophy\b", r"\bpapilledema\b", r"intracranial hypertension", r"\biih\b", r"\bgiant cell arteritis\b", r"\bhemianopsia\b", r"\bhorner\b", r"\banisocoria\b", r"\bnystagmus\b", r"\bcranial nerve\b", r"\bdiplopia\b", r"\bophthalmoplegia\b", r"ocular motility"],
    "Cataract & Lens": [r"\bcataract\b", r"\bintraocular lens\b", r"\biol\b", r"\bphaco", r"\bcapsulotomy\b", r"posterior capsule", r"\bpanoptix\b", r"\bsynergy\b", r"\bvivity\b"],
    "Comprehensive & Public Health": [r"low vision", r"visual impairment", r"\bblindness\b", r"vision screening"],
    "Retina": [r"\bretinal\b", r"\bvitreoretinal\b", r"macular degeneration", r"\bamd\b", r"geographic atrophy", r"\bdrusen\b", r"diabetic retinopathy", r"\bdme\b", r"macular edema", r"vein occlusion", r"\brvo\b", r"\bcnv\b", r"choroidal neovascular", r"anti[- ]?vegf", r"\bintravitreal\b", r"central serous", r"\bpdt\b", r"photodynamic", r"aflibercept", r"ranibizumab", r"faricimab", r"retinal detachment", r"vitrectomy", r"scleral buckle", r"macular hole", r"epiretinal membrane", r"retinopexy", r"pars plana", r"rhegmatogenous"]
}
regex_list = []
for cat, patterns in MASTER_REGEX.items():
    for pat in patterns:
        regex_list.append({'Category': cat, 'Pattern': pat})
pd.DataFrame(regex_list).to_csv('tables/Table_S2_1_Regex_Dictionary.csv', index=False)

# S3.1 Intervention Mapping
mod_map = {
    "DRUG": "Pharmacologic", "BIOLOGICAL": "Pharmacologic", "PROCEDURE": "Surgical/Interventional", "SURGICAL": "Surgical/Interventional",
    "DEVICE": "Device/Hardware", "DIAGNOSTIC_TEST": "Imaging/Diagnostics", "BEHAVIORAL": "Behavioral/Service", 
    "GENETIC": "Genetic/Gene therapy", "RADIATION": "Radiation", "OTHER": "Other/Unspecified"
}
pd.DataFrame(list(mod_map.items()), columns=['AACT_Type', 'Bucket']).to_csv('tables/Table_S3_1_Intervention_Mapping.csv', index=False)

# S3.2 Up-Rank Triggers
proc_triggers = [
    "vitrectom", "trabeculect", "blepharoplast", "phaco", "capsulotom", "keratoplast", "corneal transplant", "crosslink", 
    "pterygium excis", "laser trabeculoplasty", "iridotom", "tube shunt", "stent implant", "injection", "intravitreal", 
    "scleral buckle", "retinopexy", "enucleat", "eviscerat", "dacryocyst", "ptosis repair", "strabismus surg", "orbito", "orbitotom"
]
pd.DataFrame(proc_triggers, columns=['Trigger_Word']).to_csv('tables/Table_S3_2_Surgical_Triggers.csv', index=False)

# S4.1 AI Patterns
ai_patterns = [
    "artificial intelligence", "machine learning", "deep learning", "neural network", "computer vision", "algorithm", 
    "automated", "teleophthalm", "telemedicine", "remote monitoring", "smartphone", "mobile app", "digital health"
]
pd.DataFrame(ai_patterns, columns=['AI_Pattern']).to_csv('tables/Table_S4_1_AI_Patterns.csv', index=False)

# S4.2 Sponsor Mapping
sponsor_logic = [
    {'Pattern': 'NIH', 'Bucket': 'NIH'},
    {'Pattern': 'FED', 'Bucket': 'U.S. Fed'},
    {'Pattern': 'INDUSTRY', 'Bucket': 'Industry'},
    {'Pattern': 'ELSE', 'Bucket': 'Other'}
]
pd.DataFrame(sponsor_logic).to_csv('tables/Table_S4_2_Sponsor_Mapping.csv', index=False)

print("All tables generated successfully in 'tables/' folder.")