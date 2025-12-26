import pandas as pd
import numpy as np
import os
import re
from sqlalchemy import create_engine
from dotenv import load_dotenv
import warnings

# --- 0. CONFIG & WARNINGS ---
warnings.simplefilter(action='ignore', category=FutureWarning)
pd.set_option('future.no_silent_downcasting', True)

#DoubleCheck Again
load_dotenv()
print("Connecting to AACT Database...")
db_url = f"postgresql://{os.getenv('AACT_USER')}:{os.getenv('AACT_PASSWORD')}@{os.getenv('AACT_HOST')}:{os.getenv('AACT_PORT')}/{os.getenv('AACT_DB')}"
engine = create_engine(db_url)

# ==========================================

#MeSH ANCESTOR MAPPING
MESH_TO_BUCKET = {
    # Retina
    "Retinal Diseases": "Retina", "Macular Degeneration": "Retina", "Diabetic Retinopathy": "Retina", 
    "Choroid Diseases": "Retina", "Retinal Neovascularization": "Retina", "Retinal Vein Occlusion": "Retina", 
    "Retinal Detachment": "Retina", "Retinitis": "Retina",
    # Glaucoma
    "Glaucoma": "Glaucoma", "Ocular Hypertension": "Glaucoma", "Hydrophthalmos": "Glaucoma",
    # Cornea
    "Corneal Diseases": "Cornea & Ocular Surface", "Keratitis": "Cornea & Ocular Surface", 
    "Dry Eye Syndromes": "Cornea & Ocular Surface", "Keratoconus": "Cornea & Ocular Surface", 
    "Conjunctival Diseases": "Cornea & Ocular Surface", "Conjunctivitis": "Cornea & Ocular Surface", 
    "Conjunctivitis, Allergic": "Cornea & Ocular Surface", "Allergic Conjunctivitis": "Cornea & Ocular Surface", 
    "Rhinitis, Allergic, Seasonal": "Cornea & Ocular Surface", "Trachoma": "Cornea & Ocular Surface",
    # Cataract
    "Cataract": "Cataract & Lens", "Lens Diseases": "Cataract & Lens", "Lens, Crystalline": "Cataract & Lens", 
    "Aphakia": "Cataract & Lens",
    # Uveitis
    "Uveitis": "Uveitis & Inflammation", "Uveal Diseases": "Uveitis & Inflammation", "Choroiditis": "Uveitis & Inflammation", 
    "Endophthalmitis": "Uveitis & Inflammation", "Scleritis": "Uveitis & Inflammation", 
    "Iritis": "Uveitis & Inflammation", "Panuveitis": "Uveitis & Inflammation",
    # Neuro
    "Optic Nerve Diseases": "Neuro-Ophthalmology", "Optic Neuritis": "Neuro-Ophthalmology", 
    "Papilledema": "Neuro-Ophthalmology", "Intracranial Hypertension": "Neuro-Ophthalmology", 
    "Visual Field Defects": "Neuro-Ophthalmology", "Cranial Nerve Diseases": "Neuro-Ophthalmology", 
    "Ocular Motility Disorders": "Neuro-Ophthalmology", "Ophthalmoplegia": "Neuro-Ophthalmology",
    # Peds/Strab
    "Strabismus": "Pediatrics & Strabismus", "Amblyopia": "Pediatrics & Strabismus", 
    "Retinopathy of Prematurity": "Pediatrics & Strabismus", "Esotropia": "Pediatrics & Strabismus", 
    "Exotropia": "Pediatrics & Strabismus",
    # Plastics
    "Orbital Diseases": "Oculoplastics & Orbit", "Eyelid Diseases": "Oculoplastics & Orbit", 
    "Lacrimal Apparatus Diseases": "Oculoplastics & Orbit", "Blepharitis": "Oculoplastics & Orbit", 
    "Blepharoptosis": "Oculoplastics & Orbit",
    # Oncology
    "Eye Neoplasms": "Ocular Oncology", "Uveal Neoplasms": "Ocular Oncology", 
    "Retinoblastoma": "Ocular Oncology", "Melanoma": "Ocular Oncology", "Melanoma, Uveal": "Ocular Oncology",
    # Refractive
    "Refractive Errors": "Refractive Surgery", "Myopia": "Refractive Surgery", "Hyperopia": "Refractive Surgery", 
    "Astigmatism": "Refractive Surgery", "Presbyopia": "Refractive Surgery",
    # Comprehensive
    "Vision Disorders": "Comprehensive & Public Health", "Blindness": "Comprehensive & Public Health", 
    "Visual Impairment": "Comprehensive & Public Health"
}

