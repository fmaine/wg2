__author__ = "Francois Maine"
__copyright__ = "Copyright 2019, Preedom Partners"
__email__ = "fm@freedom-partners.com"

import os
import json
import math
import pandas as pd

import wg2.util.geocoder

class PlaceFinder():

    _default_pagesize = 50
    _reviews_filename = 'data/prod/review_db.csv'
    _reviews = ''
    _places_filename = 'data/prod/place_db.csv'
    _places = ''
    _places_found = []
    _param_keys = [
        'words', 'words_opt',
        'location', 'lat', 'lng',
        'tags_in', 'tags_out',
        'pagesize', 'pagenum',
        'token',
    ]
    _origin_labels = {'tra':'Télérama','pdl':'Guide Pudlowski','mcl':'Guide Michelin'}

    _geo = None
    _pagesize = _default_pagesize

    def __init__(self):
        self._reviews = pd.read_csv(self._reviews_filename)
        self._places = pd.read_csv(self._places_filename)
        self._geo = wg2.util.geocoder.Geocoder(cache_dir='data/prod/')

    def find(self, args):
        response = dict()
        response['lat'] = lat = args.get('lat')
        response['lng'] = lng = args.get('lng')
        response['address'] = addr = args.get('address')
        if (addr):
            coords = self._geo.geocode(addr)
            response ['lat'] = coords[0]
            response ['lng'] = coords[1]
            response ['places'] = self.find_coords(coords[0],coords[1])
#        elif (lat & lng) :
#            print(lat,' ',lng)
        return response

    def find_coords(self,lat,lng):
        self._places_found = []
        self._places['dist'] = ((self._places['lat']- lat)**2 + (self._places['lng']- lng)**2)
        self._places = self._places.sort_values('dist')
        nb_reviews = self._places.shape[0]
        n = 0
        for index, row in self._places.iterrows():
            place = dict()
            place['title'] = row['title']
            place['address'] = row['address']
            place['lat'] = row['lat']
            place['lng'] = row['lng']
            place['official_url'] = row['official_url']
            place['reviews'] = list()
            for i_review, r_review in self._reviews[self._reviews['id_place']==index].iterrows():
                review = dict()
                review['origin'] = self._origin_labels[r_review['origin']]
                review['url'] = r_review['url']
                review['review_date'] = r_review['review_date']
                review['details'] = r_review['details']
                review['tags'] = json.loads(r_review['tags'])
                place['reviews'].append(review)
            self._places_found.append(place)
            n += 1
            if (n > self._pagesize):
                break
        return self._places_found
