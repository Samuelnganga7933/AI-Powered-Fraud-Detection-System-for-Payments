"""HTTP inference service for the bundled fraud-classification model."""

from __future__ import annotations

import os
import pickle
from pathlib import Path
from typing import Any

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

from rate_limit import FixedWindowRateLimiter

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "model.pkl"))
FEATURE_COUNT = 22
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
FEATURE_NAMES = [
    "transaction_amount",
    "transaction_frequency",
    "recipient_blacklist_status",
    "device_fingerprinting",
    "vpn_or_proxy_usage",
    "behavioral_biometrics",
    "time_since_last_transaction",
    "social_trust_score",
    "account_age",
    "high_risk_transaction_times",
    "past_fraudulent_behavior_flags",
    "location_inconsistent_transactions",
    "normalized_transaction_amount",
    "transaction_context_anomalies",
    "fraud_complaints_count",
    "merchant_category_mismatch",
    "user_daily_limit_exceeded",
    "recent_high_value_transaction_flags",
    "recipient_verification_status_suspicious",
    "recipient_verification_status_verified",
    "geo_location_flags_normal",
    "geo_location_flags_unusual",
]


def load_model() -> Any:
    """Load the trusted, local model artifact once when the service starts."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model artifact not found: {MODEL_PATH}")
    with MODEL_PATH.open("rb") as model_file:
        return pickle.load(model_file)


model = load_model()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})
limiter = FixedWindowRateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)


def error(message: str, status: int):
    return jsonify({"error": message}), status


def parse_features(payload: Any) -> np.ndarray:
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object")
    features = payload.get("features")
    if not isinstance(features, list):
        raise ValueError("'features' must be an array of numbers")
    if len(features) != FEATURE_COUNT:
        raise ValueError(f"'features' must contain exactly {FEATURE_COUNT} values")
    try:
        values = np.asarray(features, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("'features' must contain only numbers") from exc
    if not np.isfinite(values).all():
        raise ValueError("'features' cannot contain NaN or infinite values")
    return values.reshape(1, -1)


@app.get("/")
def home():
    return jsonify({"service": "SafePayAI fraud detection API", "status": "ok"})


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "model": MODEL_PATH.name})


@app.get("/model-info")
def model_info():
    return jsonify({"feature_count": FEATURE_COUNT, "features": FEATURE_NAMES, "classes": [0, 1]})


@app.post("/predict")
def predict():
    client_key = request.remote_addr or "unknown"
    allowed, rate_headers = limiter.check(client_key)
    if not allowed:
        response = jsonify({"error": "prediction rate limit exceeded", "retry_after_seconds": rate_headers["Retry-After"]})
        response.status_code = 429
        response.headers.update(rate_headers)
        return response
    try:
        values = parse_features(request.get_json(silent=True))
    except ValueError as exc:
        return error(str(exc), 400)

    prediction = int(model.predict(values)[0])
    probabilities = model.predict_proba(values)[0]
    probability = {str(int(label)): round(float(score), 6) for label, score in zip(model.classes_, probabilities)}
    response = jsonify(
        {
            "prediction": prediction,
            "label": "fraud" if prediction == 1 else "legitimate",
            "probability": probability,
            "fraud_probability": probability.get("1", 0.0),
        }
    )
    response.headers.update(rate_headers)
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
