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
# file_handler = logging.FileHandler('meas_lib.log')
# file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
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
    def __init__(
            self, interval=10, gain=1,
            time_format='%Y.%m.%d %H:%M:%S.%z',
            tz_prague=pytz.timezone('Europe/Prague'),
            coeff_current=3000/560, coeff_voltage=116.8059):
        self.gain = gain
        self.interval = interval
        self.time_format = time_format
        self.tz_prague = tz_prague
        self.coeff_current = coeff_current
        self.coeff_voltage = coeff_voltage
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(self.i2c, address=0x48, gain=self.gain)
            self.ch_current = AnalogIn(self.ads, ADS.P0)
            self.ch_voltage = AnalogIn(self.ads, ADS.P3)

            # print('debug')
        except Exception as error:
            logger.error('Error while init: {}'.format(error))
            self.status = False

    def measure(self):
        return self.ch_voltage.voltage * self.coeff_voltage, self.ch_current.voltage * self.coeff_current

    @wait
    def make_measurement(self):
        time_vals = list()
        power_array = np.zeros(self.interval)
        for i in range(self.interval):
            time_vals.append(datetime.now(self.tz_prague).strftime(self.time_format))
            voltage, current = self.measure()
            power_array[i] = voltage * current
            time.sleep(0.9)
            if power_array.any():
                return power_array[~np.isnan(power_array)].mean(), time_vals[-1]
            else:
                return np.NZERO, time_vals[-1]


def main():
    energy_meter = AnalogDeviceADS(5)
    try:
        while True:
            # ldr, t = energy_meter.make_measurement()
            voltage, current = energy_meter.measure()
            print('voltage = {:.2f} V, current = {:.2f} A'.format(voltage, current))
            time.sleep(1)
            # print('-' * 30)
    except KeyboardInterrupt:
        logger.info('Script was interrupted by user.')
        pass


if __name__ == '__main__':
    main()
