from bs4 import BeautifulSoup

import requests
import json
import re
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time

doScreenCapture = False
lafourche_tag = 'jsx-2550952359 unit-price'
lafourche_tag2 = 'jsx-774668517 unit-price'
biocoop_tag = 'weight-price'
biocoop_unit_tag = 'price'
satoriz_tag = 'rqp'
#greenweez_tag = 'gds-text ProductDetailsPrice_gwz-offer-details-price__quantity__SfSbB --bold --xs'
#greenweez_int_tag = 'gds-title gds-current-price__whole --font-body --md'
#greenweez_cents_tag = 'gds-title gds-current-price__decimal --font-body --sm'
greenweez_tag = 'leading-[initial] ProductDetailsPrice_gwz-offer-details-price__quantity__SfSbB font-bold font-body text-xs'
#greenweez_int_tag = 'gds-title CurrentPrice_gwz-current-price__whole__KP5oj --font-body --xl'
greenweez_int_tag = 'leading-[initial] CurrentPrice_gwz-current-price__whole__KP5oj font-extrabold font-body text-4xl'
#greenweez_cents_tag = 'gds-title CurrentPrice_gwz-current-price__decimal__lHh0v --font-body --md'
greenweez_cents_tag = 'leading-[initial] CurrentPrice_gwz-current-price__decimal__lHh0v font-extrabold font-body text-2xl'


# Configurer les options du navigateur Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Exécuter Chrome en mode headless (sans interface graphique)

prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-extensions')

# Spécifier le chemin complet vers le chromedriver ici
chromedriver_path = "C:\\Users\\Lenovo\\PycharmProjects\\chromedriver-win64\\chromedriver.exe"


class SiteInformation:
    def __init__(self, url, qtt):
        self.url = url
        self.isUnitary = False
        if qtt == 'V':
            self.qtt = 1
        elif 'U' in qtt:
            self.isUnitary = True
            self.qtt = float(qtt.replace(',','.').replace('U', ''))
        else:
            try:
                self.qtt = float(qtt.replace(',','.'))
            except:
                self.qtt = 1
        self.price = 888888


