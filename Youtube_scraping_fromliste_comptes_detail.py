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
token_youtube_recherche = "https://www.youtube.com{}"
fichier_youtube_sortie = "C:/DATA/github/.data/youtube_labos.xlsx"

temporisation = 3
first_time = True
nombre_requete = 0
Nombre_video = 0
d = { "k" :' * 1e3', "B" :' * 1e9', "M" : '* 1e6'} #conversion des milliers, etc...

df_video = pd.DataFrame(columns =  ['video', 'date', 'vue', 'like', 'dislike', 'description', 'comment', 'abonne'])
df_video = df_video.reset_index(drop=True)
l_video = []
l_date = []
l_vue = []
l_like = []
l_dislike = []
l_description = []
l_comment = []
l_abonne = []

#fonctions
def human_to_int(s):
    return eval(''.join([d.get(c, c) for c in s]), {}, {})

# OUverture d'un VPN
#settings = initialize_VPN(area_input=['Belgium,France,Netherlands,Germany,Slovenia,Switzerland','Denmark','Croatia','Finland','Estonia'])
#rotate_VPN(settings) #refer to the instructions variable here
#time.sleep(temporisation)

# Collecte des comptes
print("{} - Ouverture du fichier des comptes".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

# Ouveture du Browser
driver = webdriver.Chrome(adresse_driver_chrome)

with open(fichier_comptes, 'r', encoding="utf-8") as f:
    
    # parsing de chaque vidéo
    print("{} - Récuperation des détails des vidéos".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

    for line in f:

        try:
            # Construction de la requête de recherche
            adresse = token_youtube_recherche.format(line)
            nombre_requete += 1

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
        
            contenu = driver.page_source.encode('utf8')
            soup_contenu = bs4.BeautifulSoup(contenu, 'html.parser')

            # recupération du block meta
            meta_block = soup_contenu.find("div", {"id":"info-contents"})
            if meta_block:

                # vues
                block_vue = meta_block.find("div", {"id":"count"})
                nb_vue = block_vue.find("span", {"class":"view-count style-scope ytd-video-view-count-renderer"}).text.replace('vues', '').replace(',', '.')
                nb_vue = re.sub('\s+', '', nb_vue)
                nb_vue_float = human_to_int(nb_vue)

                # date vidéo
                if meta_block.find("div", {"id":"info-strings"}):
                    date_video = meta_block.find("div", {"id":"info-strings"}).text
                else : 
                    date_video = ''
  
                # like
                block_like = meta_block.find_all("a", {"class":"yt-simple-endpoint style-scope ytd-toggle-button-renderer"})
                nb_like = block_like[0].text.replace(',', '.')
                nb_like = re.sub('\s+', '', nb_like)
                if nb_like.replace('.','',1).isdigit():
                    nb_like_float = human_to_int(nb_like)
                else:
                    nb_like_float = ''

                # dislike
                nb_dislike = block_like[1].text.replace(',', '.')
                nb_dislike = re.sub('\s+', '', nb_dislike)
                if nb_dislike.replace('.','',1).isdigit():
                    nb_dislike_float = human_to_int(nb_dislike)
                else:
                    nb_dislike_float = ''

            # recupération du block description
            description_block = soup_contenu.find("div", {"id":"meta-contents"})
            if description_block:

                # abonnés
                nb_abonne = description_block.find("yt-formatted-string", {"id":"owner-sub-count"}).text.replace('abonnés', '').replace(',', '.')
                nb_abonne = re.sub('\s+', '', nb_abonne)
                if human_to_int(nb_abonne):
                    nb_abonne_float = human_to_int(nb_abonne)
                else:
                    nb_abonne_float = ''

                # description
                if description_block.find("div", {"id": "content"}):
                    description = description_block.find("div", {"id": "content"}).text.rstrip()
                else:
                    description = ''

                # commentaire
                #comment_block = soup_contenu.find("div", {"id":"meta-contents"})
                #if comment_block:
                comment = 'pas pour le moment'

            print("{} - {} - video : {} - like : {}  - dislike : {}  - date : {}".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), nombre_requete, line.strip(), nb_like_float, nb_dislike_float, date_video))
        except:
            print(Fore.RED + "{} - vidéo : {} - Erreur docteur".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), line.rstrip()) + Fore.RESET)
            date_video = ''
            nb_vue_float = ''
            nb_like_float = ''
            nb_dislike_float = ''
            description = ''
            comment = ''
            nb_abonne_float = ''

        #ajout dans la liste
        l_video.append(line.strip())
        l_date.append(date_video)
        l_vue.append(nb_vue_float)
        l_like.append(nb_like_float)
        l_dislike.append(nb_dislike_float)
        l_description.append(description)
        l_comment.append(comment)
        l_abonne.append(nb_abonne_float)
        
# creation du dataframe
print("{} - Création du dataframe".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
df_video['video'] = l_video
df_video['date'] = l_date
df_video['vue'] = l_vue
df_video['like'] = l_like
df_video['dislike'] = l_dislike
df_video['description'] = l_description
df_video['comment'] = l_comment
df_video['abonne'] = l_abonne

# ecriture des fichiers de sortie
if os.path.exists(fichier_youtube_sortie):
    os.remove(fichier_youtube_sortie)

print("{} - Ecriture du fichier de sortie".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
df_video.to_excel(fichier_youtube_sortie)

#fermeture du driver
driver.quit()