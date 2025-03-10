import pandas as pd
import mysql.connector

# Connexion à la base de données
conn = mysql.connector.connect(
    host="localhost",
    user="root",  
    password="",
    database="diabete_mspr",
)
cursor = conn.cursor()

# Charger le fichier CSV
df = pd.read_csv("fichier_sortie_v8.csv", sep=",")

# Remplacer les valeurs "NA" ou "Na" par None pour db
df = df.replace(["NA", "Na"], None)


def safe_float(value):
    """Convertit en float si possible, sinon renvoie None"""
    try:
        return float(value) if value is not None else None
    except ValueError:
        return None


def safe_int(value):
    """Convertit en int si possible, sinon renvoie None"""
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None


def insert_patient(row):
    sql = """
    INSERT INTO Patient_table (age, gender, height, weight, frame, waist, hip, location)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        values = (
            safe_int(row["age"]),
            row["gender"],
            safe_float(row["height"]),
            safe_float(row["weight"]),
            row["frame"],
            safe_float(row["waist"]),
            safe_float(row["hip"]),
            row["location"],
        )
        print(f"Inserting: {values}")
        cursor.execute(sql, values)
        return cursor.lastrowid  # Récupère l'ID inséré
    except Exception as e:
        print(f"Erreur lors de l'insertion du patient: {e}")
        return None


def insert_medical_history(row, patient_id):
    if patient_id is None:
        return
    sql = """
    INSERT INTO medical_history (id, pregnancies, glucose, bloodpressure, skinthickness, insulin, bodymassindex, diabetespedigreefunction, glycatedhemoglobine)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        patient_id,
        safe_int(row["pregnancies"]),
        safe_float(row["glucose"]),
        safe_float(row["bloodpressure"]),
        safe_float(row["skinthickness"]),
        safe_float(row["insulin"]),
        safe_float(row["bmi"]),
        safe_float(row["diabetespedigreefunction"]),
        safe_float(row.get("glycatedhemoglobine", None)),
    )
    try:
        cursor.execute(sql, values)
    except Exception as e:
        print(f"Erreur lors de l'insertion des antécédents médicaux: {e}")


def insert_cholesterol_bp(row, patient_id):
    if patient_id is None:
        return
    sql = """
    INSERT INTO cholesterol_bp (id, cholesterol, stabilizedglucide, hughdensitylipoprotein, ratioglucoseinsuline)
    VALUES (%s, %s, %s, %s, %s)
    """
    values = (
        patient_id,
        safe_float(row.get("cholesterol", None)),
        safe_float(row.get("stabilizedglucide", None)),
        safe_float(row.get("hughdensitylipoprotein", None)),
        safe_float(row.get("ratioglucoseinsuline", None)),
    )
    try:
        cursor.execute(sql, values)
    except Exception as e:
        print(f"Erreur lors de l'insertion du cholestérol et de la tension: {e}")


def insert_diabetes_diagnosis(row, patient_id):
    if patient_id is None:
        return
    sql = """
    INSERT INTO diabetes_diagnosis (id, diabete)
    VALUES (%s, %s)
    """
    values = (patient_id, row["diabete"])
    try:
        cursor.execute(sql, values)
    except Exception as e:
        print(f"Erreur lors de l'insertion du diagnostic de diabète: {e}")


# Insérer les données
total_rows = len(df)
for index, row in df.iterrows():
    patient_id = insert_patient(row)
    insert_medical_history(row, patient_id)
    insert_cholesterol_bp(row, patient_id)
    insert_diabetes_diagnosis(row, patient_id)
    if index % 100 == 0:
        print(f"Progression: {index}/{total_rows}")

# Commit et fermeture
conn.commit()
cursor.close()
conn.close()
print("Import terminé avec succès.")
