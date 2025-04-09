import pandas as pd
import mysql.connector
import os


# Fonction pour exécuter un fichier SQL
def execute_sql_file(cursor, filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        sql = file.read()
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                except Exception as e:
                    print(f"Erreur lors de l'exécution de la requête : {e}")


# Connexion initiale sans spécifier de base de données
conn = mysql.connector.connect(host="localhost", user="root", password="")
cursor = conn.cursor()

# Vérifier si la base de données existe
cursor.execute("SHOW DATABASES LIKE 'diabete_mspr'")
result = cursor.fetchone()

# Si la base de données n'existe pas, la créer à partir du fichier SQL
if not result:
    print("Base de données 'diabete_mspr' non trouvée. Création via le fichier SQL...")

    # Vérifier que le fichier existe
    sql_file_path = "Diabete_MSPR-1740578494.sql"
    if os.path.exists(sql_file_path):
        execute_sql_file(cursor, sql_file_path)
        print(
            f"La base de données et les tables ont été créées à partir du fichier {sql_file_path}."
        )
    else:
        print(f"Le fichier SQL {sql_file_path} est introuvable.")
        cursor.close()
        conn.close()
        exit(1)  # Arrêter l'exécution si le fichier SQL est manquant

# Sélectionner la base de données après sa création
cursor.execute("USE diabete_mspr")

# Charger le fichier CSV
df = pd.read_csv("fichier_sortie_v8.csv", sep=",")

# Remplacer les valeurs "NA" ou "Na" par None pour db
df = df.replace(["NA", "Na"], None)


def safe_float(value):
    """Convertit une valeur en float si possible, sinon renvoie None"""
    try:
        return float(value) if pd.notna(value) and value != "" else None
    except ValueError:
        print(f"Valeur non convertible en float: {value}")
        return None


def safe_int(value):
    """Convertit en int si possible, sinon renvoie None"""
    try:
        return int(value) if pd.notna(value) and value != "" else None
    except ValueError:
        print(f"Valeur non convertible en int: {value}")
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
        safe_float(row.get("glyhb", None)),
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
        safe_float(row.get("chol", None)),
        safe_float(row.get("stab.glu", None)),
        safe_float(row.get("hdl", None)),
        safe_float(row.get("ratio", None)),
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
