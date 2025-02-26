# Ajoute la colonne "Diabete" en fonction de la valeur de "glyhb" (6.5 ou plus = Oui, moins de 6.5 = Non)
# Ajoute également la colonne "Pays" en fonction de la valeur de "location"

import glob
import os
import pandas as pd

# Spécifier le chemin du répertoire contenant les fichiers CSV
INPUT_DIRECTORY = './DATASETS_ORIGINE/*.csv'  # Remplacer par le chemin du répertoire
OUTPUT_FILE = 'fichier_sortie_v5.csv'  # Nom du fichier de sortie

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

    # Afficher les premières lignes du DataFrame fusionné
    print("Données fusionnées :")
    print(df_fusionne.head())

    # Remplacer les lignes vides de la colonne "gender" par "female"
    if 'gender' in df_fusionne.columns:
        df_fusionne['gender'] = df_fusionne['gender'].fillna('female')  # Remplacer NaN par 'female'
        df_fusionne['gender'] = df_fusionne['gender'].replace(r'^\s*$', 'female', regex=True)  # Remplacer les chaînes vides par 'female'
    else:
        print("Avertissement : La colonne 'gender' est manquante dans le DataFrame fusionné.")
        
    # Remplacer les cases vides par "Na" dans le dataframe fusionné
    df_fusionne = df_fusionne.fillna('Na')

    # Ajouter la colonne "Diabete"
    if 'glyhb' in df_fusionne.columns:
        df_fusionne['diabete'] = df_fusionne['glyhb'].apply(
            lambda x: 'Oui' if pd.to_numeric(x, errors='coerce') >= 6.5 
            else ('Non' if pd.notna(pd.to_numeric(x, errors='coerce')) else 'Na')
        )
    else:
        print("Avertissement : La colonne 'glyhb' est manquante dans le DataFrame fusionné.")
        df_fusionne['diabete'] = 'Na'

    # Ajouter la colonne "Pregnant"
    if 'pregnancies' in df_fusionne.columns:
        df_fusionne['pregnant'] = df_fusionne['pregnancies'].apply(
            lambda x: 'Na' if x == 'Na' else ('Yes' if pd.to_numeric(x, errors='coerce') > 0 else 'No')
    )
    else:
        print("Avertissement : La colonne 'pregnancies' est manquante dans le DataFrame fusionné.")
        df_fusionne['pregnant'] = 'Na'


    # Afficher les premières lignes du DataFrame avec les nouvelles colonnes
    print("Données avec les colonnes 'Diabete' et 'Pays' ajoutées :")
    print(df_fusionne.head())

# Enregistrer le DataFrame fusionné dans un nouveau fichier CSV
df_fusionne.to_csv(OUTPUT_FILE, index=False)
print(f"Données fusionnées enregistrées dans {OUTPUT_FILE}")
