from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import re

# -------------------------------
# APP INIT
# -------------------------------
app = FastAPI(title="Cybersecurity Detection API")

# -------------------------------
# LOAD MODELS (MATCH TRAINING)
# -------------------------------
model = joblib.load("Models/model.pkl")
vectorizer = joblib.load("Models/vectorizer.pkl")
le = joblib.load("Models/label_encoder.pkl")

# -------------------------------
# RULE-BASED PATTERNS
# -------------------------------
SQL_PATTERNS = [
    r"(?i)(\b(select|insert|update|delete|drop|truncate|alter|create|exec|execute|union|having|group\s+by|order\s+by)\b)",
    r"(?i)(--|\#|\/\*|\*\/)",
    r"(?i)(\bor\b\s+[\w'\"]+\s*=\s*[\w'\"]+)",
    r"(?i)(\band\b\s+[\w'\"]+\s*=\s*[\w'\"]+)",
]

XSS_PATTERNS = [
    r"(?i)<\s*script[\s>]",
    r"(?i)\bon\w+\s*=",
    r"(?i)javascript\s*:",
]

def rule_based_predict(text):
    for p in SQL_PATTERNS:
        if re.search(p, text):
            return "SQLi"
    for p in XSS_PATTERNS:
        if re.search(p, text):
            return "XSS"
    return None

# -------------------------------
# PREPROCESS (SAME AS TRAIN)
# -------------------------------
def preprocess(text):
    if not isinstance(text, str):
        return ""
    text = text.replace("&lt;", "<").replace("&gt;", ">")
    text = re.sub(r"\s+", " ", text).strip()
    return text

# -------------------------------
# INPUT FORMAT
# -------------------------------
class InputData(BaseModel):
    text: str

# -------------------------------
# ROUTES
# -------------------------------
@app.get("/")
def home():
    return {"message": "🚀 Cybersecurity Detection API Running"}

@app.post("/predict")
def predict(data: InputData):
    try:
        clean = preprocess(data.text)

        # 🔹 RULE-BASED FIRST (FAST DETECTION)
        rule = rule_based_predict(clean)
        if rule == "SQLi":
            return {"prediction": "⚠️ SQL Injection Attack", "source": "rule-based"}
        if rule == "XSS":
            return {"prediction": "⚠️ XSS Attack", "source": "rule-based"}

        # 🔹 ML PREDICTION
        vector = vectorizer.transform([clean])

        pred = model.predict(vector)[0]   # single value
        label = le.inverse_transform([pred])[0]

        # 🔹 OPTIONAL CONFIDENCE (since you used CalibratedClassifierCV)
        confidence = None
        if hasattr(model, "predict_proba"):
            prob = model.predict_proba(vector)[0]
            confidence = float(max(prob))

        # 🔹 FINAL OUTPUT
        if label == "Normal":
            result = "✅ Safe Input"
        elif label == "SQLi":
            result = "⚠️ SQL Injection Attack"
        else:
            result = "⚠️ XSS Attack"

        return {
            "prediction": result,
            "label": label,
            "confidence": confidence,
            "source": "ml-model"
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": "❌ Prediction failed"
        }