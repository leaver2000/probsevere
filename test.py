from probsevere import ProbSevere
import json
from pprint import pprint
from glob import glob
import os
from pprint import pprint


def get_feats_by_id(features,_id):
    arr =[]
    for feat in features:
        if feat['properties']['ID']== _id:
            arr.append(feat)
        else:
            pass
    return arr
        # print()


def get_sample_data(filepath):
    with open(filepath, 'r') as f:
        fc = json.load(f)
        vt = fc['validTime']
        feats = get_feats_by_id(fc['features'],'692025')
        return ProbSevere(valid_time=vt, features=feats)



    # print(feats)
    # pprint(feats)


for filename in glob(os.path.join('sample_data/', '*.json')):
    ps = get_sample_data(filename)
    # pprint(ps.feature_collection)
    # print(filename)

# features = ps.feature_collection['features']
# print(features)
    # print(feats[0])
    # for feat in feats:
    #     print(feat)

#     ps = ProbSevere(valid_time=vt, features=feats
# 
# print(features)