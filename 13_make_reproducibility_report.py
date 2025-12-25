import os, sys, platform, hashlib, pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import importlib.metadata as im

load_dotenv()
OUT = "outputs/reproducibility_report.txt"
os.makedirs("outputs", exist_ok=True)

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

engine = create_engine(f"postgresql+psycopg2://{os.environ['AACT_USER']}:{os.environ['AACT_PASSWORD']}@{os.environ['AACT_HOST']}:5432/{os.environ['AACT_DB']}?sslmode=require")

# Metadata collection
pkgs = ["pandas", "numpy", "sqlalchemy", "psycopg2-binary", "pyarrow"]
freshness = pd.read_sql("SELECT MAX(study_first_posted_date) as max_date FROM studies", engine).iloc[0,0]

with open(OUT, "w") as f:
    f.write(f"=== REPRODUCIBILITY REPORT ===\nDate: {pd.Timestamp.now()}\n")
    f.write(f"AACT Max Date: {freshness}\nOS: {platform.platform()}\nPython: {sys.version}\n\n")
    f.write("Package Versions:\n" + "\n".join([f"{p}: {im.version(p)}" for p in pkgs]) + "\n\n")
    f.write("File Hashes:\n")
    for pth in ["outputs/heatmap_counts.csv", "outputs/oph_analysis_ready.parquet"]:
        if os.path.exists(pth): f.write(f"{pth}: {sha256_file(pth)}\n")