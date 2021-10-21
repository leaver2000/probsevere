from datetime import datetime
from time import time
import numpy as np
from area import area
R = 6371000  # EARTH RADIUS


def utc_now():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

# ? _____________________________

# *         GEOJSON
# ? _____________________________


class FeatureCollection:
    def __init__(self, feature_collection):
        for key in feature_collection.keys():
            value = feature_collection[key]
            if key == 'validTime':
                self.datetime = datetime.strptime(value, '%Y%m%d_%H%M%S UTC')
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


# ? _____________________________

# *   Least Recently Used Cache
# ? _____________________________

class Current:

    def __init__(self, crds):
        areaobj = {'type': 'Polygon', 'coordinates': [crds.tolist()]}
        self.coordinates = crds
        self.center = np.mean([crds.min(axis=0), crds.max(axis=0)], axis=0)
        # self.center = np.mean(crds, axis=0)
        self.area = np.array(area(areaobj))
        self.stormtrack = None


class StormObject(object):
    """
    STORM OBJECT
    """

    def __init__(self, _id, c):
        self.name = _id
        self.history = History()

        setattr(self, 'center', c.center)
        setattr(self, 'area', c.area)
        setattr(self, 'coordinates', c.coordinates)

        setattr(self.history, 'center', c.center[np.newaxis])
        setattr(self.history, 'area', c.area[np.newaxis])
        setattr(self.history, 'coordinates', c.coordinates)

        self.stormtrack = None
        self.props = None
        self.mps = None
        self.smv = None
        pass

    def affix(self, key, value):
        setattr(self, key, value)

        try:
            prev = getattr(self.history, key)

        except AttributeError:
            prev = None

        if prev is not None:
            try:
                setattr(self.history, key, np.vstack([prev, value]))
            except:
                print(f'StormObject affix error writing {key}')
        else:
            # print(np.sum(value))
            setattr(self.history, key, value)


class History(StormObject):
    def __init__(self):
        self.center = None
        self.areas = None
        self.smv = None
        self.area = None
        self.areaD = None
        self.areaPD = None

        pass

# ? _____________________________

# *   Least Recently Used Cache
# ? _____________________________


class Node(object):
    def __init__(self, value):
        self.value = value
        self.time_stamp = time()

    def update_time_stamp(self):
        self.time_stamp = time()


class LRU(object):
    def __init__(self, max_size):
        self.max_size = max_size
        self.cache = {}
        self.length = 0

    def get(self, key):
        node = self.cache[key]
        node.update_time_stamp()
        return node.value

    def peek(self, key):
        return key in self.cache

    def add(self, key, value):
        new_node = Node(value)

        if self.length == self.max_size:
            self._remove_oldest()

        self.cache[key] = new_node
        self.length += 1

    def _remove_oldest(self):
        oldest = None
        for key in self.cache:
            life_time = self.cache[key].time_stamp
            if oldest == None:
                oldest = key
            elif life_time < self.cache[oldest].time_stamp:
                oldest = key
        del self.cache[oldest]
        self.length -= 1

        # print(self.area)
# class Tracks(StormObject):
#     def __init__(self):
#         self.linear = None

#     def set_linear(self, center, smv):
#         avg_smv = np.mean(smv, axis=0)
#         # print(smv, avg_smv)

#         offsets = [900, 1800, 2700, 3600]

#         stormtrack = center[np.newaxis].tolist()

#         for offset in offsets:
#             D60 = avg_smv*offset  # ? X 3600 = per hour

#             lat, lon = center  # ? destructure center

#             Dy, Dx = D60.flatten()  # ? destructure change in ( Y, X )

#             # ! MATH
#             _180pi = 180 / np.pi
#             cos = np.cos(lat * np.pi/180)
#             lat60 = lat + (Dy / R) * (_180pi)
#             lon60 = lon + (Dx / R) * (_180pi) / cos

#             stormtrack.append([lat60, lon60])

#         self.linear = stormtrack

#     def get(self):
#         return self.linear
#         # return stormtrack
