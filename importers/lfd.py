'''
    Le Fooding Importer
    Imports le fooding reviews
'''

__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"


import datetime
import re
import json
import xmltodict
import requests
import parsel
import pandas as pd
import wg2.importers.base


class FoodingImporter(wg2.importers.base.Importer):
    """FoodingImporter"""

    def __init__(self):
        self._origin = 'lfd'

    def acquire_list(self):
        """Loads and saves review url list"""
        df_urls = pd.DataFrame()
        res = requests.get('https://lefooding.com/sitemap.xml')
        sitemap = xmltodict.parse(res.text)
        for item in sitemap['urlset']['url']:
            url = item['loc']
            if re.match("https://lefooding.com/fr/restaurants/.+", url):
                        df_urls = df_urls.append(
                            {
                                'url': url,
                                'filename': self.url_to_filename(url)
                            },
                            ignore_index=True)
        df_urls.to_csv(self.urls_filename(), index=False)
        return df_urls

    def parse_page(self, url, page):
        selector = parsel.Selector(page)
        result = {}
        map_data = selector.css('div#mymap::attr(data-marker)').get()
        if map_data is not None:
            data = json.loads(map_data)
            result['origin'] = self._origin
            result['title'] = data['name']
            result['url'] = url
            result['official_url'] = data['website']
            result['details'] = selector.css('section div.fragment-text > p::text').get().strip()
#            result['address'] = ' '.join(item.strip() for item in selector.css('div.adr > div[itemprop]::text').getall())
            address_data = data.get('address')
            if address_data :
                result['address'] = ' '.join([address_data.get('street_name_1'),address_data.get('street_name_2'),address_data.get('postal_code'),address_data.get('city')])
                result['review_date'] = address_data.get('updated_at')
                coords = address_data.get('position')
                if coords is not None :
                    result['lat'] = coords[0]
                    result['lng'] = coords[1]
            result['tags_json'] = json.dumps([tag.strip() for tag in selector.css('span.place-tag-list > a > span[itemProp]::text').getall()])
        return result
