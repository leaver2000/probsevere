
import json
from types import SimpleNamespace
import numpy as np
from sklearn.metrics.pairwise import haversine_distances
from sklearn.linear_model import LinearRegression
from geopy import distance
from pprint import pprint
from datetime import datetime
import re
PROPSKEYS =[
    'MUCAPE',
    'MLCAPE',
    'MLCIN', 
    'EBSHEAR',#EFFECTIVE BULK SHEAR
    'SRH01KM',
    'MEANWIND_1-3kmAGL',
    'MESH',#maximum estimated size of hail
    'VIL_DENSITY',
    'FLASH_RATE',
    'FLASH_DENSITY',
    'MAXLLAZ',
    'P98LLAZ',
    'P98MLAZ'
]
class AsClass:
    def __init__(self,dict):
        for key in dict.keys():
            setattr(self,key,dict[key])

class Storms:
    _storm = {}
    _props={}
    def set(self,validTime=None,_id=None,coordinates=None,properties=None):
        coordinates=np.squeeze(coordinates)
        center = np.mean(coordinates,axis=0)
        p = np.array(list(properties.values()))[:13]
        props =np.array(p,dtype=np.float16)
        
        if _id not in self._storm.keys():
            self._props[_id] = props
            self._storm[_id]={
                'count':1,
                'coordinates':coordinates,
                'center':center,
                'props':props,
                'motion':{
                    'mps':None
                },
                'history':{
                    'props':[props],
                    'centers':[center],
                    'mps':np.array([]),
                    # 'smv':np.array([])
                }
            }
        else:
            that = self._storm[_id]
            hist = that['history']
            mps,smv =self._motion(that['center'], center)
            # avgmps = 
            lp = self._linearProg(center,smv)



            self._storm[_id]={
                'count': that['count']+1,
                'coordinates':coordinates,
                'center':center,
                'props':props,
                'mps':mps,
                'motion':smv,
                'stormTracks':{
                    'linear':lp
                },
                'change':{
                    'props':np.diff([hist['props'][-1],props],axis=0)
                },
                'history':{
                    'props':np.append(hist['props'],[props],axis=0),
                    'centers':np.append(hist['centers'],[center],axis=0),
                    'mps':np.append(hist['mps'],[mps],axis=0),
                    'smv': [smv] if len(hist['mps']) == 0 else np.concatenate((hist['mps'], [mps]), axis=0)
                }
            }
            # print(smv)
            this = self._storm[_id]
            # count = this['count']
            thisHist = this['history']
            thisChng = this['change']
            thisTracks = this['stormTracks']
            Dmps = np.diff(thisHist['mps'])

            # ###############
            storm = AsClass(self._storm[_id])
            # print(ac.count)
            if storm.count > 10:
                print(f'\n storm:\n {_id}')
                hst = AsClass(storm.history)
                # print(f'{hst.smv.shape()}')
                # b = np.reshape(hst.smv)
                # hst.smv.reshape()
                # print([smv])
                # print(col.history)

            #     print(_id,count)


            # if
            # print(len(thisHist['smv']))



            return None
    # def get_
    def _linearProg(self,center,smv):
        if False:
            print('\ncenter:\n',center,'\nsmv:\n',smv)
            print(smv*120)
        # centerRads = np.radians(center)
        # motion is meters/p 2min
        # print(Dcrds)
        # radsOffset = np.multiply(centerRads,(Dcrds*3600))
        # print(center, radsOffset* 6371000/1000)
        return None


    # def _speed(self)



    def _motion(self,start,stop):# start and stop center points for a single storm ID over 2 min span
        # get the diffrence in postion
        diff = np.diff([start,stop],axis=0)
        # if the diff y value is neagtive the storm moved south
        # if the diff x value is neagtive the storm moved west
        vector = np.where(diff>0,1,-1)

        mps = distance.distance(*np.flip([start,stop])).meters / 120
        rads = np.radians([start,stop])
        # # haversine distance between 2 points
        # # convert 2 min to second
        # # radians per second

        result = haversine_distances(rads)
        # multiply by Earth radius to get kilometers

        motion = result * 6371000 / 120
        storm_motion_vector = np.multiply(motion,vector)
        if False:
            print(f'\nstart position:\n {start}')
            print(f'stop position:\n {stop}')
            print(f'diffrence:\n {diff}')
            print(f'speed:\n {mps} mps')
            print(f'storm motion vector:\n   x           y\n{storm_motion_vector}')

        return mps, storm_motion_vector


    def _ziplist(self,props):
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

    def getById(self,_id):
        return self._storm[_id]

    def compareProps(self,_id):
        this = self._storm[_id]
        return {
            'hist': [self._ziplist(p) for p in this['propsHistory']],
            'trends': self._ziplist(*this['propsChange']),#list(*this['propsChange']),
            'props':self._ziplist(this['props'])#list(this['props'])
        }
        # return self._props[_id],self._storm[_id]

storm = Storms()



keys =[
    'MUCAPE',
    'MLCAPE',
    'MLCIN', 
    'EBSHEAR',#EFFECTIVE BULK SHEAR
    'SRH01KM',
    'MEANWIND_1-3kmAGL',
    'MESH',#maximum estimated size of hail
    'VIL_DENSITY',
    'FLASH_RATE',
    'FLASH_DENSITY',
    'MAXLLAZ',
    'P98LLAZ',
    'P98MLAZ',
    'MAXRC_EMISS',
    'MAXRC_ICECF',
    'WETBULB_0C_HGT',
    'PWAT',#PRECIPIPITABLE WATER
    'CAPE_M10M30',
    'LJA', 'SIZE', 'AVG_BEAM_HGT', 'MOTION_EAST', 'MOTION_SOUTH', 'PS', 'ID']


class ProbSevere:
    def __init__(self,features):
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
            



            storm.set(_id=_id,validTime=x.validTime, coordinates=coordinates, properties=properties)


        self.storms = storm
        pass





    def _load(self,feature):
        jd = json.dumps(feature)
        return json.loads(jd, object_hook=lambda d: SimpleNamespace(**d))