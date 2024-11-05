from bs4 import BeautifulSoup

import requests
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from PIL import Image
import time
import os

from selenium.webdriver.common.by import By

doScreenCapture = True
lafourche_tag = 'jsx-2550952359 unit-price'
lafourche_tag2 = 'jsx-774668517 unit-price'
biocoop_tag = 'weight-price'
biocoop_unit_tag = 'price'
satoriz_tag = 'rqp'
#greenweez_tag = 'gds-text ProductDetailsPrice_gwz-offer-details-price__quantity__SfSbB --bold --xs'
#greenweez_int_tag = 'gds-title gds-current-price__whole --font-body --md'
#greenweez_cents_tag = 'gds-title gds-current-price__decimal --font-body --sm'
greenweez_tag = 'leading-[initial] ProductDetailsPrice_gwz-offer-details-price__quantity__SfSbB font-bold font-body text-xs'
greenweez_int_tag = 'gds-title CurrentPrice_gwz-current-price__whole__KP5oj --font-body --xl'
greenweez_cents_tag = 'gds-title CurrentPrice_gwz-current-price__decimal__lHh0v --font-body --md'

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

class ProductComparer:
    biocoop_fontaine_base_url = "https://www.biocoop.fr/magasin-biocoop_fontaine/"
    biocoop_champollion_base_url = "https://www.biocoop.fr/magasin-biocoop_champollion/"
    biocoop_base_url = "https://www.biocoop.fr/"

    def __init__(self, product_name, lafourche_site, biocoop_champollion_site, biocoop_fontaine_site, satoriz_site, greenweez_site):
        self.product_name = product_name
        self.lafourche_site = lafourche_site
        self.biocoop_champollion_site = biocoop_champollion_site.replace(self.biocoop_base_url,self.biocoop_champollion_base_url)
        self.biocoop_fontaine_site = biocoop_fontaine_site.replace(self.biocoop_base_url,self.biocoop_fontaine_base_url)
        self.satoriz_site = satoriz_site
        self.greenweez_site = greenweez_site

    def get_prices(self):
        prices = []

        # La Fourche
        lafourche_price = self._get_price_from_lafourche()
        prices.append(lafourche_price)

        # Biocoop
        biocoop_champollion_price = self._get_price_from_site(self.biocoop_champollion_site, biocoop_tag, biocoop_unit_tag)
        prices.append(biocoop_champollion_price)

        biocoop_fonfaine_price = self._get_price_from_site(self.biocoop_fontaine_site, biocoop_tag, biocoop_unit_tag)
        prices.append(biocoop_fonfaine_price)

        # Satoriz
        satoriz_price = self._get_price_from_site(self.satoriz_site, satoriz_tag, satoriz_tag)
        if doScreenCapture:
            self._capture_screenshot_section(self.satoriz_site, os.getcwd() + '\\Images\\Satoriz_' + self.product_name + '.png', 0, 0, 1920, 820)
        prices.append(satoriz_price)

        # greenweez
        greenweez_price = self._get_price_from_greenweez()
        prices.append(greenweez_price)
        return prices

    def _get_price_from_site(self, url, tag, unit_tag=None):
        if url:
            quantity = ''
            if '>' in url:
                site_data = url.split('>')
                quantity = site_data[0]
                url = site_data[1]
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            if quantity == '':
                price_element = soup.find(class_=tag)
                quantity = '1'
            else:
                price_element = soup.find(class_=unit_tag)
            price = 888888
            if price_element is not None:
                text_price = price_element.text.strip().replace('.', '')
                text_price = text_price.replace(',', '.')
                price = round(float(re.sub(r'[^\d.,]', '', text_price))/float(quantity),2) if price_element else 888888
        else:
            price = 888888
        return price

    def _get_price_from_lafourche(self):
        if self.lafourche_site:
            try:
                response = requests.get(self.lafourche_site)
                soup = BeautifulSoup(response.text, 'html.parser')
                text_element = soup.find('script', id='__NEXT_DATA__')
                if text_element:
                    text = text_element.text.strip()
                    price = json.loads(text)['props']['pageProps']['product']['meta']['finance']['unit_price']
                else:
                    price = 888888
            except KeyError:
                print("URL : " + self.lafourche_site)
                print(self.product_name)
                price = 888888
        else:
            price = 888888
        return price

    def _get_price_from_greenweez(self):
        if self.greenweez_site:
            quantity=''
            if '>' in self.greenweez_site:
                site_data = self.greenweez_site.split('>')
                quantity = site_data[0]
                url = site_data[1]
                self.greenweez_site = url
            else:
                url=self.greenweez_site

            # Initialiser le navigateur Chrome avec le chemin spécifié
            driver = webdriver.Chrome(options=chrome_options)
            # Accéder à l'URL avec le navigateur Chrome
            driver.get(url)

            # Attendre quelques secondes pour que la page se charge complètement (vous pouvez ajuster le temps d'attente selon votre besoin)
            driver.implicitly_wait(6)

            # Obtenir le contenu de la page après que JavaScript ait pu modifier le DOM
            page_source = driver.page_source

            # Fermer le navigateur
            driver.quit()

            # Utiliser BeautifulSoup pour extraire les informations nécessaires
            soup = BeautifulSoup(page_source, 'html.parser')
            if quantity == '':
                price_element = soup.find(class_=greenweez_tag)
                price = float(re.sub(r'[^\d.,]', '', price_element.text.strip().replace(',', '.'))) if price_element else 888888
            else:
                int_price_element = soup.find(class_=greenweez_int_tag)
                cent_price_element = soup.find(class_=greenweez_cents_tag)
                if int_price_element and cent_price_element:
                     text_price = re.sub(r'[^\d.,]', '', int_price_element.text.strip()) + "." + re.sub(r'[^\d.,]', '', cent_price_element.text.strip())
                     price = round(float(text_price)/float(quantity),2)
                else:
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