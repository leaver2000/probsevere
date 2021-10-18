import numpy as np
from sklearn.metrics.pairwise import haversine_distances
import json
from probsevere import ProbSevere
from pprint import pprint
from glob import glob
import os

# controller
# from urllib import request
from urllib import request
import requests
from datetime import datetime
import pandas as pd
import re
keys = [
    'MUCAPE',
    'MLCAPE',
    'MLCIN',
    'EBSHEAR',  # EFFECTIVE BULK SHEAR
    'SRH01KM',
    'MEANWIND_1-3kmAGL',
    'MESH',  # maximum estimated size of hail
    'VIL_DENSITY',
    'FLASH_RATE',
    'FLASH_DENSITY',
    'MAXLLAZ',
    'P98LLAZ',
    'P98MLAZ',
]

class Controller:

    def __init__(self):
        pass

    def collect (self):
        url = f"https://mrms.ncep.noaa.gov/data/ProbSevere/PROBSEVERE/"
        query = "?C=M;O=D"
        page = pd.read_html(url+query)
        prods = np.array(page[0][2:-1])
        files = prods[:, [0]].flatten()[0]
        resp = requests.get(url=url+files).json()
        self.feature_collection = resp
    
    def process(self):
        ps = ProbSevere(self.feature_collection)
        print(ps.feature_collection)

        pass












if False:
# if __name__ == '__main__':
    ctrl = Controller()
    ctrl.collect()
    ctrl.process()

    pass

if __name__ == '__main__':
# if False:

    paths = glob(os.path.join('sample_data/', '*.json'))
    paths.sort()


    for path in paths:
        # print(path)
        feature_collection = json.load(open(path))
        ps = ProbSevere(feature_collection)


