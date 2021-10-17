import numpy as np
from sklearn.metrics.pairwise import haversine_distances
import json
from probsevere import ProbSevere
from pprint import pprint
samples = [
    # 'sample_data/MRMS_PROBSEVERE_20211011_000053.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000240.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000447.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000655.json'
]


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


class History:
    tory = []

    def __init__(self):
        pass

    def set(self, _id):
        print(_id)


hst = History()

if __name__ == '__main__':
    # print('hello')

    for sample in samples:
        featureCollection = json.load(open(sample))
        # print(feature['validTime'])
        validTime = featureCollection['validTime']
        for feature in featureCollection['features']:
            _id = feature['properties']['ID']
            coordinates = feature['geometry']['coordinates']
            b = np.array(list(zip([_id], coordinates)))
            # c = np.vstack(([(_id)], np.array(coordinates)))
            # print(np.hstack((_id, [(2)])))

            # print(x['_id'] == [_id])
            x = np.array([(_id, validTime, np.array(coordinates, dtype='object'))],
                         dtype=[('_id', 'U10'), ('validtime', 'U15'), ('coordinates', list)], )

            # b = np.stack([[_id], coordinates], axis=0)
            # # setattr(b, 'stuff', 'stff')
            # print(b)
