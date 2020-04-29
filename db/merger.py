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
import wg2.util.text
import pandas as pd

class PlaceDataframe():

    def __init__(self):
        self._places = pd.DataFrame(columns = ['title', 'title_n', 'address', 'addr_details',
                                                'lat', 'lng', 'official_url', 'closed'])

    def insert(self, item):
        if (self._places.shape[0] == 0):
            id = 0
        else:
            id = self._places.index.max() + 1
        item_df = pd.DataFrame(data=item,index=[id])
        self._places = pd.concat([self._places,item_df])
        return id

    def find(self,title_n,lat,lng):
        return self._places[abs(self._places['lat']-lat)<0.1][abs(self._places['lng']-lng)<0.1][self._places['title_n']==title_n]


    def find_or_insert(self,item) :
        id = 0
        df = self.find(item['title_n'],item['lat'],item['lng'])
        if df.shape[0] == 0 :
            id = self.insert(item)
        else :
            id = df.index[0]
        return id

class Merger():

    _sources = ['pdl','tra','mcl','lfd','tmo']
#    _sources = ['pdl','tra','mcl','lfd'] # Timeout import not ready...
    _data_root = 'data/'
    _reviews_filename = _data_root+'reviews.csv'
    _place_replace_filename = _data_root+'place_replace.csv'
    _place_closed_filename = _data_root+'place_closed.csv'
    _place_db_filename = _data_root+'place_db.csv'
    _review_db_filename = _data_root+'review_db.csv'

    def merge_reviews(self):
        reviews = pd.DataFrame()
        for source in self._sources:
            filename = self._data_root+source+'_dataset.csv'
            df = pd.read_csv(filename)
            reviews = reviews.append(df, ignore_index=True)
        self._reviews = reviews.sort_values(['lat','lng'])
        self._reviews.to_csv(self._reviews_filename,index=False)

    def replace_places(self):
        df_reviews = pd.read_csv(self._reviews_filename)
        df_replace = pd.read_csv(self._place_replace_filename)
        df_reviews['titleaddr'] = df_reviews['title'] + df_reviews['address']
        df_replace['titleaddr'] = df_replace['title_replace'] + df_replace['address_replace']
        for index, row in df_replace.iterrows():
            idx  = df_reviews[df_reviews['titleaddr']==row['titleaddr']].index
            logging.info('Replace : '+df_reviews['title'].iloc[idx])
            df_reviews.at[idx,'title'] = row['title']
            df_reviews.at[idx,'address'] = row['address']
        df_reviews.to_csv(self._reviews_filename,index=False)

    def close_places(self):
        df_reviews = pd.read_csv(self._reviews_filename)
        df_closed = pd.read_csv(self._place_closed_filename)
        df_reviews['titleaddr'] = df_reviews['title'] + df_reviews['address']
        df_closed['titleaddr'] = df_closed['title'] + df_closed['address']
        for index, row in df_closed.iterrows():
            idx  = df_reviews[df_reviews['titleaddr']==row['titleaddr']].index
            logging.info('Closed : '+df_reviews.iloc[idx]['title'])
            df_reviews.at[idx,'closed'] = row['closed']
        df_reviews.to_csv(self._reviews_filename,index=False)

    def create_db(self):
        pdf = PlaceDataframe()
        self._reviews = pd.read_csv(self._reviews_filename)
        self._reviews['title_n'] = self._reviews['title'].apply(lambda txt: wg2.util.text.normalize(txt))
        for i in range(0,self._reviews.shape[0]):
            item = dict()
            for key in ['title', 'title_n', 'address', 'addr_details', 'lat', 'lng', 'official_url', 'closed']:
                item[key] = self._reviews.loc[i][key]
            id = pdf.find_or_insert(item)
            self._reviews.at[i,'id_place']=id
        self._reviews.to_csv(self._review_db_filename)
        pdf._places.to_csv(self._place_db_filename)
