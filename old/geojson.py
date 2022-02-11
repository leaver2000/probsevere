# import numpy as np
# from datetime import datetime


# class FeatureCollection:
#     def __init__(self, feature_collection):
#         for key in feature_collection.keys():
#             value = feature_collection[key]
#             if key == 'validTime':
#                 self.datetime = datetime.strptime(value, '%Y%m%d_%H%M%S UTC')
#             setattr(self, key, value)


# class Feature:
#     def __init__(self, feature):
#         models = feature['models']['probsevere']
#         self.properties = feature['properties']
#         self.properties['probsevere'] = int(models["PROB"])
#         self.properties['models'] = models["LINE01"]

#         self._id = feature['properties']['ID']
#         self.geometry = feature['geometry']
#         self.coordinates = np.squeeze(feature['geometry']['coordinates'])
