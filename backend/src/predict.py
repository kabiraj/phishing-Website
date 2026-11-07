import argparse, joblib
import pandas as pd
from features import extract_features

def predict(url, model_path="models/extra_trees.joblib"):
    pack = joblib.load(model_path)
    model, cols = pack["model"], pack["features"]
    x = pd.DataFrame([extract_features(url)])[cols]
    pred = model.predict(x)[0]
    probs = model.predict_proba(x)[0] if hasattr(model, "predict_proba") else None
    result = {"url": url, "prediction": pred}
    if probs is not None:
        result["probabilities"] = dict(zip(model.classes_, map(float, probs)))
        result["trust_score"] = round(100 * result["probabilities"].get("benign", 0), 2)
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--model", default="models/extra_trees.joblib")
    a = p.parse_args()
    print(predict(a.url, a.model))
