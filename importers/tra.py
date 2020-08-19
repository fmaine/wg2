__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"

import datetime
import locale
import os
import re
import json
import requests
import parsel
import wg2.importers.base

class TeleramaImporter(wg2.importers.base.Importer):

    def __init__(self):
        self._origin = 'tra'
        self._pm.name(self._origin)

    def acquire_list(self):
        url_domain = 'https://sortir.telerama.fr'
        base_url = 'https://sortir.telerama.fr/listes/restos?page='
        df_urls = self.load_urls()
        nb_pages = 122
        for n_page in range(1,nb_pages):
            r=requests.get(url = base_url+str(n_page))
            if r.text.strip()!='':
                selector = parsel.Selector(r.text)
                urls_page = selector.css('h3.item--title > a::attr(href)').getall()
                for url in urls_page:
                    full_url = url_domain+url
                    if (df_urls['url']==full_url).any():
                        logging.info('Existing url : ' + full_url)
                    else:
                        logging.info('New url : ' + full_url)
                        df_urls = df_urls.append({'url': full_url,'filename': self.url_to_filename(url)}, ignore_index=True)
            df_urls.to_csv(self.urls_filename(), index=False)
        df_urls.to_csv(self.urls_filename(), index=False)
        return df_urls

    def parse_page(self, url, page):
        result = {}
        selector = parsel.Selector(page)
        title = selector.css('h1.fiche--title::text').get()
        if (title is not None):
            result['timestamp'] = datetime.datetime.now()
            result['origin']=self._origin
            result['url'] = url
            result['title'] = title.strip()
            result['official_url'] = selector.css('li.fiche--url>a::text').get()
            result['details'] = ' '.join(selector.css('div.fiche--wysiwyg::text').getall()).strip()
            result['details'] = result['details'] + ''.join(selector.css('div.fiche--wysiwyg>p::text').getall()).strip()
            result['lat'] = 0.0
            result['lng'] = 0.0
            if len(selector.css('p.fiche--adressbudget>span::text').getall())>1:
                result['address'] = selector.css('p.fiche--adressbudget>span::text').getall()[1].strip()
            else:
                result['address'] = ''
            result['addr_details'] = self.parse_address(result['address'])
            footer = selector.css('.fiche--footnotes>p').getall()
            dates_text = re.findall('\d+ [^0-9]* \d\d\d\d',footer[-1])
            if len(dates_text) > 0:
                locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
                DATE_FORMAT = "%d %B %Y"
                result['review_date'] = datetime.datetime.strptime(dates_text[0], DATE_FORMAT)
            result['tags_json'] = json.dumps(selector.css('div.fiche--tags>ul>li>a::text').getall())
            result['tags'] = selector.css('div.fiche--tags>ul>li>a::text').getall()
            result['rating'] = selector.css('p.rating--tra>span::text').get().strip()
        return result

    def parse_address(self, address):
        words = address.split(' ')
        if words[-1] == 'France':
            words.pop(-1)
        if address=='' or len(words)<2:
            return {
                'street' : address,
                'city' : '',
                'code' : '',
            }
        else:
            cp_mask = re.compile('\d\d\d\d\d')
            if cp_mask.match(words[-2]):
                return {
                    'street' : ' '.join(words[:-2]),
                    'city' : words[-1],
                    'code' : words[-2],
                }
            else:
                 return {
                    'street' : ' '.join(words[:-1]),
                    'city' : words[-1],
                    'code' : '',
                }
