from abc import ABC
import time
import board
import busio
import numpy as np
import logging
import pytz
from datetime import datetime
import functools
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

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


class AnalogDeviceMPC(Device):
    def __init__(
            self, interval=10,
            time_format='%Y.%m.%d %H:%M:%S.%z',
            tz_prague=pytz.timezone('Europe/Prague'),
            coeff_i=10/2, coeff_u=300/2):
        self.interval = interval
        self.time_format = time_format
        self.tz_prague = tz_prague
        self.coeff_u = coeff_u
        self.coeff_i = coeff_i
        try:
            self.spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
            self.cs = digitalio.DigitalInOut(board.D21)
            mcp = MCP.MCP3008(self.spi, self.cs)

            self.ch_u = AnalogIn(mcp, MCP.P6)
            self.ch_i = AnalogIn(mcp, MCP.P7)

        except Exception as error:
            logger.error('Error while init: {}'.format(error))
            self.status = False

    @staticmethod
    def apply_correction(u, u_base=.6, ratio=2000 / (5 - 1)):
        if u - u_base > 0.05:
            return (u + u_base) * ratio
        else:
            return 0

    def measure(self):
        return self.ch_u.voltage * self.coeff_u, self.ch_i.voltage * self.coeff_i

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
    hioki = AnalogDeviceMPC()
    u, i = hioki.measure()
    print(f'u={u}, i={i}')
    # energy_meter = AnalogDeviceADS(5)
    # try:
    #     while True:
    #         # ldr, t = energy_meter.make_measurement()
    #         voltage, current = energy_meter.measure()
    #         print('voltage = {:.2f} V, current = {:.2f} A'.format(voltage, current))
    #         time.sleep(1)
    #         # print('-' * 30)
    # except KeyboardInterrupt:
    #     logger.info('Script was interrupted by user.')
    #     pass


if __name__ == '__main__':
    main()