#PRIORITY HIERARCHY
PRIORITY = [
    "Ocular Oncology", "Glaucoma", "Uveitis & Inflammation", "Retina", "Cornea & Ocular Surface", 
    "Cataract & Lens", "Oculoplastics & Orbit", "Neuro-Ophthalmology", "Refractive Surgery", 
    "Pediatrics & Strabismus", "Comprehensive & Public Health"
]

#GENERIC EYE GATE
GENERIC_EYE_RX = re.compile(r"(ophthalm|ocular|ophthalmic|retina|retinal|cornea|corneal|glaucoma|cataract|uveit|conjunctiv|macul|vision)", re.I)

#MASTER REGEX
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

#MODALITY DEFINITIONS
MODALITY_MAP = {
    "DRUG": "Pharmacologic", "BIOLOGICAL": "Pharmacologic", 
    "PROCEDURE": "Surgical/Interventional", "SURGICAL": "Surgical/Interventional",
    "DEVICE": "Device/Hardware", "DIAGNOSTIC_TEST": "Imaging/Diagnostics", 
    "BEHAVIORAL": "Behavioral/Service", "GENETIC": "Genetic/Gene therapy", 
    "RADIATION": "Radiation", "OTHER": "Other/Unspecified"
}
MODALITY_PRECEDENCE = [
    "Genetic/Gene therapy", "Pharmacologic", "Surgical/Interventional", 
    "Device/Hardware", "Imaging/Diagnostics", "Behavioral/Service", 
    "Radiation", "Other/Unspecified"
]
PROC_RX = re.compile(
    r"(vitrectom|trabeculect|blepharoplast|phaco|capsulotom|keratoplast|corneal transplant|crosslink|pterygium excis|"
    r"laser trabeculoplasty|iridotom|tube shunt|stent implant|injection|intravitreal|scleral buckle|retinopexy|enucleat|eviscerat|"
    r"dacryocyst|ptosis repair|strabismus surg|orbito|orbitotom)",
    re.I
)

#AI/DIGITAL HEALTH DEFINITIONS
AI_RX = re.compile(
    r"(artificial intelligence|machine learning|deep learning|neural network|computer vision|algorithm|automated|teleophthalm|telemedicine|remote monitoring|smartphone|mobile app|digital health)", 
    re.I
)

# ==========================================
# ---COHORT IDENTIFICATION ---

q_mesh_ids = "SELECT DISTINCT nct_id FROM browse_conditions WHERE mesh_type='mesh-ancestor' AND mesh_term='Eye Diseases';"
ids_mesh = pd.read_sql(q_mesh_ids, engine)['nct_id'].tolist()

q_text_ids = r"""
SELECT DISTINCT s.nct_id
FROM studies s
LEFT JOIN conditions c ON s.nct_id = c.nct_id
LEFT JOIN keywords k ON s.nct_id = k.nct_id
LEFT JOIN brief_summaries bs ON s.nct_id = bs.nct_id
WHERE (
    s.official_title ~* '(ophthalm|ocular|retina|retinal|macula|macular|glaucoma|intraocular|cornea|corneal|cataract|uveit|conjunctiv|keratocon|keratit|dry[-]?eye|meibom|blephar|vitrectom|trabeculect|strabismus|amblyop|papilledem|optic\sneurit|retinopath|intravitreal|anti[-]?vegf|choroid|iritis|endophthalmit)' OR
    s.brief_title ~* '(ophthalm|ocular|retina|retinal|macula|macular|glaucoma|intraocular|cornea|corneal|cataract|uveit|conjunctiv|keratocon|keratit|dry[-]?eye|meibom|blephar|vitrectom|trabeculect|strabismus|amblyop|papilledem|optic\sneurit|retinopath|intravitreal|anti[-]?vegf|choroid|iritis|endophthalmit)' OR
    c.name ~* '(ophthalm|ocular|retina|retinal|macula|macular|glaucoma|intraocular|cornea|corneal|cataract|uveit|conjunctiv|keratocon|keratit|dry[-]?eye|meibom|blephar|vitrectom|trabeculect|strabismus|amblyop|papilledem|optic\sneurit|retinopath|intravitreal|anti[-]?vegf|choroid|iritis|endophthalmit)' OR
    k.name ~* '(ophthalm|ocular|retina|retinal|macula|macular|glaucoma|intraocular|cornea|corneal|cataract|uveit|conjunctiv|keratocon|keratit|dry[-]?eye|meibom|blephar|vitrectom|trabeculect|strabismus|amblyop|papilledem|optic\sneurit|retinopath|intravitreal|anti[-]?vegf|choroid|iritis|endophthalmit)' OR
    bs.description ~* '(ophthalm|ocular|retina|retinal|macula|macular|glaucoma|intraocular|cornea|corneal|cataract|uveit|conjunctiv|keratocon|keratit|dry[-]?eye|meibom|blephar|vitrectom|trabeculect|strabismus|amblyop|papilledem|optic\sneurit|retinopath|intravitreal|anti[-]?vegf|choroid|iritis|endophthalmit)'
);
"""
ids_text = pd.read_sql(q_text_ids, engine)['nct_id'].tolist()

