__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, freedom Partners"
__email__ = "fm@freedom-partners.com"

import unicodedata

def normalize(text):
    txt = text
    ret = unicodedata.normalize('NFKD', txt).encode('ascii', 'ignore').decode()
    return ret.lower()
