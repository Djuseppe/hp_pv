from abc import ABC
import time
import board
import busio
import numpy as np
import pandas as pd
import logging
import pytz
from datetime import datetime
import functools
import digitalio
from lib.influx.influx_lib import InfluxDBServerError, InfluxClient
from requests.exceptions import ConnectionError
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
if not len(logger.handlers):
    logger.addHandler(stream_handler)
    logger.propagate = False


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
            writer=None,
            time_format='%Y.%m.%d %H:%M:%S.%z',
            tz_prague=pytz.timezone('Europe/Prague'),
            coeff_i=10/2, coeff_u=300/2):
        self.writer = writer
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

            self.ch_eva = AnalogIn(mcp, MCP.P3)
            self.ch_cond = AnalogIn(mcp, MCP.P4)
            self.ch_cw = AnalogIn(mcp, MCP.P5)

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
        p_corr = 0
        fr_eva = self.apply_correction(self.ch_eva.voltage, ratio=2000 / (5 - .9))
        fr_cond = self.apply_correction(self.ch_cond.voltage)  #  (self.ch4.voltage, ratio=2000 / (5 - 1))
        fr_cw = self.apply_correction(self.ch_cw.voltage)
        p = self.ch_u.voltage * self.coeff_u * self.ch_i.voltage * self.coeff_i + p_corr
        return p, fr_eva, fr_cond, fr_cw

    @wait
    def make_measurement(self):
        # time_vals = list()
        cols = ['hp_el_power', 'fr_eva', 'fr_cond', 'fr_cw']
        col_fr = ['fr_eva', 'fr_cond', 'fr_cw']
        col_power = ['hp_el_power']
        # res_array = np.zeros(shape=(self.interval, n_cols), dtype=float)
        df = pd.DataFrame(
            np.zeros(shape=(self.interval, len(cols)), dtype=float),
            index=range(self.interval),
            columns=cols
        )
        for i in range(self.interval):
            # time_vals.append(datetime.now(self.tz_prague).strftime(self.time_format))
            # power, fr_e, fr_c, fr_cw = self.measure()
            meas = self.measure()
            df.loc[i, :] = meas
            time.sleep(0.9)
        if not df.empty:
            _df = df[~df.isna()]
            return _df[col_power].mean().round(2).to_dict(), _df[col_fr].mean().round(2).to_dict()
        else:
            return np.NZERO

    def write_to_db(self, power, flows):
        tags_dict = {
            'project': "hp_pv",
            'type': "hp",
            'device': "rpi42n"
        }
        try:
            t = datetime.now(self.tz_prague).strftime(self.time_format)
            # write hp el power
            self.writer.write(
                t,
                tags_dict,
                'hp_el_power',
                **power
            )
            # write flow rates
            self.writer.write(
                t,
                tags_dict,
                'hp_flow_rates',
                **flows
            )

        except (ConnectionError, InfluxDBServerError) as e:
            logger.error('{}'.format(e))


def main():
    m = AnalogDeviceMPC()
    # values = hioki.measure()
    # print(values)
    # print(m.make_measurement())

    while True:
        print(m.make_measurement())

    # print(f'u={u:.1f}, i={i:.1f}')
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
