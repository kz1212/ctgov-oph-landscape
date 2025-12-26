import pandas as pd
import sys
import hashlib
import datetime
import os
import platform

def get_file_hash(filepath):
    """Calculates SHA256 hash of a file to prove data integrity."""
    if not os.path.exists(filepath):
        return "File Not Found"
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

print("Generating Reproducibility Report...")

report = []
report.append("========================================================")
report.append("       OCULAR LANDSCAPE ANALYSIS - REPRODUCIBILITY LOG")
report.append("========================================================")
report.append(f"Date Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"OS Platform:    {platform.platform()}")
report.append(f"Python Version: {sys.version.split()[0]}")
report.append("-" * 50)
report.append("LIBRARY VERSIONS")
report.append(f"Pandas:         {pd.__version__}")
try:
    import sqlalchemy
    report.append(f"SQLAlchemy:     {sqlalchemy.__version__}")
except: pass
try:
    import seaborn
    report.append(f"Seaborn:        {seaborn.__version__}")
except: pass
report.append("-" * 50)
report.append("OUTPUT FILE HASHES (SHA256)")
report.append("These hashes prove that the dataset has not been altered.")
report.append("")

files_to_hash = [
    'outputs/oph_master_final_rebuild.csv',
    'outputs/Ocular_Landscape_Frozen_Dataset.csv',
    'outputs/Table_S6_2_Corrected.csv'
]

for f in files_to_hash:
    h = get_file_hash(f)
    report.append(f"{f}:")
    report.append(f"  {h}")

# Save to file
with open("outputs/reproducibility_report.txt", "w") as f:
    f.write("\n".join(report))

print("Done. Report saved to 'outputs/reproducibility_report.txt'.")