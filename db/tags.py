__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"

'''
    wg2 Merger
    Synopsis :
        merger.merge_reviews() : Merge all reviews ina single file / dataframe
        merger.replace_places() : unify matching places with different names
        merger.close_places() : Marks closed corresponding places
        merger.create_db() : Creates db files for website

'''

import logging
import json
import wg2.util.text
import wg2.util.progress_monitor

class TagList():

    def __init__(self):
        self._tags = list()

    def loads(self,text):
        if (type(text) == str):
            self._tags = json.loads(text)
        else:
            self._tags = list()

    def dumps(self):
        return json.dumps(self._tags)

    def list():
        return self._tags

_rating_tags = {
 'On aime beaucoup': 'Télérama aime beaucoup',
 'On aime un peu': 'Télérama aime un peu',
 "Cet événement n'a pas été vu par la rédaction": '',
 'CoupCoeur': 'Pudlo Coup de coeur',
 "L'Assiette MICHELIN : une cuisine de qualité": "Assiette Michelin",
 'Une étoile MICHELIN : une cuisine d’une grande finesse. Vaut l’étape !': 'Une étoile Michelin',
 'Deux étoiles MICHELIN : une cuisine d’exception. Vaut le détour !': 'Deux étoiles Michelin',
 'Bib Gourmand : nos meilleurs rapports qualité-prix ≤ 34 € (38 € à Paris)': 'Bib gourmand Michelin',
 'Trois étoiles MICHELIN : une cuisine unique. Vaut le voyage !': 'Trois étoiles Michelin',
 'CoupGueule': 'Pudlo Coup de gueule',
 'On aime passionnément': 'Télérama aime passionément',
 'On n’aime pas': 'Télérama n’aime pas'
}


_tag_list = {
 "L'Assiette MICHELIN : une cuisine de qualité": 2203,
 'Restos': 1811,
 'Cuisine moderne': 1671,
 'Standing simple.': 1283,
 'Bon standing.': 1089,
 'Restaurants français Paris': 958,
 'Terrasses': 912,
 'Cuisine française': 774,
 'Antidépresseur': 662,
 'Cuisine traditionnelle': 659,
 'Bib Gourmand : nos meilleurs rapports qualité-prix ≤ 34 € (38 € à Paris)': 556,
 'Terrasse': 513,
 'Une étoile MICHELIN : une cuisine d’une grande finesse. Vaut l’étape !': 500,
 'De 16 à 35 €': 447,
 'Ouvert le lundi': 446,
 'Rencontres': 422,
 'Manger seul': 387,
 'Ouvert le dimanche': 384,
 'Cuisiniers': 367,
 'Très bon standing.': 316,
 'Gastronomique': 276,
 'Cuisine du monde': 272,
 'Take-away': 260,
 'Néobistrot': 223,
 'Très bon standing. Nos plus belles adresses.': 221,
 'Bon standing. Nos plus belles adresses.': 219,
 'Kid friendly': 215,
 'De 36 à 50 €': 208,
 'Cuisine créative': 199,
 'Cuisine du marché': 198,
 '13 à table': 185,
 'Italien': 174,
 'Standing simple. Nos plus belles adresses.': 163,
 "Cuisine d'auteur": 160,
 'Bar à vins / Cave à manger': 150,
 'Asiatique': 149,
 'Brunch': 146,
 'Poissons et fruits de mer': 143,
 'Bistrot': 139,
 'Cuisine classique': 135,
 'Moins de 15 €': 129,
 'Terroir': 101,
 'Relais & Châteaux': 97,
 'Bars Paris': 96,
 'Plus de 51 €': 92,
 'Faim de nuit': 90,
 'Japonais': 88,
 'Bistronomie': 88,
 'Deux étoiles MICHELIN : une cuisine d’exception. Vaut le détour !': 84,
 'Lèche-doigts': 84,
 'Grandes Tables': 82,
 'Street food': 82,
 'Meilleurs Ouvriers de France': 79,
 'Voir et se faire voir': 72,
 'Fais-moi mal': 68,
 'Les Collectionneurs': 59,
 'Café / Coffee Shop': 58,
 'Michelin': 53,
 'Excellent standing. Nos plus belles adresses.': 51,
 'Trattoria Paris': 49,
 'Cuisine provençale': 44,
 'Tapas': 43,
 'Végétarien': 43,
 'Oriental': 43,
 'Cuisine italienne': 42,
 'Pizzas': 39,
 'Bouchon': 38,
 'Biocool': 36,
 'Cuisine moderne,Cuisine créative': 35,
 'Cuisine méditerranéenne': 34,
 'Sandwichs / Bagels': 34,
 'Restaurants français Bordeaux': 34,
 'Méditerranéen': 33,
 'Restaurants français Courchevel': 33,
 'Bistrots Strasbourg': 33,
 'Epiceries Paris': 33,
 'Cuisine japonaise': 32,
 'Salon de thé / Pâtisserie': 30,
 'Snack / Tartes / Salades / Soupes / Bols': 28,
 'Rendez-vous Paris 9ème': 28,
 'Planches / Assiettes froides': 27,
 'Trois étoiles MICHELIN : une cuisine unique. Vaut le voyage !': 27,
 'Top Chef': 26,
 'Cafés Paris 9ème': 26,
 'Vins': 25,
 'Chinois': 21,
 'Cuisine régionale': 19,
 'Bars': 15,
 "Table d'hôte": 14,
 'Indien': 14,
 'Casse-croûte': 11,
 'Excellent standing.': 11,
 'Burgers': 11,
}
