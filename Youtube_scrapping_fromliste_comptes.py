# Bibliotheque
import os
import time
import pandas as pd
import time
import bs4
import re

from datetime import datetime
from colorama import Fore, Back, Style
from selenium import webdriver
from nordvpn_switcher import initialize_VPN, rotate_VPN

# variables
fichier_comptes = "C:/DATA/github/.params/nouveau.txt"
adresse_driver_chrome = "C:/DATA/github/drivers/chromedriver.exe"
token_youtube_recherche = "https://www.youtube.com/{}/videos"
fichier_youtube_sortie = "C:/DATA/github/.data/youtube_labos.xlsx"

temporisation = 3
scroll_max = 3
first_time = True
limite_requete = 140 #Limite avant de se faire sortir par twitter
nombre_requete = 0
Nombre_video = 0

df_video = pd.DataFrame(columns =  ['compte', 'persona', 'labo', 'pays', 'titre', 'vue', 'lien'])
df_video = df_video.reset_index(drop=True)
l_titre = []
l_vue = []
l_compte = []
l_lien = []
l_laboratoire = []
l_persona = []
l_pays = []

# OUverture d'un VPN
#settings = initialize_VPN(area_input=['Belgium,France,Netherlands,Germany,Slovenia,Switzerland','Denmark','Croatia','Finland','Estonia'])
#rotate_VPN(settings) #refer to the instructions variable here
#time.sleep(temporisation)

# Collecte des comptes
print("{} - Ouverture du fichier des comptes".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

# Ouveture du Browser
driver = webdriver.Chrome(adresse_driver_chrome)

with open(fichier_comptes, 'r', encoding="utf-8") as f:
    
    # Recherche de vidéos
    print("{} - Recherche des vidéos".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

    # parsing de chaque vidéo
    print("{} - Récuperation des détails des vidéos".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

    for line in f:
        liste_line = line.split(',')
        nombre_requete += 1
        Nombre_video = 0

        #reinitialisation du driver tous les X requetes (limite twitter)
        #if nombre_requete == limite_requete:
            #driver.quit()
            #driver = webdriver.Chrome(adresse_driver_chrome)
            #nombre_requete = 0

        # Construction de la requête de recherche
        adresse = token_youtube_recherche.format(liste_line[0])

        # browsing de la page
        driver.get(adresse)
        time.sleep(temporisation)

        # Click on the 'accept' button, si premiere fois
        if first_time:
            try:
                driver.find_element_by_xpath("//button[@jsname='higCR']").click()
                first_time = False
            except:
                print("{} - Pas trouvé ce p.... de bouton".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
                first_time = False
        
        #scroll down pour récupérer plus de contenu
        for i in range(1, scroll_max):
            contenu = driver.page_source.encode('utf8')
            soup_contenu = bs4.BeautifulSoup(contenu, 'html.parser')

            # recupération des blocks
            result_block = soup_contenu.find_all("div", {"id":"dismissible"})
            if result_block:
                for result in result_block:

                    # Titre de la vidéo
                    titre_video = result.find("a", {"id":"video-title"}).text

                    # Metadata de la vidéo
                    vue_video = result.find("div", {"id": "metadata"}).text

                    # lien de la vidéo
                    lien_video = result.find("a", {"id": "video-title"}).get('href')
                    
                    #ajout dans la liste
                    if titre_video not in l_titre:
                        Nombre_video +=1
                        l_titre.append(titre_video)
                        l_vue.append(vue_video)
                        l_lien.append(lien_video)
                        l_compte.append(liste_line[0])
                        l_laboratoire.append(liste_line[2])
                        l_persona.append(liste_line[1])
                        l_pays.append(liste_line[3])

            #scroll
            last_height = driver.execute_script("return document.documentElement.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(temporisation)
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        print("{} - {} - Compte : {} - Vidéos : {}".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nombre_requete, liste_line[0].rstrip(), Nombre_video))

# creation du dataframe
print("{} - Création du dataframe".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
df_video['compte'] = l_compte
df_video['persona'] = l_persona
df_video['labo'] = l_laboratoire
df_video['pays'] = l_pays
df_video['titre'] = l_titre
df_video['vue'] = l_vue
df_video['lien'] = l_lien

# ecriture des fichiers de sortie
if os.path.exists(fichier_youtube_sortie):
    os.remove(fichier_youtube_sortie)

print("{} - Ecriture du fichier de sortie".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
df_video.to_excel(fichier_youtube_sortie)

#fermeture du driver
driver.quit()