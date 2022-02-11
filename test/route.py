from __future__ import annotations
from glob import glob
import os

from probsevere import ProbSevere
# IDX = pd.
if __name__ == "__main__":
    paths = sorted(glob(os.path.join('sample_data/', '*.json')))

    for i, path in enumerate(paths[0:5]):
        with open(path) as feature_collection:
            if i == 0:
                prob = ProbSevere(feature_collection)
            else:
                prob.set_collection(feature_collection)

    print(prob.latest)
