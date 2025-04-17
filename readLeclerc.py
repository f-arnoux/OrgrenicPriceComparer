import re
import json


def extract_json_block(content, start_index):
    """
    Fonction pour extraire un bloc JSON complet en analysant rigoureusement les crochets ouvrants et fermants.
    Elle s'assure qu'on prend bien tout un bloc JSON sans manquer de fermeture ou ouvrir des crochets incorrectement.
    """
    depth = 0  # Nombre de crochets ou accolades ouverts
    json_block = ""
    for i in range(start_index, len(content)):
        char = content[i]

        if char == '[':
            # Un crochet ou une accolade ouvrant, on l'ajoute et on augmente la profondeur
            depth += 1
            if depth > 0:
                json_block += char
        elif char == ']':
            # Un crochet ou une accolade fermant, on diminue la profondeur
            depth -= 1
            if depth > 0:
                json_block += char
            elif depth == 0:
                # Le bloc JSON est terminé ici
                json_block += char
                break
        else:
            # Ajouter tous les autres caractères au bloc JSON
            if depth > 0:
                json_block += char

    # Vérification que la profondeur est revenue à zéro, sinon le bloc n'est pas complet
    if depth != 0:
        raise ValueError("Erreur : La structure JSON est incomplète ou mal formée.")

    return json_block


# Fonction pour extraire les données recherchées
def extract_targeted_data(file_path):
    # Lire le contenu du fichier
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Rechercher toutes les occurrences de Utilitaires.widget.initOptions
    script_pattern = re.compile(r"Utilitaires\.widget\.initOptions\('([^']+)',\s*(\{.*?)(?=\);|\Z)", re.DOTALL)
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

    start_index = 0
    # Recherche d'un bloc contenant l'identifiant cible
    while True:
        # Recherche de l'identifiant dans le contenu
        start_index = target_json.find("lstElements", start_index)
        if start_index < 0:
            break  # Si plus de correspondances, on arrête

        # Extraire la portion de contenu après l'identifiant
        end_index = target_json.find("objStickers", start_index)

        if start_index < 0 or end_index < 0:
            raise ValueError("Erreur : Structure incorrecte du script.")

        # Extraire le JSON brut contenu dans cette portion
        json_data_raw = target_json[start_index:end_index].strip()

        try:
            # Extraire le bloc JSON complet en vérifiant les ouvertures/fermetures
            target_json = extract_json_block(json_data_raw, 0)
            break  # On s'arrête dès qu'on a trouvé un bloc valide
        except ValueError:
            start_index = end_index + 2  # Si on échoue, on passe à la prochaine occurrence

    if not target_json:
        return f"Aucun bloc JSON trouvé avec l'identifiant cible '{target_identifier}'."

    try:
        # Charger le JSON validé
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
                                         obj_element.get("sPrixParUniteDeMesure").replace(',', '.')) if obj_element.get("sPrixParUniteDeMesure") else None,
                    "url": obj_element.get("sUrlPageProduit")
                })
            # Vérifier les enfants et continuer à explorer
            lst_enfants = element.get("lstEnfants", [])
            if lst_enfants:
                parse_elements(lst_enfants)

    # Lancer l'exploration des éléments
    for category in json_data:
        parse_elements(category["lstEnfants"])

    # Afficher les produits extraits
    for product in products:
        print(product)

    return products

def get_product_list(file_path):
    data = extract_targeted_data(file_path)
    # Appel de la fonction pour extraire les produits
    products_list = extract_products(data)
    return products_list

get_product_list("C:\\Users\\Lenovo\\Documents\\OrgrenicPriceComparer\\Listes\\detail-liste-42056440.aspx")

