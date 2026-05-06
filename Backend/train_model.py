"""
train_model.py — Cybersecurity Attack Detection System
Hybrid ML + Rule-Based approach with multiclass classification.
"""

import re
import pandas as pd
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
from sklearn.pipeline import FeatureUnion
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 1. RULE-BASED ENGINE
# ─────────────────────────────────────────────

SQL_PATTERNS = [
    r"(?i)(\b(select|insert|update|delete|drop|truncate|alter|create|exec|execute|union|having|group\s+by|order\s+by)\b)",
    r"(?i)(--|\#|\/\*|\*\/)",
    r"(?i)(\bor\b\s+[\w'\"]+\s*=\s*[\w'\"]+)",
    r"(?i)(\band\b\s+[\w'\"]+\s*=\s*[\w'\"]+)",
]

<<<<<<< HEAD:Backend/train_model.py
df = pd.read_excel("Datasets/balanced_dataset_75000.xlsx")
=======
XSS_PATTERNS = [
    r"(?i)<\s*script[\s>]",
    r"(?i)\bon\w+\s*=",
    r"(?i)javascript\s*:",
]
>>>>>>> d95d008 (Add dataset and trained model files):train_model.py

def rule_based_predict(text):
    sql_hits = sum(1 for p in SQL_PATTERNS if re.search(p, text))
    xss_hits = sum(1 for p in XSS_PATTERNS if re.search(p, text))

    if sql_hits > 0:
        return "SQLi"
    if xss_hits > 0:
        return "XSS"
    return None


# ─────────────────────────────────────────────
# 2. PREPROCESS
# ─────────────────────────────────────────────

def preprocess(text):
    if not isinstance(text, str):
        return ""
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    text = re.sub(r"\s+", " ", text).strip()
    return text


# ─────────────────────────────────────────────
# 3. LOAD DATA
# ─────────────────────────────────────────────

print("Loading dataset...")
df = pd.read_excel("Datasets/balanced_dataset_15000.xlsx")

df = df.dropna(subset=["text", "attack_type"])
df = df.drop_duplicates(subset=["text"])
df["text"] = df["text"].apply(preprocess)

le = LabelEncoder()
y = le.fit_transform(df["attack_type"])
X_text = df["text"].values

print("Classes:", dict(zip(le.classes_, le.transform(le.classes_))))

# ─────────────────────────────────────────────
# 4. VECTORIZER (FIXED)
# ─────────────────────────────────────────────

vec_char = TfidfVectorizer(
    analyzer="char_wb",
    ngram_range=(2, 4),
    max_features=20000,
)

vec_word = TfidfVectorizer(
    analyzer="word",
    ngram_range=(1, 2),
    max_features=10000,
    token_pattern=r"(?u)\b\w+\b|['\"\-\#\;<>\/]",
)

# ✅ SINGLE COMBINED VECTORIZER (FIX)
vectorizer = FeatureUnion([
    ("char", vec_char),
    ("word", vec_word)
])

X = vectorizer.fit_transform(X_text)

print("Feature shape:", X.shape)

# ─────────────────────────────────────────────
# 5. HANDLE IMBALANCE
# ─────────────────────────────────────────────

smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

# ─────────────────────────────────────────────
# 6. SPLIT
# ─────────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, stratify=y_res, random_state=42
)

# ─────────────────────────────────────────────
# 7. MODEL
# ─────────────────────────────────────────────

model = CalibratedClassifierCV(
    LinearSVC(class_weight="balanced"),
    cv=3
)

model.fit(X_train, y_train)

print("Model trained!")

# ─────────────────────────────────────────────
# 8. EVALUATION
# ─────────────────────────────────────────────

y_pred = model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nReport:\n", classification_report(y_test, y_pred))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))

# ─────────────────────────────────────────────
# 9. SAVE (FIXED)
# ─────────────────────────────────────────────

import os
os.makedirs("Models", exist_ok=True)

joblib.dump(model, "Models/model.pkl")
joblib.dump(vectorizer, "Models/vectorizer.pkl")
<<<<<<< HEAD:Backend/train_model.py
=======
joblib.dump(le, "Models/label_encoder.pkl")
>>>>>>> d95d008 (Add dataset and trained model files):train_model.py

print("Model saved!")

# ─────────────────────────────────────────────
# 10. PREDICT FUNCTION (FIXED)
# ─────────────────────────────────────────────

def predict_input(text):
    clean = preprocess(text)

    rule = rule_based_predict(clean)
    if rule == "SQLi":
        return "SQL Injection Attack"
    if rule == "XSS":
        return "XSS Attack"

    vector = vectorizer.transform([clean])
    pred = model.predict(vector)[0]
    label = le.inverse_transform([pred])[0]

    if label == "Normal":
        return "Safe Input"
    elif label == "SQLi":
        return "SQL Injection Attack"
    else:
        return "XSS Attack"


# ─────────────────────────────────────────────
# 11. TEST
# ─────────────────────────────────────────────

tests = [
    "<script>alert(1)</script>",
    "' OR 1=1--",
    "https://google.com"
]

for t in tests:
    print(t, "→", predict_input(t))