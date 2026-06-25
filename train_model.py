import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score

df = pd.read_csv("dataset/electricity_data.csv")

df["Sudden_Drop"] = df["Sudden_Drop"].map({"YES":1,"NO":0})
df["Area_Mismatch"] = df["Area_Mismatch"].map({"YES":1,"NO":0})
df["Feeder_Mismatch"] = df["Feeder_Mismatch"].map({"YES":1,"NO":0})

X = df[[
"Monthly_Consumption",
"Avg_6_Months",
"Area_Avg",
"Feeder_Avg",
"Deviation",
"Sudden_Drop",
"Area_Mismatch",
"Feeder_Mismatch"
]]

y = df["NTL_Label"]

X_train, X_test, y_train, y_test = train_test_split(
X, y, test_size=0.2, random_state=42
)

scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=100)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("Accuracy:", accuracy)
print("Precision:", precision)
print("Recall:", recall)
print("F1:", f1)
print("Confusion Matrix:", cm)

joblib.dump(model, "model/model.pkl")
joblib.dump(scaler, "model/scaler.pkl")

metrics = {
"accuracy":accuracy,
"precision":precision,
"recall":recall,
"f1":f1,
"confusion_matrix":cm.tolist()
}

joblib.dump(metrics,"model/metrics.pkl")