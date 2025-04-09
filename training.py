import joblib
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
import mysql.connector
import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error


# Fonction pour entraîner et sauvegarder le modèle
def train_and_save_model():
    # Connexion à la base de données et récupération des données
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="diabete_mspr",
    )
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT age, glucose, bloodpressure, skinthickness, insulin, bodymassindex, diabetespedigreefunction, glycatedhemoglobine, diabete
        FROM medical_history mh
        JOIN diabetes_diagnosis dd ON mh.id = dd.id
    """
    )
    data = cursor.fetchall()
    conn.close()

    # Conversion en DataFrame
    df = pd.DataFrame(data)

    # Variables d'entrée et cible
    X = df[
        [
            "age",
            "glucose",
            "bloodpressure",
            "skinthickness",
            "insulin",
            "bodymassindex",
            "diabetespedigreefunction",
            "glycatedhemoglobine",
        ]
    ]
    y = df["diabete"]

    # Séparer les données en ensembles d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Modèles
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    knn_model = KNeighborsRegressor(n_neighbors=5)
    svr_model = SVR(kernel="rbf")

    # Modèle ensemble
    ensemble_model = VotingRegressor(
        estimators=[("rf", rf_model), ("knn", knn_model), ("svr", svr_model)]
    )

    # Entraîner le modèle ensemble
    ensemble_model.fit(X_train, y_train)

    # Calcul de l'erreur sur le test
    y_pred = ensemble_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Erreur absolue moyenne : {mae:.3f}")

    # Sauvegarder le modèle entraîné
    joblib.dump(ensemble_model, "diabetes_model.joblib")
    print("Modèle sauvegardé avec succès.")


# Entraîner et sauvegarder le modèle
train_and_save_model()
