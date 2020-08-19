'''
    wg2 Merger
    Synopsis :
        pc.acquire_lists() :
        pc.acquire_pages() :
        pc.init_dataset() :
        pc.geocode()

'''
__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"

import logging
import json
import pandas as pd
import wg2.util.text
import wg2.util.progress_monitor
import wg2.importers.lfd
import wg2.importers.mcl
import wg2.importers.pdl
import wg2.importers.tmo
import wg2.importers.tra

class PipelineControler():

    def __init__(self):
        logging.basicConfig(
            filename='PipelineControler.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self._origins = ['lfd','mcl','pdl','tra']
        self._importers = {}
        self._importers['lfd'] = wg2.importers.lfd.FoodingImporter()
        self._importers['mcl'] = wg2.importers.mcl.MichelinImporter()
        self._importers['pdl'] = wg2.importers.pdl.PudloImporter()
        self._importers['tra'] = wg2.importers.tra.TeleramaImporter()

    def acquire_lists(self):
        for origin in self._origins:
            self._importers[origin].acquire_list()

    def acquire_pages(self):
        for origin in self._origins:
            self._importers[origin].acquire_pages()

    def init_dataset(self):
        for origin in self._origins:
            self._importers[origin].init_dataset()

    def geocode(self):
        for origin in self._origins:
            self._importers[origin].geocode()
