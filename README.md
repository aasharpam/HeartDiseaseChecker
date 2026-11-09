# Heart Health Checker (PulseCheck)

Author: **Aashar Pamidiparti**

A hobby project that turns a logistic regression model into a mobile-friendly screening form. You enter clinical indicators from `heart.csv`, the app validates them, and a saved classifier estimates the chance of a heart-disease signal.

This tool is for educational and experimental use only. It is not a diagnosis, medical advice, or a substitute for professional care.

## Features

- Responsive form with light/dark theme slider
- About popup describing the project and author
- Client and server validation for every input
- Max heart rate auto-filled as `220 − Age`
- Logistic regression prediction with a probability score

## Inputs

Age, Sex, Chest Pain Type, Resting Blood Pressure, Cholesterol, FastingBS, RestingECG, Max Heart Rate, Exercise Angina, Oldpeak, and ST_Slope.

## Project layout

```
app.py                 Flask server and /predict API
train_model.py         Retrains and saves heart_classifier.joblib
heart_model.py         Original Colab-style training / CLI script
heart.csv              Training dataset
heart_classifier.joblib
templates/index.html
static/css/style.css
static/js/app.js
Images/Favicon/        Site favicon
requirements.txt
```

## Setup

Python 3.12+ is recommended.

```bash
python -m pip install -r requirements.txt
```

Train (or retrain) the model:

```bash
python train_model.py
```

Run the site:

```bash
python app.py
```

Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

## How prediction works

1. Categorical fields are one-hot encoded with a fixed category list.
2. Dummy columns are aligned to the columns stored with the model.
3. `LogisticRegression` returns a class label and a probability.

`heart_model.py` is the earlier Google Colab workflow. The website uses `train_model.py` and `app.py` instead.

## Disclaimer

This application is built strictly for educational, experimental, and hobbyist exploration. It is not intended to serve as a diagnostic tool, medical advice, or a substitute for professional healthcare evaluation.
