from pathlib import Path
import argparse, json, joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

FEATURE_EXCLUDE = {"url", "type"}

def metrics(y_true, y_pred):
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    return {"accuracy": accuracy_score(y_true, y_pred), "precision_weighted": p,
            "recall_weighted": r, "f1_weighted": f}

def main(data_path, models_dir, results_dir):
    df = pd.read_csv(data_path)
    train_idx = pd.read_csv(Path(data_path).with_name("train_indices.csv"))["index"].to_numpy()
    test_idx = pd.read_csv(Path(data_path).with_name("test_indices.csv"))["index"].to_numpy()

    feature_cols = [c for c in df.columns if c not in FEATURE_EXCLUDE]
    X_train, X_test = df.loc[train_idx, feature_cols], df.loc[test_idx, feature_cols]
    y_train, y_test = df.loc[train_idx, "type"], df.loc[test_idx, "type"]

    # ADDED HYPERPARAMETER LIMITS TO DRASTICALLY DROP DISK SIZE AND PREVENT OVERFITTING
    models = {
        "logistic_regression": Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, class_weight="balanced", n_jobs=None))
        ]),
        "random_forest": RandomForestClassifier(
            n_estimators=100, max_depth=12, min_samples_leaf=4, class_weight="balanced_subsample", random_state=42, n_jobs=-1
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=100, max_depth=12, min_samples_leaf=4, class_weight="balanced", random_state=42, n_jobs=-1
        ),
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            max_iter=150, learning_rate=0.08, max_leaf_nodes=31, random_state=42
        ),
    }

    Path(models_dir).mkdir(parents=True, exist_ok=True)
    Path(results_dir).mkdir(parents=True, exist_ok=True)
    all_metrics = {}

    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        all_metrics[name] = metrics(y_test, pred)
        all_metrics[name]["classification_report"] = classification_report(
            y_test, pred, output_dict=True, zero_division=0
        )
        all_metrics[name]["confusion_matrix"] = confusion_matrix(
            y_test, pred, labels=sorted(y_test.unique())
        ).tolist()

        # ADDED COMPRESS=3 ARGUMENT TO FORCIBLY SHRINK FILE SIZE BY ~90%
        joblib.dump({"model": model, "features": feature_cols, "classes": sorted(y_train.unique())},
                    Path(models_dir) / f"{name}.joblib", compress=3)

    with open(Path(results_dir) / "model_metrics.json", "w") as f:
        json.dump(all_metrics, f, indent=2)
    pd.DataFrame({k: {m:v for m,v in d.items() if isinstance(v, (int,float))}
                  for k,d in all_metrics.items()}).T.to_csv(Path(results_dir)/"model_comparison.csv")
    print(pd.DataFrame({k: {m:v for m,v in d.items() if isinstance(v, (int,float))}
                        for k,d in all_metrics.items()}).T)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--data", default="data/processed/features.csv")
    p.add_argument("--models", default="models")
    p.add_argument("--results", default="results")
    a = p.parse_args()
    main(a.data, a.models, a.results)
