from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# --- 1. Connexion à MongoDB ---
client = MongoClient("mongodb://localhost:27017")
db = client["meteo"]
hours_col = db["Hours"]
days_col = db["Days"]

# --- 2. Chargement des données ---
hours_docs = list(hours_col.find({"city": "Antananarivo"}))
days_docs = list(days_col.find({"city": "Antananarivo"}))

df_hours = pd.DataFrame(hours_docs)
df_days = pd.DataFrame(days_docs)

# --- 3. Préparation des dates ---
df_hours["date"] = df_hours["_id"].str[:10]
df = pd.merge(df_hours, df_days[["date", "sunrise", "sunset"]], on="date", how="left")

# --- 4. Traitement des types et valeurs manquantes ---
numeric_cols = ["feels_like", "temp_min", "temp_max", "humidity", "rain"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Conversion des heures en secondes
def time_to_seconds(t):
    if isinstance(t, str) and len(t.split(":")) == 3:
        h, m, s = map(int, t.split(":"))
        return h * 3600 + m * 60 + s
    return np.nan

df["sunrise_sec"] = df["sunrise"].apply(time_to_seconds)
df["sunset_sec"] = df["sunset"].apply(time_to_seconds)

# Suppression des lignes incomplètes
df.dropna(subset=numeric_cols + ["sunrise_sec", "sunset_sec"], inplace=True)

# --- 5. Création des features et target ---
features = ["feels_like", "temp_min", "temp_max", "humidity", "rain", "sunrise_sec", "sunset_sec"]
X = df[features].values
y = df["feels_like"].shift(-1).dropna().values
X = X[:-1]  # synchroniser les tailles
df = df.iloc[:-1]  # même filtrage

infos = df[["time", "description", "icon"]].copy()

# --- 6. Séparation et normalisation ---
X_train, X_test, y_train, y_test, infos_train, infos_test = train_test_split(
    X, y, infos, test_size=0.2, random_state=42
)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- 7. Entraînement du modèle ---
model = MLPRegressor(hidden_layer_sizes=(32, 16), max_iter=500, random_state=42)
model.fit(X_train_scaled, y_train)

# --- 8. Évaluation ---
y_pred = model.predict(X_test_scaled)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"✅ RMSE sur test : {rmse:.2f} °C")

# --- 9. Affichage des résultats ---
n = min(10, len(infos_test))
for i in range(n):
    info = infos_test.iloc[i]
    print(f"\n🕒 Heure         : {info['time']}")
    print(f"📋 Description   : {info['description']}")
    print(f"🌡️ Prédit        : {round(y_pred[i], 2)} °C")
    print(f"🌡️ Réel (T+1)    : {round(y_test[i], 2)} °C")
    print(f"🌥️ Icône         : {info['icon']}")


# --- 10. Visualisation : courbe de perte ---
if hasattr(model, "loss_curve_"):
    plt.figure(figsize=(8, 4))
    plt.plot(model.loss_curve_)
    plt.title("Courbe de perte (MLP)")
    plt.xlabel("Itérations")
    plt.ylabel("Loss")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# --- 11. Fonction de prédiction future ---
def predict_future_weather(input_features):
    input_scaled = scaler.transform([input_features])
    return model.predict(input_scaled)[0]
