import numpy as np
from sklearn.metrics.pairwise import haversine_distances
import json
from probsevere import ProbSevere
from pprint import pprint
samples = [
    # 'sample_data/MRMS_PROBSEVERE_20211011_000053.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000240.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000447.json',
    'sample_data/MRMS_PROBSEVERE_20211011_000655.json'
    ]


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
]



if __name__ == '__main__':
    # print('hello')

    for sample in samples:
        feature = json.load(open(sample))
        ps = ProbSevere(feature).storms
        # ps.getCollection()

    # pprint(ps.compareProps('90101'))
    # pprint(ps.getCollection())


