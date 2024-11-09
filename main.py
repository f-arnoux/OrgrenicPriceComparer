import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.styles.differential import DifferentialStyle
from openpyxl.formatting.rule import Rule
import csv
import os
from tqdm import tqdm
from datetime import datetime
from ProductComparer import ProductComparer

metabase_elefan_start = 'https://metabase.lelefan.org/public/dashboard/53c41f3f-5644-466e-935e-897e7725f6bc?rayon=&d%25C3%25A9signation='
metabase_elefan_end = '&fournisseur=&date_d%25C3%25A9but=&date_fin='

def extract_price_from_hyperlink(cell_value):
    # Extraire le prix de l'hyperlien
    price = None
    if isinstance(cell_value, str) and cell_value.startswith('=HYPERLINK("'):
        end_pos = cell_value.rfind('"')  # Trouver la position du dernier guillemet dans la formule
        start_pos = cell_value.rfind('"', 0, end_pos - 1) + 1  # Trouver la position du guillemet précédent
        price = float(cell_value[start_pos:end_pos])
    return price

def search_product_line(reference_sheet, product_name):
    # Recherche du nom de produit dans la première colonne de la feuille de référence
    row_index = None
    reference_column = reference_sheet['A']  # Première colonne de la feuille de référence

    for cell in reference_column:
        if cell.value == product_name:
            # Correspondance trouvée, obtenir le prix de référence
            row_index = cell.row
            break  # Sortir de la boucle dès que la correspondance est trouvée
    return row_index

def set_row_fill(row_index, color_fill):
    # Recherche du nom de produit dans la première colonne de la feuille de référence
    col_index = 1
    while col_index < 12:
        cell = mois_annee_sheet.cell(row=row_index, column=col_index)
        cell.fill = color_fill
        col_index += 1


# Liste des produits à partir du fichier CSV
products_info = []
with open(os.getcwd() + '\\liste produits.csv', 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=';')
    for row in csv_reader:
        products_info.append({
            'Catégorie principale': row['Catégorie principale'],
            'Catégorie': row['Catégorie'],
            'Sous Catégories': row['Sous Catégories'],
            'name': row['Produit'],
            'lafourche_site': row['Site La Fourche'],
            'lafourche_qtt': row['Quantité La Fourche'],
            'biocoop_champollion_site': row['Site Biocoop Champollion'],
            'biocoop_champollion_qtt': row['Quantité Biocoop Champollion'],
            'biocoop_fontaine_site': row['Site Biocoop Fontaine'],
            'biocoop_fontaine_qtt': row['Quantité Biocoop Fontaine'],
            'satoriz_site': row['Site Satoriz'],
            'satoriz_qtt': row['Quantité Satoriz'],
            'greenweez_site': row['Site GreenWeez'],
            'greenweez_qtt': row['Quantité GreenWeez'],
            'elefan_code': row['Code Elefan'],
            'elefan_qtt': row['Quantité Elefan'],
            'proportion': float(row['Proportion']) if row['Proportion'] else 0
        })

# Trier les produits selon les trois niveaux de catégories
sorted_products_info = sorted(products_info, key=lambda x: (x['Catégorie principale'], x['Catégorie'], x['Sous Catégories']))

# Obtenir le nom du mois et de l'année actuelle
current_date = datetime.now()
month_year = current_date.strftime('%B %Y')

# Charger la feuille "Reference 2023" pour obtenir les prix de référence
reference_workbook = openpyxl.load_workbook(os.getcwd() + '\\comparaison_prix.xlsx')
reference_sheet = reference_workbook['Reference 2024']

# Ajouter une nouvelle feuille "Mois année" si elle n'existe pas
if month_year not in reference_workbook.sheetnames:
    reference_workbook.create_sheet(month_year)

mois_annee_sheet = reference_workbook[month_year]

# Entêtes du tableau
mois_annee_sheet.cell(row=1, column=1).value = 'Produit'
mois_annee_sheet.cell(row=1, column=2).value = 'La Fourche'
mois_annee_sheet.cell(row=1, column=3).value = 'Évolution La Fourche'
mois_annee_sheet.cell(row=1, column=4).value = 'Biocoop Champollion'
mois_annee_sheet.cell(row=1, column=5).value = 'Évolution Biocoop Champollion'
mois_annee_sheet.cell(row=1, column=6).value = 'Biocoop Fontaine'
mois_annee_sheet.cell(row=1, column=7).value = 'Évolution Biocoop Fontaine'
mois_annee_sheet.cell(row=1, column=8).value = 'Satoriz'
mois_annee_sheet.cell(row=1, column=9).value = 'Évolution Satoriz'
mois_annee_sheet.cell(row=1, column=10).value = 'GreenWeez'
mois_annee_sheet.cell(row=1, column=11).value = 'Évolution GreenWeez'
mois_annee_sheet.cell(row=1, column=12).value = 'Elefan'
mois_annee_sheet.cell(row=1, column=13).value = 'Évolution Elefan'


