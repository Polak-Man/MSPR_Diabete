import pandas as pd
import glob
import os

# Spécifiez le chemin du répertoire contenant les fichiers CSV
# Par exemple, si vos fichiers sont dans un dossier nommé 'data', utilisez 'data/*.csv'
input_directory = (
    "./DATASETS_ORIGINE/*.csv"  # Remplacez par le chemin de votre répertoire
)
output_file = "fichier_sortie.csv"  # Nom du fichier de sortie

# Utiliser glob pour récupérer tous les fichiers CSV dans le répertoire spécifié
csv_files = glob.glob(input_directory)

# Vérifier si des fichiers CSV ont été trouvés
if not csv_files:
    print("Aucun fichier CSV trouvé dans le répertoire spécifié.")
else:
    # Lire et fusionner tous les fichiers CSV
    df_list = []  # Liste pour stocker les DataFrames
    for file in csv_files:
        df = pd.read_csv(file)
        df_list.append(df)  # Ajouter le DataFrame à la liste
        print(f"Données du fichier {file} :")
        print(df.head())  # Afficher les premières lignes de chaque fichier

    # Fusionner tous les DataFrames dans la liste
    df_fusionne = pd.concat(df_list, ignore_index=True)

    # Afficher les premières lignes du DataFrame fusionné
    print("Données fusionnées :")
    print(df_fusionne.head())

    # Enregistrer le DataFrame fusionné dans un nouveau fichier CSV
    df_fusionne.to_csv(output_file, index=False)

    print(f"Données fusionnées enregistrées dans {output_file}")
