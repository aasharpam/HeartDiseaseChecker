# -*- coding: utf-8 -*-
# Author: Aashar Pamidiparti
# Original Colab-style training and command-line prediction notebook.

import pandas as pd
from google.colab import files
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import random

uploaded = files.upload()  # Prompt for heart.csv in Google Colab

data = pd.read_csv("heart.csv")
data.head()

X = data.drop("HeartDisease", axis = 1)  # Drop the label before encoding
Y = data["HeartDisease"]

# Known category levels for one-hot encoding
catagories = {
    "ChestPainType": ['ATA', 'NAP', 'ASY', 'TA'],
    "Sex": ['M', 'F'],
    "RestingECG": ['Normal', 'ST', 'LVH'],
    "ExerciseAngina": ['N', 'Y'],
    "ST_Slope": ['Up', 'Flat', 'Down']
}

X = pd.get_dummies(X, columns = catagories.keys())
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size = 0.2, random_state = 42)
Logisitic_Classifier = LogisticRegression()
Logisitic_Classifier.fit(X_train, Y_train)

def get_user_input():
  """Collect one patient profile from the terminal."""
  age = int(input("Enter Age:"))
  sex = input("Enter Gender (M/F):").upper()
  chest_pain_type = input("Enter Chest Pain Type (ATA/NAP/ASY/TA):")
  resting_bp = int(input("Enter Resting Blood Pressure:"))
  cholesterol = int(input("Enter Cholesterol:"))
  fasting_bs = int(input("Enter Fasting Blood Sugar:"))
  resting_ecg = input("Enter Resting ECG (Normal/ST/LVH):")
  max_hr = int(input("Enter max heart rate:"))
  exercise_angina = input("Enter Exercise Angina (N/Y):")
  oldpeak = float(input("Enter Old Peak:"))
  st_slope = input("Enter ST Slope (Up/Flat/Down):")

  return {
      "Age": age,
      "Sex": sex,
      "ChestPainType": chest_pain_type,
      "RestingBP": resting_bp,
      "Cholesterol": cholesterol,
      "FastingBS": fasting_bs,
      "RestingECG": resting_ecg,
      "MaxHR": max_hr,
      "ExerciseAngina": exercise_angina,
      "Oldpeak": oldpeak,
      "ST_Slope": st_slope
  }

patient_data = get_user_input()
patient_df = pd.DataFrame([patient_data])
patient_df = pd.get_dummies(patient_df, columns = catagories.keys())

# A single row will not contain every dummy column, so pad missing ones with 0.
missing_features = set(X_train.columns) - set(patient_df.columns)

for feature in missing_features:
  patient_df[feature] = 0

patient_df = patient_df[X_train.columns]  # Match the training column order
prediction = Logisitic_Classifier.predict(patient_df)

if prediction[0] == 1:
  print("Heart Disease Detected")
else:
  print("Normal")
