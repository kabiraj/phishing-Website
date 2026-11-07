from pathlib import Path
import argparse
import pandas as pd
from sklearn.model_selection import train_test_split
from features import extract_dataframe

def prepare(input_csv, output_csv, random_state=42):
    df = pd.read_csv(input_csv, usecols=["url", "type"])
    df = df.dropna(subset=["url", "type"]).copy()
    df["url"] = df["url"].astype(str).str.strip()
    df["type"] = df["type"].astype(str).str.strip().str.lower()
    df = df[df["url"].str.len() > 0]
    df = df.drop_duplicates(subset=["url"]).reset_index(drop=True)

    X = extract_dataframe(df)
    out = pd.concat([df[["url", "type"]], X], axis=1)
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_csv, index=False)

    train_idx, test_idx = train_test_split(
        out.index, test_size=0.20, random_state=random_state, stratify=out["type"]
    )
    pd.DataFrame({"index": train_idx}).to_csv(
        Path(output_csv).with_name("train_indices.csv"), index=False
    )
    pd.DataFrame({"index": test_idx}).to_csv(
        Path(output_csv).with_name("test_indices.csv"), index=False
    )
    print(f"Prepared {len(out):,} unique URLs -> {output_csv}")
    print(out["type"].value_counts())

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="data/raw/malicious_phish.csv")
    p.add_argument("--output", default="data/processed/features.csv")
    args = p.parse_args()
    prepare(args.input, args.output)
