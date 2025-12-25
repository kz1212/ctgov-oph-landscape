import os, re, json, pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pathlib import Path

load_dotenv()
engine = create_engine(f"postgresql+psycopg2://{os.environ.get('AACT_USER')}:{os.environ.get('AACT_PASSWORD')}@{os.environ.get('AACT_HOST')}:{os.environ.get('AACT_PORT', '5432')}/{os.environ.get('AACT_DB', 'aact')}?sslmode=require")

df = pd.read_parquet("oph_master_base.parquet")
RX = r"(ophthalm|ocular|retina|retinal|macula|macular|glaucoma|intraocular|cornea|corneal|cataract|uveit|conjunctiv|keratocon|keratit|dry[ -]?eye|meibom|blephar|vitrectom|trabeculect|strabismus|amblyop|papilledem|optic neurit|retinopath|intravitreal|anti[- ]?vegf|choroid|iritis|endophthalmit)"

q_int = """
SELECT i.nct_id, string_agg(DISTINCT i.intervention_type, ' | ' ORDER BY i.intervention_type) AS intervention_types
FROM interventions i GROUP BY i.nct_id;
"""
ints = pd.read_sql(q_int, engine)
df = df.merge(ints, on="nct_id", how="left").fillna({"intervention_types": ""})

AI_RX = re.compile(r"(artificial intelligence|machine learning|deep learning|neural network|computer vision|algorithm|automated|teleophthalm|telemedicine|remote monitoring|smartphone|mobile app|digital health)", re.I)
PROC_RX = re.compile(r"(vitrectom|trabeculect|blepharoplast|phaco|capsulotom|keratoplast|corneal transplant|crosslink|pterygium excis|laser trabeculoplasty|iridotom|tube shunt|stent implant|injection|intravitreal|scleral buckle|retinopexy|enucleat|eviscerat|dacryocyst|ptosis repair|strabismus surg|orbito|orbitotom)", re.I)

def get_modality(types_str):
    if not types_str: return "Other/Unspecified", []
    mapping = {"drug": "Pharmacologic", "biological": "Pharmacologic", "biologic": "Pharmacologic", "device": "Device/Hardware", "procedure": "Surgical/Interventional", "surgery": "Surgical/Interventional", "diagnostic test": "Imaging/Diagnostics", "behavioral": "Behavioral/Service", "genetic": "Genetic/Gene therapy", "radiation": "Radiation"}
    raw_lc = [t.lower().replace("_", " ").strip() for t in types_str.split("|")]
    tags = sorted(list(set(mapping[t] for t in raw_lc if t in mapping)))
    prec = ["Genetic/Gene therapy", "Pharmacologic", "Surgical/Interventional", "Device/Hardware", "Imaging/Diagnostics", "Behavioral/Service", "Radiation"]
    primary = next((p for p in prec if p in tags), "Other/Unspecified")
    return primary, tags

res = []
for _, row in df.iterrows():
    text = " ".join([str(row.get(c, "")) for c in ["brief_title", "official_title", "conditions_text", "keywords_text", "brief_summary"] if row.get(c)]).lower()
    primary, tags = get_modality(row["intervention_types"])
    proc_match = bool(PROC_RX.search(text))
    reason = "as_registered"
    if primary in ["Device/Hardware", "Other/Unspecified", "Imaging/Diagnostics"] and proc_match:
        primary, reason = "Surgical/Interventional", "upranked_by_proc_verbs"
        if primary not in tags: tags.append(primary)
    res.append({"axisB_primary": primary, "axisB_tags": "|".join(tags), "tag_ai": bool(AI_RX.search(text)), "tag_procedure_verbs": proc_match, "axisB_reason": reason})

df = pd.concat([df, pd.DataFrame(res)], axis=1)
df.to_parquet("oph_master_with_axisB.parquet", index=False)
df.to_csv("oph_master_with_axisB.csv", index=False)

Path("outputs").mkdir(exist_ok=True)
for name, content in [("text_anchor_regex.txt", RX), ("ai_regex.txt", AI_RX.pattern), ("procedure_regex.txt", PROC_RX.pattern)]:
    Path(f"outputs/{name}").write_text(content)