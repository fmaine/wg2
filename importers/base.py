__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"

'''
    wg2 Importer

    Base class for wg2 data imports
    Nedds to be subclassed for each datasource

    Synopsys :
        importer.acquire_list() : get the list of urls
        importer.acquire_pages() : get the html pages
        importer.init_dataset() / update_dataset : Parse the pages into the dataset

'''

import logging
import os
import urllib
import re
import requests
import parsel
import pandas as pd
import wg2.util.geocoder
import wg2.util.progress_monitor


class Importer():

    _origin = ''
    _data_root = 'data/'
    _page_extension = '.html'
    _user_agent = 'wherebot'
    _place_keys = [
        'title', 'address', 'addr_details', 'lat', 'lng', 'official_url', 'timestamp', 'closed',
        'origin', 'url', 'tags', 'rating', 'review_date', 'details',
    ]
    _dataset = ''
    _pm = wg2.util.progress_monitor.ProgressMonitor()

    def __init__(self):
        pass

    def urls_filename(self):
        filename = self._data_root+self._origin+'_urls.csv'
        return filename

    def dataset_filename(self):
        filename = self._data_root+self._origin+'_dataset.csv'
        return filename

    def url_to_filename(self,url):
        result = urllib.parse.urlparse(url).path.split('/')[-1]
        return result

    def load_urls(self):
        filename = self.urls_filename()
        if (os.path.exists(filename)):
            return pd.read_csv(filename)
        else:
            return pd.DataFrame(columns=['url','filename'])

    def load_dataset(self):
        filename = self.dataset_filename()
        if (os.path.exists(filename)):
            self._dataset = pd.read_csv(filename)
        else:
            self._dataset = pd.DataFrame(columns=self._place_keys)
        return self._dataset

    def save_dataset(self):
        filename = self.dataset_filename()
        self._dataset.to_csv(filename, index=False)

    def acquire_list(self):
        pass

    def parse_page(self, url, page):
        pass

    def acquire_pages(self):
        df_urls = self.load_urls()
        for index, row in df_urls.iterrows():
            filename = self._data_root+'html/'+self._origin+'/'+row['filename']+'.html'
            if (os.path.exists(filename)):
                logging.info("Ignoring "+self._origin+" "+row['filename'])
                pass
            else :
                logging.info("Acquiring "+self._origin+" "+row['filename'])
                r=requests.get(row['url'])
                f = open(filename, "a")
                f.write(r.text)
                f.close()

    def init_dataset(self):
        self._dataset = pd.DataFrame(columns=self._place_keys)
        df_urls = self.load_urls()
        for index, row in df_urls.iterrows():
            logging.info('Processing : '+self._origin+" "+str(index)+' - '+row['url'])
            filename = self._data_root+'html/'+self._origin+'/'+row['filename']+self._page_extension
            if (os.path.exists(filename)):
                with open(filename) as file:
                    page = file.read()
                    data = self.parse_page(row['url'],page)
                    if (data.get('title') and data.get('details')):
                        self._dataset = self._dataset.append(data, ignore_index=True)
                    else:
                        logging.warning('No title or details')
            else:
                logging.error('File not found')
        self._dataset = self._dataset[self._dataset['details'].notnull()]
        self.save_dataset()
        return self._dataset

    def update_dataset(self):
        self.load_dataset()
        df_urls = self.load_urls()
        for index, row in df_urls.iterrows():
            if (self._dataset['url'] == row['url']).any():
                logging.info('Existing url : '+self._origin+" "+row['url'])
            else:
                logging.info('New url : '+self._origin+" "+row['url'])
                filename = self._data_root+'html/'+self._origin+'/'+row['filename']+'.html'
                if (os.path.exists(filename)):
                    with open(filename) as file:
                        page = file.read()
                        data = self.parse_page(row['url'],page)
                        if ('title' in data):
                            self._dataset = self._dataset.append(data, ignore_index=True)
        self.save_dataset()
        return self._dataset

    def geocode(self):
        geo = wg2.util.geocoder.Geocoder(cache_dir=self._data_root)
        self._dataset = self.load_dataset()
        for index in range(0,self._dataset.shape[0]):
            if (self._dataset.at[index,'lat'] == 0):
                coords = geo.geocode(self._dataset.at[index,'address'])
                self._dataset.at[index,'lat'] = coords[0]
                self._dataset.at[index,'lng'] = coords[1]
        self.save_dataset()
