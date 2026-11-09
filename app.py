"""
Heart Health Checker web server.

Author: Aashar Pamidiparti
"""

from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_from_directory

# Project root so model, templates, and image assets resolve the same way locally.
ROOT = Path(__file__).resolve().parent

# Categorical values must match the dummy columns used during training.
CATEGORIES = {
    "ChestPainType": ["ATA", "NAP", "ASY", "TA"],
    "Sex": ["M", "F"],
    "RestingECG": ["Normal", "ST", "LVH"],
    "ExerciseAngina": ["N", "Y"],
    "ST_Slope": ["Up", "Flat", "Down"],
}

# Clinically reasonable bounds used for both API and form validation.
LIMITS = {
    "Age": (18, 100),
    "RestingBP": (80, 200),
    "Cholesterol": (50, 600),
    "Oldpeak": (-3.0, 7.0),
}

app = Flask(__name__)
bundle = joblib.load(ROOT / "heart_classifier.joblib")  # Trained logistic regression + column order
MODEL = bundle["model"]
COLUMNS = bundle["columns"]


def validate(payload: dict) -> tuple[dict | None, str | None]:
    """Parse JSON input and reject values outside the expected clinical ranges."""
    try:
        age = int(payload.get("Age"))
        sex = str(payload.get("Sex", "")).upper()
        chest = str(payload.get("ChestPainType", "")).upper()
        resting_bp = int(payload.get("RestingBP"))
        cholesterol = int(payload.get("Cholesterol"))
        fasting_bs = int(payload.get("FastingBS"))
        resting_ecg = str(payload.get("RestingECG", ""))
        max_hr = int(payload.get("MaxHR"))
        exercise_angina = str(payload.get("ExerciseAngina", "")).upper()
        oldpeak = float(payload.get("Oldpeak"))
        st_slope = str(payload.get("ST_Slope", ""))
    except (TypeError, ValueError):
        return None, "Please enter valid numbers for all numeric fields."

    if not (LIMITS["Age"][0] <= age <= LIMITS["Age"][1]):
        return None, "Age must be between 18 and 100."
    if sex not in CATEGORIES["Sex"]:
        return None, "Sex must be Male or Female."
    if chest not in CATEGORIES["ChestPainType"]:
        return None, "Choose a valid chest pain type."
    if not (LIMITS["RestingBP"][0] <= resting_bp <= LIMITS["RestingBP"][1]):
        return None, "Resting blood pressure must be between 80 and 200 mmHg."
    if not (LIMITS["Cholesterol"][0] <= cholesterol <= LIMITS["Cholesterol"][1]):
        return None, "Cholesterol must be between 50 and 600 mg/dL."
    if fasting_bs not in (0, 1):
        return None, "Fasting blood sugar must be 0 (<120 mg/dL) or 1 (≥120 mg/dL)."
    if resting_ecg not in CATEGORIES["RestingECG"]:
        return None, "Choose a valid resting ECG result."

    expected_hr = 220 - age  # Age-predicted maximum heart rate
    if not (60 <= max_hr <= 220):
        return None, "Max heart rate must be between 60 and 220 bpm."
    if abs(max_hr - expected_hr) > 40:
        return None, f"Max heart rate should be near 220 − age ({expected_hr} bpm)."
    if exercise_angina not in CATEGORIES["ExerciseAngina"]:
        return None, "Exercise angina must be Yes or No."
    if not (LIMITS["Oldpeak"][0] <= oldpeak <= LIMITS["Oldpeak"][1]):
        return None, "Oldpeak must be between -3.0 and 7.0."
    if st_slope not in CATEGORIES["ST_Slope"]:
        return None, "Choose a valid ST slope."

    return {
        "Age": age,
        "Sex": sex,
        "ChestPainType": chest,
        "RestingBP": resting_bp,
        "Cholesterol": cholesterol,
        "FastingBS": fasting_bs,
        "RestingECG": resting_ecg,
        "MaxHR": max_hr,
        "ExerciseAngina": exercise_angina,
        "Oldpeak": oldpeak,
        "ST_Slope": st_slope,
    }, None


def encode(row: dict) -> pd.DataFrame:
    """One-hot encode a single patient so the vector matches the trained feature columns."""
    frame = pd.DataFrame([row])
    for column, values in CATEGORIES.items():
        frame[column] = pd.Categorical(frame[column], categories=values)
    encoded = pd.get_dummies(frame, columns=list(CATEGORIES.keys()))
    for feature in COLUMNS:
        if feature not in encoded.columns:
            encoded[feature] = 0  # Missing dummy columns would otherwise break predict()
    return encoded[COLUMNS]


@app.route("/")
def index():
    """Render the screening form."""
    return render_template("index.html")


@app.route("/images/<path:filename>")
def project_image(filename):
    """Serve files from the Images folder (favicon and other project artwork)."""
    return send_from_directory(ROOT / "Images", filename)


@app.post("/predict")
def predict():
    """Return a disease probability from the saved logistic regression model."""
    cleaned, error = validate(request.get_json(silent=True) or {})
    if error:
        return jsonify({"ok": False, "error": error}), 400

    encoded = encode(cleaned)
    probability = float(MODEL.predict_proba(encoded)[0][1])
    label = int(MODEL.predict(encoded)[0])
    return jsonify(
        {
            "ok": True,
            "prediction": label,
            "probability": round(probability * 100, 1),
            "max_hr_formula": 220 - cleaned["Age"],
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
