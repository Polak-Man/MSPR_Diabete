from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Union
import mysql.connector
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

app = FastAPI(
    title="Diabetes API",
    description="API pour gérer les patients et diagnostics du diabète",
    version="1.0.0",
)


# Connexion à la base de données
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="diabete_mspr",
    )


# Fonction pour entraîner les modèles IA
def train_model():
    # Récupérer les données nécessaires depuis la base de données
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT age, glucose, bloodpressure, skinthickness, insulin, bodymassindex, diabetespedigreefunction, glycatedhemoglobine, diabete
        FROM medical_history mh
        JOIN diabetes_diagnosis dd ON mh.id = dd.id
        JOIN patient_table pt ON mh.id = pt.id
    """
    )
    data = cursor.fetchall()
    conn.close()

    # Convertir les données en DataFrame pour l'entraînement
    df = pd.DataFrame(data)

    # Imputer les valeurs manquantes avec la moyenne
    df.fillna(df.mean(), inplace=True)

    # Sélectionner les variables d'entrée (features) et la variable cible (target)
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

    # Diviser les données en données d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Créer les modèles
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    knn_model = KNeighborsRegressor(n_neighbors=5)
    svr_model = SVR(kernel="rbf")

    # Créer un modèle d'ensemble (VotingRegressor)
    ensemble_model = VotingRegressor(
        estimators=[("rf", rf_model), ("knn", knn_model), ("svr", svr_model)]
    )

    # Entraîner le modèle ensemble
    ensemble_model.fit(X_train, y_train)

    # Calculer les erreurs sur l'ensemble de test
    y_pred = ensemble_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Erreur absolue moyenne sur l'ensemble de test: {mae:.3f}")

    return ensemble_model


# Entraîner le modèle au démarrage
model = train_model()


# Modèles Pydantic
class Patient(BaseModel):
    age: int
    gender: str
    height: Optional[float]
    weight: Optional[float]
    frame: Optional[str]
    waist: Optional[float]
    hip: Optional[float]
    location: Optional[str]


class MedicalHistory(BaseModel):
    pregnancies: Optional[int] = None
    glucose: Optional[Union[int, float]] = None
    bloodpressure: Optional[Union[int, float]] = None
    skinthickness: Optional[Union[int, float]] = None
    insulin: Optional[Union[int, float]] = None
    bodymassindex: Optional[Union[int, float]] = None
    diabetespedigreefunction: Optional[Union[int, float]] = None
    glycatedhemoglobine: Optional[Union[int, float]] = None


class CholesterolBP(BaseModel):
    cholesterol: Optional[Union[int, float]] = None
    stabilizedglucide: Optional[Union[int, float]] = None
    hughdensitylipoprotein: Optional[Union[int, float]] = None
    ratioglucoseinsuline: Optional[Union[int, float]] = None


class DiabetesDiagnosis(BaseModel):
    diabete: bool


class PredictionRequest(BaseModel):
    age: int
    glucose: float
    bloodpressure: float
    skinthickness: float
    insulin: float
    bodymassindex: float
    diabetespedigreefunction: float
    glycatedhemoglobine: float


class DiabetesPredictionResponse(BaseModel):
    prediction: bool
    probability: float


# Routes CRUD pour Patient_table
@app.get("/patients", response_model=List[Patient], tags=["Patients"])
def get_patients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Patient_table")
    patients = cursor.fetchall()
    conn.close()
    return patients


@app.post("/patients", tags=["Patients"])
def add_patient(patient: Patient):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO Patient_table (age, gender, height, weight, frame, waist, hip, location)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        patient.age,
        patient.gender,
        patient.height,
        patient.weight,
        patient.frame,
        patient.waist,
        patient.hip,
        patient.location,
    )
    cursor.execute(sql, values)
    conn.commit()
    patient_id = cursor.lastrowid
    conn.close()
    return {"message": "Patient ajouté", "id": patient_id}


@app.put("/patients/{id}", tags=["Patients"])
def update_patient(id: int, patient: Patient):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    UPDATE Patient_table SET age=%s, gender=%s, height=%s, weight=%s, frame=%s, waist=%s, hip=%s, location=%s WHERE id=%s
    """
    values = (
        patient.age,
        patient.gender,
        patient.height,
        patient.weight,
        patient.frame,
        patient.waist,
        patient.hip,
        patient.location,
        id,
    )
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return {"message": "Patient mis à jour"}


@app.delete("/patients/{id}", tags=["Patients"])
def delete_patient(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Patient_table WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return {"message": "Patient supprimé"}


# Routes CRUD pour MedicalHistory
@app.get(
    "/medical_history", response_model=List[MedicalHistory], tags=["Medical History"]
)
def get_medical_histories():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medical_history")
    data = cursor.fetchall()
    conn.close()
    return data


@app.post("/medical_history", tags=["Medical History"])
def add_medical_history(history: MedicalHistory):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    INSERT INTO medical_history (pregnancies, glucose, bloodpressure, skinthickness, insulin, bodymassindex, diabetespedigreefunction, glycatedhemoglobine)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        history.pregnancies,
        history.glucose,
        history.bloodpressure,
        history.skinthickness,
        history.insulin,
        history.bodymassindex,
        history.diabetespedigreefunction,
        history.glycatedhemoglobine,
    )
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return {"message": "Historique médical ajouté"}


@app.put("/medical_history/{id}", tags=["Medical History"])
def update_medical_history(id: int, history: MedicalHistory):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = """
    UPDATE medical_history SET pregnancies=%s, glucose=%s, bloodpressure=%s, skinthickness=%s, insulin=%s, bodymassindex=%s, diabetespedigreefunction=%s, glycatedhemoglobine=%s WHERE id=%s
    """
    values = (
        history.pregnancies,
        history.glucose,
        history.bloodpressure,
        history.skinthickness,
        history.insulin,
        history.bodymassindex,
        history.diabetespedigreefunction,
        history.glycatedhemoglobine,
        id,
    )
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return {"message": "Historique médical mis à jour"}


@app.delete("/medical_history/{id}", tags=["Medical History"])
def delete_medical_history(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medical_history WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return {"message": "Historique médical supprimé"}


# Routes pour la prédiction de diabète
@app.post("/predict", response_model=DiabetesPredictionResponse, tags=["Prediction"])
def predict_diabetes(request: PredictionRequest):
    input_data = np.array(
        [
            [
                request.age,
                request.glucose,
                request.bloodpressure,
                request.skinthickness,
                request.insulin,
                request.bodymassindex,
                request.diabetespedigreefunction,
                request.glycatedhemoglobine,
            ]
        ]
    )

    # Faire la prédiction avec le modèle entraîné
    prediction = model.predict(input_data)
    predicted_class = (prediction >= 0.5).astype(
        int
    )  # Seuil de 0.5 pour classifier (diabète ou non)
    return DiabetesPredictionResponse(
        prediction=bool(predicted_class[0]), probability=prediction[0]
    )


# Lancer le serveur
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
