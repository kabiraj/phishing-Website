from pathlib import Path
import argparse, joblib
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report

def main(data_path, model_path, results_dir="results"):
    df = pd.read_csv(data_path)
    pack = joblib.load(model_path)
    model, feature_cols = pack["model"], pack["features"]
    train_idx = pd.read_csv(Path(data_path).with_name("train_indices.csv"))["index"].to_numpy()
    test_idx = pd.read_csv(Path(data_path).with_name("test_indices.csv"))["index"].to_numpy()

    # Deliberately harder subset: unusually long URLs in the untouched test set.
    test = df.loc[test_idx].copy()
    threshold = df.loc[train_idx, "url_length"].quantile(0.95)
    hard = test[test["url_length"] >= threshold].copy()
    if len(hard) < 100:
        hard = test.nlargest(min(1000, len(test)), "url_length").copy()

    hard["prediction"] = model.predict(hard[feature_cols])
    report = classification_report(hard["type"], hard["prediction"], output_dict=True, zero_division=0)
    out = Path(results_dir); out.mkdir(exist_ok=True)
    pd.DataFrame(report).T.to_csv(out/"hard_test_metrics.csv", index=True)

    test["prediction"] = model.predict(test[feature_cols])
    fp = test[(test["type"] == "benign") & (test["prediction"] != "benign")].head(25)
    fn = test[(test["type"] != "benign") & (test["prediction"] == "benign")].head(25)
    fp.to_csv(out/"false_positives.csv", index=False)
    fn.to_csv(out/"false_negatives.csv", index=False)
    print(f"Hard-test threshold: URL length >= {threshold:.1f}; n={len(hard):,}")
    print(pd.DataFrame(report).T)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/processed/features.csv")
    p.add_argument("--model", default="models/extra_trees.joblib")
    p.add_argument("--results", default="results")
    a = p.parse_args()
    main(a.data, a.model, a.results)
