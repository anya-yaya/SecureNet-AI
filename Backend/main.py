from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import re

# -------------------------------
# APP INIT
# -------------------------------
app = FastAPI()

# -------------------------------
# LOAD MODELS
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
    sql_hits = sum(1 for p in SQL_PATTERNS if re.search(p, text))
    xss_hits = sum(1 for p in XSS_PATTERNS if re.search(p, text))

    if sql_hits > 0:
        return "SQLi"
    if xss_hits > 0:
        return "XSS"
    return None

# -------------------------------
# PREPROCESS
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
    return {"message": "🚀 API running"}

@app.post("/predict")
def predict(data: InputData):
    try:
        text = data.text
        clean = preprocess(text)

        # 🔹 RULE-BASED FIRST
        rule = rule_based_predict(clean)
        if rule == "SQLi":
            return {"result": "⚠️ SQL Injection Attack"}
        if rule == "XSS":
            return {"result": "⚠️ XSS Attack"}

        # 🔹 ML PREDICTION
        vector = vectorizer.transform([clean])
        pred = model.predict(vector)

        # 🔥 SAFE decoding
        pred_label = le.inverse_transform(pred)[0]

        # 🔹 FINAL OUTPUT
        if pred_label == "Normal":
            return {"result": "✅ Safe Input"}
        elif pred_label == "SQLi":
            return {"result": "⚠️ SQL Injection Attack"}
        else:
            return {"result": "⚠️ XSS Attack"}

    except Exception as e:
        return {
            "error": str(e),
            "message": "❌ Prediction failed"
        }