class ProductComparer:
    biocoop_fontaine_base_url = "https://www.biocoop.fr/magasin-biocoop_fontaine/"
    biocoop_champollion_base_url = "https://www.biocoop.fr/magasin-biocoop_champollion/"
    biocoop_base_url = "https://www.biocoop.fr/"
    lafourcheId = 0
    biocoopChampollionId = 1
    biocoopFontaineId = 2
    satorizId = 3
    greenWeezId = 4
    elefanId = 5

    def __init__(self, product_info, product_list, elefan_data, to_do_list=None):
        self.product_name = product_info['name']
        self.product_list = product_list
        self.all_elefan_data_list = elefan_data
        self.data_list = []

        self.data_list.append(SiteInformation(product_info['lafourche_site'], product_info['lafourche_qtt']))
        self.data_list.append(SiteInformation(
            product_info['biocoop_champollion_site'].replace(self.biocoop_base_url, self.biocoop_champollion_base_url)
            , product_info['biocoop_champollion_qtt']))
        self.data_list.append(SiteInformation(
            product_info['biocoop_fontaine_site'].replace(self.biocoop_base_url, self.biocoop_fontaine_base_url)
            , product_info['biocoop_fontaine_qtt']))
        self.data_list.append(SiteInformation(product_info['satoriz_site'], product_info['satoriz_qtt']))
        self.data_list.append(SiteInformation(product_info['greenweez_site'], product_info['greenweez_qtt']))
        self.data_list.append(SiteInformation(product_info['elefan_code'], product_info['elefan_qtt']))

        previousProduct = self._find_url_in_list()
        for id, product in enumerate(self.data_list, start = 0):
            if to_do_list[id]:
                if previousProduct is not None and previousProduct[1].count(id) > 0:
                    self.data_list[id].price = previousProduct[0].data_list[id].price
                else:
                    self._get_product_price(id)

    def _get_product_price(self, id):
        if id == self.lafourcheId:
            self.data_list[id].price = self._get_price_from_lafourche()
        elif id == self.biocoopChampollionId or id == self.biocoopFontaineId:
            self.data_list[id].price = self._get_price_from_site(id, biocoop_tag, biocoop_unit_tag)
        elif id == self.satorizId:
            self.data_list[id].price = self._get_price_from_site(id, satoriz_tag, satoriz_tag)
        elif id == self.greenWeezId:
            self.data_list[id].price = self._get_price_from_greenweez()
        elif id == self.elefanId:
            self.data_list[id].price = self._get_prices_from_elefan()

    def _get_price_from_site(self, site_id, tag, unit_tag=None):
        if site_id:
            product = self.data_list[site_id]
            if product:
                quantity = product.qtt
                response = requests.get(product.url)
                soup = BeautifulSoup(response.text, 'html.parser')
                if product.isUnitary:
                    price_element = soup.find(class_=unit_tag)
                else:
                    price_element = soup.find(class_=tag)
            else:
                return 888888

            price = 888888
            if price_element is not None:
                text_price = price_element.text.strip().replace('.', '')
                text_price = text_price.replace(',', '.')
                price = round(float(re.sub(r'[^\d.,]', '', text_price))/quantity,2) if price_element else 888888
        else:
            price = 888888
        return price

    def _get_price_from_lafourche(self):
        if self.data_list[self.lafourcheId].url:
            try:
                response = requests.get(self.data_list[self.lafourcheId].url)
                soup = BeautifulSoup(response.text, 'html.parser')
                text_element = soup.find('script', id='__NEXT_DATA__')
                if text_element:
                    text = text_element.text.strip()
                    price = json.loads(text)['props']['pageProps']['product']['meta']['finance']['unit_price']
                else:
                    price = 888888
            except KeyError:
                print("URL : " + self.data_list[self.lafourcheId].url)
                print(self.product_name)
                price = 888888
        else:
            price = 888888
        return price

    def _get_price_from_greenweez(self):
        if self.data_list[self.greenWeezId].url:
            # Initialiser le navigateur Chrome avec le chemin spécifié
            driver = webdriver.Chrome(options=chrome_options)
            # Accéder à l'URL avec le navigateur Chrome
            driver.get(self.data_list[self.greenWeezId].url)

            # Attendre quelques secondes pour que la page se charge complètement (vous pouvez ajuster le temps d'attente selon votre besoin)
            driver.implicitly_wait(6)

            # Obtenir le contenu de la page après que JavaScript ait pu modifier le DOM
            page_source = driver.page_source

            # Fermer le navigateur
            driver.quit()

            # Utiliser BeautifulSoup pour extraire les informations nécessaires
            soup = BeautifulSoup(page_source, 'html.parser')
            if self.data_list[self.greenWeezId].isUnitary:
                int_price_element = soup.find(class_=greenweez_int_tag)
                cent_price_element = soup.find(class_=greenweez_cents_tag)
                if int_price_element and cent_price_element:
                     text_price = re.sub(r'[^\d.,]', '', int_price_element.text.strip()) + "." + re.sub(r'[^\d.,]', '', cent_price_element.text.strip())
                     price = round(float(text_price)/self.data_list[self.greenWeezId].qtt,2)
                else:
                    price = 888888
            else:
                price_element = soup.find(class_=greenweez_tag)
                price = float(re.sub(r'[^\d.,]', '', price_element.text.strip().replace(',', '.'))) if price_element else 888888


        else:
            price = 888888
        return price

    def _get_prices_from_elefan(self):
        if self.data_list[self.elefanId].url:
            # Filtre le produit dont la désignation correspond exactement à 'SAVON LAVANDE'
            produits_filtrés = [produit for produit in self.all_elefan_data_list if
                                produit["designation"] == self.data_list[self.elefanId].url]

            # Vérifie si le produit a été trouvé et affiche les informations
            if produits_filtrés:
                produit = produits_filtrés[0]  # Comme il y a un seul produit recherché, on prend le premier résultat
                price = round(produit.get("prix_vente") / self.data_list[self.elefanId].qtt, 2)
            else:
                print(f"Aucun produit trouvé avec la désignation '{self.data_list[self.elefanId].url}'")
                price = 888888
        else:
            price = 888888
        return price

    def _capture_screenshot_section(self, url, save_path, left, top, width, height):
        # Configurer le service pour le driver
        service = Service(chromedriver_path)

        # Options pour Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Ouvrir Chrome en mode sans tête

        driver = webdriver.Chrome(service=service, options=options)

        try:
            # Ouvrir l'URL
            driver.get(url)
            driver.set_window_size(1920, 1080)  # Taille de la fenêtre en pixels
            time.sleep(2)  # Attendre le chargement de la page

            # Accepter les cookies si le bandeau est présent
            try:
                # Remplacer "ID_DU_BOUTON_COOKIES" par l'ID réel ou utiliser un autre sélecteur
                cookie_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accepter')]")
                cookie_button.click()
                print("Bandeau de cookies accepté.")
            except:
                print("Bandeau de cookies non trouvé ou déjà accepté.")

            time.sleep(2)  # Attendre le chargement de la page

            # Prendre une capture d'écran de toute la page
            full_screenshot_path = "full_screenshot.png"
            driver.save_screenshot(full_screenshot_path)

            # Charger l'image complète et définir la région
            full_image = Image.open(full_screenshot_path)
            box = (left, top, left + width, top + height)

            # Découper la section
            cropped_image = full_image.crop(box)
            cropped_image.save(save_path)
            print(f"Section de la capture d'écran sauvegardée sous : {save_path}")

        finally:
            driver.quit()

    def _find_url_in_list(self):
        list_len = len(self.product_list)
        i = 1
        list_id = []
        while i < 3 and list_len >= i:
            if self.product_list[list_len - i].data_list[self.lafourcheId].url == self.data_list[
                self.lafourcheId].url:
                list_id.append(self.lafourcheId)
            elif self.product_list[list_len - i].data_list[self.biocoopChampollionId].url == self.data_list[
                self.biocoopChampollionId].url:
                list_id.append(self.biocoopChampollionId)
            elif self.product_list[list_len - i].data_list[self.biocoopFontaineId].url == self.data_list[
                self.biocoopFontaineId].url:
                list_id.append(self.biocoopFontaineId)
            elif self.product_list[list_len - i].data_list[self.satorizId].url == self.data_list[
                self.satorizId].url:
                list_id.append(self.satorizId)
            elif self.product_list[list_len - i].data_list[self.greenWeezId].url == self.data_list[
                self.greenWeezId].url:
                list_id.append(self.greenWeezId)
            elif self.product_list[list_len - i].data_list[self.elefanId].url == self.data_list[
                self.elefanId].url:
                list_id.append(self.elefanId)
            if len(list_id) > 0:
                return (self.product_list[list_len - i], list_id)
            i = i + 1
        return None