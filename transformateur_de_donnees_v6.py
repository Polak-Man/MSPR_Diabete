# Ajoute la colonne "Diabete" en fonction de la valeur de "glyhb" (6.5 ou plus = Oui, moins de 6.5 = Non) et "outcome" (1 = Oui, 0 = Non)

import glob
import os
import pandas as pd

# Spécifier le chemin du répertoire contenant les fichiers CSV
INPUT_DIRECTORY = './DATASETS_ORIGINE/*.csv'  # Remplacer par le chemin du répertoire
OUTPUT_FILE = 'fichier_sortie_v7.csv'  # Nom du fichier de sortie

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
        df.columns = df.columns.str.lower()  # Convertir tous les noms de colonnes en minuscules
        
        df_list.append(df)  # Ajouter le DataFrame à la liste
        print(f"Données du fichier {file} :")
        print(df.head())  # Afficher les premières lignes de chaque fichier

    # Fusionner tous les DataFrames dans la liste
    df_fusionne = pd.concat(df_list, ignore_index=True)

    # Supprimer les lignes en doublon
    df_fusionne = df_fusionne.drop_duplicates()

    # Remplacer les cases vides par "Na" dans le dataframe fusionné
    df_fusionne = df_fusionne.fillna('Na')

# Remplacer les lignes vides de la colonne "gender" par "female"
if 'gender' in df_fusionne.columns:
        df_fusionne['gender'] = df_fusionne['gender'].fillna('female')  # Remplacer NaN par 'female'
        df_fusionne['gender'] = df_fusionne['gender'].replace(r'^\s*$', 'female', regex=True)  # Remplacer les chaînes vides par 'female'
else:
    print("Avertissement : La colonne 'gender' est manquante dans le DataFrame fusionné.")



    # Ajouter la colonne "Diabete"

if 'glyhb' in df_fusionne.columns and 'outcome' in df_fusionne.columns:
    df_fusionne['diabete'] = df_fusionne.apply(
        lambda row: '1' if (pd.to_numeric(row['glyhb'], errors='coerce') >= 6.5 or row['outcome'] == 1)
        else ('0' if (pd.to_numeric(row['glyhb'], errors='coerce') < 6.5 or row['outcome'] == 0)
        else 'Na'), axis=1
    )
else:
    print("Avertissement : Les colonnes 'glyhb' ou 'outcome' sont manquantes dans le DataFrame fusionné.")
    df_fusionne['diabete'] = 'Na'



    # Ajouter la colonne "Pregnant"

if 'pregnancies' in df_fusionne.columns:
    df_fusionne['pregnant'] = df_fusionne['pregnancies'].apply(
        lambda x: 'Na' if x == 'Na' else ('Yes' if pd.to_numeric(x, errors='coerce') > 0 else 'No')
    )
else:
    print("Avertissement : La colonne 'pregnancies' est manquante dans le DataFrame fusionné.")
    df_fusionne['pregnant'] = 'Na'



    # Remplacer les valeurs 'Na' dans la colonne bloodpressure par la moyenne de bp.1s et bp.1d

if all(col in df_fusionne.columns for col in ['bloodpressure', 'bp.1s', 'bp.1d']):
    # Convertir 'bp.1s' et 'bp.1d' en numérique, en remplaçant 'Na' par NaN
    df_fusionne['bp.1s'] = pd.to_numeric(df_fusionne['bp.1s'].replace('Na', pd.NA), errors='coerce')
    df_fusionne['bp.1d'] = pd.to_numeric(df_fusionne['bp.1d'].replace('Na', pd.NA), errors='coerce')
        
    # Calculer la moyenne des colonnes bp.1s et bp.1d, en ignorant les valeurs NaN
    moyenne_bp = df_fusionne[['bp.1s', 'bp.1d']].mean(axis=1, skipna=True)
        
    # Remplacer les valeurs 'Na' dans la colonne bloodpressure
    df_fusionne.loc[df_fusionne['bloodpressure'] == 'Na', 'bloodpressure'] = moyenne_bp

    # Supprimer les colonnes bp.1s et bp.1d et bp.2s et bp.2d
    df_fusionne = df_fusionne.drop(columns=['bp.2s', 'bp.2d'])
else:
    print("Avertissement : Une ou plusieurs colonnes nécessaires pour le calcul de la pression artérielle sont manquantes.")


# Enregistrer le DataFrame fusionné dans un nouveau fichier CSV
df_fusionne.to_csv(OUTPUT_FILE, index=False)
print(f"Données fusionnées enregistrées dans {OUTPUT_FILE}")
