
import json
from pprint import pprint
from glob import glob
import os
from pprint import pprint
from types import SimpleNamespace
import numpy as np
# from stormy import Stormy
import numpy as np
from sklearn.metrics.pairwise import haversine_distances


class Stormy:
    _storm = {}

    def set(self, _id=None, coordinates=None, properties=None):
        crds = np.array(coordinates)
        center = np.mean(np.squeeze(crds), axis=0)
        # this = self._storm[_id]

        if _id not in self._storm.keys():
            self._storm[_id] = {
                'coordinates': [crds],  # np.array(coordinates),
                'center': np.array([center])  # [center]
            }

        else:
            this = self._storm[_id]
            this = {
                'coordinates': [this['coordinates'][0], crds],
                'center': np.append(this['center'], [center], axis=0),
                'motion': [self._motion(_id)]
            }
            print(this)

            return None

    def _motion(self, _id):
        rads = np.radians(self._storm[_id]['center'][-2:])
        D2min = haversine_distances(rads)
        return D2min * 6371000/1000

    def getById(self, _id):
        return self._storm[_id]

    def getAll(self):
        return self._storm

    def getFeatureCollection(self):
        return self._storm


stm = Stormy()
samples = [
    'sample_data/MRMS_PROBSEVERE_20211011_000240.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000447.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000655.json'
]


# def load(feature):
#     jd = json.dumps(feature)
#     return json.loads(jd, object_hook=lambda d: SimpleNamespace(**d))


def ready(featureCollection):
    for feature in featureCollection['features']:
        coordinates = feature['geometry']['coordinates']
        _id = feature['properties']['ID']
        stm.set(_id=_id, coordinates=coordinates)
    return stm


if __name__ == '__main__':
    arr = []
    for sample in samples:

        data = ready(json.load(open(sample)))
        allData = data.getAll()
        arr.append(allData)
        # print(allData)
        # try:
        #     print(allData['motion'])
        # except:
        #     pass

    # print(dir(data))
    # pprint()
    # for d in data.getA
    # pprint(arr)
    # try:
    #     print(d['motion'])
    # except:
    #     pass
