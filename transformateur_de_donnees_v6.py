# Ajoute la colonne "Diabete" en fonction de la valeur de "glyhb" (6.5 ou plus = Oui, moins de 6.5 = Non) et "outcome" (1 = Oui, 0 = Non)

import glob
import os
import mysql.connector
import csv
import numpy as np
import pandas as pd

# Configuration de la connexion MySQL
DB_NAME = "diabete_mspr"
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": DB_NAME,
}

# Connexion au serveur MySQL
conn = mysql.connector.connect(
    host=DB_CONFIG["host"], user=DB_CONFIG["user"], password=DB_CONFIG["password"]
)
cursor = conn.cursor()

# Création de la base de données si elle n'existe pas
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
conn.database = DB_NAME

# Supprimer toutes les tables existantes
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()
for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table[0]}")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

# Lire le fichier SQL et exécuter les requêtes
with open("Diabete_MSPR-1740578494.sql", "r") as sql_file:
    sql_script = sql_file.read()
    for statement in sql_script.split(";"):
        if statement.strip():
            cursor.execute(statement)

conn.commit()

# Spécifier le chemin du répertoire contenant les fichiers CSV
INPUT_DIRECTORY = "./DATASETS_ORIGINE/*.csv"  # Remplacer par le chemin du répertoire
OUTPUT_FILE = "fichier_sortie_v8.csv"  # Nom du fichier de sortie

# Inititalisation de la connexion de la base de données


# Utiliser glob pour récupérer tous les fichiers CSV dans le répertoire spécifié
csv_files = glob.glob(INPUT_DIRECTORY)

# Vérifier si des fichiers CSV ont été trouvés
if not csv_files:
    print("Aucun fichier CSV trouvé dans le répertoire spécifié.")
else:
    # Lire et fusionner tous les fichiers CSV
    df_list = []  # Liste pour stocker les DataFrames
    for file in csv_files:
        df = pd.read_csv(file)

        # Normaliser la casse des noms de colonnes
        df.columns = (
            df.columns.str.lower()
        )  # Convertir tous les noms de colonnes en minuscules

        df_list.append(df)  # Ajouter le DataFrame à la liste
        print(f"Données du fichier {file} :")
        print(df.head())  # Afficher les premières lignes de chaque fichier

    # Fusionner tous les DataFrames dans la liste
    df_fusionne = pd.concat(df_list, ignore_index=True)

    # Supprimer les lignes en doublon
    df_fusionne = df_fusionne.drop_duplicates()

    # Remplacer les cases vides par "Na" dans le dataframe fusionné
    df_fusionne = df_fusionne.fillna("Na")

    df_fusionne = df_fusionne[df_fusionne["glyhb"] != "Na"]
    
    # Remplacer les lignes vides de la colonne "gender" par "female"
    if "gender" in df_fusionne.columns:
        df_fusionne["gender"] = df_fusionne["gender"].fillna(
            "female"
        )  # Remplacer NaN par 'female'
        df_fusionne["gender"] = df_fusionne["gender"].replace(
            r"^\s*$", "female", regex=True
        )  # Remplacer les chaînes vides par 'female'
    else:
        print(
            "Avertissement : La colonne 'gender' est manquante dans le DataFrame fusionné."
        )

    # Ajouter la colonne "Diabete"
    if "glyhb" in df_fusionne.columns and "outcome" in df_fusionne.columns:
        df_fusionne["diabete"] = df_fusionne.apply(
            lambda row: (
                "1"
                if (
                    pd.to_numeric(row["glyhb"], errors="coerce") >= 6.5
                    or row["outcome"] == 1
                )
                else (
                    "0"
                    if (
                        pd.to_numeric(row["glyhb"], errors="coerce") < 6.5
                        or row["outcome"] == 0
                    )
                    else "Na"
                )
            ),
            axis=1,
        )
    else:
        print(
            "Avertissement : Les colonnes 'glyhb' ou 'outcome' sont manquantes dans le DataFrame fusionné."
        )
        df_fusionne["diabete"] = "Na"

    # Ajouter la colonne "Pregnant"
    if "pregnancies" in df_fusionne.columns:
        df_fusionne["pregnant"] = df_fusionne["pregnancies"].apply(
            lambda x: (
                "Na"
                if x == "Na"
                else ("1" if pd.to_numeric(x, errors="coerce") > 0 else "0")
            )
        )
    else:
        print(
            "Avertissement : La colonne 'pregnancies' est manquante dans le DataFrame fusionné."
        )
        df_fusionne["pregnant"] = "Na"

    # Remplacer les valeurs 'Na' dans la colonne bloodpressure par la moyenne de bp.1s et bp.1d
