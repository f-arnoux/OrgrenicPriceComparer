import json
import os
from pathlib import Path

# Définir le répertoire contenant les fichiers JSON
directory = 'C:\\Users\\Lenovo\\Documents\\OrgrenicPriceComparer\\Listes'  # Remplacez par le chemin de votre répertoire si nécessaire

# Trouver les deux fichiers JSON les plus récents
def get_two_most_recent_files(directory):
    json_files = [file for file in Path(directory).glob("*.json")]
    json_files.sort(key=os.path.getmtime, reverse=True)
    return json_files[:2]

# Charger les deux fichiers JSON les plus récents
most_recent_files = get_two_most_recent_files(directory)

if len(most_recent_files) < 2:
    print("Il n'y a pas suffisamment de fichiers JSON dans le répertoire.")
else:
    try:
        with open(most_recent_files[0], 'r', encoding='utf-8') as file1, open(most_recent_files[1], 'r', encoding='utf-8') as file2:
            data1 = json.load(file1)
            data2 = json.load(file2)
    except UnicodeDecodeError as e:
        print(f"Erreur lors de la lecture des fichiers : {e}")
        exit(1)

    # Extraire les titres et barcodes des produits sous forme de dictionnaire
    products_old = {hit["handle"]: hit.get("barcode", "N/A") for hit in data1["results"][0]["hits"]}
    products_new = {hit["handle"]: hit.get("barcode", "N/A") for hit in data2["results"][0]["hits"]}

    # Identifier les produits ajoutés et supprimés
    added_products = {handle: barcode for handle, barcode in products_new.items() if handle not in products_old}
    removed_products = {handle: barcode for handle, barcode in products_old.items() if handle not in products_new}

    # Afficher les résultats
    print("Produits supprimés:")
    for handle, barcode in added_products.items():
        print(f" - {handle} (Barcode: {barcode})")

    print("\nProduits ajoutés:")
    for handle, barcode in removed_products.items():
        print(f" - {handle} (Barcode: {barcode})")