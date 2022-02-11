import math
import numpy as np
R = 6371000


def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d


def use_time_delta(self, distD, azi, lon1, lat1):
    lat2 = math.asin(math.sin(lat1)*math.cos(distD/R) +
                     math.cos(lat1)*math.sin(distD/R)*math.cos(azi))

    lon2 = lon1 + math.atan2(math.sin(azi)*math.sin(distD/R)*math.cos(lat1),
                             math.cos(distD/R)-math.sin(lat1)*math.sin(lat2))

    return np.rad2deg([lon2, lat2])


def deviation(key, x, c):

    # print(f'current velocity:\n {c.velocity}')

    # print(f'velocity history:\n {x.history.velocity}')
    # print()

    x_value = getattr(x.history, key)
    c_value = getattr(c, key)

    meanV = np.mean(x_value)
    # print(x.history.velocity)
    # print('last 5')
    last10 = x_value[-10:]
    avg10 = np.mean(last10)
    # print(np.diff([avg10, c.velocity]))
    # print(meanV)
    diff = np.diff([avg10, c_value])
    veloc_dev = diff / avg10
    if veloc_dev % 1 > 0.5:
        print(veloc_dev*100)
    # print(veloc_dev % 1>1)
    # x.affix('area_change', area_change)
    # growth_rate = np.mean(x.history.area_change)
    pass
