# from probsevere import ProbSevere
import json
from pprint import pprint
from glob import glob
import os
from pprint import pprint
from types import SimpleNamespace
# from sklearn.metrics.pairwise import haversine_distances
import numpy as np
from sklearn.metrics.pairwise import haversine_distances


def load(feature):
    jd = json.dumps(feature)
    # print(jd)
    return json.loads(jd, object_hook=lambda d: SimpleNamespace(**d))


        # arr.append(geometry)
# array =[[1,2,3],[1,2,3]]


# print(array[0][0])
class Storms:
    _storm = {}
    def set(self,_id=None,coordinates=None,properties=None):
        center = np.mean(np.squeeze(coordinates),axis=0)
        self._id = _id

        # self._id = self._storm[_id]

        if _id not in self._storm.keys():
            self._storm[_id]={
                'coordinates':np.array(coordinates),
                'center':np.array([center])#[center]
            }
        else:
            self._storm[_id]['center'] = np.append(self._storm[_id]['center'],[center],axis=0)
            rads = np.radians(self._storm[_id]['center'][-2:])
            D2min=haversine_distances(rads)

            self._storm[_id]['motion']=D2min* 6371000/1000 
            


       


            return None
    def getById(self,_id):
        return self._storm[_id]

stm = Storms()





samples = [
    # 'sample_data/MRMS_PROBSEVERE_20211011_000053.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000240.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000447.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000655.json'
    ]




def ready(featureCollection):
    for feature in featureCollection['features']:
        geometry = load(feature['geometry'])
        properties = load(feature['properties'])
        stm.set(_id=properties.ID,coordinates=geometry.coordinates)

for sample in samples:
    ready(json.load(open(sample)))

a = stm.getById('90077')
print(a['motion'])









def get_feats_by_id(features,_id):
    arr =[]
    for feat in features:
        if feat['properties']['ID']== _id:
            arr.append(feat)
        else:
            # print()
            pass
    return arr
        # print()


def get_sample_data(filepath, storm_id=None):
    # print(storm_id)
    with open(filepath, 'r') as f:
        fc = json.load(f)
        vt = fc['validTime']
        if storm_id is None:

        # feats = get_feats_by_id(fc['features'],'692025')

            return ProbSevere(valid_time=vt, features=fc['features'])
        else:
            feats = get_feats_by_id(fc['features'],storm_id)
            # print(feats)
            return ProbSevere(valid_time=vt,features=feats)




# for filename in glob(os.path.join('sample_data/', '*.json')):
#     ps=get_sample_data(filename, storm_id='692025')
    # pprint(ps.feature_collection)
