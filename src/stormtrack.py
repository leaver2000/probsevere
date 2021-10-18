
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
from helpers import Object
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



class StormHistory:
    def __init__(self, validTime):
        pass

# class Object:
#     pass



class StormMotionVector:
    def __init__(self,smv):
        self.smv = smv

    def mean(self,_slice=None):
        obj = Object()
        smv = self.smv if _slice is None else self.smv[_slice:]
        obj.mps = np.mean(smv, axis=0)
        obj.kmh = np.mean(smv, axis=0) * 3.6
        obj.knots = np.mean(smv, axis=0) * 1.943844
        
        return obj


class StormTrack:
    _storm = {}
    _verbose = False
    def __init__(self):
        pass

    def set_storm(self, validTime=None, _id=None, coordinates=None, properties=None):
        crds = np.squeeze(coordinates)
        center = np.mean(crds, axis=0)
        propV = np.array(list(properties.values()))[:13]
        props = np.array(propV, dtype=np.float16)

        # * if the _storm object does not contain the _storm[_id] key a new _storm[_id] object is created
        if _id not in self._storm.keys():

            self._storm[_id] = StormHistory(validTime)  # *  initialize _storm[_id]
            x = self._storm[_id]  # *      x is given the value of _storm[_id]

            # ? first order attributes
            x.count = 1
            x.coordinates = crds
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
            x.tracks =None


        else:

            x = self._storm[_id]  # * x is set to previous _storm[_id]

            # * pass x.center and current center returns meters/second and the storm motion vector
            mps, smv = self._motion(x.center, center)

            # ? first order attributes
            x.count = x.count + 1
            x.coordinates = crds
            x.center = center
            x.props = props
            x.time['end'] = validTime

            # ? second order attributes
            x.mps = mps  # * meters per second
            x.smv = smv  # * storm motion vector

            # ? third order storm history attributes
            y = x.hst
            x.hst = {
                'centers':centers if y['centers'] is None else np.concatenate((y['centers'],[center]),axis=0),
                # 'mps': [mps] if y['mps'] is None else [*y['mps'], mps],
                'mps': [[mps]] if y['mps'] is None else np.concatenate((y['mps'],[[mps]]),axis=0), 
                # storm motion vector value in mps
                'smv': smv if y['smv'] is None else np.concatenate((y['smv'],smv),axis=0)
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
                    print(f'applying mean().mps to center\n {smv.mean().mps} mps')

                avg_smv = smv.mean().mps#np.mean(x.hst['smv'][:-RANGE+1], axis=0)
                offsets = [900,1800,2700,3600]
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
                    stormtrack.append([lat60,lon60])

                x.tracks = {
                    'center':center.tolist(),
                    'motion': mps,
                    'linear':stormtrack
                }
            else:
                x.tracks = {
                    'center':center.tolist(),
                    'motion': mps
                }
            # if False:
            #     rads = np.radians(center)
            



            #     mean_smv=smv.mean().mps
            #     time_offset = np.array([[900],[1800],[2700],[3600]])
            #     change_overtime = np.multiply(mean_smv,time_offset)
            #     print('changeover time')
            #     print(change_overtime)
            #     print(change_overtime.shape)
            #     print()
            #     Dy = np.take(change_overtime,[0,2,4,6])
            #     Dx = np.take(change_overtime,[1,3,5,7])
            #     # print(Dlats,'\n',Dlons)

            #     # print(mean_smv*3600)




            #     # D60 = np.multiply(smv.mean().mps,[900,3600])# ? X 3600 = per hour



            #     print(f'center\n{rads}')

            #     _180pi = 180 / np.pi
            #     cos = np.cos(rads[0] * np.pi/180)
            #     lats0 = rads[0] + (Dy/ R) * (_180pi)
  
            #     # lat60 = lat + (Dy / R) * (_180pi)
            #     # lon60 = lon + (Dx / R) * (_180pi) / cos
            #     # cos = np.cos(lat * np.pi/180)
            #     lat60 = rads[0] + (Dy / R) * (_180pi)
            #     lon60 = rads[1] + (Dx / R) * (_180pi) / cos
            #     print(lat60,lon60)


            #     # print(x.tracks)




            # if False:

            #     # offsets = [900, 1800, 2700, 3600]
            #     print(x.hst['smv'])

            #     # ? average speed over last {_range}
            #     avg_smv = np.mean(x.hst['smv'][:-RANGE+1], axis=0)
            #     D60 = avg_smv*3600  # ? X 3600 = per hour

            #     lat, lon = cent  # ? destructure center

            #     Dy, Dx = D60.flatten()  # ? destructure change in ( Y, X )

            #     # ! MATH
            #     _180pi = 180 / np.pi
            #     cos = np.cos(lat * np.pi/180)
            #     lat60 = lat + (Dy / R) * (_180pi)
            #     lon60 = lon + (Dx / R) * (_180pi) / cos

            #     if self._verbose:
            #         print('____________________________________________________\n')
            #         print(f'\nstorm  count\n{_id}  {x.count}\n')
            #         print(f'start pos:\n {cent}\n')
            #         print(D60, Dy, Dx)
            #         print(f'pos1hr:\n {[lat60,lon60]}')

            #     x.tracks = np.array([lat60, lon60])

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
    def getStormTracksById(self,_id):
         return self._storm[_id].tracks


    def getTracks(self, _id):
        x = self._storm[_id]
        try:
            return x.tracks
        except:
            return None
    def getById(self,_id):
        return self._storm[_id]
        # return x.mean_mps
    # def getMotion(self, _id):
    #     x = self._storm[_id]
    #     return x
        # motions



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


    def compareProps(self, _id):
        this = self._storm[_id]
        return {
            'hist': [self._ziplist(p) for p in this['propsHistory']],
            # list(*this['propsChange']),
            'trends': self._ziplist(*this['propsChange']),
            'props': self._ziplist(this['props'])  # list(this['props'])
        }
        # return self._props[_id],self._storm[_id]