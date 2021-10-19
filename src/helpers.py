from datetime import datetime
import numpy as np


class Object:
    pass


class StormMotionVector:
    def __init__(self, smv):
        self.smv = smv

    def mean(self, _slice=None):
        obj = Object()
        smv = self.smv if _slice is None else self.smv[_slice:]
        obj.mps = np.mean(smv, axis=0)
        obj.kmh = np.mean(smv, axis=0) * 3.6
        obj.knots = np.mean(smv, axis=0) * 1.943844

        return obj


class StormHistory:
    def __init__(self):
        #
        pass


class FeatureCollection:
    def __init__(self, feature_collection):
        for key in feature_collection.keys():
            value = feature_collection[key]
            if key == 'validTime':
                self.datetime = datetime.strptime(value[:-4], '%Y%m%d_%H%M%S')
            setattr(self, key, value)


class Feature:
    def __init__(self, feature):
        models = feature['models']['probsevere']
        self.properties = feature['properties']
        self.properties['probsevere'] = int(models["PROB"])
        self.properties['models'] = models["LINE01"]

        self._id = feature['properties']['ID']
        self.geometry = feature['geometry']
        self.coordinates = np.squeeze(feature['geometry']['coordinates'])


def utc_now():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
