import logging
import pytz
# import os
from datetime import datetime
# from influxdb import ConnectionError
from lib.influx.influx_lib import InfluxClient
from lib.pv_lib import AnalogDeviceADS


# set logger here
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('in module %(name)s, in func %(funcName)s, '
                              '%(levelname)-8s: [%(filename)s:%(lineno)d] %(message)s')
file_handler = logging.FileHandler('pv_measurement.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def main():
    # power sensor init
    power_sensor = AnalogDeviceADS()

    # init influx client
    client = InfluxClient(
        host=r'10.208.8.93', port=8086,
        user='eugene', password='7vT4g#1@K',
        dbname='uceeb'
    )
    while True:
        try:
            power, t = power_sensor.make_measurement()
            try:
                _write_res = client.write(
                    time_val=t,
                    measurement="pv_measurement",
                    tags={
                        'project': "hp_pv",
                        'type': "pv",
                        'device': "curr_volt_transformer"
                    },
                    power=round(power, 2)
                )
            except KeyError as e:
                logger.error('Writing to DB error: {}'.format(e))
            print('power = {:.1f},\nt = {}'.format(power, t))
            print('-' * 30)
        except KeyboardInterrupt:
            logger.info('Script was interrupted by user.')
            break


if __name__ == '__main__':
    main()
