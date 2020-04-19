__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"

import datetime
import os
import requests
import re
import json
import urllib.parse
import parsel
import wg2.importers.base

class PudloImporter(wg2.importers.base.Importer):

    def __init__(self):
        self._origin = 'pdl'

    def acquire_list(self):
        ws_url = 'http://www.gillespudlowski.com/wp-admin/admin-ajax.php'
        ws_data = {'action': 'plusetablissement','req[PAYS]': 'France','req[type_poi]': 'Restaurants','req[type_poi_2]': '0', 'paged': 0}
        df_urls = self.load_urls()
        num_page=0
        continue_loop = True
        while continue_loop :
            ws_data['paged'] = num_page
            print ('Requesting : ',ws_data)
            r=requests.post(url = ws_url, data = ws_data)
            if r.text.strip()=='':
                continue_loop = False
            else:
                selector = parsel.Selector(r.text)
                urls_page = selector.css('h3.h3_poi>a::attr(href)').getall()
                for url in urls_page:
                    if (df_urls['url']==url).any():
                        print('Existing url : ',url)
                        continue_loop = False
                    else:
                        print('New url : ',url)
                        df_urls = df_urls.append({'url':url,'filename':self.url_to_filename(url)}, ignore_index=True)
            num_page += 1
            df_urls.to_csv(self.urls_filename(), index=False)
        df_urls.to_csv(self.urls_filename(), index=False)
        return df_urls

    def parse_page(self, url, page):
        selector = parsel.Selector(page)
        ret = {}
        ret['timestamp'] = datetime.datetime.now()
        ret['origin']=self._origin
        ret['url'] = url
        ret['title'] = selector.css('#H1_Article_Single::text').get()
        ret['ariane_tags'] = json.dumps(selector.css('#ariane-line>span>a::attr(title)').getall())
        ret['review_date'] = self.format_date(selector.css('span.date_article_time::text').get())
        coords = self.parse_coords(page)
        ret['lat'] = coords[0]
        ret['lng'] = coords[1]
        details_html=''.join(selector.css('div.entry>p').getall()).strip()
        res_re = re.split('<[^>]*>', details_html)
        ret['details']=''.join(res_re)

        street = ''
        city = ''
        for u in selector.css('span.Etab_adresse_mip_ligne>a::attr(href)').getall():
            if re.match('^http://.*',u):
                ret['official_url'] = u
        for s in selector.css('.Etab_adresse_mip_ligne'):
            if 'itemprop' in s.attrib:
                if s.attrib['itemprop'] == 'streetAddress':
                    street = s.css('::text').get()
                elif s.attrib['itemprop'] == 'addressLocality':
                    city_str = s.css('::text').get()
                    words = city_str.split(' ')
                    code = ''
                    city = ''
                    if words[0] == 'Paris':
                        art = re.sub('[erm]','', words[-1])
                        code = str(75000+int(art))
                        city = 'Paris'
                    else:
                        code = words[0]
                        city = ' '.join(words[1:])
                    ret['address'] = street + ', ' + code + ', '+city
                    ret['addr_details'] = {'street' : street, 'city' : city, 'code' : code,}
        ret['tags'] = json.dumps(selector.css('span.apropos_info_tag>a::text').getall())
        ret['categories'] = json.dumps(selector.css('span.apropos_info_cat>a::text').getall())
        if selector.css('div.icone_coeur_article').get() != None:
            ret['rating'] = 'CoupCoeur'
        elif selector.css('div.icone_gueule_article').get() != None:
            ret['rating'] = 'CoupGueule'
        else:
            ret['rating'] = ''
        return ret

    def parse_coords(self, page):
        ret = [0.,0.]
        selector = parsel.Selector(page)
        gmapurl = selector.css('iframe::attr(src)').get()
        if ( gmapurl is not None):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(gmapurl)[4])['q'][0]
            if re.match('^[\d\.]*,[\d\.\-]*$',q):
                coords_txt = q.split(',')
                ret = [float(coords_txt[0]),float(coords_txt[1])]
        return ret


    def format_date(self, datetext):
        result = ''
        date_array = []
        res = re.search("\d\d?.*\d\d\d\d",datetext)
        if res :
            date_array = res.group().split()
        if len(date_array) == 3:
            j = date_array[0]
            if len(j)==1:
                j='0'+j
            result = date_array[2]+'-'+self._month_dic.get(date_array[1])+'-'+j
        return result

    _month_dic = {'janvier' : '01' , 'février' : '02' ,'mars' : '03' ,
                 'avril' : '04' , 'mai' : '05' ,'juin' : '06' ,
                 'juillet' : '07' , 'août' : '08' ,'septembre' : '09' ,
                 'octobre' : '10' , 'novembre' : '11' ,'décembre' : '12' ,
                }
