import numpy as np
from stormtrack import StormTrack
from stormutility import FeatureCollection, Feature
from datetime import datetime


def utc_now():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')


DESCRIPTION = """
alterations have been made to the NSSL MRMS ProbSevere output.
The models section was removed because in many cases they were
redundant.  Only the properties, coordinates, and prob values
have been retained. Additionally a storm track algorithm plots
coordinate postions for the movement of the storm.

NOTE: due to this model being fed directly to a Leaflet Web
application which utilizes an inversed lat/lon shema all lat/lons
are inverted.
"""

# st = StormTrack()

# ? reshape the ProbSevere FeatureCollection


class ProbSevere:
    def __init__(self, feature_collection):
        # * initialize feature_collection as fc
        fc = FeatureCollection(feature_collection)

        self.datetime = fc.datetime
        # print(f'initalizing new probsevere {fc.datetime} UTC')

        # * set feature collection
        self.feature_collection = {
            'source': fc.source,
            'product': fc.product,
            'validTime': fc.validTime,
            'type': fc.type,
            'description': None,
            # ? FOR FEATURE IN FEATURES USE FEATURE CLASS OBJECT
            'features': [self._use(Feature(feature), fc.datetime) for feature in fc.features]

        }

    # ? (self, feature, feature_collection)
    def _use(self, f, validtime):

        st = StormTrack(feature=f, validtime=validtime)
        # ! get_storm_tracks by feature Id
        center, tracks = st.get_storm_tracks(f._id)
        # print(f._id)

        return {
            'properties': f.properties,
            '_id': f._id,
            # ? The Geometry object is reconstructed as a GeomertyCollection.
            # ? Point and MulitiLineString value are set in the Object.
            # ? Coordinates formated consistent with the Leaflet map application.
            'geometry': {
                "type": "GeometryCollection",
                "geometries": [{
                    "type": "LeafletPoint",
                    "coordinates": np.flip([center], (0, 1)).flatten().tolist()
                }, {
                    "type": "LeafletPolygon",
                    "coordinates": [np.flip(f.coordinates, (0, 1)).tolist()]
                },
                    {
                    "type": "LeafletMultiLineString",
                    "coordinates": np.flip(tracks, (0, 1)).tolist() if tracks is not None else None
                }]
            }

        }