# ---MASTER FETCH ---
all_ids_list = list(set(ids_mesh) | set(ids_text))
all_ids_tuple = tuple(all_ids_list)
print(f"  > Total Unique Trials: {len(all_ids_list)}")

# ADDED: enrollment, enrollment_type
q_master = f"""
SELECT nct_id, study_first_posted_date, start_date, overall_status, phase, 
       official_title, brief_title, enrollment, enrollment_type 
FROM studies WHERE nct_id IN {all_ids_tuple}
"""
df_main = pd.read_sql(q_master, engine)

set_mesh = set(ids_mesh)
set_text = set(ids_text)
df_main['source_mesh'] = df_main['nct_id'].apply(lambda x: x in set_mesh)
df_main['source_text'] = df_main['nct_id'].apply(lambda x: x in set_text)
df_main['date_dt'] = pd.to_datetime(df_main['study_first_posted_date'])
df_main['year'] = df_main['date_dt'].dt.year

# ---ENRICHMENT ---

# Text Fields
q_conditions = f"SELECT nct_id, name FROM conditions WHERE nct_id IN {all_ids_tuple}"
df_cond_grouped = pd.read_sql(q_conditions, engine).groupby('nct_id')['name'].apply(lambda x: ' '.join(x.astype(str))).reset_index(name='conditions_text')
df_main = df_main.merge(df_cond_grouped, on='nct_id', how='left')

q_keywords = f"SELECT nct_id, name FROM keywords WHERE nct_id IN {all_ids_tuple}"
df_kw_grouped = pd.read_sql(q_keywords, engine).groupby('nct_id')['name'].apply(lambda x: ' '.join(x.astype(str))).reset_index(name='keywords_text')
df_main = df_main.merge(df_kw_grouped, on='nct_id', how='left')

q_sum = f"SELECT nct_id, description FROM brief_summaries WHERE nct_id IN {all_ids_tuple}"
df_sum = pd.read_sql(q_sum, engine).rename(columns={'description': 'brief_summary'})
df_main = df_main.merge(df_sum, on='nct_id', how='left')

q_browse = f"SELECT nct_id, mesh_term FROM browse_conditions WHERE nct_id IN {all_ids_tuple}"
df_browse = pd.read_sql(q_browse, engine)

# SPONSORS (Deduplicated)
q_sponsor = f"SELECT nct_id, agency_class FROM sponsors WHERE nct_id IN {all_ids_tuple} AND lead_or_collaborator='lead'"
df_sponsor = pd.read_sql(q_sponsor, engine)
df_sponsor = df_sponsor.groupby('nct_id').first().reset_index()
df_main = df_main.merge(df_sponsor, on='nct_id', how='left')

def map_funder(x):
    x = str(x).upper()
    if "NIH" in x: return "NIH"
    if "FED" in x: return "U.S. Fed"
    if "INDUSTRY" in x: return "Industry"
    return "Other"
df_main['sponsor_class'] = df_main['agency_class'].apply(map_funder)

# COUNTRIES
q_geo = f"SELECT nct_id, name FROM countries WHERE nct_id IN {all_ids_tuple}"
df_geo = pd.read_sql(q_geo, engine).groupby('nct_id')['name'].apply(lambda x: '|'.join(sorted(list(set(x))))).reset_index(name='countries')
df_main = df_main.merge(df_geo, on='nct_id', how='left')
df_main['countries'] = df_main['countries'].fillna("Missing/Not Listed")


