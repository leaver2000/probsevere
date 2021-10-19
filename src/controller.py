import requests
import numpy as np
import pandas as pd
from probsevere import ProbSevere
from pymongo import MongoClient
# from pprint import pprint
from glob import glob
import json
import os
try:
    from dotenv import dotenv_values
    env = dotenv_values('.env')
    username = env['MONGO_USER']
    password = env['MONGO_PASSWORD']
    print('mongodb username and password loaded from dotenv')
except:
    print('failed to load dotenv')
    pass
url = f"mongodb+srv://{username}:{password}@wild-blue-yonder.jy40m.mongodb.net/database?retryWrites=true&w=majority"
client = MongoClient(url)
db = client.sigmet
bp = db.baseProducts  # ? PRODUCT DIRECTORY METADATA
ps = db.probsevere  # ? PROBSEVERE COLLECTION


class Timestamps:
    pass


class State:
    initialize = False
    collect = False
    process = False
    process = False
    save = False


class Controller:
    state = State()

    validTimes = list()
    baseproduct = {
        'name': 'probsevere',
        'longName': "MRMS ProbSevere V3.01",
        'prodType': "PROBSEVERE",
        'subType': "GeoJSON",
        'validTimes': validTimes
    }

    def __init__(self):
        try:
            resp = bp.find_one({'name': 'probsevere'}, {
                               "validTimes": 1, '_id': 0})
            # self.baseproduct['_id'] = resp['_id']

            self.validTimes = np.array(resp['validTimes'])
            self.state.initialize = True

        except:
            print('reinitializing probsevere baseproduct directory')
            bp.insert_one(self.baseproduct)

        pass

    def collect(self):  # ?scrape mrms dataset for probsevere object

        # ! additional logic required to compare availiable products to database
        url = "https://mrms.ncep.noaa.gov/data/ProbSevere/PROBSEVERE/"
        query = "C=M;O=D"
        page = pd.read_html(f"{url}?{query}")
        prods = np.array(page[0][2:-1])
        files = prods[:, [0]].flatten()[0]
        res = requests.get(f'{url}{files}')
        try:
            self.initial_feature = res.json()
            self.state.collect = True
        except:
            print('controller collection error')
            self.initial_feature = None
        pass

    def validate(self):
        self.state.validate = True
        pass

    def process(self):
        # ? ProbSevere class to perform operations on JSON object
        # ? instance retures feature_collection and datetime object
        fc = ProbSevere(self.initial_feature)
        self.feature_collection = fc.feature_collection
        self.datetime = fc.datetime
        self.state.process = True
        pass

    def save(self):
        # ? baseproduct directory utility maintenance
        cleanup = self._set_valid_times(self.feature_collection)
        # ?
        validTimes = self.validTimes.tolist()
        query = {"name": "probsevere"}
        vt = {"$set": {"validTimes": validTimes}}
        bp.update_one(query, vt)  # ? updating base product directory

        if cleanup is not None:  # ? remove expired ps object
            ps.remove({"validTime": cleanup})

        ps.insert_one(self.feature_collection)  # ? create ps object
        self.state.save = True
        pass

    def _set_valid_times(self, fc):
        vt = self.validTimes
        cleanup = vt[0] if len(vt) >= 5 else None
        # ? truncating baseproduct validtime to len = 15 + 1
        self.validTimes = np.append(vt[-15:], fc['validTime'])
        return cleanup

    def test(self):
        paths = glob(os.path.join('sample_data/', '*.json'))
        paths.sort()
        for path in paths:
            feature_collection = json.load(open(path))
            fc = ProbSevere(feature_collection)
            self.feature_collection = fc.feature_collection
            self.datetime = fc.datetime

            # print(fc.feature_collection)

            # print(ps.feature_collection['features'][-1])
