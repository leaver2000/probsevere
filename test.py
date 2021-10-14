from probsevere import ProbSevere
import json
from pprint import pprint
from glob import glob
import os
from pprint import pprint
from types import SimpleNamespace



def load(feature):
    jd = json.dumps(feature)
    print(jd)
    return json.loads(jd, object_hook=lambda d: SimpleNamespace(**d))


# ? schedule itterator to run every 8 mins
def ready(featureCollection):
    for feature in featureCollection['features']:
        print()
        geometry = load(feature['geometry'])
        properties = load(feature['properties'])
        print(geometry.coordinates,'\n',properties.ID)
        


ready(json.load(open('sample_data/MRMS_PROBSEVERE_20210925_144634.json')))

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