# ---CLASSIFICATION ---
q_inv = f"SELECT nct_id, intervention_type FROM interventions WHERE nct_id IN {all_ids_tuple}"
df_inv = pd.read_sql(q_inv, engine)

def classify_row(nct_id, intervention_types, text_blob, mesh_terms):
    # --- MODALITY ---
    buckets = set()
    for t in intervention_types:
        t_upper = str(t).upper()
        if t_upper in MODALITY_MAP:
            buckets.add(MODALITY_MAP[t_upper])
        else:
            buckets.add("Other/Unspecified")
    
    primary_mod = "Other/Unspecified"
    for p in MODALITY_PRECEDENCE:
        if p in buckets:
            primary_mod = p
            break
            
    # Surgical Up-Rank
    up_rank_flag = False
    WEAK_CATEGORIES = ["Device/Hardware", "Imaging/Diagnostics", "Other/Unspecified", "Behavioral/Service"]
    if primary_mod in WEAK_CATEGORIES:
        if PROC_RX.search(text_blob):
            primary_mod = "Surgical/Interventional"
            up_rank_flag = True
            
    # --- SUBSPECIALTY ---
    candidates = set()
    if mesh_terms:
        candidates.update(mesh_terms)
    for cat, patterns in MASTER_REGEX.items():
        for pat in patterns:
            if re.search(pat, text_blob, re.I):
                candidates.add(cat)
    
    primary_sub = "General/Other"
    if candidates:
        found = False
        for p in PRIORITY:
            if p in candidates:
                primary_sub = p
                found = True
                break
        if not found:
            primary_sub = list(candidates)[0]
    else:
        if not GENERIC_EYE_RX.search(text_blob):
             pass
             
    # --- AI TAGGING ---
    is_ai = bool(AI_RX.search(text_blob))
    
    return primary_mod, primary_sub, is_ai, up_rank_flag

inv_lookup = df_inv.groupby('nct_id')['intervention_type'].apply(list).to_dict()
df_browse = df_browse[df_browse['mesh_term'].isin(MESH_TO_BUCKET.keys())]
df_browse['bucket'] = df_browse['mesh_term'].map(MESH_TO_BUCKET)
mesh_lookup = df_browse.groupby('nct_id')['bucket'].apply(set).to_dict()

def apply_logic(row):
    nct = row['nct_id']
    invs = inv_lookup.get(nct, [])
    mesh_terms = mesh_lookup.get(nct, set())
    text_blob = " ".join([
        str(row.get('official_title', '')),
        str(row.get('brief_title', '')),
        str(row.get('conditions_text', '')),
        str(row.get('keywords_text', '')),
        str(row.get('brief_summary', ''))
    ]).lower()
    return classify_row(nct, invs, text_blob, mesh_terms)

print("  > Running Comprehensive Classifier...")
res = df_main.apply(apply_logic, axis=1, result_type='expand')
df_main['axisB_modality'] = res[0]
df_main['axisA_subspecialty'] = res[1]
df_main['tag_ai'] = res[2]
df_main['is_upranked'] = res[3]

def split_retina(row):
    if row['axisA_subspecialty'] == 'Retina':
        if row['axisB_modality'] == 'Surgical/Interventional': return 'Surgical Retina'
        if row['axisB_modality'] == 'Pharmacologic': return 'Medical Retina'
        return 'Retina (Other/Unclear)'
    return row['axisA_subspecialty']

df_main['final_category'] = df_main.apply(split_retina, axis=1)

# ---EXPORT ---
print("Generating Final Artifacts...")
table_s6 = df_main.groupby('year').agg(
    mesh_count=('source_mesh', 'sum'),
    text_only_count=('source_mesh', lambda x: (~x).sum()),
    total_hybrid_count=('nct_id', 'count')
).reset_index()

table_s6 = table_s6[(table_s6['year'] >= 1999) & (table_s6['year'] <= 2025)]

if not os.path.exists('outputs'): os.makedirs('outputs')
table_s6.to_csv('outputs/Table_S6_2_Corrected.csv', index=False)
df_main.to_csv('outputs/oph_master_final_rebuild.csv', index=False)
print("Pipeline Complete.")