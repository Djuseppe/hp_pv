from abc import ABC
import time
# import board
# import busio
# import digitalio
# import adafruit_dht as dht_lib
# import adafruit_mcp3xxx.mcp3008 as MCP
# from adafruit_mcp3xxx.analog_in import AnalogIn
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


class MeasurePV(Device):
    def measure(self, interval=10):
        return 235 + random.random() * 5

    @wait
    def make_measurement(
            self, time_format='%Y.%m.%d %H:%M:%S.%z',
            tz_prague=pytz.timezone('Europe/Prague')
    ):
        start_time = time.time()
        time_vals = list()
        voltage, current = np.zeros(self.interval, dtype=float), np.zeros(self.interval, dtype=float)
        for i in range(self.interval):
            voltage[i], current[i] = self.measure()
            # res[i] = self.measure() if i != 4 else np.nan
            # time_vals.append(round(time.time() - start_time, 2))
            time_vals.append(datetime.now(tz_prague).strftime(time_format))
            time.sleep(0.9)

        return voltage[~np.isnan(voltage)].mean(), current[~np.isnan(current)].mean(), time_vals[-1]


class DHTTemp(Device):
    def __init__(self, interval=10):
        self.interval = interval
        try:
            self.dhtDevice = dht_lib.DHT22(board.D19)
        except RuntimeError as error:
            logger.debug('DHT was not inited: {}'.format(error))

    def measure(self):
        try:
            self.dhtDevice.measure()
            _temp = self.dhtDevice.temperature
            _hum = self.dhtDevice.humidity
        except RuntimeError as e:
            logger.debug('Error while measuring: {}'.format(e))
            _temp, _hum = np.nan, np.nan
        temp = _temp if isinstance(_temp, (float, int)) else np.nan
        hum = _hum if isinstance(_hum, (float, int)) else np.nan
        return temp, hum

    @wait
    def make_measurement(
            self, time_format='%Y.%m.%d %H:%M:%S.%z',
            tz_prague=pytz.timezone('Europe/Prague')
    ):
        temps = np.zeros(self.interval, dtype=float)
        hums = np.zeros(self.interval, dtype=float)
        time_vals = list()
        # start_time = datetime.now().strftime(time_format)
        # print('start_time = {}'.format(start_time))
        start = time.time()
        for i in range(self.interval):
            temps[i], hums[i] = self.measure()
            # res[i] = self.measure() if i != 4 else np.nan
            # time_vals.append(round(time.time() - start_time, 2))
            time_vals.append(datetime.now(tz_prague).strftime(time_format))
            time.sleep(0.9)
        stop = time.time()
        if stop - start < self.interval:
            time.sleep(self.interval - (stop - start))
        return temps[~np.isnan(temps)].mean(), hums[~np.isnan(hums)].mean(), time_vals[-1]


class LDRSensor(Device):
    def __init__(self, interval=10, digital_io=board.D5, ch_num=MCP.P0):
        self.interval = interval
        try:
            spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
            cs = digitalio.DigitalInOut(digital_io)
            mcp = MCP.MCP3008(spi, cs)
            self.channel = AnalogIn(mcp, ch_num)
            # print('debug')
        except Exception as error:
            logger.error('Error while init: {}'.format(error))
            self.status = False

    def measure(self):
        return self.channel.value / 500

    @wait
    def make_measurement(
            self, time_format='%Y.%m.%d %H:%M:%S.%z',
            tz_prague=pytz.timezone('Europe/Prague')):
        time_vals = list()
        lcd_vals = np.zeros(self.interval)
        for i in range(self.interval):
            time_vals.append(datetime.now(tz_prague).strftime(time_format))
            lcd_vals[i] = self.measure()
            time.sleep(0.9)
            return lcd_vals[~np.isnan(lcd_vals)].mean(), time_vals[-1]


class AnalogDevice(Device):
    def __init__(self, interval=10, digital_io=board.D5, ch_num=MCP.P2):
        self.interval = interval
        self.time_format = '%Y.%m.%d %H:%M:%S.%z'
        self.tz_prague = pytz.timezone('Europe/Prague')
        try:
            spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
            cs = digitalio.DigitalInOut(digital_io)
            mcp = MCP.MCP3008(spi, cs)
            self.channel = AnalogIn(mcp, ch_num)
            # print('debug')
        except Exception as error:
            logger.error('Error while init: {}'.format(error))
            self.status = False

    def measure(self):
        return self.channel.voltage, datetime.now(self.tz_prague).strftime(self.time_format)

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


class PV(Device):
    def __init__(self, interval=10, digital_io=board.D5, ch_num=MCP.P1):
        self.interval = interval
        try:
            spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
            cs = digitalio.DigitalInOut(digital_io)
            mcp = MCP.MCP3008(spi, cs)
            self.channel = AnalogIn(mcp, ch_num)
            # print('debug')
        except Exception as error:
            logger.error('Error while init: {}'.format(error))
            self.status = False

    def measure(self):
        return self.channel.voltage * 2

    @wait
    def make_measurement(
            self, time_format='%Y.%m.%d %H:%M:%S.%z',
            tz_prague=pytz.timezone('Europe/Prague')):
        time_vals = list()
        volt_vals = np.zeros(self.interval)
        for i in range(self.interval):
            time_vals.append(datetime.now(tz_prague).strftime(time_format))
            volt_vals[i] = self.measure()
            time.sleep(0.9)
            return volt_vals[~np.isnan(volt_vals)].mean(), time_vals[-1]


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