# Variables pour le formatage
category_main_style = Font(bold=True, size=14)
category_sub_style = Font(bold=True)
separator_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
category_main_fill = PatternFill(start_color="B7C9E2", end_color="B7C9E2", fill_type="solid")  # Couleur de fond pour les catégories principales
category_sub_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")  # Couleur de fond pour les sous-catégories

# Initialisation des totaux par site
total_lafourche = 0
total_biocoop_champollion = 0
total_biocoop_fontaine = 0
total_satoriz = 0
total_greenweez = 0
total_elefan = 0

# Obtenir les prix pour chaque produit
current_category_main = None
current_category_sub = None
current_row = 2  # Variable pour garder le numéro de ligne actuel
product_list = []
with tqdm(sorted_products_info, desc="Traitement des produits", dynamic_ncols=True) as pbar:
    for product_info in pbar:
        product_name = product_info['name']
        pbar.set_description(f"Traitement - {product_name}")
        # Vérifier si la catégorie principale a changé
        if current_category_main != product_info['Catégorie principale']:
            current_row += 1
            current_category_main = product_info['Catégorie principale']
            # Écrire le nom de la catégorie principale avec un style différent
            main_category_cell = mois_annee_sheet.cell(row=current_row, column=1)
            main_category_cell.value = current_category_main
            main_category_cell.font = category_main_style
            set_row_fill(current_row, category_main_fill)
            current_row += 1

        # Vérifier si la catégorie a changé
        if current_category_sub != product_info['Catégorie']:
            current_category_sub = product_info['Catégorie']
            # Écrire le nom de la catégorie avec un style différent
            sub_category_cell = mois_annee_sheet.cell(row=current_row, column=1)
            sub_category_cell.value = current_category_sub
            sub_category_cell.font = category_sub_style
            set_row_fill(current_row, category_sub_fill)
            # sheet.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=4)
            current_row += 1

        # Écrire le nom du produit
        mois_annee_sheet.cell(row=current_row, column=1).value = product_info['name']
        current_row += 1

        # Obtenir les prix pour chaque produit
        product = ProductComparer(
            product_name=product_info['name'],
            product_list = product_list,
            lafourche_site=product_info['lafourche_site'],
            lafourche_qtt=product_info['lafourche_qtt'],
            biocoop_champollion_site=product_info['biocoop_champollion_site'],
            biocoop_champollion_qtt=product_info['biocoop_champollion_qtt'],
            biocoop_fontaine_site=product_info['biocoop_fontaine_site'],
            biocoop_fontaine_qtt=product_info['biocoop_fontaine_qtt'],
            satoriz_site=product_info['satoriz_site'],
            satoriz_qtt=product_info['satoriz_qtt'],
            greenweez_site=product_info['greenweez_site'],
            greenweez_qtt=product_info['greenweez_qtt'],
            elefan_code=product_info['elefan_code'],
            elefan_qtt=product_info['elefan_qtt']
        )
        prices = product.get_prices()
        product_list.append(product)
        total_lafourche += prices[0] * product_info['proportion']
        total_biocoop_champollion += prices[1] * product_info['proportion']
        total_biocoop_fontaine += prices[2] * product_info['proportion']
        total_satoriz += prices[3] * product_info['proportion']
        total_greenweez += prices[4] * product_info['proportion']
        total_elefan += prices[5] * product_info['proportion']
        if product_info['proportion'] != 0:
            mois_annee_sheet.cell(row=current_row - 1, column=14).value = product_info['proportion']
        min_price = min(prices)  # Prix minimum dans la liste des prix

        # Écrire les prix pour chaque site
        for col, price in enumerate(prices, start=1):  # Commencer à partir de la première colonne (colonne 1)
            price_cell = mois_annee_sheet.cell(row=current_row - 1, column=2*col)
            price_cell.value = price

            site_url = None
            if col == 1:  # La Fourche
                site_url = product_info['lafourche_site']
            elif col == 2:  # Biocoop champollion
                site_url = product_info['biocoop_champollion_site'].replace(ProductComparer.biocoop_base_url, ProductComparer.biocoop_champollion_base_url)
            elif col == 3:  # Biocoop fontaine
                site_url = product_info['biocoop_fontaine_site'].replace(ProductComparer.biocoop_base_url, ProductComparer.biocoop_fontaine_base_url)
            elif col == 4:  # Satoriz
                site_url = product_info['satoriz_site']
            elif col == 5:  # Greenweez
                site_url = product_info['greenweez_site']
            elif col == 6:  # Greenweez
                metabase_elefan_start + product_info['elefan_code'] + metabase_elefan_end

            if site_url:
                hyperlink = f'=HYPERLINK("{site_url}","{price}")'
                price_cell.value = hyperlink
                price_cell.font = Font(underline="single", color="0563C1")

            if price == min_price:
                price_cell.fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
            else:
                price_cell.fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

            # Calcul de l'évolution par rapport à la feuille de référence
            reference_price = None
            new_price = 888888
            reference_column = None
            row_index = search_product_line(reference_sheet=reference_sheet, product_name=product_info['name'])
            if row_index is not None:
                if col == 1:  # Prix La Fourche
                    reference_price = extract_price_from_hyperlink(
                        reference_sheet.cell(row=row_index, column=2).value)
                    reference_column = 3  # Colonne pour l'évolution La Fourche
                elif col == 2:  # Prix Biocoop Champollion
                    reference_price = extract_price_from_hyperlink(
                        reference_sheet.cell(row=row_index, column=4).value)
                    reference_column = 5  # Colonne pour l'évolution Biocoop Champollion
                elif col == 3:  # Prix Biocoop Fontaine
                    reference_price = extract_price_from_hyperlink(
                        reference_sheet.cell(row=row_index, column=6).value)
                    reference_column = 7  # Colonne pour l'évolution Biocoop Fontaine
                elif col == 4:  # Prix Satoriz
                    reference_price = extract_price_from_hyperlink(
                        reference_sheet.cell(row=row_index, column=8).value)
                    reference_column = 9  # Colonne pour l'évolution Satoriz
                elif col == 5:  # Prix GreenWeez
                    reference_price = extract_price_from_hyperlink(
                        reference_sheet.cell(row=row_index, column=10).value)
                    reference_column = 11  # Colonne pour l'évolution GreenWeez
                    if price == 888888:
                        all_sheet = reference_workbook.sheetnames
                        index = 2
                        while (index < len(all_sheet) - 1 and new_price == 888888):
                            previous_sheet = all_sheet[len(all_sheet)-index]
                            row_index = search_product_line(reference_sheet=previous_sheet,
                                                            product_name=product_info['name'])
                            new_price = extract_price_from_hyperlink(
                            previous_sheet.cell(row=row_index, column=10).value)
                            index = index + 1

            if reference_price is not None:
                price_change = ((price - reference_price) / reference_price) * 100
                evolution_cell = mois_annee_sheet.cell(row=current_row - 1, column=reference_column)
                evolution_cell.value = f"{price_change:.2f}%"

                if reference_price == 888888:
                    evolution_cell.fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF",
                                                      fill_type="solid")  # Couleur de fond blanc
                elif price == 888888:
                    evolution_cell.value = "-"
                    evolution_cell.fill = PatternFill(start_color="5E6D6D", end_color="5E6D6D",
                                                      fill_type="solid")  # Couleur de fond grise
                    if new_price != 888888:
                        price_cell.value = new_price

                elif price_change < 0:
                    evolution_cell.fill = PatternFill(start_color="B7E1CD", end_color="B7E1CD",
                                                      fill_type="solid")  # Couleur de fond bleue pastel
                elif price_change > 0:
                    evolution_cell.fill = PatternFill(start_color="F4CCCC", end_color="F4CCCC",
                                                      fill_type="solid")  # Couleur de fond rouge pastel

