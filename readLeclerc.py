import re
import json



# Fonction pour extraire les données recherchées
def extract_targeted_data(file_path):
    # Lire le contenu du fichier
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Rechercher toutes les occurrences de Utilitaires.widget.initOptions
    script_pattern = re.compile(r"Utilitaires\.widget\.initOptions\('([^']+)',(\{.*?\})\);", re.DOTALL)
    script_matches = script_pattern.findall(content)

    if not script_matches:
        return "Aucun JSON trouvé dans les balises script."

    print(f"Nombre de blocs initOptions trouvés : {len(script_matches)}\n")

    # Parcourir et afficher les blocs pour vérifier leur contenu
    target_identifier = "ctl00_ctl00_mainMutiUnivers_main_ctl05_pnlElementProduitDetailListe"
    target_json = None

    for idx, (identifier, json_data) in enumerate(script_matches):
        print(f"Bloc {idx + 1} - Identifiant : {identifier}")

        # Vérifier si cet identifiant correspond à celui recherché
        if identifier == target_identifier:
            target_json = json_data
            print(f"-> Bloc JSON trouvé avec l'identifiant cible : {identifier}\n")
            break
        else:
            print(f"-> Ignoré (Identifiant non correspondant : {identifier})\n")

    if not target_json:
        return f"Aucun bloc JSON contenant l'identifiant cible '{target_identifier}' trouvé."

    # Charger le JSON correspondant
    try:
        parsed_json = json.loads(target_json)
    except json.JSONDecodeError as e:
        return f"Erreur lors du chargement du JSON : {e}"

    return parsed_json

def extract_products(json_data):
    products = []

    def parse_elements(elements):
        for element in elements:
            obj_element = element.get("objElement", {})
            if obj_element.get("sType") == "Produit":
                products.append({
                    "id": obj_element.get("iIdProduit"),
                    "name": obj_element.get("sLibelleLigne1"),
                    "price": obj_element.get("sPrixUnitaire"),
                    "unitPrice" : re.sub(r'[^\d.,]', '',
                                         obj_element.get("sPrixParUniteDeMesure").replace(',', '.')),
                    "url": obj_element.get("sUrlPageProduit")
                })
            # Vérifier les enfants et continuer à explorer
            lst_enfants = element.get("lstEnfants", [])
            if lst_enfants:
                parse_elements(lst_enfants)

    # Lancer l'exploration des éléments
    if "objContenu" in json_data:
        lst_elements = json_data["objContenu"].get("lstElements", [])
        parse_elements(lst_elements)

    # Afficher les produits extraits
    for product in products:
        print(product)

    return products

def get_product_list(file_path):
    data = extract_targeted_data(file_path)
    # Appel de la fonction pour extraire les produits
    products_list = extract_products(data)
    return products_list

#get_product_list("C:\\Users\\Lenovo\\Downloads\\detail-liste-42056440.aspx")

