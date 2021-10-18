
import json
from types import SimpleNamespace
import numpy as np
from numpy.core.arrayprint import _make_options_dict
from sklearn.metrics.pairwise import haversine_distances
from sklearn.linear_model import LinearRegression
from geopy import Point, distance
# from geopy import Point
# from geopy.distance import distance, VincentyDistance
from pprint import pprint
from datetime import datetime
import re
R = 6371000
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


class History:
    def __init__(self, validTime):
        # print(validTime)
        pass


class Storms:
    _storm = {}
    _verbose = False

    def set(self, validTime=None, _id=None, coordinates=None, properties=None):
        coordinates = np.squeeze(coordinates)
        center = np.mean(coordinates, axis=0)
        p = np.array(list(properties.values()))[:13]
        props = np.array(p, dtype=np.float16)

        if _id not in self._storm.keys():
            self._storm[_id] = History(validTime)
            x = self._storm[_id]

            # ? first order attributes
            x.count = 1
            x.coordinates = coordinates
            x.center = center
            x.props = props

            # ? second/third order placeholders
            x.mps = None
            x.smv = None
            x.hst = {
                'mps': None,
                'smv': None
            }

        else:
            # * set x to previous storm attributes
            x = self._storm[_id]

            # * pass x.center and current center to return meters/second and storm motion vector
            mps, smv = self._motion(x.center, center)

            # ? first order attributes
            x.count = x.count + 1
            x.coordinates = coordinates
            x.center = center
            x.props = props

            # ? second order attributes
            x.mps = mps  # * meters per second
            x.smv = smv  # * storm motion vector

            # ? third order storm history attributes
            y = x.hst
            x.hst = {
                'mps': [mps] if y['smv'] is None else [*y['mps'], mps],
                'smv': [smv] if y['smv'] is None else [*y['smv'], smv]
            }
            _range = 5
            if x.count > _range:
                # offsets = [900, 1800, 2700, 3600]

                # ? average speed over last {_range}
                avg_smv = np.mean(x.hst['smv'][:-_range+1], axis=0)
                D60 = avg_smv*3600  # ? X 3600 = per hour

                lat, lon = center  # ? destructure center

                Dy, Dx = D60.flatten()  # ? destructure change in ( Y, X )

                # ! MATH
                _180pi = 180 / np.pi
                cos = np.cos(lat * np.pi/180)
                lat60 = lat + (Dy / R) * (_180pi)
                lon60 = lon + (Dx / R) * (_180pi) / cos

                if self._verbose:
                    print('____________________________________________________\n')
                    print(f'\nstorm  count\n{_id}  {x.count}\n')
                    print(f'start pos:\n {center}\n')
                    print(D60, Dy, Dx)
                    print(f'pos1hr:\n {[lat60,lon60]}')

                x.tracks = np.array([lat60, lon60])

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
        if False:
            print(f'\nstart position:\n {start}')
            print(f'stop position:\n {stop}')
            print(f'diffrence:\n {diff}')
            print(f'speed:\n {mps} mps')
            print(
                f'storm motion vector:\n   x           y\n{storm_motion_vector}')

        return mps, storm_motion_vector

    def getTracks(self, _id):
        x = self._storm[_id]
        try:
            return x.tracks
        except:
            return None

    def getMotion(self, _id):
        x = self._storm[_id]
        try:
            return (x.center, x.mps, x.tracks)
        except:
            return None

    def _ziplist(self, props):
        result = zip(PROPSKEYS, props)
        return list(result)

    def getCollection(self):
        # this = self._storm[_id]
        [self._reduce(_id) for _id in self._storm]
        # print(features)

    def _reduce(self, _id):
        this = self._storm[_id]
        try:
            print(this['motion'])

        except:
            pass
        # print()
        # return {
        #     'coordinates':list(this['coordinates'])

        # }

        # return self._storm

    def getById(self, _id):
        return self._storm[_id]

    def compareProps(self, _id):
        this = self._storm[_id]
        return {
            'hist': [self._ziplist(p) for p in this['propsHistory']],
            # list(*this['propsChange']),
            'trends': self._ziplist(*this['propsChange']),
            'props': self._ziplist(this['props'])  # list(this['props'])
        }
        # return self._props[_id],self._storm[_id]


storm = Storms()


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
    'MAXRC_EMISS',
    'MAXRC_ICECF',
    'WETBULB_0C_HGT',
    'PWAT',  # PRECIPIPITABLE WATER
    'CAPE_M10M30',
    'LJA', 'SIZE', 'AVG_BEAM_HGT', 'MOTION_EAST', 'MOTION_SOUTH', 'PS', 'ID']


class ProbSevere:
    def __init__(self, features):
        x = self._load(features)
        b = datetime.strptime(x.validTime[:-4], '%Y%m%d_%H%M%S')
        # print()
        if b.minute % 10 == 0:
            print(x.validTime)
        for feature in features['features']:
            coordinates = self._load(feature['geometry']['coordinates'])
            properties = feature['properties']
            _id = properties['ID']
            # properties = self._load(feature['properties'])

            # print(list(props.keys())[-7])
            # b = list(props.values())
            # print(np.array(b)[:-7])
            # print

            storm.set(_id=_id, validTime=x.validTime,
                      coordinates=coordinates, properties=properties)
            motion = storm.getMotion(_id)
            # print(tracks)
            if motion is not None:
                center, mps, tracks = motion
                if int(properties['PS']) > 40:
                    print(f'\nstormId: {_id}')
                    print(f'probSevere: {properties["PS"]}%')
                    print(f'start:\n {center}')
                    print(f'mps:\n {mps}')
                    print(f'knots:\n {mps*1.94384}')
                    print(f'coordinates @ 1hr:\n {tracks}')
                    # print()
                    # print(f'{center}\n{mps}\n{tracks}')

        self.storms = storm
        pass

    def _load(self, feature):
        jd = json.dumps(feature)
        return json.loads(jd, object_hook=lambda d: SimpleNamespace(**d))
