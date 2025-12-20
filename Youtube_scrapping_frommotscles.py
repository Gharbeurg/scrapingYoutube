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
fichier_motscles = "C:/DATA/github/.params/liste_motscles.txt"
adresse_driver_chrome = "C:/DATA/github/drivers/chromedriver.exe"
token_youtube_recherche = "https://www.youtube.com/results?search_query={}"
fichier_youtube_sortie = "C:/DATA/github/.data/twitter_comptes.xlsx"

temporisation = 3
scroll_max = 2
first_time = True

df_video = pd.DataFrame(columns =  ['titre', 'auteur', 'vue', 'duree', 'description', 'lien'])
df_video = df_video.reset_index(drop=True)
l_titre = []
l_auteur = []
l_vue = []
l_duree = []
l_description = []
l_lien = []
s_motscles = ''

# OUverture d'un VPN
settings = initialize_VPN(area_input=['Belgium,France,Netherlands,Germany,Slovenia,Switzerland','Denmark','Croatia','Finland','Estonia'])
rotate_VPN(settings) #refer to the instructions variable here
time.sleep(temporisation)

# Collecte des mots_cles
print("{} - Ouverture du fichier des mots clés".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
with open(fichier_motscles, 'r', encoding="utf-8") as f:
    for line in f:
        try:
            s_motscles += line.rstrip() + " OR "
        except:
            print(Fore.RED + "Pas de mot clé récupéré" + Fore.RESET)

#Suppression du dernier OR
s_motscles = s_motscles[:len(s_motscles) - 4]

#fermeture du fichier
f.close()

# Recherche de vidéos
print("{} - Recherche de vidéos".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

# Ouveture du Browser
driver = webdriver.Chrome(adresse_driver_chrome)

# Construction de la requête de recherche
adresse = token_youtube_recherche.format(s_motscles)

# browsing de la page
driver.get(adresse)
time.sleep(temporisation)

if first_time:
    # Click on the 'accept' button
    try:
        driver.find_element_by_xpath("//button[@jsname='higCR']").click()
        first_time = False
    except:
        print("{} - Pas trouvé ce p.... de bouton".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        first_time = False
    
# scrolling
print("{} - Scrolling, scrolling, scrolling".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

for i in range(1, scroll_max + 1):
    #scroll down
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(temporisation)

    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# parsing de chaque vidéo
print("{} - Récuperation des détails des vidéos".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

try:
    contenu = driver.page_source.encode('utf8')
    soup_contenu = bs4.BeautifulSoup(contenu, 'html.parser')
    
    # recupération du compte
    result_block = soup_contenu.find_all("div", {"id":"dismissible"})
    if result_block:
        for result in result_block:

            # Titre de la vidéo
            titre_video = result.find("h3", {"class": re.compile("^title-and-badge")}).text # la classe commence par ...
            if titre_video:
                l_titre.append(titre_video)
            else:
                l_titre.append('pas de titre')

            # Auteur de la vidéo
            auteur_video = result.find("div", {"id": "channel-info"}).text # la classe commence par ...
            if auteur_video:
                l_auteur.append(auteur_video)
            else:
                l_auteur.append('pas de auteur')

            # Vue et date de la vidéo
            vue_video = result.find("div", {"id": "metadata-line"}).text # la classe commence par ...
            if vue_video:
                l_vue.append(vue_video)
            else:
                l_vue.append('pas de vue ou date')

            # Duree de la vidéo
            duree_video = result.find("div", {"id": "overlays"}).text # la classe commence par ...
            if duree_video:
                l_duree.append(duree_video)
            else:
                l_duree.append('pas de duree')

            # Description de la vidéo
            description_video = result.find("div", {"class": re.compile("^metadata-snippet-container")}).text # la classe commence par ...
            if description_video:
                l_description.append(description_video)
            else:
                l_description.append('pas de description')

            # lien de la vidéo
            lien_video = result.find("a", {"id": "video-title"}).get('href') # la classe commence par ...
            if lien_video:
                l_lien.append(lien_video)
            else:
                l_lien.append('pas de lien')

except:
    print("{} - Il y en a qui ont essayé, ils ont eu des problèmes".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        
# creation du dataframe
print("{} - Création du dataframe".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
df_video['titre'] = l_titre
df_video['auteur'] = pd.Series(l_auteur)
df_video['vue'] = pd.Series(l_vue)
df_video['duree'] = pd.Series(l_duree)
df_video['description'] = pd.Series(l_description)
df_video['lien'] = pd.Series(l_lien)

# ecriture des fichiers de sortie
if os.path.exists(fichier_youtube_sortie):
    os.remove(fichier_youtube_sortie)

print("{} - Ecriture du fichier de sortie".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
df_video.to_excel(fichier_youtube_sortie)

#fermeture du driver
driver.quit()