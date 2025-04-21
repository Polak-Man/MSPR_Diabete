# Ajoute la colonne "Diabete" en fonction de la valeur de "glyhb" (6.5 ou plus = Oui, moins de 6.5 = Non) et "outcome" (1 = Oui, 0 = Non)

import glob
import os
import mysql.connector
import csv
import numpy as np
import pandas as pd

# Spécifier le chemin du répertoire contenant les fichiers CSV
INPUT_DIRECTORY = "./DATASETS_ORIGINE/*.csv"  # Remplacer par le chemin du répertoire
OUTPUT_FILE = "fichier_sortie_v8.csv"  # Nom du fichier de sortie

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
        # Créer une condition pour les lignes à conserver
        condition = (
            (pd.to_numeric(df_fusionne["glyhb"], errors="coerce") >= 6.5) | 
            (df_fusionne["outcome"] == 1)
        )
    
        # Appliquer la condition pour créer la colonne "diabete"
        df_fusionne["diabete"] = np.where(condition, "1", "0")

        # Si vous souhaitez supprimer les lignes qui ne remplissent pas les critères, conservez cette ligne
        # df_fusionne = df_fusionne[condition]
    else:
        print(
            "Avertissement : Les colonnes 'glyhb' ou 'outcome' sont manquantes dans le DataFrame fusionné."
        )

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

    # Mettre "pregnant" à "0" si "gender" est "male"
    if "gender" in df_fusionne.columns:
        df_fusionne.loc[df_fusionne["gender"] == "male", "pregnant"] = "0"
    else:
        print(
            "Avertissement : La colonne 'gender' est manquante dans le DataFrame fusionné."
        )

# Mettre "gender" à "female" si "gender" est "Na" et "pregnant" est "1"
if "gender" in df_fusionne.columns and "pregnant" in df_fusionne.columns:
    df_fusionne.loc[
        (df_fusionne["gender"] == "Na") & (df_fusionne["pregnant"] == "1"),
        "gender"
    ] = "female"
else:
    print("Avertissement : Les colonnes 'gender' ou 'pregnant' sont manquantes dans le DataFrame fusionné.")

# Mettre "gender" à "female" si "pregnancies" n'est pas "Na"
if "pregnancies" in df_fusionne.columns:
    df_fusionne.loc[df_fusionne["pregnancies"] != "Na", "gender"] = "female"
else:
    print("Avertissement : La colonne 'pregnancies' est manquante dans le DataFrame fusionné.")

# Mettre "gender" à "female" si "gender" est "Na" et "pregnant" est "1"
if "gender" in df_fusionne.columns and "pregnant" in df_fusionne.columns:
    df_fusionne.loc[
        (df_fusionne["gender"] == "Na") & (df_fusionne["pregnant"] == "1"),
        "gender"
    ] = "female"
else:
    print("Avertissement : Les colonnes 'gender' ou 'pregnant' sont manquantes dans le DataFrame fusionné.")

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


    # Liste des colonnes à convertir en numérique
colonnes_a_convertir = [
    "chol",
    "glyhb",
    "hdl",
    "height",
    "hip",
    "id",
    "ratio",
    "stab.glu",
    "waist",
    "weight",
    "time.ppn"
]

# Convertir les colonnes spécifiées en numérique
for col in colonnes_a_convertir:
    if col in df_fusionne.columns:
        df_fusionne[col] = pd.to_numeric(df_fusionne[col].replace("Na", pd.NA), errors='coerce')
    else:
        print(f"Avertissement : La colonne '{col}' est manquante dans le DataFrame fusionné.")

# Enregistrer le DataFrame fusionné dans un nouveau fichier CSV
df_fusionne.to_csv(OUTPUT_FILE, index=False)
print(f"Données fusionnées enregistrées dans {OUTPUT_FILE}")

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