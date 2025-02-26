import glob
import pandas as pd
import mysql.connector

# Dossiers et fichiers
INPUT_DIRECTORY = "./DATASETS_ORIGINE/*.csv"  # Adapter selon ton dossier
OUTPUT_DIRECTORY = "./DATASETS_CLEANED/"  # Dossier de sortie des fichiers finaux

# Connexion MySQL
DB_CONFIG = {
    "host": "localhost",
    "user": "root",  # Modifier selon ton utilisateur MySQL
    "password": "",  # Modifier selon ton mot de passe MySQL
    "database": "diabete_MSPR",
}


def load_csv_files():
    csv_files = glob.glob(INPUT_DIRECTORY)
    if not csv_files:
        print("Aucun fichier CSV trouvé.")
        return []
    return [pd.read_csv(file) for file in csv_files]


def clean_and_transform_data(df_list):
    for df in df_list:
        df.columns = df.columns.str.lower().str.strip()
    df_combined = pd.concat(df_list, ignore_index=True)
    df_combined = df_combined.drop_duplicates()
    df_combined["gender"] = df_combined.get("gender", pd.Series()).fillna("female")
    df_combined["diabete"] = df_combined.get("glyhb", pd.Series()).apply(
        lambda x: "Oui" if pd.notna(x) and x >= 6.5 else "Non"
    )
    return df_combined


def split_into_tables(df):
    patient_cols = [
        "age",
        "gender",
        "height",
        "weight",
        "frame",
        "waist",
        "hip",
        "location",
    ]
    medical_cols = [
        "pregnancies",
        "glucose",
        "bloodpressure",
        "skinthickness",
        "insulin",
        "bmi",
        "diabetespedigreefunction",
        "glyhb",
    ]
    cholesterol_cols = [
        "chol",
        "stab.glu",
        "hdl",
        "ratio",
        "bp.1s",
        "bp.1d",
        "bp.2s",
        "bp.2d",
    ]
    diabetes_cols = ["outcome", "diabete"]

    df_patient = df[patient_cols].dropna().reset_index(drop=True)
    df_patient.insert(0, "id", range(1, len(df_patient) + 1))

    df_medical = df[medical_cols].dropna().reset_index(drop=True)
    df_medical.insert(0, "id", df_patient["id"])

    df_cholesterol = df[cholesterol_cols].dropna().reset_index(drop=True)
    df_cholesterol.insert(0, "id", df_patient["id"])

    df_diabetes = df[diabetes_cols].dropna().reset_index(drop=True)
    df_diabetes.insert(0, "id", df_patient["id"])

    return df_patient, df_medical, df_cholesterol, df_diabetes


def save_to_mysql(df_patient, df_medical, df_cholesterol, df_diabetes):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Remplacement des NaN par des valeurs par défaut adaptées
    df_diabetes = df_diabetes.fillna({"outcome": 0, "diabete": "Inconnu"})

    for _, row in df_diabetes.iterrows():
        # Vérifier si la ligne contient encore des NaN (au cas où)
        if row.isnull().values.any():
            print(f"Attention: Valeur NaN détectée dans la ligne {row.to_dict()}")
            continue  # Passer cette ligne pour éviter l'erreur

        # Forcer les types pour éviter tout problème avec MySQL
        id_value = int(row["id"]) if pd.notna(row["id"]) else None
        outcome_value = int(row["outcome"]) if pd.notna(row["outcome"]) else 0
        diabete_value = str(row["diabete"]) if pd.notna(row["diabete"]) else "Inconnu"

        cursor.execute(
            """
            INSERT INTO diabetes_diagnosis (id, outcome, diabete)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE outcome=COALESCE(VALUES(outcome), outcome), diabete=COALESCE(VALUES(diabete), diabete)
            """,
            (id_value, outcome_value, diabete_value),
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("Données envoyées à MySQL avec succès !")


def main():
    df_list = load_csv_files()
    if not df_list:
        return
    df_cleaned = clean_and_transform_data(df_list)
    df_patient, df_medical, df_cholesterol, df_diabetes = split_into_tables(df_cleaned)
    save_to_mysql(df_patient, df_medical, df_cholesterol, df_diabetes)


if __name__ == "__main__":
    main()
