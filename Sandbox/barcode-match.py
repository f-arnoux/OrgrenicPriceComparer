import json

# Liste de votre JSON initial
liste_initiale = [
  {"produit": "ROUGE A LEVRE COULEURS DIVERSES", "code": "3135213513515"},
  {"produit": "ROUGE A LEVRE FRAMBOISE", "code": "3662217006915"},
  {"produit": "BAUME A LEVRE", "code": "3662217003891"},
  {"produit": "LAIT CORPOREL", "code": "3662217001774"},
  {"produit": "DISSOLVANT DOUX", "code": "3662217002238"},
  {"produit": "LOTION MICELLAIRE", "code": "3662217002283"},
  {"produit": "RECHARGE LOTION MICELLAIRE", "code": "3662217017881"},
  {"produit": "BAUME APRES RASAGE", "code": "3662217006847"},
  {"produit": "GEL INTIME", "code": "3662217006472"},
  {"produit": "GEL NETTOYANT VISAGE HOMME", "code": "3662217007110"},
  {"produit": "GEL NETTOYANT VISAGE", "code": "3662217006250"},
  {"produit": "SERUM VISAGE LISSANT", "code": "3662217006137"},
  {"produit": "MASQUE VISAGE PURIFIANT", "code": "3662217006182"},
  {"produit": "MASQUE VISAGE ENERGISANT", "code": "3662217017102"},
  {"produit": "MASQUE VISAGE NOURRISSANT", "code": "3662217011339"},
  {"produit": "GOMMAGE VISAGE", "code": "3662217015627"},
  {"produit": "CREME POUR LES MAINS", "code": "3662217002306"},
  {"produit": "CREME VISAGE ET CORPS", "code": "3662217004867"},
  {"produit": "CEME JOUR ET NUIT", "code": "3662217015610"},
  {"produit": "CREME DESALTERANTE", "code": "3662217015948"},
  {"produit": "CREME DE RASAGE - SAVON SOLIDE", "code": "3662217014422"},
  {"produit": "CREME SOIN CONTOUR YEUX ET LEVRES", "code": "3662217014446"},
  {"produit": "CREME SOLAIRE VISAGE SPF 50", "code": "3662217007240"},
  {"produit": "CREME SOIN HYDRATANT HOMME", "code": "3662217008162"},
  {"produit": "CREME DE JOUR PEAUX NORMALES A MIXTES", "code": "3662217001729"},
  {"produit": "CREME DE JOUR PEAUX SECHES ET SENSIBLES", "code": "3662217018123"},
  {"produit": "LAIT DEMAQUILLANT", "code": "3662217004256"},
  {"produit": "HUILE VEGETALE DE NOYAUX ABRICOT", "code": "3662217007219"},
  {"produit": "FARD A PAUPIERES CANNELLE", "code": "3662217004553"},
  {"produit": "FARD A PAUPIERES DESERT", "code": "3662217000722"},
  {"produit": "FOND DE TEINT CLAIR", "code": "3662217000623"},
  {"produit": "FOND DE TEINT MIEL", "code": "3662217004805"},
  {"produit": "GEL DOUCHE DOUCEUR D ABRICOT", "code": "3662217004881"},
  {"produit": "HUILE DE RICIN", "code": "3662217006151"},
  {"produit": "DUO LINER NOIR/TAUPE", "code": "3662217006526"},
  {"produit": "DUO LINER CUIVRE/TERRE BRULEE", "code": "3662217006533"},
  {"produit": "EYELINER", "code": "3662217003884"},
  {"produit": "CRAYON YEUX BRUN", "code": "3662217006373"},
  {"produit": "CRAYON YEUX NOIR", "code": "3662217000784"},
  {"produit": "MASCARA MARRON", "code": "3662217006816"},
  {"produit": "MASCARA NOIR", "code": "3662217017133"},
  {"produit": "DENTIFRICE", "code": "3662217007059"},
  {"produit": "RECHARGE DE DENTIFRICE", "code": "3662217018390"},
  {"produit": "FLACON RECHARGEABLE POUR DENTIFRICE", "code": "3662217018444"},
  {"produit": "SERUM VISAGE DESALTERANT", "code": "3662217011254"},
  {"produit": "CRAYON YEUX BRONZE CUIVRE", "code": "3662217011469"},
  {"produit": "HUILE LEVRE COULEUR DIVERS", "code": "3662217011971"},
  {"produit": "HUILE DE SOIN CHEVEUX COLORES", "code": "3662217012589"},
  {"produit": "VERNIS A ONGLES PRUNE", "code": "3662217010455"},
  {"produit": "VERNIS A ONGLES BASE ET TOP COAT", "code": "3662217010523"},
  {"produit": "VERNIS A ONGLES SABLE DORE NACRE", "code": "3662217014989"},
  {"produit": "VERNIS A ONGLES CORAIL", "code": "3662217015009"},
  {"produit": "VERNIS A ONGLES ROUGE OPERA", "code": "3662217015016"},
  {"produit": "VERNIS A ONGLES LAIT DE ROSE", "code": "3662217015207"},
  {"produit": "VERNIS A ONGLES GUIMAUVE", "code": "3662217015382"},
  {"produit": "SHAMPOING DOUCHE", "code": "3662217006854"},
  {"produit": "SHAMPOING DOUX 500ML", "code": "3662217015481"},
  {"produit": "SHAMPOING ANTI PELLICULAIRE 500ML", "code": "3662217015528"},
  {"produit": "SHAMPOING PURIFIANT 500ML", "code": "3662217016006"},
  {"produit": "SHAMPOING USAGE FREQUENT 500ML", "code": "3662217016013"},
  {"produit": "APRES SHAMPOOING", "code": "3662217012541"},
  {"produit": "APRES SHAMPOING SOLIDE", "code": "3662217018888"},
  {"produit": "MASQUE CAPILLAIRE", "code": "3662217012558"},
  {"produit": "RECHARGE GEL DOUCHE ABRICOT", "code": "3662217018055"},
  {"produit": "ORICULI", "code": "3760109053808"},
  {"produit": "FUROSHIKI EMBALLAGE CADEAU REUTILISABLE", "code": "3662217014309"}
]


# Chargement de la seconde liste depuis un fichier JSON
fichier_json = "C:\\Users\\Lenovo\\Documents\\OrgrenicPriceComparer\\Listes\\query.json"  # Remplacez par le chemin de votre fichier

try:
    with open(fichier_json, "r", encoding="utf-8") as file:
        liste_a_comparer = json.load(file)
except FileNotFoundError:
    print(f"Erreur : Le fichier {fichier_json} est introuvable.")
    exit()
except json.JSONDecodeError:
    print(f"Erreur : Le fichier {fichier_json} n'est pas un JSON valide.")
    exit()

# Comparaison des codes
for produit in liste_initiale:
    for hit in liste_a_comparer.get("hits", []):
        if produit["code"] == hit.get("barcode"):
            print(f"Titre correspondant trouvé : {hit['title']} - {produit['produit']}")
