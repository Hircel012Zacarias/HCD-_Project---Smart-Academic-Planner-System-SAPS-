import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle

print("=== TRAINING MODEL ===")

# LOAD REAL DATA
df_real = pd.read_csv(r"d:\SAPS Project\Student Academic Planner\SAPS dataset.csv - Form Responses 1 (1).csv")

if "Timestamp" in df_real.columns:
    df_real = df_real.drop(columns=["Timestamp"])

df_real.columns = [
    "year",
    "study_hours",
    "sleep_hours",
    "attendance",
    "screen_time",
    "extracurricular",
    "performance",
    "overwhelmed",
    "procrastination",
    "time_management",
    "schedule",
    "phone_usage",
    "lifestyle_impact"
]

# MAP CATEGORICAL DATA
df_real["procrastination"] = df_real["procrastination"].map({
    "Never": 0, "Rarely": 1, "Sometimes": 2, "Often": 3, "Always": 4
})

df_real["time_management"] = df_real["time_management"].map({
    "Very Poor": 1, "Poor": 2, "Average": 3, "Good": 4, "Excellent": 5
})

df_real["schedule"] = df_real["schedule"].map({
    "Yes": 1, "No": 0
})

df_real["lifestyle_impact"] = df_real["lifestyle_impact"].map({
    "Not at all": 1, "Slightly": 2, "Moderately": 3,
    "Significantly": 4, "Extremely": 5
})

# CLEAN NUMERIC COLUMNS (FIXED)
cols_to_clean = [
    "study_hours",
    "sleep_hours",
    "attendance",
    "screen_time",
    "extracurricular",
    "performance",
    "phone_usage"
]

for col in cols_to_clean:
    df_real[col] = df_real[col].astype(str).str.replace(r"[^\d.]", "", regex=True)
    df_real[col] = pd.to_numeric(df_real[col], errors='coerce')

# remover apenas linhas inválidas dessas colunas
df_real = df_real.dropna(subset=cols_to_clean)

print("Real data cleaned:", df_real.shape)
print(df_real.head())

# SYNTHETIC DATA
n = 300

df_syn = pd.DataFrame({
    "study_hours": np.random.uniform(1, 10, n),
    "sleep_hours": np.random.uniform(4, 9, n),
    "attendance": np.random.uniform(50, 100, n),
    "screen_time": np.random.uniform(1, 8, n),
    "extracurricular": np.random.uniform(0, 5, n)
})

df_syn["performance"] = (
    df_syn["study_hours"] * 6 +
    df_syn["sleep_hours"] * 3 +
    df_syn["attendance"] * 0.4 -
    df_syn["screen_time"] * 2.5 +
    df_syn["extracurricular"] * 1.5 +
    np.random.normal(0, 5, n)
)

df_syn["performance"] = np.clip(df_syn["performance"], 0, 100)

# MERGE DATA
df_real_small = df_real[[
    "study_hours",
    "sleep_hours",
    "attendance",
    "screen_time",
    "extracurricular",
    "performance"
]]

df_final = pd.concat([df_syn, df_real_small])

print("Final dataset:", df_final.shape)

# TRAIN MODEL
X = df_final.drop("performance", axis=1)
y = df_final["performance"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = LinearRegression()
model.fit(X_train, y_train)

# SAVE MODEL
pickle.dump(model, open("model.pkl", "wb"))
print("Model trained and saved as model.pkl")

from sklearn.metrics import mean_absolute_error, r2_score

# TESTE
y_pred = model.predict(X_test)

print("MAE:", mean_absolute_error(y_test, y_pred))
print("R2 Score:", r2_score(y_test, y_pred))
