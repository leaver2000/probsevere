from __future__ import annotations
from glob import glob
import os
import json

from probsevere import ProbSevere
import pandas as pd
from shapely.geometry import shape, Polygon
import numpy.typing as npt
import nvector as nv
import numpy as np
IDX = pd.IndexSlice
WGS84 = nv.FrameE(name='WGS84')

# WGS84.GeoPoint(
#                         longitude=longitude,
#                         latitude=latitude,
#                         degrees=True,
#                         z=0),


class PS:
    def __init__(self, feature_collection):
        self._dataframe = self._load(feature_collection)

    def set(self, feature_collection):
        df = self._load(feature_collection)
        df = pd.concat([self._dataframe, df], axis=1)

        valid: pd.DatetimeIndex = df.columns.unique('validTime')

        has_geo: npt.NDArray = (
            df.loc[:, IDX[valid[-2:], 'geopoint']].notna().values.all(1))

        def storm_motion_vector(s):
            a, b = s
            return s
        vect = (
            df.loc[has_geo, IDX[valid[-2:], 'geopoint']].apply(storm_motion_vector, axis=1))

        print(vect)

        self._dataframe = df

    def _load(self, feature_collection):
        fc = json.load(feature_collection)

        features = pd.DataFrame.from_records(fc['features'])
        props = features['properties'].apply(pd.Series)
        props['validTime'] = pd.to_datetime(
            fc['validTime'], format='%Y%m%d_%H%M%S %Z')

        props['geometry'] = features['geometry'].apply(shape)
        props['area'] = props['geometry'].apply(lambda s: s.area)
        # props['centroid'] = props['geometry'].apply(lambda s: s.centroid)
        props['geopoint'] = props['geometry'].apply(
            lambda geom: WGS84.GeoPoint(
                longitude=geom.centroid.x,
                latitude=geom.centroid.y
            )
        )

        return (
            props
            .set_index(['validTime', 'ID'])
            .rename_axis('parameters', axis=1)
            .stack()
            .unstack(['validTime', 'parameters'])
            # .loc[['PS', 'geometry', 'area', 'centroid'], :]
            .loc[:, IDX[:, ['PS', 'geometry', 'area', 'geopoint']]]
        )


if __name__ == "__main__":
    paths = sorted(glob(os.path.join('sample_data/', '*.json')))

    for i, path in enumerate(paths[0:2]):
        with open(path) as feature_collection:
            if i == 0:
                # prob = ProbSevere(feature_collection)
                prob = PS(feature_collection)
            else:
                prob.set(feature_collection)

                # pass
                # prob.set_collection(feature_collection)

    # print(prob.latest)
