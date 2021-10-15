import numpy as np
from sklearn.metrics.pairwise import haversine_distances


VERSION = '3.0.1'
TYPE = 'FeatureCollection'
PRODUCT = "probSevere:vectors"
SOURCE = "NOAA/NCEP Central Operations"
PRINT_DIV = '----------------\n'
PRINT_BR = '\n################\n'
# 6.3710 * 100**3
R = 6_371_000  # earth raidus in meters


class StormCache(object):
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
    # def


class NewCache():
    motion = None
    center = None
    slope = None
    storm_motion = None


nc = NewCache()


class StormVectors:
    """
    StormTrackVector maintains a persistent cachry state to itterate over previous storm
    Id's and attempts to predict the next position.
    """
    _sv = {}
    count = 0

    def _motion_slope(self, me, ms):
        a = np.array([me, ms], dtype=np.float32)
        _motion = np.multiply(a, [1, -1], dtype=np.float32)
        _slope = np.divide(*_motion[[1, 0]])
        return(_motion, _slope)

    def set_vector(self, valid_time=None, _id=None, center=None, motion_east=None, motion_south=None):

        self._id = _id
        self._center = np.array(center)
        motion, slope = self._motion_slope(motion_east, motion_south)

        if _id not in self._sv.keys():
            base_motion_vector = self._storm_motion_vector(motion)
            self._sv[_id] = {
                "motion": motion,  # self._motion,# np.array(self.motion),
                "initial_center": np.array(center),
                "center": np.array(center),
                "slope": slope,
                "base_motion_vector": base_motion_vector,
                "mean_base_vector": base_motion_vector,
                "haversine_vector": None,
                "mean_haversine": None,
                "mean_vector": None
            }

        else:
            # The stormcache class provides an api for the previous storm
            sc = StormCache(self._sv[_id])
            # storm motion forecast
            # sm_fcst = sc.storm_motion[0]
            # dM_dT = np.rollaxis(np.array([sc.motion, motion]), 1, 0)
            # prog_diff = np.diff([sc.center, center], axis=0)
            # print('diff:', np.diff([sc.center, center], axis=0), prog_diff)
            # print(f'\nstorm_motion{motion}prevcenter{sc.center}center{center}')
            #! MOTION VECTOR PROCESSING
            # ? X_MOTION = SOME.FUNC()
            # ? X_VECTOR= self._storm_motion_vector(X_MOTION)
            #! X_MOTIONS

            haversine_motion = self._haversine_mps(sc.center, center)
            #!X_VECTORS
            # ? BASE
            base_motion_vector = self._storm_motion_vector(motion)
            # ? BASE_MEAN
            mean_base_vector = np.mean(
                [base_motion_vector, sc.mean_base_vector], axis=0)
            # ? HAVERSINE
            haversine_vector = self._storm_motion_vector(
                haversine_motion)
            # ? CRUDE_PROG

            # crude_offset = np.array([0.60, 4.50, 9.00, 13.50, 18.00])
            # prog_diff = np.diff([sc.center, center], 1, 0)
            # crude_vector = np.array([center+np.multiply(prog_diff, x)
            #                          for x in np.nditer(crude_offset)]).reshape((5, 2))
            # print('crude vector', crude_vector)

            # prog_diff = np.diff([sc.center, center], axis=0)
            # prog_diff*4.5
            # crude_vector = np.multiply(haversine_vector)
            # try:
            #     mean_haversine = np.mean(
            #         [haversine_vector, sc.haversine_vector], axis=0)

            # except:
            if sc.haversine_vector is None:
                mean_haversine = haversine_vector
            else:
                mean_haversine = np.mean(
                    [haversine_vector, sc.mean_haversine], axis=0)
                print(
                    f"\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nhaversine_vector:\n{haversine_vector}\nsc.haversine_vector:\n{sc.haversine_vector}\nmean_haversine:\n{mean_haversine}\n")
                # print(f"\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n", haversine_vector, sc.haversine_vector, "!!!!!!!!!!!!!!!!!!!!!!!!!!", np.mean(
                #     [haversine_vector, sc.haversine_vector], axis=0), '\n\n')
                # mean_haversine = haversine_vector

            mean_vector = np.mean(
                [mean_base_vector, mean_haversine], axis=0)

            # storm_prog = self._storm_prog_vector(prog_diff)

            # print(f'prog_diff{prog_diff*4.5}')
            # print(f'center:{center}')
            # print(f'stormprog:{storm_prog}')

            sm_err = np.diff([sc.base_motion_vector[0], center], axis=0)
            try:
                sp_err = np.diff([*sc.storm_prog, center], axis=0)
                # print("$$$$$$$$$$$$$$$$$")
                # print(f'prev{sc.center}\ncurr{center}')

                # print("$$$$$$$$$$$$$$$$$")
            except:
                sp_err = None
            # prog_err
            # print('diff:', np.diff([sc.center, center], axis=0), )
            # change in movement change in time
            if False:
                print('base_motion_vector:\n', base_motion_vector)
                print('mean_base_vector:\n', mean_base_vector)
                print('haversine_vector:\n', haversine_vector)
                print('mean_haversine:\n', mean_haversine)
                print('mean_vector:\n', mean_vector)
                print('\n#################################\n')
                print(
                    'STORM HISTORY LOG: \nUNITS:\n pos:[longitude, latitude]\n')
                print(' ')
                print('#################################\n')
                print('STORM ID:', _id, '\nvalidtime:', valid_time)
                print('INITIAL POS:', sc.initial_center)
                # PREVIOUS STORM
                print('\nPREVIOUS STORM INFO:')
                print('POSITION:   ', sc.center)

                print('SM_FCST POS:', storm_motion)
                print('SM_FCST ERR:', sm_err)
                print('SP_FCST POS:', storm_prog)
                print('SP_FCST ERR:', sp_err)

                print('\nCURRENT STORM INFO:')
                print('POSITION:   ', np.array(center))

            self._sv[_id] = {
                "motion": motion,
                "initial_center": sc.initial_center,
                "center": np.array(center),
                "slope": slope,
                "base_motion_vector": base_motion_vector,
                "mean_base_vector": mean_base_vector,
                "haversine_vector": haversine_motion,
                "mean_haversine": mean_haversine,
                "mean_vector": mean_vector
            }
    # GET THE DISTANCE BETWEEN TWO POINTS

    def _haversine_mps(self, prev_center, center):
        # converting degs to rads
        lon1, lat1, lon2, lat2 = np.deg2rad(
            [*prev_center, *center], dtype=np.float32)
        # haversine distance storm moved south
        dSouth = haversine_distances(
            [[lat1, lon1], [lat2, lon1]])
        # haversine distance storm moved east
        dEast = haversine_distances(
            [[lat1, lon1], [lat1, lon2]])
        # correction for movment
        x = 1 if lon1 > lon2 else -1
        y = 1 if lat1 > lat2 else -1
        # returns motion south multiplied by the earths radius over time
        return np.multiply([dEast[0, 1]*x, dSouth[0, 1]*y], 637_100/120)

    def _storm_prog_vector(self, diff):
        return np.add(self._center, diff)

    def _storm_motion_vector(self, mps=None):
        print(mps)
        """

        """
        time_offset = [120, 900, 1800, 2700,
                       3600]  # mps offset for 2,15,30,45,60

        distances = [np.multiply(mps, x) for x in time_offset]

        lat, lon = self._center
        arr = []

        # for dn, de in self._offsets():
        for dn, de in distances:
            # Coordinate offsets in radians
            dLat = dn/R
            radLat = np.multiply(np.pi, lat/180)
            dLon = de/(R*np.cos(radLat))
            # OffsetPosition, decimal degrees
            latO = lat + dLat * 180/np.pi
            lonO = lon + dLon * 180/np.pi
            arr.append([latO, lonO])

        return np.array(arr)

    def _multi_line_string(self):
        mls = self._sv[self._id]
        return [
            mls['base_motion_vector'],
            mls['mean_base_vector'],
            mls['haversine_vector'],
            mls['mean_haversine'],
            mls['mean_vector']
        ]


