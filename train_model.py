

import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 🔥 Best model for text
from sklearn.svm import LinearSVC

print(" Starting Training...")

df = pd.read_excel("Datasets/balanced_dataset_75000.xlsx")

print(" Dataset Loaded!")
print(df.head())


df = df.dropna()
df = df.drop_duplicates()


X = df['text']
y = df['label']

vectorizer = TfidfVectorizer(
    ngram_range=(1,2),
    max_features=5000,
    stop_words='english'
)

X_vectorized = vectorizer.fit_transform(X)


X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42
)


model = LinearSVC()

model.fit(X_train, y_train)

print(" Model Training Completed!")


y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n Accuracy:", accuracy)
print("\n Classification Report:\n", classification_report(y_test, y_pred))
print("\n Confusion Matrix:\n", confusion_matrix(y_test, y_pred))


joblib.dump(model, "Models/model.pkl")
joblib.dump(vectorizer, "Models/vectorizer.pkl")

print("\n Model Saved Successfully!")

def predict_input(text):
    vector = vectorizer.transform([text])
    prediction = model.predict(vector)[0]
    
    return " Attack Detected" if prediction == 1 else " Safe Input"

print("\n Testing Samples:")
print("<script>alert(1)</script> →", predict_input("<script>alert(1)</script>"))
print("' OR 1=1-- →", predict_input("' OR 1=1--"))
print("https://google.com →", predict_input("https://google.com"))