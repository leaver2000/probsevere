import numpy as np
from stormtrack import StormTrack
from helpers import FeatureCollection, Feature


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

st = StormTrack()

# ? reshape the ProbSevere FeatureCollection


class ProbSevere:
    def __init__(self, feature_collection):
        # * initialize feature_collection as fc
        fc = FeatureCollection(feature_collection)
        self.datetime = fc.datetime
        print(f'initalizing new probsevere {fc.datetime} UTC')

        # * set feature collection
        self.feature_collection = {
            'source': fc.source,
            'product': fc.product,
            'validTime': fc.validTime[:-6],
            'type': fc.type,
            'description': None,
            # !
            'features': [self._use(Feature(feature), fc) for feature in fc.features]

        }

    # ? (self, feature, feature_collection)
    def _use(self, f, fc):
        st.storm_track(feature=f, validTime=fc.validTime)
        # ! call to StormTrack
        center, linear = st.getGeometryCollection(f._id)
        # print(f.properties)

        return {
            'properties': f.properties,
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
                    "coordinates": [np.flip(linear, (0, 1)).tolist() if linear is not None else None]
                }]
            }

        }
    # "geometry": { // unique geometry member
    #   "type": "GeometryCollection", // the geometry can be a GeometryCollection
    #   "geometries": [ // unique geometries member
    #     { // each array item is a geometry object
        # return{
        #     'geometry': {
        #         "type": "LeafletPolygon",
        #         'coordinates': np.flip(f.coordinates, (0, 1)).tolist()
        #     },
        #     'properties': f.properties,
        #     # ! entry point to rebuilding feature object
        #     # 'vectors': [vectors if vectors is not None else None]
        #     "vectors": {
        #         "type": "StormMotionVector",
        #         "coordinates": [vectors if vectors is not None else None]
        #     }
        # }
