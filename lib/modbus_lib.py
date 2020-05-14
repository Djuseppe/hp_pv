from abc import ABC
import time
import pytz
import numpy as np
from datetime import datetime
from functools import wraps
import logging
import argparse
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusIOException
from lib.influx.influx_lib import InfluxClient

# import modbus_lib as mdb


# set logger here
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('in module %(name)s, in func %(funcName)s, '
                              '%(levelname)-8s: [%(filename)s:%(lineno)d] %(message)s')
file_handler = logging.FileHandler('modbus_lib.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class ModbusInterface(ABC):
    def __init__(self, interval=10):
        self.interval = interval

    def read_registers(self):
        pass

    def start_reading(self):
        pass


class Decorators(object):
    @classmethod
    def status_check(cls, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            conn_status = args[0].conn_status
            if conn_status:
                res = func(*args, **kwargs)
            else:
                logger.error('Failed to connect to host {} at port {}'.format(args[0].host, args[0].port))
                res = None
            return res

        return wrapped

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


class ModbusClient(ModbusInterface):
    def __init__(
            self, host='147.32.99.72', port=64072, interval=10, writer=None,
            time_format='%Y.%m.%d %H:%M:%S.%z',
            tz_prague=pytz.timezone('Europe/Prague')
    ):
        super().__init__(interval)
        self.host = host
        self.port = port
        self.writer = writer
        self.time_format = time_format
        self.tz_prague = tz_prague
        self.keys = [
            '0_set_temp',
            '1_sens_on',
            '2_sens_off',
            '3_hp_on_off',
            '4_hysteresis_on',
            '5_hysteresis_off'
        ]
        self.client, self.conn_status = self.client_init()

    def client_init(self):
        try:
            client = ModbusTcpClient(self.host, self.port)
            conn_status = client.connect()
        except ConnectionException as error:
            logger.error('Failed to connect to host {} at port {}: {}'.format(self.host, self.port, error))
            client = None
            conn_status = False
        return client, conn_status

    def _read_one_register(self, reg_num):
        try:
            register_read = self.client.read_holding_registers(reg_num).registers[0]
        except ModbusIOException as error:
            register_read = np.NZERO
            logger.info('Error when reading register num = {}: {}'.format(reg_num, error))
        return register_read

    @Decorators.wait
    @Decorators.status_check
    def read_registers(self):
        reg_dict = dict()
        for i, k in zip(range(6), self.keys):
            res = self._read_one_register(i)
            if k == '0_set_temp':
                res *= 0.1
            elif k == '4_hysteresis_on' and res >= 1000:
                res -= 2 ** 16
            elif k == '5_hysteresis_off' and res >= 1000:
                res -= 2 ** 16
            reg_dict[k] = float(res)
        return reg_dict
        # reg_dict = {k: v for k, v in zip(keys, [int(reg_0 / 10), reg_1, reg_2, reg_3, reg_4, reg_5])}

    def _create_nan_dict(self):
        return {k: np.NZERO for k in self.keys}

    def start_reading(self):
        while True:
            try:
                _res = self.read_registers()
                res = _res if _res is not None else self._create_nan_dict()
                tags_dict = {
                    'project': "hp_pv",
                    'type': "hp",
                    'device': "rpi44"
                }
                try:
                    self.writer.write(
                        datetime.now(self.tz_prague).strftime(self.time_format),
                        tags_dict,
                        'hp_measurement',
                        **res
                    )
                except Exception as e:
                    logger.error('{}'.format(e))
                print(res)
            except KeyboardInterrupt:
                logger.info('Interrupted by user: exiting.')
                break


class WriterPrinter:
    @staticmethod
    def write(*args):
        print(args)
        # print(kwargs)


def parse_args():
    """Parse the args from main."""
    parser = argparse.ArgumentParser(
        description='example code to play with InfluxDB')
    parser.add_argument('--host', type=str, required=False,
                        default='147.32.99.72',
                        help='hostname of heat pump tcp ip')
    parser.add_argument('--port', type=int, required=False, default=64072,
                        help='port of heat pump tcp ip')
    parser.add_argument('--user', type=str, required=False, default='eugene',
                        help='user name')
    parser.add_argument('--password', type=str, required=False, default='7vT4g#1@K',
                        help='user password')
    parser.add_argument('--database', type=str, required=False, default='uceeb',
                        help='database name')
    return parser.parse_args()


def main(host, port, user, password, database):
    print()
    m = ModbusClient(
        host, port, writer=InfluxClient(
            host=host, port=port,
            user=user, password=password,
            dbname=database
        )
    )
    m.start_reading()


if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port)