current_row += 1
# Afficher les résultats à la fin du tableau
mois_annee_sheet.cell(row=current_row + 1, column=1).value = 'Prix du Panier'
mois_annee_sheet.cell(row=current_row + 1, column=2).value = '=SUMPRODUCT($N5:$N' + str(current_row) + '*B5:B' + str(current_row) + ')'
mois_annee_sheet.cell(row=current_row + 1, column=4).value = '=SUMPRODUCT($N5:$N' + str(current_row) + '*D5:D' + str(current_row) + ')'
mois_annee_sheet.cell(row=current_row + 1, column=6).value = '=SUMPRODUCT($N5:$N' + str(current_row) + '*F5:F' + str(current_row) + ')'
mois_annee_sheet.cell(row=current_row + 1, column=8).value = '=SUMPRODUCT($N5:$N' + str(current_row) + '*H5:H' + str(current_row) + ')'
mois_annee_sheet.cell(row=current_row + 1, column=10).value = '=SUMPRODUCT($N5:$N' + str(current_row) + '*J5:J' + str(current_row) + ')'


# Sauvegarder le classeur Excel
reference_workbook.save('C:\\Users\\Lenovo\\Documents\\comparaison_prix.xlsx')

# Ouvrir le fichier Excel après sa génération
os.startfile('C:\\Users\\Lenovo\\Documents\\comparaison_prix.xlsx')