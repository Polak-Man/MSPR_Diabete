#Ajoute la colonne "Diabete" en focntion de la valeur de "glyhb" (6.5 ou plus = Oui, moins de 6.5 = Non)

import glob
import os
import pandas as pd

# Spécifier le chemin du répertoire contenant les fichiers CSV
INPUT_DIRECTORY = './DATASETS_ORIGINE/*.csv'  # Remplacer par le chemin du répertoire
OUTPUT_FILE = 'fichier_sortie_v2.csv'  # Nom du fichier de sortie

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

    # Afficher les premières lignes du DataFrame fusionné
    print("Données fusionnées :")
    print(df_fusionne.head())

    # Ajouter la colonne "Diabete"
    df_fusionne['diabete'] = df_fusionne['glyhb'].apply(lambda x: 'Oui' if x >= 6.5 else 'Non')

    # Afficher les premières lignes du DataFrame avec la nouvelle colonne
    print("Données avec la colonne 'Diabete' ajoutée :")
    print(df_fusionne.head())

    # Enregistrer le DataFrame fusionné dans un nouveau fichier CSV
    df_fusionne.to_csv(OUTPUT_FILE, index=False)

    print(f"Données fusionnées enregistrées dans {OUTPUT_FILE}")