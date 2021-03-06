import pandas as pd
import numpy as np
import pytz
import logging
import os
from datetime import datetime
import json
import time
from apscheduler.schedulers.background import BackgroundScheduler
from lib.influx.influx_lib import InfluxDataFrameReader

# logger config
logging.basicConfig()
logger = logging.getLogger('data_proc')
logger.setLevel(logging.DEBUG)


class DataFrameProcessor:
    def __init__(self, df_list, tz=pytz.timezone('Europe/Prague')):
        self.tz = tz
        self.df_list = df_list

    @property
    def df_list(self):
        return self._df_list

    @df_list.setter
    def df_list(self, df_list):
        self._df_list = list()
        # self._df_list = [df for df in df_list if isinstance(df, pd.core.frame.DataFrame)]
        for df in df_list:
            if isinstance(df, pd.core.frame.DataFrame):
                df.index = df.index.tz_convert(self.tz)
                df_resampled = df.resample('1min').mean()
                self._df_list.append(df_resampled)

    def process(self):
        if self.df_list:
            d = pd.concat(self.df_list, axis=1)
        else:
            d = None
        df = d[~d.isna()]
        return df


class FileWriter:
    def __init__(self, file_name):
        self.file_name = file_name

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, file_name):
        self._file_name = file_name
        if os.path.exists(file_name):
            pass
        elif file_name:
            with open(file_name, 'w'):
                pass

    def write(self, df):
        with open(self.file_name, 'r') as f:
            data = f.read()
        if data:
            df_read = pd.read_json(self.file_name)
            df_t = df_read.append(df)
            with open(self.file_name, 'w') as f:
                f.write(df_t.to_json(date_format='iso'))
        else:
            with open(self.file_name, 'w') as f:
                f.write(df.to_json(date_format='iso'))


def ctrl():
    host = '10.208.8.93'  # 'localhost'
    port = 8086
    dbname = 'uceeb'
    username = 'eugene'
    password = '7vT4g#1@K'
    interval = '5m'

    client = InfluxDataFrameReader(
        host=host, port=port,
        user=username, password=password,
        dbname=dbname
    )
    df_pv = client.time_query('pv_measurement', interval)
    df_hp = client.time_query('hp_measurement', interval)
    df = DataFrameProcessor([
        df_pv.loc[:, ['power']],
        df_hp.loc[:, ['0_set_temp', '1_sens_on', '2_sens_off',
                      '3_hp_on_off', '4_hysteresis_on', '5_hysteresis_off']]]).process()
    print()

    if df.power >= 1000:
        pass


def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(ctrl, 'interval', seconds=10)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    start = time.time()
    try:
        while True:
            print('Still working at time = {:.2f} h after start'.format((time.time() - start) / 3600))
            time.sleep(5*60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == '__main__':
    # main()
    ctrl()
