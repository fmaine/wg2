__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"

'''
    wg2 Merger

    Base class for wg2 data imports
    Nedds to be subclassed for each datasource

'''

import unicodedata
import pandas as pd

class PlaceDataframe():

    def __init__(self):
        self._places = pd.DataFrame(columns = ['title', 'address', 'addr_details',
                                                'lat', 'lng', 'official_url', 'closed'])
    def insert(self, item):
        if (self._places.shape[0] == 0):
            id = 0
        else:
            id = self._places.index.max() + 1
        item_df = pd.DataFrame(data=item,index=[id])
        self._places = pd.concat([self._places,item_df])
        return id

#    def normalize_text(txt):
#        return unicodedata.normalize('NFKD', txt).encode('ascii', 'ignore').decode().lower()

#    def compare_places(row,title,lat,lng):
#        return abs(row['lat']-lat)<0.1 and abs(row['lng']-lng)<0.1 and normalize_text(row['title']) == normalize_text(title)

    def find(self,title,lat,lng):
        return self._places[abs(self._places['lat']-lat)<0.1][abs(self._places['lng']-lng)<0.1][self._places['title']==title]


    def find_or_insert(self,item) :
        id = 0
        df = self.find(item['title'],item['lat'],item['lng'])
        if df.shape[0] == 0 :
            id = self.insert(item)
        else :
            id = df.index[0]
        return id

class Merger():

    _sources = ['pdl','tra','mcl','lfd','tmo',]
    _data_root = 'data/'
    _place_db_filename = _data_root+'place_db.csv'
    _review_db_filename = _data_root+'review_db.csv'

    def merge_reviews(self):
        reviews = pd.DataFrame()
        for source in self._sources:
            df = pd.read_csv(self._data_root+source+'_dataset.csv')
            reviews = reviews.append(df, ignore_index=True)
        self._reviews = reviews.sort_values(['lat','lng'])
        self._reviews.to_csv('data/reviews.csv',index=False)

    def create_db(self):
        pdf = PlaceDataframe()
        for i in range(0,self._reviews.shape[0]):
            item = dict()
            for key in ['title', 'address', 'addr_details', 'lat', 'lng', 'official_url', 'closed']:
                item[key] = self._reviews.loc[i][key]
            id = pdf.find_or_insert(item)
            self._reviews.at[i,'id_place']=id
        self._reviews.to_csv(self._review_db_filename)
        pdf._places.to_csv(self._place_db_filename)
