#!/usr/bin/env python3
"""
pediatric_keyword_screen.py

- Reads the trial dataset
- Flags rows containing pediatric-related terms in specified text columns 
- Exports an Excel file 1)rows with a hit + matched terms + matched column and 2) summary 

Usage [!!must input the file name and path!!]:
    python pediatric_keyword_screen.py --input frozen_dataset.xlsx --output pediatric_hits.xlsx
    python3 pediatric_keyword_screen.py --input oph_master_final_rebuild.csv --output pediatric_hits.xlsx --id-col NCT_ID
    python pediatric_keyword_screen.py --input frozen_dataset.xlsx --output pediatric_hits.xlsx --text-cols brief_title official_title brief_summary conditions keywords

- !!This is keyword-based and inclusive.
"""

import argparse
import re
from pathlib import Path
import pandas as pd
import numpy as np

DEFAULT_TERMS = [
    # core
    "juvenile", "child", "children", "kid", "kids",
    "pediatric", "paediatric", "peds", "paeds",
    "neonate", "neonatal", "infant", "newborn",
    "adolescent", "teen", "teenage",
    "prepubescent", "pre-pubescent", "prepubertal", "pre-pubertal",
    # common variants
    "school-age", "school age", "toddler", "toddlers",
]

def build_regex(terms):
    """
    Case-insensitive regex
    - Handles hyphen/space variants 
    """
    patterns = []
    for t in terms:
        t = t.strip().lower()
        if not t:
            continue
        # hyphen/space flexiblibility
        t = re.escape(t)
        t = t.replace(r"\-", r"[-\s]?")
        t = t.replace(r"\ ", r"[-\s]+")
        # Word boundary on both sides but allow slash/paren punctuation
        patterns.append(r"(?<![A-Za-z])" + t + r"(?![A-Za-z])")
    return re.compile("(" + "|".join(patterns) + ")", flags=re.IGNORECASE)

def read_any(path, sheet=None):
    path = Path(path)
    if path.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(path, sheet_name=sheet if sheet else 0)
    elif path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    elif path.suffix.lower() in [".tsv", ".txt"]:
        return pd.read_csv(path, sep="\t")
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to frozen dataset (CSV/Excel).")
    ap.add_argument("--output", required=True, help="Path to output Excel file.")
    ap.add_argument("--sheet", default=None, help="Excel sheet name/index (optional).")
    ap.add_argument("--id-col", default=None, help="ID column name (e.g., NCT_ID). Optional.")
    ap.add_argument("--text-cols", nargs="*", default=None,
                    help="Text columns to scan. If omitted, auto-detect object/string columns.")
    ap.add_argument("--terms", nargs="*", default=None,
                    help="Override pediatric terms (space-separated). If omitted, uses defaults.")
    args = ap.parse_args()

    df = read_any(args.input, sheet=args.sheet)

    # Text columns
    if args.text_cols and len(args.text_cols) > 0:
        text_cols = [c for c in args.text_cols if c in df.columns]
        missing = [c for c in args.text_cols if c not in df.columns]
        if missing:
            print(f"Warning: missing specified columns: {missing}")
    else:
        # auto-detection
        text_cols = [c for c in df.columns
                     if (df[c].dtype == "object" or pd.api.types.is_string_dtype(df[c]))
                     and (args.id_col is None or c != args.id_col)]

    if not text_cols:
        raise ValueError("No text columns found to scan. Provide --text-cols explicitly.")

    terms = args.terms if args.terms and len(args.terms) > 0 else DEFAULT_TERMS
    rx = build_regex(terms)

    # Normalize text + search
    text_block = (
        df[text_cols]
        .fillna("")
        .astype(str)
    )

    # Hits per cell
    def cell_matches(s):
        return rx.findall(s)  # list of matched substrings

    matches = {}
    for c in text_cols:
        matches[c] = text_block[c].apply(cell_matches)

    # RowAggregation
    matched_terms = []
    matched_cols = []
    any_hit = []

    for i in range(len(df)):
        row_terms = []
        row_cols = []
        for c in text_cols:
            hits = matches[c].iat[i]
            if hits:
                row_cols.append(c)
                row_terms.extend(hits)
        # de-duplicate + order preserved
        seen = set()
        row_terms_unique = []
        for h in row_terms:
            h0 = h.lower()
            if h0 not in seen:
                seen.add(h0)
                row_terms_unique.append(h)
        matched_terms.append(", ".join(row_terms_unique))
        matched_cols.append(", ".join(row_cols))
        any_hit.append(bool(row_terms_unique))

    out = df.copy()
    out["pediatric_hit"] = any_hit
    out["matched_terms"] = matched_terms
    out["matched_columns"] = matched_cols

    hits_df = out[out["pediatric_hit"]].copy()

    # ID first if provided
    if args.id_col and args.id_col in hits_df.columns:
        front = [args.id_col, "pediatric_hit", "matched_terms", "matched_columns"]
        rest = [c for c in hits_df.columns if c not in front]
        hits_df = hits_df[front + rest]

    summary = pd.DataFrame({
        "parameter": ["input", "sheet", "id_col", "text_cols_scanned", "n_rows", "n_hits", "hit_rate", "terms_used"],
        "value": [
            str(Path(args.input).resolve()),
            str(args.sheet),
            str(args.id_col),
            ", ".join(text_cols),
            len(df),
            len(hits_df),
            f"{(len(hits_df)/len(df))*100:.2f}%" if len(df) else "NA",
            ", ".join(terms),
        ]
    })

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

        # Optional summaries 
    label_cols = {}
    for cand in ["subspecialty", "sub_specialty", "oph_subspecialty", "subspeciality"]:
        if cand in [c.lower() for c in df.columns]:
            # actual column name + original case
            actual = [c for c in df.columns if c.lower() == cand][0]
            label_cols["subspecialty"] = actual
            break
    for cand in ["modality", "intervention_modality", "treatment_modality"]:
        if cand in [c.lower() for c in df.columns]:
            actual = [c for c in df.columns if c.lower() == cand][0]
            label_cols["modality"] = actual
            break

    summaries = {}
    if "subspecialty" in label_cols:
        c = label_cols["subspecialty"]
        summaries["by_subspecialty"] = (hits_df.groupby(c).size()
                                        .reset_index(name="pediatric_hits")
                                        .sort_values("pediatric_hits", ascending=False))
    if "modality" in label_cols:
        c = label_cols["modality"]
        summaries["by_modality"] = (hits_df.groupby(c).size()
                                    .reset_index(name="pediatric_hits")
                                    .sort_values("pediatric_hits", ascending=False))

    with pd.ExcelWriter(out_path, engine="openpyxl") as w:
        hits_df.to_excel(w, index=False, sheet_name="pediatric_hits")
        summary.to_excel(w, index=False, sheet_name="summary")
        for name, sdf in summaries.items():
            sdf.to_excel(w, index=False, sheet_name=name)

    print(f"Done. Wrote {len(hits_df)} pediatric hits to: {out_path}")

if __name__ == "__main__":
    main()