if all(col in df_fusionne.columns for col in ["bloodpressure", "bp.1s", "bp.1d"]):
    # Convertir 'bp.1s' et 'bp.1d' en numérique, en remplaçant 'Na' par NaN
    df_fusionne["bp.1s"] = pd.to_numeric(
        df_fusionne["bp.1s"].replace("Na", pd.NA), errors="coerce"
    )
    df_fusionne["bp.1d"] = pd.to_numeric(
        df_fusionne["bp.1d"].replace("Na", pd.NA), errors="coerce"
    )

    # Calculer la pression artérielle moyenne en gérant les NaN et arrondir à 1 chiffre après la virgule
    df_fusionne["moyenne_bp"] = df_fusionne.apply(
        lambda row: (
            round(row["bp.1d"] + (1 / 3 * (row["bp.1s"] - row["bp.1d"])), 1)
            if pd.notna(row["bp.1s"]) and pd.notna(row["bp.1d"])
            else np.nan
        ),
        axis=1,
    )

    # Remplacer les valeurs 'Na' dans la colonne bloodpressure
    df_fusionne.loc[df_fusionne["bloodpressure"] == "Na", "bloodpressure"] = (
        df_fusionne["moyenne_bp"]
    )

    # Arrondir également la colonne bloodpressure à 1 chiffre après la virgule
    df_fusionne["bloodpressure"] = pd.to_numeric(
        df_fusionne["bloodpressure"], errors="coerce"
    ).round(1)

    # Supprimer les colonnes bp.1s, bp.1d, bp.2s, bp.2d et moyenne_bp
    df_fusionne = df_fusionne.drop(
        columns=["bp.1s", "bp.1d", "bp.2s", "bp.2d", "moyenne_bp"]
    )
else:
    print(
        "Avertissement : Une ou plusieurs colonnes nécessaires pour le calcul de la pression artérielle sont manquantes."
    )


# Enregistrer le DataFrame fusionné dans un nouveau fichier CSV
df_fusionne.to_csv(OUTPUT_FILE, index=False)
print(f"Données fusionnées enregistrées dans {OUTPUT_FILE}")

<<<<<<< HEAD
# Charger les données depuis le CSV


def insert_data(table_name, columns, data):
    placeholders = ", ".join(["%s"] * len(columns))
    column_names = ", ".join(columns)
    query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
    cursor.executemany(query, data)
    conn.commit()


# Insérer les données dans Patient_table
if all(
    col in df_fusionne.columns
    for col in [
        "age",
        "gender",
        "height",
        "weight",
        "frame",
        "waist",
        "hip",
        "location",
    ]
):
    patient_data = df_fusionne[
        ["age", "gender", "height", "weight", "frame", "waist", "hip", "location"]
    ].values.tolist()
    insert_data(
        "Patient_table",
        ["age", "gender", "height", "weight", "frame", "waist", "hip", "location"],
        patient_data,
    )

# Insérer les données dans medical_history
if all(
    col in df_fusionne.columns
    for col in [
        "pregnancies",
        "glucose",
        "bloodpressure",
        "skinthickness",
        "insulin",
        "bodymassindex",
        "diabetespedigreefunction",
        "glyhb",
    ]
):
    medical_data = df_fusionne[
        [
            "pregnancies",
            "glucose",
            "bloodpressure",
            "skinthickness",
            "insulin",
            "bodymassindex",
            "diabetespedigreefunction",
            "glyhb",
        ]
    ].values.tolist()
    insert_data(
        "medical_history",
        [
            "pregnancies",
            "glucose",
            "bloodpressure",
            "skinthickness",
            "insulin",
            "bodymassindex",
            "diabetespedigreefunction",
            "glycatedhemoglobine",
        ],
        medical_data,
    )

# Insérer les données dans cholesterol_bp
if all(
    col in df_fusionne.columns
    for col in [
        "cholesterol",
        "stabilizedglucide",
        "hughdensitylipoprotein",
        "ratioglucoseinsuline",
    ]
):
    cholesterol_data = df_fusionne[
        [
            "cholesterol",
            "stabilizedglucide",
            "hughdensitylipoprotein",
            "ratioglucoseinsuline",
        ]
    ].values.tolist()
    insert_data(
        "cholesterol_bp",
        [
            "cholesterol",
            "stabilizedglucide",
            "hughdensitylipoprotein",
            "ratioglucoseinsuline",
        ],
        cholesterol_data,
    )

# Insérer les données dans diabetes_diagnosis
if "diabete" in df_fusionne.columns:
    diagnosis_data = df_fusionne[["diabete"]].values.tolist()
    insert_data("diabetes_diagnosis", ["diabete"], diagnosis_data)

# Fermeture de la connexion
cursor.close()
conn.close()
print("Base de données mise à jour avec succès !")
=======
# Connexion à la base de données
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="MSPR"
)

cursor = db.cursor()

# Lire les en-têtes du CSV
with open(OUTPUT_FILE, 'r') as file:
    csv_reader = csv.reader(file)
    headers = next(csv_reader)

# Fonction pour échapper les noms de colonnes
def escape_column_name(name):
    return f"`{name.replace('`', '``')}`"

# Construire la requête CREATE TABLE avec les noms de colonnes échappés
create_table_query = f"CREATE TABLE IF NOT EXISTS diabete_data ({', '.join([f'{escape_column_name(header)} VARCHAR(255)' for header in headers])})"

# Exécuter la requête pour créer la table
cursor.execute(create_table_query)

# Modifier la requête d'insertion pour utiliser les noms de colonnes échappés
insert_query = f"INSERT INTO diabete_data ({', '.join(escape_column_name(header) for header in headers)}) VALUES ({', '.join(['%s' for _ in headers])})"

# Insérer les données
with open(OUTPUT_FILE, 'r') as file:
    csv_data = csv.reader(file)
    next(csv_data)  # Sauter les en-têtes
    for row in csv_data:
        cursor.execute(insert_query, row)


# Valider les changements
db.commit()

# Fermer la connexion
cursor.close()
db.close()

print("Table créée et données insérées avec succès dans diabete_data.")

>>>>>>> a87bb0d1c13e345451f9d5436efc5562c1543cc7
