import numpy as np
# from pprint import pprint
VERSION = '3.0.1'
TYPE = 'FeatureCollection'
PRODUCT = "probSevere:vectors"
SOURCE = "NOAA/NCEP Central Operations"


class StormTrackVector:
    """
    StormTrackVector maintains a persistent memory state to itterate over previous storm
    Id's and attempts to predict the next position.
    """
    _stv = {}

    def set_vector(self, _id=None, center=None, motion_east=None, motion_south=None):
        self._id = _id
        self._center = center
        me = float(motion_east)
        # convert motion south to motion north
        mn = np.multiply(float(motion_south), -1)
        self.motion = np.array([me, mn])
        slope = np.divide(mn, me)

        if _id in self._stv.keys():
            # additional development
            # is required to apply
            # a correction to the
            # expected vector based
            # on the previous deviation
            pass

        else:
            self._stv[_id] = {
                "motion": self.motion,
                "center": center,
                "slope": slope,
                "vector_space": self._space()
            }

    def _offsets(self):
        time_offset = [900, 1800, 2700, 3600]  # mps offset for 15,30,45,60
        return[np.multiply(self.motion, x) for x in time_offset]

    def _space(self):
        lat, lon = self._center
        arr = []
        R = 6378137
        for dn, de in self._offsets():
            # Coordinate offsets in radians
            dLat = dn/R
            radLat = np.multiply(np.pi, lat/180)
            dLon = de/(R*np.cos(radLat))
            # OffsetPosition, decimal degrees
            latO = lat + dLat * 180/np.pi
            lonO = lon + dLon * 180/np.pi
            arr.append([latO, lonO])
        return arr

    def _multi_line_string(self):
        mls = self._stv[self._id]
        return [mls['vector_space']]


stv = StormTrackVector()


class ProbSevere:
    """
    probsevere class is an API for a probsevere featurecollection

    """
    features = []

    def __init__(self, valid_time=None, features=None):
        self.feature_collection = {
            'version': VERSION,
            'type': TYPE,
            'validtime': valid_time,
            'product': PRODUCT,
            'source': SOURCE,
            'features': features,
        }
        for feat in features:
            self._reduce(feat)
        return

    def _reduce(self, feat):
        geometries = []
        # PROPS
        geom = feat['geometry']
        props = feat['properties']
        props['MODELS'] = feat['models']['probsevere']['LINE01']
        # CRDS
        lons, lats = np.rollaxis(np.array(geom['coordinates']), 2, 0)
        geometries.append(geom)

        ################################|   MEAN CENTER    |############################################
        center = [np.mean(lons), np.mean(lats)]
        geometries.append({
            'type': 'point',
            'coordinates': center
        })

        ################################|   MultiLineString    |############################################
        storm_id = props['ID']
        mtn_s = props['MOTION_SOUTH']
        mtn_e = props['MOTION_EAST']
        stv.set_vector(_id=storm_id, motion_east=mtn_e,
                       motion_south=mtn_s, center=center)

        geometries.append({
            'type': 'MultiLineString',
            'coordinates': stv._multi_line_string()
        })

        ################################|   PROB SEVERE POLLYGON    |############################################
        feat['geometry'] = {
            'geometries': geometries
        }

        del feat['models']
        self.features.append(feat)

        return None
