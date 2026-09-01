import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "Category", "Term", "Count", "P-Value",
    "Benjamini", "Fold Enrichment", "User Ids"
]

def _read_david_csv(path):
    df = pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            "Missing required DAVID columns: " + ", ".join(missing)
        )
    return df

def _prepare(df, direction):
    df = df[df["Category"].astype(str).str.strip() == "KEGG_PATHWAY"].copy()
    if df.empty:
        return df

    for col in ["Count", "P-Value", "Benjamini", "Fold Enrichment"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["P-Value"]).copy()
    df["P-Value"] = df["P-Value"].clip(lower=np.finfo(float).tiny)
    df["Benjamini"] = pd.to_numeric(df["Benjamini"], errors="coerce")
    df["Direction"] = direction
    df["Term_clean"] = (
        df["Term"].astype(str)
        .str.replace(r"^hsa\d+:\s*", "", regex=True)
        .str.strip()
    )
    df["neglog10p"] = -np.log10(df["P-Value"])
    return df

def analyze_kegg(up_path, dn_path):
    up = _prepare(_read_david_csv(up_path), "Upregulated")
    dn = _prepare(_read_david_csv(dn_path), "Downregulated")

    up = up.sort_values("P-Value", ascending=False)
    dn = dn.sort_values("P-Value", ascending=False)
    all_df = pd.concat([dn, up], ignore_index=True)

    if all_df.empty:
        raise ValueError("No KEGG_PATHWAY records were found in the uploaded files.")

    export = all_df[
        ["Term_clean", "Direction", "Count", "P-Value",
         "Benjamini", "Fold Enrichment", "neglog10p", "User Ids"]
    ].copy()

    export.columns = [
        "Pathway", "Direction", "Gene_Count", "P_Value",
        "Benjamini_FDR", "Fold_Enrichment", "negLog10_Pval", "Genes"
    ]
    export = export.sort_values(["Direction", "P_Value"]).reset_index(drop=True)

    summary = {
        "total_pathways": int(len(all_df)),
        "upregulated": int(len(up)),
        "downregulated": int(len(dn)),
        "significant_fdr": int((all_df["Benjamini"] < 0.05).sum()),
        "max_neglog10p": float(all_df["neglog10p"].max()),
    }

    return {"data": all_df, "export": export, "summary": summary}
