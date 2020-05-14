from lib.influx.influx_lib import InfluxDataFrameReader
from lib.data_proc import DataFrameProcessor
import logging
from datetime import datetime
import pandas as pd
import numpy as np

# set logger here
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('in module %(name)s, in func %(funcName)s, '
                              '%(levelname)-8s: [%(filename)s:%(lineno)d] %(message)s')
# file_handler = logging.FileHandler('pv_measurement.log')
# file_handler.setLevel(logging.ERROR)
# file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def main():
    host = 'localhost'
    port = 8086
    dbname = 'uceeb'
    username = 'eugene'
    password = '7vT4g#1@K'
    interval = '10m'

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


if __name__ == '__main__':
    main()
    # _df()
