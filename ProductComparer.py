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
import os

doScreenCapture = False
lafourcheId = 0
biocoopChampollionId = 1
biocoopFontaineId = 2
satorizId = 3
greenWeezId = 4
elefanId = 5
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
elefan_tag = 'fullscreen-normal-text fullscreen-night-text emotion-16s53r6 e1h7b1g11'
elefan_tag2 = 'cellData emotion-1vgqzmj e1h7b1g10'

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
        self.qtt = qtt
        self.price = None


class ProductComparer:
    biocoop_fontaine_base_url = "https://www.biocoop.fr/magasin-biocoop_fontaine/"
    biocoop_champollion_base_url = "https://www.biocoop.fr/magasin-biocoop_champollion/"
    biocoop_base_url = "https://www.biocoop.fr/"

    def __init__(self, product_name, product_list, lafourche_site, lafourche_qtt,
                 biocoop_champollion_site, biocoop_champollion_qtt,
                 biocoop_fontaine_site, biocoop_fontaine_qtt,
                 satoriz_site, satoriz_qtt,
                 greenweez_site, greenweez_qtt,
                 elefan_site, elefan_qtt):
        self.product_name = product_name
        self.product_list = product_list
        self.lafourche = SiteInformation(lafourche_site,lafourche_qtt)
        self.biocoop_champollion = SiteInformation(
            biocoop_champollion_site.replace(self.biocoop_base_url,self.biocoop_champollion_base_url)
            ,biocoop_champollion_qtt)
        self.biocoop_fontaine = SiteInformation(
            biocoop_fontaine_site.replace(self.biocoop_base_url,self.biocoop_fontaine_base_url)
            ,biocoop_fontaine_qtt)
        self.satoriz = SiteInformation(satoriz_site,satoriz_qtt)
        self.greenweez = SiteInformation(greenweez_site,greenweez_qtt)
        self.elefan = SiteInformation(elefan_site,elefan_qtt)

    def get_prices(self):
        prices = []

        previousProduct = self._find_url_in_list()

        # La Fourche
        if previousProduct is not None and previousProduct[1].count(lafourcheId) > 0:
            self.lafourche.price = previousProduct[0].lafourche.price
        else:
            self.lafourche.price = self._get_price_from_lafourche()
        prices.append(self.lafourche.price)

        # Biocoop
        if previousProduct is not None and previousProduct[1].count(biocoopChampollionId) > 0:
            self.biocoop_champollion.price = previousProduct[0].biocoop_champollion.price
        else:
            self.biocoop_champollion.price = self._get_price_from_site(self.biocoop_champollion.url, biocoop_tag,
                                                                       biocoop_unit_tag, biocoopChampollionId)
        prices.append(self.biocoop_champollion.price)

        if previousProduct is not None and previousProduct[1].count(biocoopFontaineId) > 0:
            self.biocoop_fontaine.price = previousProduct[0].biocoop_fontaine.price
        else:
            self.biocoop_fontaine.price = self._get_price_from_site(self.biocoop_fontaine.url, biocoop_tag,
                                                                    biocoop_unit_tag, biocoopFontaineId)
        prices.append(self.biocoop_fontaine.price)

        # Satoriz
        if previousProduct is not None and previousProduct[1].count(satorizId) > 0:
            self.satoriz.price = previousProduct[0].satoriz.price
        else:
            self.satoriz.price = self._get_price_from_site(self.satoriz.url, satoriz_tag, satoriz_tag, satorizId)
        prices.append(self.satoriz.price)

        # greenweez
        if previousProduct is not None and previousProduct[1].count(greenWeezId) > 0:
            self.greenweez.price = previousProduct[0].greenweez.price
        else:
            self.greenweez.price = self._get_price_from_greenweez()
        prices.append(self.greenweez.price)

        # Elefan
        if previousProduct is not None and previousProduct[1].count(elefanId) > 0:
            self.elefan.price = previousProduct[0].elefan.price
        else:
            self.elefan.price = self._get_prices_from_elefan()
        prices.append(self.elefan.price)

        self.previousProduct = self
        return prices

    def _get_price_from_site(self, url, tag, unit_tag=None, site_id = 0):
        if url:
            quantity = '1'
            if site_id == biocoopChampollionId:
                quantity = self.biocoop_champollion.qtt
            if site_id == biocoopFontaineId:
                quantity = self.biocoop_fontaine.qtt
            if site_id == satorizId:
                quantity = self.satoriz.qtt

            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            if 'U' in quantity:
                price_element = soup.find(class_=unit_tag)
                quantity = quantity.replace('U','')
                quantity = quantity.replace(',','.')
            else:
                price_element = soup.find(class_=tag)
                quantity = '1'

            price = 888888
            if price_element is not None:
                text_price = price_element.text.strip().replace('.', '')
                text_price = text_price.replace(',', '.')
                price = round(float(re.sub(r'[^\d.,]', '', text_price))/float(quantity),2) if price_element else 888888
        else:
            price = 888888
        return price

    def _get_price_from_lafourche(self):
        if self.lafourche.url:
            try:
                response = requests.get(self.lafourche.url)
                soup = BeautifulSoup(response.text, 'html.parser')
                text_element = soup.find('script', id='__NEXT_DATA__')
                if text_element:
                    text = text_element.text.strip()
                    price = json.loads(text)['props']['pageProps']['product']['meta']['finance']['unit_price']
                else:
                    price = 888888
            except KeyError:
                print("URL : " + self.lafourche.url)
                print(self.product_name)
                price = 888888
        else:
            price = 888888
        return price

    def _get_price_from_greenweez(self):
        if self.greenweez.url:
            quantity= self.greenweez.qtt

            # Initialiser le navigateur Chrome avec le chemin spécifié
            driver = webdriver.Chrome(options=chrome_options)
            # Accéder à l'URL avec le navigateur Chrome
            driver.get(self.greenweez.url)

            # Attendre quelques secondes pour que la page se charge complètement (vous pouvez ajuster le temps d'attente selon votre besoin)
            driver.implicitly_wait(6)

            # Obtenir le contenu de la page après que JavaScript ait pu modifier le DOM
            page_source = driver.page_source

            # Fermer le navigateur
            driver.quit()

            # Utiliser BeautifulSoup pour extraire les informations nécessaires
            soup = BeautifulSoup(page_source, 'html.parser')
            if 'U' in quantity:
                quantity = quantity.replace('U','')
                quantity = quantity.replace(',','.')
                int_price_element = soup.find(class_=greenweez_int_tag)
                cent_price_element = soup.find(class_=greenweez_cents_tag)
                if int_price_element and cent_price_element:
                     text_price = re.sub(r'[^\d.,]', '', int_price_element.text.strip()) + "." + re.sub(r'[^\d.,]', '', cent_price_element.text.strip())
                     price = round(float(text_price)/float(quantity),2)
                else:
                    price = 888888
            else:
                price_element = soup.find(class_=greenweez_tag)
                price = float(re.sub(r'[^\d.,]', '', price_element.text.strip().replace(',', '.'))) if price_element else 888888


        else:
            price = 888888
        return price

    def _get_prices_from_elefan(self):
        if self.elefan.url:
            # Initialiser le navigateur Chrome avec le chemin spécifié
            driver = webdriver.Chrome(options=chrome_options)
            # Accéder à l'URL avec le navigateur Chrome
            driver.get(self.elefan.url)

            # Attendre quelques secondes pour que la page se charge complètement (vous pouvez ajuster le temps d'attente selon votre besoin)
            # Attendre que l'élément soit disponible
            try:
                price_element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, elefan_tag))
                )
            except TimeoutException:
                print("Erreur acquisition prix " + self.product_name + " Elefan")
                return 888888

            # Obtenir le contenu de la page après que JavaScript ait pu modifier le DOM
            page_source = driver.page_source

            # Fermer le navigateur
            driver.quit()

            soup = BeautifulSoup(page_source, 'html.parser')

            self.elefan.qtt = self.elefan.qtt.replace(',', '.')

            price_element = price_element.find(class_ = elefan_tag2)
            if price_element:
                text_price = re.sub(r'[^\d.,]', '', price_element.text.strip()).replace(',', '.')
                price = round(float(text_price) / float(self.elefan.qtt), 2) if price_element else 888888
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

    def _find_url_in_list(self):
        list_len = len(self.product_list)
        i = 1
        list_id = []
        while i<3 and list_len >= i:
            if self.product_list[list_len-i].lafourche.url == self.lafourche.url:
                list_id.append(lafourcheId)
            elif self.product_list[list_len-i].biocoop_champollion.url == self.biocoop_champollion.url:
                list_id.append(biocoopChampollionId)
            elif self.product_list[list_len-i].biocoop_fontaine.url == self.biocoop_fontaine.url:
                list_id.append(biocoopFontaineId)
            elif self.product_list[list_len-i].satoriz.url == self.satoriz.url:
                list_id.append(satorizId)
            elif self.product_list[list_len-i].greenweez.url == self.greenweez.url:
                list_id.append(greenWeezId)
            elif self.product_list[list_len-i].elefan.url == self.elefan.url:
                list_id.append(elefanId)
            if len(list_id) > 0:
                return (self.product_list[list_len-i], list_id)
            i= i+1
        #for product in enumerate(list.reverse):
        #   if (product.lafourche.url == url
         #           or product.biocoop_champollion.url == url
          #          or product.biocoop_fontaine.url == url
           #         or product.satoriz.url == url
             #       or product.greenweez.url == url):
              #  return product
        return None