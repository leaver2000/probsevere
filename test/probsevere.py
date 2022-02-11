from __future__ import annotations
import json
from typing import Any, Dict, List, TextIO, Iterator, Union
# 3rd party
import numpy as np
import numpy.typing as npt
import pandas as pd
import nvector as nv
from pygc import great_circle
IDX = pd.IndexSlice
WGS84 = nv.FrameE(name='WGS84')


class ProbSevere:
    """a class for generating a storm prediction from the NSSL MRMS ProbSevere Dataset."""

    def __init__(self, feature_collection: TextIO):
        self._dataframe = self._from_collection(feature_collection)

    def set_collection(self, feature_collection: TextIO, mean_range=5) -> None:
        # generate a new dataframe from the featurecollection
        now = self._from_collection(feature_collection)
        # valid time histoy
        hist = self._dataframe

        time_hist: pd.DatetimeIndex = hist.columns.unique('ValidTime')

        time_now: pd.Timestamp = now.columns.unique('ValidTime')[0]

        time: pd.Series[Union[pd.Timestamp, pd.DatetimeIndex, float]] = pd.Series({
            # DatetimeIndex
            'Full': [*time_hist, time_now],
            'Hist': time_hist,
            # a mean time range var to compute outliers
            'Mean': [*time_hist[-mean_range:], time_now],
            # timestamps
            'Prev': time_hist[-1],  # previous
            'Now': time_now,  # current
            # time delta from previous to now
            'Delta': abs(time_hist[-1] - time_now).total_seconds()
        })
        # join the storm history and current storm into a single dataframe
        df = pd.concat([hist, now], axis=1)

        # boolean series for indexing ID with both a previous and current postion
        with_geo: pd.Series[bool] = (
            df.loc[:, IDX[[time.Prev, time.Now], 'GeoPoint']].notna().all(axis=1))

        def mean(param_idx: str, time_idx=time.Full) -> pd.Series[float]:
            """\
            retruns the mean value of a parameter.
            only computes if GeoPoints are present 2 most recent columns.
            rounds the mean value to 2 decimals.
            """
            return np.around(
                df.loc[with_geo, IDX[time_idx, param_idx]].mean(axis=1),
                decimals=2)

        def delta_from_mean(param: str) -> pd.Series:
            the_mean = mean(param, time.Mean)
            the_delta = abs(df.loc[with_geo, IDX[time.Now, param]]-the_mean)
            delta_series: pd.Series = np.divide(
                the_delta,
                the_mean,
                out=np.zeros_like(the_delta),
                where=the_mean != 0)
            return delta_series

        def derived_parameters(s: pd.Series) -> pd.Series[Union[int, float]]:
            """\
            with a previous GeoPoint and the current GeoPoint
            calculate the Velocity=Distance/time_delta and Azimuth.
            """
            prev, now = (
                s.loc[[time.Prev, time.Now], 'GeoPoint'])
            P2N: nv.Pvector = prev.delta_to(now)
            az = P2N.azimuth_deg
            # ----------------------------------
            s.loc[time.Now, 'Distance'] = round(P2N.length, 2)
            s.loc[time.Now, 'Azimuth'] = round(az if az >= 0 else az+360, 2)
            return s

        # use the geopoints to derive Distance and Azimuth
        df[with_geo] = df[with_geo].apply(derived_parameters, axis=1)
        # determine the Velocitiy by distance / time
        df.loc[with_geo, IDX[time.Now, 'Velocity']] = (
            df.loc[with_geo, IDX[time.Now, 'Distance']]/time.Delta)
        # setting a growth rate for future use.  if grow rate is excessive it
        # will throw off the stom track
        df.loc[with_geo, IDX[time.Now, ['GrowthRate']]] = (
            delta_from_mean('Size'))
        # the mean velocity and azimuth
        mean_velocity, mean_azimuth = mean(
            'Velocity', time.Mean), mean('Azimuth', time.Mean)

        def stormtrack(s: pd.Series) -> pd.Series:

            if mean_velocity.loc[s.name].any():
                distance = (
                    # multiply the average velocity by time to create distance
                    np.multiply([1, 900, 1800, 2700, 3600], mean_velocity.loc[s.name]))

                azimuth = mean_azimuth.loc[s.name]

                longitude = s.loc[time.Now, 'Longitude']

                latitude = s.loc[time.Now, 'Latitude']

                gc = great_circle(
                    distance=distance,
                    azimuth=azimuth,
                    latitude=latitude,
                    longitude=longitude
                )

                s.loc[time.Now, 'StormTrack'] = np.around(
                    np.moveaxis([gc['longitude'], gc['latitude']], 1, 0),
                    decimals=2)
                s.loc[time.Now, 'ReverseAzimuth'] = gc['reverse_azimuth']
                # s.loc[time.Now, 'Distance'] =  s.loc[time.Now, 'Distance'].round(2)
            else:
                pass
                # print(np.any(mean_velocity.loc[s.name]),
                #       mean_velocity.loc[s.name].any())

            return s
        # build the storm track
        will_round = df.loc[:, IDX[:, 'Velocity']].any(1)
        df.loc[will_round] = np.around(df.loc[will_round], 2)
        df.loc[with_geo, IDX[time.Now, :]] = (
            df.loc[with_geo, IDX[time.Mean, :]]
            .apply(stormtrack, axis=1))

        self._dataframe = df

        return

    @staticmethod
    def _from_collection(feature_collection: TextIO) -> pd.DataFrame:

        collection = json.load(feature_collection)

        features: List[Dict[str, Dict[str, Any]]] = collection.pop('features')

        def make_coords() -> Iterator[Dict[str, Any]]:
            for feat in features:

                coordinates: npt.NDArray = (
                    np.squeeze(feat['geometry']['coordinates']))

                longitude, latitude = np.around(
                    np.mean([coordinates.min(axis=0),
                             coordinates.max(axis=0)], axis=0),
                    decimals=2
                )
                probs = {
                    f'{name[0:4].title()}{name[4:].title()}': model['PROB']
                    for name, model in
                    feat['models'].items()
                }

                yield {
                    'ID': feat['properties']['ID'],
                    'Size': int(feat['properties']['SIZE']),
                    'GeoPoint': WGS84.GeoPoint(
                        longitude=longitude,
                        latitude=latitude,
                        degrees=True,
                        z=0),
                    **probs,
                    'Coordinates': coordinates,
                    'Latitude': latitude,
                    'Longitude': longitude,
                    'Distance': pd.NA,
                    'Azimuth': pd.NA,
                    'Count': pd.NA,
                    'Velocity': pd.NA,
                    'GrowthRate': pd.NA,
                    'StormTrack': pd.NA,
                    'ReverseAzimuth': pd.NA
                }

        coord_df = pd.DataFrame.from_records(tuple(make_coords()), index='ID')

        coord_df['ValidTime'] = (
            pd.to_datetime(collection['validTime'], format='%Y%m%d_%H%M%S %Z'))

        return(
            coord_df
            .set_index(['ValidTime'], append=True, drop=True)
            .stack(dropna=False)
            .unstack(1)
            .rename_axis(['ID', 'Parameters'])
            .unstack(1)
        )

    @ property
    def dataframe(self) -> pd.DataFrame:
        return (
            self._dataframe
            .drop('GeoPoint', axis=1, level=1)
            .fillna(np.nan)
        )

    @property
    def latest(self):
        return (
            self.dataframe
            .stack()
            .iloc[:, -1]
            .unstack()
            .dropna()
            .loc[:, [
                'ProbSevere',
                'ProbTor',
                'ProbHail',
                'ProbWind',
                'Size',
                'Longitude',
                'Latitude',
                'Azimuth',
                'Distance',
                'Velocity',
                'Coordinates',
                'StormTrack']]
            # Size', 'GeoPoint', 'ProbSevere', 'ProbTor', 'ProbHail', 'ProbWind', 'Coordinates', 'Latitude', 'Longitude', 'Distance', 'Azimuth', 'Count', 'Velocity', 'GrowthRate', 'StormTrack', 'ReverseAzimuth'
        )

    @property
    def storm_ids(self):
        return self.latest.index

    @property
    def parameters(self):
        return (
            self._dataframe
            .columns
            .unique('Parameters')
            .tolist())
    # def
# Azimuth                                        Coordinates     Distance GrowthRate
#                                     ReverseAzimuth    Size
#      StormTrack   Velocity
