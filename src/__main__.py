import os
import json
from glob import glob
import sched
import time
from controller import Controller
from helpers import utc_now

TEST = False


def start():

    print(f'\ncontroller initialized at {utc_now()}')
    ctrl = Controller()
    state = ctrl.state

    ctrl.collect()  # ? scrape mrms dataset

    if state.collect is not None:
        ctrl.validate()  # ? validate data requirement
        ctrl.process()  # ? process data
        if ctrl.datetime.minute % 10 == 0:
            ctrl.save()

    else:
        print('skipping save on non 10 min interval')

    print(f'\ncontroller routine completed {utc_now()}\n state:')
    print(f'   - initialize: {state.initialize}')
    print(f'   - collect: {state.collect}')
    print(f'   - validate: {state.validate}')
    print(f'   - process: {state.process}')
    print(f'   - save: {state.save}')

    pass


def ready(sc, x):
    s.enter(120, 1, ready, (sc, x))
    start()
    pass


# start()
if __name__ == '__main__':
    if TEST:
        ctrl = Controller()
        ctrl.test()
    else:

        print(f'scheduler initialized at {utc_now()}')

        # ? schedule itterator to run every 2 mins
        s = sched.scheduler(time.time, time.sleep)
        s.enter(120, 1, ready, (s, None))
        s.run()


if False:
    ctrl = Controller()
    ctrl.test()
    # paths = glob(os.path.join('sample_data/', '*.json'))
    # paths.sort()
    # for path in paths:
    #     feature_collection = json.load(open(path))
    #     ps = ProbSevere(feature_collection)
    #     print(ps.feature_collection['features'][-1])
