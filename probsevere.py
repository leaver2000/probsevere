import numpy as np
# from pprint import pprint
VERSION = '3.0.1'
TYPE = 'FeatureCollection'
PRODUCT = "probSevere:vectors"
SOURCE = "NOAA/NCEP Central Operations"
PRINT_DIV ='----------------\n'
PRINT_BR ='\n################\n'

class StormVectors:
    """
    StormTrackVector maintains a persistent memory state to itterate over previous storm
    Id's and attempts to predict the next position.
    """
    _stv = {}
    count = 0
    def _motion_slope(self,me,ms):
        a = np.array([me,ms],dtype=np.float32)
        _motion = np.multiply(a,[1,-1],dtype=np.float32)
        _slope=np.divide(*_motion[[1,0]])
        return(_motion,_slope)

    def set_vector(self, _id=None, center=None, motion_east=None, motion_south=None):
        self._id = _id
        self._center = center
        motion,slope=self._motion_slope(motion_east,motion_south)

        # self._motion = motion
        # self._slope = slope


        

        if _id in self._stv.keys():

            _prevS= self._stv[_id]
            
            # previous _mps_correction prog
            # _vs = self._predictions()
            sm_fcst=_prevS["storm_motion"][0]
            predicition =np.array([sm_fcst,center])
            
            diff = np.diff(predicition,axis=0)
            dM_dT = np.rollaxis(np.array([_prevS["motion"],motion]), 1, 0)



            # change in movement change in time
            print('[lon,lat]')
            print(f'{sm_fcst}#expected\n{center}#actual')
            print(f'{diff}#diff' )
            print(f'{PRINT_DIV}[[mpsE,mpsN]#previous\n [mpsE,mpsN]]#current')
            print(dM_dT)
            # storm motion change
            print('2 min change in motion_vector:mps')
            print(np.diff(dM_dT).reshape(1,2))
            print(PRINT_BR)

            self._stv[_id] = {
                "motion": motion,#self._motion,#np.array(self.motion),
                # "changeInMotion":np.diff(dM_dT),
                "center": center,
                "slope": slope,
                "storm_motion": self._mps_correction(motion,)
            }

        else:
            self._stv[_id] = {
                "motion":motion,#self._motion,# np.array(self.motion),
                "center": center,
                "slope": slope,
                "storm_motion": self._mps_correction(motion)
            }
    def _predictions(self):
        pass
    # def _offsets(self):
    #     time_offset = [120, 900, 1800, 2700, 3600]  # mps offset for 15,30,45,60
    #     return[np.multiply(self._motion, x) for x in time_offset]

    def _mps_correction(self,mps=None):
        """
        
        """
        time_offset = [120, 900, 1800, 2700, 3600]  # mps offset for 15,30,45,60
        # offsets=[np.multiply(self._motion, x) for x in time_offset]
        offsets=[np.multiply(mps, x) for x in time_offset]

        lat, lon = self._center
        arr = []
        R = 6378137
        # for dn, de in self._offsets():
        for dn, de in offsets:
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
        return [mls['storm_motion']]


sv = StormVectors()


class ProbSevere:
    """
    probsevere class is an API for a probsevere featurecollection

    """
    _features = []

    def __init__(self, valid_time=None, features=None):
        self.feature_collection = {
            'version': VERSION,
            'type': TYPE,
            'validtime': valid_time,
            'product': PRODUCT,
            'source': SOURCE,
            'features': self._features,
        }
        [self._reduce(feat) for feat in features]

        return None

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
        sv.set_vector(_id=storm_id, motion_east=mtn_e,
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
        self._features.append(feat)

        return None
