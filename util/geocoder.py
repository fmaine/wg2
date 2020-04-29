__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"

import os
import re
import requests
import unicodedata
import logging
import json

class Geocoder():

    _cache = dict()
    _cache_dir  = ''
    _cache_filename = 'geocoder_cache.json'

    def __init__(self,cache_dir=''):
        self._cache_dir = cache_dir
        self.load_cache()

    def load_cache(self):
        if os.path.isfile(self._cache_dir+self._cache_filename):
            with open(self._cache_dir+self._cache_filename) as file :
                self._cache = json.load(file)
            return True
        else:
            return False

    def save_cache(self):
    	with open(self._cache_dir+self._cache_filename,'w') as file :
            json.dump(self._cache,file)

    def normalize(self,text):
        txt = '+'.join(re.split('\W+', text))
        ret = unicodedata.normalize('NFKD', txt).encode('ascii', 'ignore').decode()
        return ret.lower()

    def geocode(self,address):
        normaddr = self.normalize(address)
        if normaddr in self._cache:
            logging.info('Address in cache : ' + address)
            geocode_result=self._cache[normaddr]
        else:
            logging.info('Geocoding address : ' + address)
            geocode_result=self._geocode_bano(address)
            self._cache[normaddr]=geocode_result
            self.save_cache()
        return geocode_result[::-1] # Ordre inverse dans la bano...

    def _geocode_bano(self,address):
        r = requests.get('https://api-adresse.data.gouv.fr/search/?q='+address)
        data = json.loads(r.text)
        if (len(data['features'])>0):
            geocode_result = data['features'][0]['geometry']['coordinates']
            return geocode_result
        else:
            return [0.,0.]
