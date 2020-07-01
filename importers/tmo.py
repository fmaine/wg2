'''
    Le Fooding Importer
    Imports le fooding reviews
'''

__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"


import datetime
import unicodedata
import re
import json
import xmltodict
import requests
import parsel
import pandas as pd
import wg2.importers.base


class TimeoutImporter(wg2.importers.base.Importer):
    """Timeout Importer"""

    def __init__(self):
        self._origin = 'tmo'
        self._page_extension = '.json'

    def clean_text(self,txt):
        txt2 = None
        if txt is not None :
            txt2 = unicodedata.normalize("NFKD", txt)
            txt2 = txt2.replace('Ã©','é')
            txt2 = txt2.replace('Å“','è')
            txt2 = txt2.replace('Ãa','ê')
            txt2 = txt2.replace("Ã ́",'ô')
            txt2 = txt2.replace('Ã ̄','ï')
            txt2 = txt2.replace('Ã®','î')
            txt2 = txt2.replace('Ã ','à')
            txt2 = txt2.replace('Ã§','ç')
            txt2 = txt2.replace('Ã»','û')
            txt2 = txt2.replace('Ã1','ù')
            txt2 = txt2.replace('â€TM',"'")
            txt2 = txt2.replace('Â ',' ')
        return txt2


    def acquire_list(self):
        """Loads and saves review url list"""

        def save_data(item):
            base_dir = self._data_root+'html/tmo/'
            filename = base_dir + item['to_website'].split('/')[-1] + '.json'
            with open(filename, 'w') as file:
                file.write(json.dumps(item))

        df_urls = pd.DataFrame()
        url_list = list()
        base_url ='https://www.timeout.fr/graffiti/v1/sites/fr-paris/search?view=complete&locale=fr-FR&what=((`node-7083`))&page_size=1000&page_number='
        for page_num in range(0,12):
            print(page_num)
            url = base_url+str(page_num+1)
            r = requests.get(url,headers={'Authorization': 'Bearer QNVHoWr0RSevFb-nUgUueoxTPKNyhgubP2StprnIoN0'})
            data = json.loads(r.text)
            for item in data['body']:
                url = item['to_website']
                df_urls = df_urls.append(
                    {
                        'url': url,
                        'filename': self.url_to_filename(url)
                    },
                    ignore_index=True)
                save_data(item)
        df_urls.to_csv(self.urls_filename(), index=False)
        return df_urls

    def acquire_pages(self):
        pass

    def parse_page(self, url, page):

        def is_tag(tag):
            if tag == 'Note de Time Out' or tag == 'Catégories' or tag == 'Prix' or re.match('^€+$', tag):
                return False
            if tag.isdigit() or tag.startswith('xx'):
                return False
            return True

        def find_rate_in_tags(tags):
            for tag in tags:
                if tag['name'].isdigit():
                    return tag['name']
            return None

        item = json.loads(page)
        result = {}
        result['origin'] = self._origin
        result['type'] = item['type']
        result['url'] = item['url']
        result['title'] = self.clean_text(item['name'])
        result['details'] = self.clean_text(item.get('annotation'))
        result['lat'] = item.get('latitude')
        result['lng'] = item.get('longitude')
        result['address'] = self.clean_text(item.get('address1', '') + ' ' + item.get('address2', '') + ' ' + item.get('city', ''))
        result['addr_details'] = {'street' : item.get('address1', ''), 'city' : item.get('city', ''), 'code' : ''}
        result['tags_json'] = json.dumps([self.clean_text(tag['name']) for tag in item['categorisation']['tags'] if is_tag(tag['name'])])
        result['rating'] = find_rate_in_tags(item['categorisation']['tags'])
        result['review_date'] = item['published_at'][:10]

        return result
