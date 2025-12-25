import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(
    f"postgresql+psycopg2://{os.environ.get('AACT_USER')}:{os.environ.get('AACT_PASSWORD')}@"
    f"{os.environ.get('AACT_HOST')}:{os.environ.get('AACT_PORT', '5432')}/"
    f"{os.environ.get('AACT_DB', 'aact')}?sslmode=require"
)

cols = set(pd.read_sql("SELECT column_name FROM information_schema.columns WHERE table_name='studies';", engine)["column_name"])
f_post = next((c for c in ["first_posted_date", "study_first_posted_date", "first_posted"] if c in cols), None)
l_post = next((c for c in ["last_update_posted_date", "study_last_updated_date", "last_update_posted"] if c in cols), None)

RX = r"(ophthalm|ocular|retina|retinal|macula|macular|glaucoma|intraocular|cornea|corneal|cataract|uveit|conjunctiv|keratocon|keratit|dry[ -]?eye|meibom|blephar|vitrectom|trabeculect|strabismus|amblyop|papilledem|optic neurit|retinopath|intravitreal|anti[- ]?vegf|choroid|iritis|endophthalmit)"

q = f"""
WITH mesh AS (SELECT DISTINCT nct_id FROM browse_conditions WHERE mesh_type = 'mesh-ancestor' AND mesh_term = 'Eye Diseases'),
text_hits AS (
    SELECT nct_id, 'title' AS src FROM studies WHERE (COALESCE(brief_title,'') || ' ' || COALESCE(official_title,'')) ~* %(rx)s
    UNION SELECT nct_id, 'condition' FROM conditions WHERE name ~* %(rx)s
    UNION SELECT nct_id, 'keyword' FROM keywords WHERE name ~* %(rx)s
    UNION SELECT nct_id, 'summary' FROM brief_summaries WHERE description ~* %(rx)s
),
text AS (SELECT nct_id, string_agg(DISTINCT src, ',' ORDER BY src) AS text_sources FROM text_hits GROUP BY nct_id),
cohort AS (
    SELECT COALESCE(mesh.nct_id, text.nct_id) AS nct_id,
    CASE WHEN mesh.nct_id IS NOT NULL AND text.nct_id IS NOT NULL THEN 'both' WHEN mesh.nct_id IS NOT NULL THEN 'mesh' ELSE 'text' END AS included_by,
    COALESCE(text.text_sources, '') AS text_sources FROM mesh FULL OUTER JOIN text ON text.nct_id = mesh.nct_id
),
cond AS (SELECT nct_id, string_agg(DISTINCT name, ' | ' ORDER BY name) AS conditions_text FROM conditions GROUP BY nct_id),
keyw AS (SELECT nct_id, string_agg(DISTINCT name, ' | ' ORDER BY name) AS keywords_text FROM keywords GROUP BY nct_id)
SELECT c.*, s.brief_title, s.official_title, s.study_type, s.phase, s.overall_status, s.enrollment, s.enrollment_type, s.start_date, s.primary_completion_date, s.completion_date,
{f"s.{f_post} AS first_posted," if f_post else ""} {f"s.{l_post} AS last_update_posted," if l_post else ""}
cond.conditions_text, keyw.keywords_text, bs.description AS brief_summary
FROM cohort c JOIN studies s ON s.nct_id = c.nct_id LEFT JOIN cond ON cond.nct_id = s.nct_id LEFT JOIN keyw ON keyw.nct_id = s.nct_id LEFT JOIN brief_summaries bs ON bs.nct_id = s.nct_id;
"""

df = pd.read_sql(q, engine, params={"rx": RX})
df.to_parquet("oph_master_base.parquet", index=False)
df.to_csv("oph_master_base.csv", index=False)