
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
# from stormtrack import StormTrack
from helpers import Object, StormHistory, StormMotionVector
R = 6371000
RANGE = 10
# standard_deviation = 95%

PROPSKEYS = [
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
    'P98MLAZ'
]


class StormTrack:
    _storm = {}
    _verbose = False

    # def set_storm(self, validTime=None, _id=None, coordinates=None, properties=None):
    def storm_track(self, feature=None, validTime=None):
        coordinates = feature.coordinates
        properties = feature.properties
        _id = feature._id
        # validTime = feature.validTime

        # crds = np.squeeze(coordinates)
        center = np.mean(coordinates, axis=0)
        self.center = center
        propV = np.array(list(properties.values()))[:13]
        props = np.array(propV, dtype=np.float16)

        # * if the _storm object does not contain the _storm[_id] key a new _storm[_id] object is created
        must_init = _id not in self._storm.keys()
        if must_init:
            self._storm[_id] = StormHistory()  # *  initialize _storm[_id]
            x = self._storm[_id]  # *  x is given the value of _storm[_id]

            # ? first order attributes
            x.count = 1
            x.coordinates = coordinates
            x.center = center
            x.props = props
            x.time = {
                'start': validTime,
                'end': validTime
            }

            # ? second, third, & fouth order placeholders
            x.mps = None  # *   meters per second
            x.smv = None  # * storm motion vector
            x.hst = {
                'centers': [center],
                'mps': None,  # *  meters per second history
                'smv': None  # * storm motion vector history
            }
            x.mpsX = None  # * meters per second maX
            x.mpsN = None  # * meters per second miN
            x.mpsA = None  # * meters per second Avg
            x.tracks = {
                'center': center,
                'motion': None,
                'linear': None
            }

        else:

            x = self._storm[_id]  # * x is set to previous _storm[_id]

            # * pass x.center and current center returns meters/second and the storm motion vector
            mps, smv = self._motion(x.center, center)

            # ? first order attributes
            x.count = x.count + 1
            x.coordinates = coordinates
            x.center = center
            x.props = props
            x.time['end'] = validTime

            # ? second order attributes
            x.mps = mps  # * meters per second
            x.smv = smv  # * storm motion vector

            # ? third order storm history attributes
            y = x.hst
            x.hst = {
                'centers': centers if y['centers'] is None else np.concatenate((y['centers'], [center]), axis=0),
                # 'mps': [mps] if y['mps'] is None else [*y['mps'], mps],
                'mps': [[mps]] if y['mps'] is None else np.concatenate((y['mps'], [[mps]]), axis=0),
                # storm motion vector value in mps
                'smv': smv if y['smv'] is None else np.concatenate((y['smv'], smv), axis=0)
            }

            # ? fourth order storm history mins/max/avg
            x.mpsX = np.max(x.hst['mps'])  # * meters per second maX
            x.mpsN = np.min(x.hst['mps'])
            x.mpsA = np.mean(x.hst['mps'])

            if x.count > RANGE:
                smv = StormMotionVector(x.hst['smv'])
                if self._verbose:
                    print(f'\ncalculating storm track:\nstorm_id: {_id}')
                    print(f'current center position:\n {center}')
                    print(
                        f'applying mean().mps to center\n {smv.mean().mps} mps')

                # np.mean(x.hst['smv'][:-RANGE+1], axis=0)
                avg_smv = smv.mean().mps
                offsets = [900, 1800, 2700, 3600]
                stormtrack = []
                for offset in offsets:
                    D60 = avg_smv*offset  # ? X 3600 = per hour

                    lat, lon = center  # ? destructure center

                    Dy, Dx = D60.flatten()  # ? destructure change in ( Y, X )

                    # ! MATH
                    _180pi = 180 / np.pi
                    cos = np.cos(lat * np.pi/180)
                    lat60 = lat + (Dy / R) * (_180pi)
                    lon60 = lon + (Dx / R) * (_180pi) / cos
                    stormtrack.append([lat60, lon60])

                x.tracks = {
                    'center': center,
                    'motion': mps,
                    'linear': stormtrack
                }
            else:
                x.tracks = {
                    'center': center,
                    'motion': mps,
                    'linear': None
                }

            if self._verbose:
                try:
                    print(f'\n{x.center}')
                    print(f'{x.mps} mps')
                    print(f'{x.tracks} tracks')
                except:
                    print(f'no tracks count = {x.count}')
                    pass

    def _motion(self, start, stop):
        # * positional diffrence
        diff = np.diff([start, stop], axis=0)

        # ? y diff value == negative ? the storm moved south: north
        # ? x diff value == negative ? the storm moved west: east
        vector = np.where(diff > 0, 1, -1)

        mps = distance.distance(*np.flip([start, stop])).meters / 120
        rads = np.radians([start, stop])
        # * haversine distance between 2 points
        # # convert 2 min to second
        # # radians per second

        result = np.add(*haversine_distances(rads))
        # multiply by Earth radius to get kilometers

        motion = result * 6371000 / 120
        storm_motion_vector = np.multiply(motion, vector)

        return mps, storm_motion_vector

    def getGeometryCollection(self, _id):
        x = self._storm[_id].tracks

        return x['center'], x['linear']
