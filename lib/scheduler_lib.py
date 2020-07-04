from datetime import datetime
import time
import logging
import os
import numpy as np
import time
from apscheduler.schedulers.background import BackgroundScheduler


# set logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('in module %(name)s, in func %(funcName)s, '
                              '%(levelname)-8s: [%(filename)s:%(lineno)d] %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
if not len(logger.handlers):
    logger.addHandler(stream_handler)
    logger.propagate = False


class Controller:
    def __init__(self, interval=5):
        self.interval = interval
        self.scheduler = BackgroundScheduler()

    def start(self):
        pass


def some_func():
    return np.random.rand()


def tick(start=0):
    # print('Tick! The time is: %s' % datetime.now())
    print('Tick! time is {:.2f}'.format(time.time() - start))


def reading_db():
    pass


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(tick, 'interval', args=(time.time(), ), seconds=5)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    start = time.time()
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            print('value = {} at time = {:.2f}'.format(some_func(), time.time() - start))
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
