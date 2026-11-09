"""
Train and save the Heart Health Checker classifier.

Author: Aashar Pamidiparti
"""

import joblib
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parent

# Keep dummy-variable order identical to the web app encoder.
CATEGORIES = {
    "ChestPainType": ["ATA", "NAP", "ASY", "TA"],
    "Sex": ["M", "F"],
    "RestingECG": ["Normal", "ST", "LVH"],
    "ExerciseAngina": ["N", "Y"],
    "ST_Slope": ["Up", "Flat", "Down"],
}


def main() -> None:
    """Fit logistic regression on heart.csv and write heart_classifier.joblib."""
    data = pd.read_csv(ROOT / "heart.csv")
    X = data.drop("HeartDisease", axis=1)  # Clinical features only
    y = data["HeartDisease"]  # 1 = disease signal, 0 = none

    for column, values in CATEGORIES.items():
        X[column] = pd.Categorical(X[column], categories=values)

    X = pd.get_dummies(X, columns=list(CATEGORIES.keys()))
    # Hold out 20% so training matches the original notebook split.
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=2000)
    model.fit(X_train, y_train)

    payload = {
        "model": model,
        "columns": list(X_train.columns),  # Stored so inference can realign dummies
        "categories": CATEGORIES,
    }
    out = ROOT / "heart_classifier.joblib"
    joblib.dump(payload, out)
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
