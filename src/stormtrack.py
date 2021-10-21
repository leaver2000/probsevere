import numpy as np
from stormutility import LRU, StormObject, Current
# from sklearn.metrics.pairwise import haversine_distances
# from sklearn.linear_model import LinearRegression
import average as avg
import nvector as nv
import pandas as pd
from pygc import great_circle
R = 6371000
RANGE = 10
# COMMENT COLOR CODE
# !  ATTENTION -> NEEDS DEVELOPMENT
# *  DESCRIPTION ->
# ?  INFO ->

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
    _lru = LRU(250)

    def get_storm_tracks(self, _id):
        # ? get StormObject from LRU by ID
        x = self._lru.get(_id)
        # ? get stormtrack from StormObject
        return getattr(x, 'center'), getattr(x, 'stormtrack')

    def __init__(self, feature=None, validtime=None):

        coordinates = feature.coordinates
        properties = feature.properties
        _id = feature._id
        self._id = _id

        # ? values in c are the current storm values
        # ? avaliable attributes in c are area and center
        c = Current(coordinates)  # * current object is c
        setattr(c, 'validtime', validtime)

        # ? look for the storm _id in the Least Recently Used Cache
        # ? STAGE 0: [INITALIZE STORM]
        if not self._lru.peek(_id):
            x = StormObject(_id, c)  # * initialize StormObject with C
            setattr(x, 'properties', properties)  # * set props
            setattr(x, 'validtime', validtime)
            self._lru.add(_id, x)  # * add StormObject to cache

        else:
            x = self._lru.get(_id)  # * existing StormObject()

            # ? STAGE 1: [ VALIDATE CENTER ]
            if np.any(x.center != c.center):  # * verify movement

                # ? STAGE 2: [ ]
                # * - [ TIME DELTA ]
                timeD = (c.validtime - x.validtime).total_seconds()
                # * timeD used by _azimuth_velocity()
                setattr(c, 'timeD', timeD)
                # * - [ AZIMUTH VELOCITY ]
                self._azimuth_velocity(x, c)  # ! change in

                # ? STAGE 3: [ QUANTITY CHECK ]
                if len(x.history.area) < 5:  # *

                    # ? STAGE 4a: [ AFFIX c2x ]
                    # * calculated values from c are
                    # * affixed -> set & appended 2 x
                    x.affix('validtime', validtime)
                    x.affix('center', c.center)
                    x.affix('coordinates', c.coordinates)
                    x.affix('area', c.area)

                    x.affix('azimuth', c.azimuth)
                    x.affix('velocity', c.velocity)
                    pass
                else:
                    index = np.s_[-5:]
                    # * standard_deviation = 95%
                    a_d = self._deviates('area', x, c, index=index)
                    v_d = self._deviates('velocity', x, c, index=index)
                    az_d = self._deviates('azimuth', x, c, index=index)
                    # print(az_d)

                    # ? STAGE 5: [ MAKE PREDICTION ]
                    # if not a_d and not v_d:
                    if True:

                        # ? GENERATE LINEAR STORM PLOT
                        self._extrapolate(x, c)

                        x.affix('validtime', validtime)
                        x.affix('center', c.center)
                        x.affix('coordinates', c.coordinates)
                        x.affix('area', c.area)
                        x.affix('azimuth', c.azimuth)
                        x.affix('velocity', c.velocity)
                        x.affix('stormtrack', c.stormtrack)
                    else:
                        # ! REMOVE AREA VELOCITY OUTLIERS
                        pass
                # * excessive growth in area is expected
                # * to throw off the storm track

                # CHANGE IN TIME

                # * calculate motion from previous to current pos
                # self._set_storm_motion_vector(x, c)  # ? stt val mps
                # self._set_area_change(x, c)

                # # ? STAGE 4: [ AFFIX c2x ]
                # # * calculated values from c are
                # # * affixed -> set & appended 2 x
                # x.affix('validtime', validtime)
                # x.affix('center', c.center)
                # x.affix('coordinates', c.coordinates)

            else:
                # * storm centers with no change in movement are not recorded
                pass

    def _deviates(self, key, x, c, index=np.s_[-5:], sd=0.95):
        """ 
        returns True if a current value deviates from
        from x.history beyond standard deviation threshold.

        default values:

        last=5 # last 5 history key array values.
        """

        x_val = getattr(x.history, key)  # * hst val from key
        c_val = getattr(c, key)  # * curr val from key
        # print(x_value[index])
        mean = np.mean(x_val[index])
        diff = np.diff([mean, c_val])

        return bool(diff / mean * 1 > sd)

    def _extrapolate(self, x, c):
        lon, lat = c.center
        vel_trnds = x.history.velocity[-5:]
        vel_mean = np.mean(np.append(vel_trnds, c.azimuth))

        azi_trnds = x.history.azimuth[-5:]
        azi_avg = avg.azimuth(np.append(azi_trnds, c.azimuth))

        time_deltas = [1, 900, 1800, 2700, 3600]
        timeD = np.multiply(vel_mean, time_deltas)

        gc = great_circle(distance=timeD, azimuth=azi_avg,
                          latitude=lat, longitude=lon)
        lons_lats = np.array([gc['longitude'], gc['latitude']])

        stormtrack = np.rollaxis(lons_lats, 1, 0)

        setattr(c, 'stormtrack', stormtrack)

        TEXT = f"""
                STORMID: {self._id}
VELOCITY:
 - current: {c.velocity} mps
 - mean: {vel_mean} mps
 - trends:[\n {vel_trnds}
]

AZIMUTH:
 - current: {c.azimuth}°
 - mean: {azi_avg}°
 - trends:[\n {azi_trnds}
 ]
                """
        # print(TEXT)

        pass

    def _azimuth_velocity(self, x, c):  # ? change in vector
        lonX, latX = x.center  # * x->PREVIOUS
        lonC, latC = c.center  # * c->CURRENT
        wgs84 = nv.FrameE(name='WGS84')

        pointC = wgs84.GeoPoint(  # * CURRENT CENTER POINT
            latitude=latC, longitude=lonC, z=0, degrees=True)

        pointX = wgs84.GeoPoint(  # * PREVIOUS CENTER POINT
            latitude=latX, longitude=lonX, z=0, degrees=True)

        A2B = pointX.delta_to(pointC)  # * PREVIOUS DELTA TO CURRENT
        # xD, yD, zD = A2B.pvector.ravel()
        # * velocity = DISTANCE OVER TIME DELTA
        velocity = A2B.length/c.timeD

        az = A2B.azimuth_deg
        azimuth = np.where(az > 0, az, az+360)

        setattr(c, 'velocity', velocity)
        setattr(c, 'azimuth', azimuth)

        pass
