
import json
from types import SimpleNamespace
import numpy as np
from sklearn.metrics.pairwise import haversine_distances
from sklearn.linear_model import LinearRegression
from pprint import pprint

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


class Storms:
    _storm = {}
    _props={}
    def set(self,_id=None,coordinates=None,properties=None):
        center = np.mean(np.squeeze(coordinates),axis=0)
        p = np.array(list(properties.values()))[:13]
        props =np.array(p,dtype=np.float16)
        
        # print(props)

        # self._id = _id


        # self._id = self._storm[_id]

        if _id not in self._storm.keys():
            self._props[_id]= props
            self._storm[_id]={
                'count':1,
                'coordinates':np.array(coordinates),
                'center':center,
                'centers':[center],
                'props':props,
                'propsHistory':[props]
            }
        else:
            that = self._storm[_id]
            motion =self._motion([that['center'],center])



            self._storm[_id]={
                'count': that['count']+1,
                'coordinates':np.array(coordinates),
                'center':center,
                'centers':np.append(that['centers'],[center],axis=0),
                'motion':motion,
                'props':props,
                'propsHistory':[*that['propsHistory'],props],
                'propsChange':np.diff([that['props'],props],axis=0)
            }
            this = self._storm[_id]
            print(f'\n{_id}\nthat',that,'\nthis',this)

            # self._storm[_id]['center'] = np.append(self._storm[_id]['center'],[center],axis=0)

            return None
    # def get_
    def _motion(self,position):
        rads = np.radians(position)
        D2min=haversine_distances(rads)
        return D2min* 6371000/1000

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
        meta = self._load(features)
        print(meta.validTime)
        for feature in features['features']:
            coordinates = self._load(feature['geometry']['coordinates'])
            properties = feature['properties']
            _id = properties['ID']
            # properties = self._load(feature['properties'])

            # print(list(props.keys())[-7])
            # b = list(props.values())
            # print(np.array(b)[:-7])
            # print



            storm.set(_id=_id,coordinates=coordinates, properties=properties)
        self.storms = storm
        pass





    def _load(self,feature):
        jd = json.dumps(feature)
        return json.loads(jd, object_hook=lambda d: SimpleNamespace(**d))