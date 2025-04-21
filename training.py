import os
import joblib
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error


# Connexion MySQL
def get_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="diabete_mspr",
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT pt.age, mh.glucose, mh.bloodpressure, mh.skinthickness, mh.insulin, mh.bodymassindex, mh.diabetespedigreefunction, mh.glycatedhemoglobine, dd.diabete
        FROM patient_table pt
        JOIN medical_history mh ON pt.id = mh.id
        JOIN diabetes_diagnosis dd ON mh.id = dd.id
        """
    )
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data)


os.makedirs("joblib", exist_ok=True)


# Fonction générique d'entraînement
def train_model(X, y, model_name):
    # Imputer les valeurs manquantes dans X
    imputer_X = SimpleImputer(strategy="mean")
    X_imputed = imputer_X.fit_transform(X)

    # Imputer les valeurs manquantes dans y (cibles)
    imputer_y = SimpleImputer(strategy="mean")
    y_imputed = imputer_y.fit_transform(y.values.reshape(-1, 1)).ravel()

    X_train, X_test, y_train, y_test = train_test_split(
        X_imputed, y_imputed, test_size=0.2, random_state=42
    )

    # Modèles
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    knn = KNeighborsRegressor(n_neighbors=5)
    svr = SVR(kernel="rbf")

    model = VotingRegressor(estimators=[("rf", rf), ("knn", knn), ("svr", svr)])
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"[{model_name}] Erreur absolue moyenne : {mae:.3f}")

    # Sauvegarder le modèle dans le dossier 'joblib'
    joblib.dump(model, f"joblib/{model_name}.joblib")
    print(f"Modèle '{model_name}' sauvegardé dans le dossier 'joblib'.\n")


# Fonction centrale
def train_all_models():
    df = get_data()

    features = [
        "age",
        "glucose",
        "bloodpressure",
        "skinthickness",
        "insulin",
        "bodymassindex",
        "diabetespedigreefunction",
        "glycatedhemoglobine",
    ]

    # 1. Prédiction du diabète
    X_diabetes = df[features]
    y_diabetes = df["diabete"]
    train_model(X_diabetes, y_diabetes, "diabetes_model")

    # 2. Glucose
    X_glucose = df.drop(columns=["glucose"])
    y_glucose = df["glucose"]
    train_model(X_glucose, y_glucose, "glucose_model")

    # 3. Insuline
    X_insulin = df.drop(columns=["insulin"])
    y_insulin = df["insulin"]
    train_model(X_insulin, y_insulin, "insulin_model")

    # 4. Pression artérielle
    X_bp = df.drop(columns=["bloodpressure"])
    y_bp = df["bloodpressure"]
    train_model(X_bp, y_bp, "bloodpressure_model")

    # 5. BMI
    X_bmi = df.drop(columns=["bodymassindex"])
    y_bmi = df["bodymassindex"]
    train_model(X_bmi, y_bmi, "bmi_model")

    # 6. HbA1c
    X_hba1c = df.drop(columns=["glycatedhemoglobine"])
    y_hba1c = df["glycatedhemoglobine"]
    train_model(X_hba1c, y_hba1c, "hba1c_model")

    # 7. Diabetes Pedigree Function
    X_dpf = df.drop(columns=["diabetespedigreefunction"])
    y_dpf = df["diabetespedigreefunction"]
    train_model(X_dpf, y_dpf, "dpf_model")

    # 8. Épaisseur de peau
    X_skin = df.drop(columns=["skinthickness"])
    y_skin = df["skinthickness"]
    train_model(X_skin, y_skin, "skinthickness_model")

    # 9. Score de risque calculé
    df["risk_score"] = (
        df["diabete"] * 0.7
        + (df["glucose"] / 200) * 0.15
        + (df["bodymassindex"] / 50) * 0.15
    )
    X_risk = df[features]
    y_risk = df["risk_score"]
    train_model(X_risk, y_risk, "risk_score_model")


if __name__ == "__main__":
    train_all_models()