sv = StormVectors()


class ProbSevere:
    """
    probsevere class is an API for a probsevere featurecollection

    """
    features = []

    def __init__(self, feature_collection=None, valid_time=None, features=None):
        if feature_collection is not None:
            _features = feature_collection['features']
            self._valid_time = feature_collection['validTime']
        else:
            _features = features
            self._valid_time = valid_time

        self.feature_collection = {
            'version': VERSION,
            'type': TYPE,
            'validtime': self._valid_time,
            'product': PRODUCT,
            'source': SOURCE,
            'features': self.features,
        }
        [self._reduce(feat) for feat in _features]

        return None

    def _reduce(self, feat):
        geometries = []
        # PROPS
        geom = feat['geometry']
        coordinates = geom['coordinates']
        props = feat['properties']
        props['MODELS'] = feat['models']['probsevere']['LINE01']
        # coordinates = geom['coordinates']
        # CRDS
        # lons, lats = np.rollaxis(np.array(geom['coordinates']), 2, 0)
        geometries.append(geom)

        ################################|   MEAN CENTER    |############################################

        center = np.mean(*coordinates, axis=0)

        geometries.append({
            'type': 'point',
            'coordinates': center
        })

        ################################|   MultiLineString    |############################################
        storm_id = props['ID']
        mtn_s = props['MOTION_SOUTH']
        mtn_e = props['MOTION_EAST']
        sv.set_vector(_id=storm_id, motion_east=mtn_e, valid_time=self._valid_time,
                      motion_south=mtn_s, center=center)

        geometries.append({
            'type': 'MultiLineString',
            'coordinates': sv._multi_line_string()
        })

        ################################|   PROB SEVERE POLLYGON    |############################################
        feat['geometry'] = {
            'geometries': geometries
        }

        del feat['models']
        self.features.append(feat)

        return None
