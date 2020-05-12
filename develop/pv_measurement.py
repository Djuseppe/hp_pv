import logging
import pytz
# import os
from datetime import datetime
# from influxdb import ConnectionError
from lib.influx_lib import InfluxClient
from lib.meas_lib import AnalogDeviceADS


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
    time_format = '%Y.%m.%d %H:%M:%S.%z'
    tz_prague = pytz.timezone('Europe/Prague')
    
    # power sensor init
    power_sensor = AnalogDeviceADS()

    # init influx client
    client = InfluxClient(
        host=r'10.208.8.93', port=8086,
        user='eugene', password='7vT4g#1@K',
        dbname='uceeb'
    )
    
    try:
        while True:
            power, t = power_sensor.make_measurement()
            
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
            print('power = {:.1f},\nt = {}'.format(power, t))
            print('-' * 30)
    except KeyboardInterrupt:
        logger.info('Script was interrupted by user.')
        pass


if __name__ == '__main__':
    main()
