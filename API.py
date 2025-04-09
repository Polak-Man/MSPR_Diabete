from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Union
import mysql.connector

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


# CRUD pour CholesterolBP
@app.get("/cholesterol_bp", response_model=List[CholesterolBP], tags=["Cholesterol BP"])
def get_cholesterol_bp():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cholesterol_bp")
    data = cursor.fetchall()
    conn.close()
    return data


@app.post("/cholesterol_bp", tags=["Cholesterol BP"])
def add_cholesterol_bp(cholesterol: CholesterolBP):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO cholesterol_bp (cholesterol, stabilizedglucide, hughdensitylipoprotein, ratioglucoseinsuline) VALUES (%s, %s, %s, %s)"
    values = (
        cholesterol.cholesterol,
        cholesterol.stabilizedglucide,
        cholesterol.hughdensitylipoprotein,
        cholesterol.ratioglucoseinsuline,
    )
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return {"message": "Données cholestérol ajoutées"}


@app.put("/cholesterol_bp/{id}", tags=["Cholesterol BP"])
def update_cholesterol_bp(id: int, cholesterol: CholesterolBP):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE cholesterol_bp SET cholesterol=%s, stabilizedglucide=%s, hughdensitylipoprotein=%s, ratioglucoseinsuline=%s WHERE id=%s"
    values = (
        cholesterol.cholesterol,
        cholesterol.stabilizedglucide,
        cholesterol.hughdensitylipoprotein,
        cholesterol.ratioglucoseinsuline,
        id,
    )
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return {"message": "Données cholestérol mises à jour"}


@app.delete("/cholesterol_bp/{id}", tags=["Cholesterol BP"])
def delete_cholesterol_bp(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cholesterol_bp WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return {"message": "Données cholestérol supprimées"}


# CRUD pour DiabetesDiagnosis
@app.get("/diagnoses", response_model=List[DiabetesDiagnosis], tags=["Diagnoses"])
def get_diagnoses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM diabetes_diagnosis")
    data = cursor.fetchall()
    conn.close()
    return data


@app.post("/diagnoses", tags=["Diagnoses"])
def add_diagnosis(diagnosis: DiabetesDiagnosis):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "INSERT INTO diabetes_diagnosis (diabete) VALUES (%s)"
    values = (diagnosis.diabete,)
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return {"message": "Diagnostic ajouté"}


@app.put("/diagnoses/{id}", tags=["Diagnoses"])
def update_diagnosis(id: int, diagnosis: DiabetesDiagnosis):
    conn = get_db_connection()
    cursor = conn.cursor()
    sql = "UPDATE diabetes_diagnosis SET diabete=%s WHERE id=%s"
    values = (diagnosis.diabete, id)
    cursor.execute(sql, values)
    conn.commit()
    conn.close()
    return {"message": "Diagnostic mis à jour"}


@app.delete("/diagnoses/{id}", tags=["Diagnoses"])
def delete_diagnosis(id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM diabetes_diagnosis WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return {"message": "Diagnostic supprimé"}


# Lancer le serveur
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
