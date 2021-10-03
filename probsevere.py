import numpy as np
# from pprint import pprint
VERSION = '3.0.1'
TYPE = 'FeatureCollection'
PRODUCT = "probSevere:vectors"
SOURCE = "NOAA/NCEP Central Operations"
PRINT_DIV ='----------------\n'
PRINT_BR ='\n################\n'
R = 6378137
class StormCache(object):
    def __init__(self, my_dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])
    # def
  
class NewCache():
    motion=None
    center=None
    slope=None
    storm_motion=None


    
nc=NewCache()
class StormVectors:
    """
    StormTrackVector maintains a persistent cachry state to itterate over previous storm
    Id's and attempts to predict the next position.
    """
    _sv = {}
    count = 0
    def _motion_slope(self,me,ms):
        a = np.array([me,ms],dtype=np.float32)
        _motion = np.multiply(a,[1,-1],dtype=np.float32)
        _slope=np.divide(*_motion[[1,0]])
        return(_motion,_slope)

    def set_vector(self, valid_time=None,_id=None, center=None, motion_east=None, motion_south=None):
        
        self._id = _id
        self._center = center
        motion,slope=self._motion_slope(motion_east,motion_south)

        if _id not in self._sv.keys():
            self._sv[_id] = {
                "motion":motion,#self._motion,# np.array(self.motion),
                "initial_center":center,
                "center": center,
                "slope": slope,
                "storm_motion": self._mps_correction(motion),
                "storm_prog":None
            }
        else:
            # The stormcache class provides an api for the previous storm
            sc = StormCache(self._sv[_id])
            # storm motion forecast
            sm_fcst=sc.storm_motion[0]
            # forecast err
            
            
            dM_dT = np.rollaxis(np.array([sc.motion,motion]), 1, 0)
            prog_diff =np.diff([sc.center,center],1,0)
            storm_prog=np.add(center,prog_diff)
            storm_motion=self._mps_correction(motion)
            # determine err
            sm_err = np.diff([sc.storm_motion[0],center],axis=0)
            # sp_err = np.diff([sc.storm_prog,center],axis=0)


      



            # change in movement change in time
            print('STORM HISTORY LOG: \nunits:POS:[Longitude, latitude]\n')
            print('STORM ID:', _id, '\nvalidtime:',valid_time)
            print('INITIAL POS:',sc.initial_center )
            # PREVIOUS STORM
            print('\nPREVIOUS STORM INFO:')
            print('POSITION:   ',sc.center )
            print('SM_FCST POS:',sc.storm_motion[0] )
            print('SP_FCST POS:',sc.storm_prog )
            #CURRENT STORM
            print('\nCURRENT STORM INFO:')
            print('POSITION:   ',center)
            print('SM_FCST POS:',storm_motion[0] )
            print('SP_FCST POS:',*storm_prog )
            print('SM_FCST ERR:',fcst_err)
            print('STMPRG FCST:',storm_prog)
            
            # print()
            ##############################

    
            print(f'{PRINT_DIV}[[mpsE,mpsN]#previous\n [mpsE,mpsN]]#current')
            print(dM_dT)
            # # storm motion change
            print('2 min change in motion_vector:mps')
            print(np.diff(dM_dT).reshape(1,2))
            print(PRINT_BR)
            print()
            # print('change!!',self._storm_prog(sc.center,center),'\n',)

            self._sv[_id] = {
                "motion": motion,
                "initial_center": sc.initial_center,
                "center": center,
                "slope": slope,
                "storm_motion": storm_motion,
                "storm_prog":storm_prog
            }
    # GET THE DISTANCE BETWEEN TWO POINTS
    def _crds_distance(self,crds1,crds2):
        lat1 = np.radians(crds1[0])
        lon1 = np.radians(crds1[1])
        lat2 = np.radians(crds2[0])
        lon2 = np.radians(crds2[1])


        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        distance = R * c
        return distance
        print("Result:", distance)
        print("Should be:", 278.546, "km")


    def _mps_correction(self,mps=None):
        """
        
        """
        time_offset = [120, 900, 1800, 2700, 3600]  # mps offset for 2,15,30,45,60

        distances=[np.multiply(mps, x) for x in time_offset]

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
        return arr

    def _multi_line_string(self):
        mls = self._sv[self._id]
        return [mls['storm_motion']]


sv = StormVectors()


class ProbSevere:
    """
    probsevere class is an API for a probsevere featurecollection

    """
    features = []

    def __init__(self, feature_collection=None,valid_time=None, features=None):
        if feature_collection is not None:
            _features =  feature_collection['features']
            self._valid_time = feature_collection['validTime']
        else:
            _features = features
            self._valid_time= valid_time

        # print(_valid_time,'\n')
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
