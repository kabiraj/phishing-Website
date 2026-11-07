from pathlib import Path
import argparse
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def main(data_path, target_class="phishing", k=4, sample_size=30000):
    df = pd.read_csv(data_path)
    subset = df[df["type"].eq(target_class)].copy()
    if len(subset) > sample_size:
        subset = subset.sample(sample_size, random_state=42)

    feature_cols = [c for c in df.columns if c not in {"url", "type"}]
    X = subset[feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0)

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    model = KMeans(n_clusters=k, random_state=42, n_init=20)
    subset["cluster"] = model.fit_predict(Xs)

    overall = X.mean()
    rows = []
    for c in sorted(subset["cluster"].unique()):
        mask = subset["cluster"].eq(c)
        means = X.loc[mask].mean()
        diff = (means - overall).abs().sort_values(ascending=False)
        top = diff.head(3).index.tolist()
        rows.append({
            "cluster": int(c),
            "size": int(mask.sum()),
            "majority_label_check": target_class,
            "top_feature_1": top[0] if len(top)>0 else "",
            "top_feature_1_delta": float(means[top[0]] - overall[top[0]]) if top else 0,
            "top_feature_2": top[1] if len(top)>1 else "",
            "top_feature_2_delta": float(means[top[1]] - overall[top[1]]) if len(top)>1 else 0,
            "top_feature_3": top[2] if len(top)>2 else "",
            "top_feature_3_delta": float(means[top[2]] - overall[top[2]]) if len(top)>2 else 0,
        })
    out = Path("results")
    out.mkdir(exist_ok=True)
    subset[["url","type","cluster"]].to_csv(out/"cluster_assignments.csv", index=False)
    pd.DataFrame(rows).to_csv(out/"cluster_summary.csv", index=False)
    print(pd.DataFrame(rows).to_string(index=False))

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/processed/features.csv")
    p.add_argument("--class-name", default="phishing")
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--sample-size", type=int, default=30000)
    a = p.parse_args()
    main(a.data, a.class_name, a.k, a.sample_size)
