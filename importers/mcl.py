__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"

import datetime
import os
import re
import json
import requests
import parsel
import wg2.importers.base

class MichelinImporter(wg2.importers.base.Importer):

    def __init__(self):
        self._origin = 'mcl'

    def acquire_list(self):
        url_domain = 'https://www.viamichelin.fr'
        base_url = 'https://www.viamichelin.fr/web/Recherche_Restaurants/Restaurants-France?page='
        df_urls = self.load_urls()
        nb_pages = 101
        for n_page in range(1,nb_pages):
            r=requests.get(url = base_url+str(n_page))
            if r.text.strip()!='':
                selector = parsel.Selector(r.text)
                urls_page = selector.css('div.poi-item-name>a::attr(href)').getall()
                for url in urls_page:
                    full_url = url_domain+url
                    if (df_urls['url']==full_url).any():
                        print('Existing url : ',full_url)
                    else:
                        print('New url : ',full_url)
                        df_urls = df_urls.append({'url': full_url,'filename': self.url_to_filename(url)}, ignore_index=True)
            df_urls.to_csv(self.urls_filename(), index=False)
        df_urls.to_csv(self.urls_filename(), index=False)
        return df_urls

    def parse_page(self, url, page):
        ret = {}
        ret['timestamp'] = datetime.datetime.now()
        ret['url'] = url
        ret['origin'] = self._origin
        selector = parsel.Selector(page)
        data_raw = selector.xpath('//script[@type="application/ld+json"]/text()').get()
        if (data_raw is not None):
            data_page = json.loads(data_raw)
            ret['title'] = data_page['name']
            ret['review_date'] = data_page['review']['datePublished']
            details = selector.css('div.datasheet-description::text').get()
            if details is not None:
                ret['details'] = details.strip()
            ret['address'] = selector.css('div.datasheet-infos-address>em::text').get().strip()
            ret['lat'] = data_page['geo']['latitude']
            ret['lng'] = data_page['geo']['longitude']
            ret['addr_details'] = self.parse_address(ret['address'])
            details = selector.css('.datasheet-more-infos>li>a::text').getall()
            for detail in details:
                if re.match('^http://.*',detail):
                    ret['official_url'] = detail
            tag_str = selector.css('div.datasheet-infos-cooking-type>span::text').get()
            if tag_str:
                tags = tag_str.split('|')
            rating_list = selector.css('ul.datasheet-restaurant-quotation>li>strong::text').getall()
            if len(rating_list)>0:
                ret['rating'] = rating_list[0]
                tags = tags + rating_list
            ret['tags'] = json.dumps(tags)
        return ret

    def parse_address(self, address):
        cp_mask = '\d\d\d\d\d'
        words = re.split(cp_mask, address, 1)
        street = words[0]
        city = re.sub('\d','', words[1])
        code = address[re.search(cp_mask, address).start():re.search(cp_mask, address).end()]
        return {
            'street' : street,
            'code' : code,
            'city' : city,
        }
