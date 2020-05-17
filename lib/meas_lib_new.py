import logging
from functools import wraps
import time
from abc import ABC
import pytz
import numpy as np
import pandas as pd
from datetime import datetime
from lib.influx.influx_lib import InfluxDBServerError, InfluxClient
from requests.exceptions import ConnectionError
import argparse

import board
import busio
import digitalio
import adafruit_max31865


# set logger here
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('in module %(name)s, in func %(funcName)s, '
                              '%(levelname)-8s: [%(filename)s:%(lineno)d] %(message)s')
# file_handler = logging.FileHandler('meas_lib_new.log')
# file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class Device(ABC):
    def measure(self):
        pass

    def make_measurement(self, *args, **kwargs):
        pass

    def run_measurement(self):
        pass


class Decorators(object):
    @classmethod
    def wait(cls, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            interval = args[0].interval
            start = time.time()
            res = func(*args, **kwargs)
            stop = time.time()
            if stop - start < interval:
                time.sleep(interval - (stop - start))
            return res
        return wrapped


class TemperatureMeasurementDevice:
    def __init__(
            self, interval=10, writer=None,
            time_format='%Y.%m.%d %H:%M:%S.%z', tz_prague=pytz.timezone('Europe/Prague')):
        self.writer = writer
        self.interval = interval
        self.time_format = time_format
        self.tz_prague = tz_prague
        self.spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

        # create a thermocouple object with the above
        self.thermocouple_1 = adafruit_max31865.MAX31865(
            self.spi, digitalio.DigitalInOut(board.D20), wires=4)
        self.thermocouple_2 = adafruit_max31865.MAX31865(
            self.spi, digitalio.DigitalInOut(board.D21), wires=4)
        self.thermocouple_3 = adafruit_max31865.MAX31865(
            self.spi, digitalio.DigitalInOut(board.D12), wires=4)
        self.thermocouple_4 = adafruit_max31865.MAX31865(
            self.spi, digitalio.DigitalInOut(board.D25), wires=4)
        self.thermocouple_5 = adafruit_max31865.MAX31865(
            self.spi, digitalio.DigitalInOut(board.D26), wires=4)
        self.thermocouple_6 = adafruit_max31865.MAX31865(
            self.spi, digitalio.DigitalInOut(board.D24), wires=4)
        self.thermocouple_7 = adafruit_max31865.MAX31865(
            self.spi, digitalio.DigitalInOut(board.D22), wires=4)
        self.thermocouple_8 = adafruit_max31865.MAX31865(
            self.spi, digitalio.DigitalInOut(board.D27), wires=4)
        self.thermocouple_9 = adafruit_max31865.MAX31865(
            self.spi, digitalio.DigitalInOut(board.D17), wires=4)
        self.thermocouple_10 = adafruit_max31865.MAX31865(
            self.spi, digitalio.DigitalInOut(board.D4), wires=4)
        self.thermocouple_list = [
            self.thermocouple_1,
            self.thermocouple_2,
            self.thermocouple_3,
            self.thermocouple_4,
            self.thermocouple_5,
            self.thermocouple_6,
            self.thermocouple_7,
            self.thermocouple_8,
            self.thermocouple_9,
            self.thermocouple_10
        ]
        self.therm_names = [
            'thermocouple_1',
            'thermocouple_2',
            'thermocouple_3',
            'thermocouple_4',
            'thermocouple_5',
            'thermocouple_6',
            'thermocouple_7',
            'thermocouple_8',
            'thermocouple_9',
            'thermocouple_10'
        ]

    def measure(self):
        result = list()
        for therm in self.thermocouple_list:
            result.append(therm.temperature)
        return np.array(result)

    def write_to_db(self, data=None):
        tags_dict = {
            'project': "hp_pv",
            'type': "hp",
            'device': "rpi42"
        }
        try:
            self.writer.write(
                datetime.now(self.tz_prague).strftime(self.time_format),
                tags_dict,
                'temperatures',
                **data
            )
        except (ConnectionError, InfluxDBServerError) as e:
            logger.error('{}'.format(e))

    @Decorators.wait
    def make_measurement(self):
        time_vals = list()
        df = pd.DataFrame(
            np.zeros(shape=(self.interval, len(self.thermocouple_list)), dtype=float),
            columns=self.therm_names, index=range(self.interval))
        for i, (ind, _) in zip(range(self.interval), df.iterrows()):
            time_vals.append(datetime.now(self.tz_prague).strftime(self.time_format))
            df.loc[ind, :] = self.measure()
            time.sleep(0.9)
        return df.mean(axis=1).round(2).to_dict()


def parse_args():
    """Parse the args from main."""
    parser = argparse.ArgumentParser(
        description='example code to play with InfluxDB')
    parser.add_argument('--host', type=str, required=False,
                        default='10.208.8.93',
                        help='hostname of influx db')
    parser.add_argument('--port', type=int, required=False, default=8086,
                        help='port of influx db')
    return parser.parse_args()


def main(host, port):
    m = TemperatureMeasurementDevice(
        writer=InfluxClient(
            host=host, port=port,
            user='eugene', password='7vT4g#1@K',
            dbname='uceeb'
        )
    )
#
    while True:
        try:
            res = m.make_measurement()
            print(res, end='')
            m.write_to_db(res)
        except KeyboardInterrupt:
            print('Interrupted by user.')
            break


if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port)
