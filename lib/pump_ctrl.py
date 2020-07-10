import time
import os
import argparse
import pandas as pd
import numpy as np
import logging
from lib.influx.influx_lib import InfluxClient, DBReader, InfluxDataFrameReader
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from lib.tcp_lib import Client

# set logger here
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('in module %(name)s, in func %(funcName)s, '
                              '%(levelname)-8s: [%(filename)s:%(lineno)d] %(message)s')
# file_handler = logging.FileHandler('meas_lib.log')
# file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
if not len(logger.handlers):
    logger.addHandler(stream_handler)
    logger.propagate = False


def _get_last_value_from_df(df: pd.DataFrame, col: str = 'hp_el_power'):
    if isinstance(df, pd.DataFrame) and col in df.columns:
        arr = df.loc[:, 'hp_el_power'].values
        return arr[-2:]
    else:
        logger.debug(f'while parsing df from InfluxDB got error: df is not DataFrame or {col} is not in columns')


def run_pumps(threshold: int = 50):
    c = InfluxDataFrameReader(
        host='10.208.8.93', port=8086,
        dbname='uceeb', user='eugene', password='7vT4g#1@K')
    res = c.time_query('hp_el_power', '40s')
    print(res)
    last, prev = _get_last_value_from_df(res)
    # print(f'p0 = {p0}, p1 = {p1}')
    if last > threshold:
        # if prev value is also > threshold: pass it
        if prev > threshold:
            logger.info('status = {1.1}')
            pass
        else:
            # turn on pumps
            pump = Client('10.208.8.106', 65432)
            pump.send('on')
            logger.info('turned pump on')
            logger.info('status = {1.2}')
    else:
        # if prev value is also < threshold: pass it
        if prev < threshold:
            logger.info('status = {2.1}')
            pass
        else:
            pump = Client('10.208.8.106', 65432)
            pump.send('off')
            logger.info('turned pump off')
            logger.info('status = {2.2}')


# def listener(event):
#     if not event.exception:
#         job = scheduler.get_job(event.job_id)
        # pump = Client('10.208.8.106', 65432)
        # if job.retval > 50:
        #     pump.send('on')
        #     logger.info('turned pump on')
        # else:
        #     pump.send('off')
        #     logger.info('turned pump off')


if __name__ == '__main__':
    start = time.time()
    scheduler = BackgroundScheduler()
    # scheduler.add_listener(listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.add_job(run_pumps, 'interval', seconds=10)
    scheduler.start()
    logger.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            logger.info(f'Still working at time = {(time.time() - start) / 3600:.2f} hour after start')
            time.sleep(5 * 60)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
