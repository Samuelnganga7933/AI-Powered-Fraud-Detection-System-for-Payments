"""Train a reproducible fraud model from the committed synthetic CSV.

Usage:
    python scripts/train_model.py --data fraud_dataset_Generator_using_numpy.csv --output artifacts/fraud_model.joblib
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder


def build_pipeline(frame: pd.DataFrame) -> Pipeline:
    numeric = frame.drop(columns=["Label"]).select_dtypes(include="number").columns.tolist()
    categorical = [
        column for column in frame.drop(columns=["Label"]).columns
        if frame[column].dtype == "object"
    ]
    preprocess = ColumnTransformer(
        transformers=[
            ("numeric", MinMaxScaler(), numeric),
            ("categorical", OneHotEncoder(handle_unknown="ignore", drop="first"), categorical),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocess", preprocess),
            ("classifier", RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)),
        ]
    )


def train(data_path: Path, output_path: Path) -> dict[str, float]:
    frame = pd.read_csv(data_path)
    if "Label" not in frame:
        raise ValueError("Dataset must contain a Label column")
    features = frame.drop(columns="Label")
    labels = frame["Label"]
    train_x, test_x, train_y, test_y = train_test_split(
        features, labels, test_size=0.2, random_state=42, stratify=labels
    )
    pipeline = build_pipeline(frame)
    pipeline.fit(train_x, train_y)
    predictions = pipeline.predict(test_x)
    probabilities = pipeline.predict_proba(test_x)[:, 1]
    metrics = {
        "roc_auc": float(roc_auc_score(test_y, probabilities)),
        "accuracy": float((predictions == test_y).mean()),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, output_path)
    print(classification_report(test_y, predictions))
    print(f"Saved {output_path}")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    train(args.data, args.output)


if __name__ == "__main__":
    main()
