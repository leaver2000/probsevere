
import json
from types import SimpleNamespace
import numpy as np
# from numpy.core.arrayprint import _make_options_dict
from sklearn.metrics.pairwise import haversine_distances
from sklearn.linear_model import LinearRegression
from geopy import distance
# from geopy import Point
# from geopy.distance import distance, VincentyDistance
from pprint import pprint
from datetime import datetime
from stormtrack import StormTrack
from helpers import ReduceObject



st = StormTrack()


class ProbSevere:
    def __init__(self, features):

        # self._reduce_features(features)
        x = ReduceObject(features, delete='models')

        print(f'initalizing new probsevere {x.validTime} UTC')
        print(x.validTime.minute)



        self.features =[]
        for feature in x.features:
            coordinates = feature['geometry']['coordinates']
            properties = feature['properties']
            _id = properties['ID']
            st.set_storm(_id=_id, validTime=x.validTime, coordinates=coordinates, properties=properties)
            tracks = st.getStormTracksById(_id)
            if tracks is not None:
                print(tracks)
                pass
 

            if False:
                center, mps, tracks = motion
                # if int(properties['PS']) > 20:
                feature['models']['probtrack'] = {
                    'center': [center.tolist()],
                    'linear': [tracks.tolist()]
                }
                print(feature)

                # pprint(feature['models'])
                if True:

                    print(f'\nstormId: {_id}')
                    # print(st.time)
                    print(f'probSevere: {properties["PS"]}%')
                    print(f'start:\n {center}')
                    print(f'mps:\n {mps}')
                    print(f'knots:\n {mps*1.94384}')
                    print(f'coordinates @ 1hr:\n {tracks.tolist()}')

        self.feature_collection ={
            'validTime': x.validTime,
            'features': self.features
        }

    def _reduce_features(self,features):
        for feature in features['features']:
            del feature['models']
        self.feature_collection = features

    def _set_track(self):
        pass


    def _load(self, feature):
        jd = json.dumps(feature)
        return json.loads(jd, object_hook=lambda d: SimpleNamespace(**d))
