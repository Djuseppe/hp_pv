import logging
from functools import wraps
import time
from abc import ABC
import pytz
import numpy as np
import pandas as pd
from datetime import datetime

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


class BoardSPI:
    def __init__(self):
        self.spi = busio.SPI(board.SCK, board.MOSI, board.MISO)


class BaseCS:
    def __init__(self, digital_pin=board.D20):
        self.cs = digitalio.DigitalInOut(digital_pin)


class TemperatureMeasurementDevice:
    def __init__(self, interval=10, time_format='%Y.%m.%d %H:%M:%S.%z', tz_prague=pytz.timezone('Europe/Prague')):
        self.interval = interval
        self.time_format = time_format
        self.tz_prague = tz_prague
        self.spi = BoardSPI()
        # cs1 = BaseCS(board.D20)
        # cs2 = BaseCS(board.D21)
        # cs3 = BaseCS(board.D12)
        # cs4 = BaseCS(board.D25)
        # cs5 = BaseCS(board.D26)
        # cs6 = BaseCS(board.D24)
        # cs7 = BaseCS(board.D22)
        # cs8 = BaseCS(board.D27)
        # cs9 = BaseCS(board.D17)
        # cs10 = BaseCS(board.D4)

        # create a thermocouple object with the above
        self.thermocouple_1 = adafruit_max31865.MAX31865(self.spi, BaseCS(board.D20), wires=4)
        self.thermocouple_2 = adafruit_max31865.MAX31865(self.spi, BaseCS(board.D21), wires=4)
        self.thermocouple_3 = adafruit_max31865.MAX31865(self.spi, BaseCS(board.D12), wires=4)
        self.thermocouple_4 = adafruit_max31865.MAX31865(self.spi, BaseCS(board.D25), wires=4)
        self.thermocouple_5 = adafruit_max31865.MAX31865(self.spi, BaseCS(board.D26), wires=4)
        self.thermocouple_6 = adafruit_max31865.MAX31865(self.spi, BaseCS(board.D24), wires=4)
        self.thermocouple_7 = adafruit_max31865.MAX31865(self.spi, BaseCS(board.D22), wires=4)
        self.thermocouple_8 = adafruit_max31865.MAX31865(self.spi, BaseCS(board.D27), wires=4)
        self.thermocouple_9 = adafruit_max31865.MAX31865(self.spi, BaseCS(board.D17), wires=4)
        self.thermocouple_10 = adafruit_max31865.MAX31865(self.spi, BaseCS(board.D4), wires=4)
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

    @Decorators.wait
    def make_measurement(self):
        time_vals = list()
        df = pd.DataFrame(
            np.zeros(shape=(self.interval, len(self.thermocouple_list)), dtype=float),
            columns=self.therm_names, index=range(self.interval))
        for i, (ind, row) in zip(range(self.interval), df.iterrows()):
            time_vals.append(datetime.now(self.tz_prague).strftime(self.time_format))
            df.loc[ind, row] = self.measure()
            time.sleep(0.9)
            return df.mean(axis=1)

# # create a spi object
# spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
#
# # allocate a CS pin and set the direction
# cs1 = digitalio.DigitalInOut(board.D20)
# cs2 = digitalio.DigitalInOut(board.D21)
# cs3 = digitalio.DigitalInOut(board.D12)
# cs4 = digitalio.DigitalInOut(board.D25)
# cs5 = digitalio.DigitalInOut(board.D26)
# cs6 = digitalio.DigitalInOut(board.D24)
# cs7 = digitalio.DigitalInOut(board.D22)
# cs8 = digitalio.DigitalInOut(board.D27)
# cs9 = digitalio.DigitalInOut(board.D17)
# cs10 = digitalio.DigitalInOut(board.D4)
#
# # create a thermocouple object with the above
# thermocouple_1 = adafruit_max31865.MAX31865(spi, cs1, wires=4)
# thermocouple_2 = adafruit_max31865.MAX31865(spi, cs2, wires=4)
# thermocouple_3 = adafruit_max31865.MAX31865(spi, cs3, wires=4)
# thermocouple_4 = adafruit_max31865.MAX31865(spi, cs4, wires=4)
# thermocouple_5 = adafruit_max31865.MAX31865(spi, cs5, wires=4)
# thermocouple_6 = adafruit_max31865.MAX31865(spi, cs6, wires=4)
# thermocouple_7 = adafruit_max31865.MAX31865(spi, cs7, wires=4)
# thermocouple_8 = adafruit_max31865.MAX31865(spi, cs8, wires=4)
# thermocouple_9 = adafruit_max31865.MAX31865(spi, cs9, wires=4)
# thermocouple_10 = adafruit_max31865.MAX31865(spi, cs10, wires=4)
# therm_list = [
#     thermocouple_1,
#     thermocouple_2,
#     thermocouple_3,
#     thermocouple_4,
#     thermocouple_5,
#     thermocouple_6,
#     thermocouple_7,
#     thermocouple_8,
#     thermocouple_9,
#     thermocouple_10
# ]
#
# while True:
#     try:
#         for i, therm in enumerate(therm_list):
#             print('t_{} = {:.1f} C\t'.format(i + 1, therm.temperature), end='')
#         print()
#         # print(
#         #     'thermocouple_1 = {:.2f} C,\tthermocouple_2 = {:.2f} C'.format(
#         #         thermocouple_1.temperature,
#         #         thermocouple_2.temperature
#         #     )
#         # )
#         # print('thermocouple_2 = {:.2f}'.format(thermocouple_2.temperature))
#     except KeyboardInterrupt:
#         print('Interrupted by user.')
#         break
