from abc import ABC
import time
import board
import busio
import numpy as np
import logging
import pytz
from datetime import datetime
import random
import functools

from adafruit_ads1x15 import ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


# set logger here
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('in module %(name)s, in func %(funcName)s, '
                              '%(levelname)-8s: [%(filename)s:%(lineno)d] %(message)s')
file_handler = logging.FileHandler('meas_lib.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def wait(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        wait_time = 10
        start = time.time()
        res = func(*args, **kwargs)
        stop = time.time()
        if stop - start < wait_time:
            time.sleep(wait_time - (stop - start))
        return res
    return wrapped


class Device(ABC):
    def measure(self):
        pass

    def make_measurement(self, *args, **kwargs):
        pass


class AnalogDeviceADS(Device):
    def __init__(self, interval=10, digital_io=board.D5, ch_num=MCP.P2, gain=1):
        self.gain = gain
        self.interval = interval
        self.time_format = '%Y.%m.%d %H:%M:%S.%z'
        self.tz_prague = pytz.timezone('Europe/Prague')
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(self.i2c, address=0x48, gain=self.gain)
            self.ch_0 = AnalogIn(self.ads, ADS.P0)
            self.ch_1 = AnalogIn(self.ads, ADS.P1)
            self.ch_2 = AnalogIn(self.ads, ADS.P2)
            self.ch_3 = AnalogIn(self.ads, ADS.P3)
            # print('debug')
        except Exception as error:
            logger.error('Error while init: {}'.format(error))
            self.status = False

    def measure(self):
        # return self.ch_0.voltage, self.ch_3.voltage, datetime.now(self.tz_prague).strftime(self.time_format)
        return self.ch_0.voltage, self.ch_1.voltage, self.ch_2.voltage, self.ch_3.voltage

    @wait
    def make_measurement(
            self, time_format='%Y.%m.%d %H:%M:%S.%z',
            tz_prague=pytz.timezone('Europe/Prague')):
        time_vals = list()
        analog_voltage = np.zeros(self.interval)
        for i in range(self.interval):
            time_vals.append(datetime.now(tz_prague).strftime(time_format))
            analog_voltage[i] = self.measure()
            time.sleep(0.9)
            return analog_voltage[~np.isnan(analog_voltage)].mean(), time_vals[-1]


def main():
    energy_meter = AnalogDeviceADS(5)
    try:
        while True:
            # ldr, t = energy_meter.make_measurement()
            _meas = energy_meter.measure()
            print(_meas)
            time.sleep(1)
            # print('-' * 30)
    except KeyboardInterrupt:
        logger.info('Script was interrupted by user.')
        pass


if __name__ == '__main__':
    main()
