from lib.influx.influx_lib import InfluxDataFrameReader, DataFrameProcessor
import logging
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
    dbname = 'home'
    username = 'eugene'
    password = '7vT4g#1@K'

    client = InfluxDataFrameReader(
        host=host, port=port,
        user=username, password=password,
        dbname=dbname
    )
    df_pv = client.time_query('pv_measurement', '1h')
    df_hp = client.time_query('hp_measurement', '1h')
    print()
    # df_proc = DataFrameProcessor()


if __name__ == '__main__':
    main()
    # _df()
