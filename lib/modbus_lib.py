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
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadBuilder
from lib.influx.influx_lib import InfluxDBServerError, InfluxClient
from requests.exceptions import ConnectionError

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
# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)
if not len(logger.handlers):
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.propagate = False


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

    def connect(self):
        try:
            self.conn_status = self.client.connect()
        except ConnectionException as error:
            logger.error('Failed to connect to host {} at port {}: {}'.format(self.host, self.port, error))

    def disconnect(self):
        self.client.close()
        self.conn_status = False

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
        # if self.conn_status:
        #     pass
        # else:
        #     self.connect()
            # self.conn_status = True
        try:
            register_read = self.client.read_holding_registers(reg_num).registers[0]
        except ModbusIOException as error:
            register_read = np.NZERO
            logger.info('Error when reading register num = {}: {}'.format(reg_num, error))
        # self.disconnect()
        return register_read

    @staticmethod
    def _build_payload(value):
        builder = BinaryPayloadBuilder(
            byteorder=Endian.Big,
            wordorder=Endian.Little
        )
        # builder.add_32bit_float(value)
        builder.add_32bit_int(value)
        payload = builder.to_registers()[0]
        return payload

    def _write_one_register(self, reg_num, value):
        payload = self._build_payload(value)
        self.client.write_register(reg_num, payload, skip_encode=False)

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

    def set_upper_temperature(self, temp):
        temp *= 10
        self._write_one_register(0, temp)
        self._write_one_register(1, 0)
        self._write_one_register(2, 0)

    def set_bottom_temperature(self, temp):
        temp *= 10
        self._write_one_register(0, temp)
        self._write_one_register(1, 7)
        self._write_one_register(2, 7)

    def set_hysteresis(self, value):
        half_hyster = value / 2
        _half_hyster = half_hyster if isinstance(half_hyster, int) else int(half_hyster)
        self._write_one_register(4, -_half_hyster)
        self._write_one_register(5, _half_hyster)

    def start_hp(self):
        self._write_one_register(3, 1)

    def stop_hp(self):
        self._write_one_register(3, 0)

    # @Decorators.wait
    def _create_nan_dict(self):
        return {k: np.NZERO for k in self.keys}

    def write_to_db(self):
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
        except (ConnectionError, InfluxDBServerError) as e:
            logger.error('{}'.format(e))

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
    return parser.parse_args()


def main(host, port):
    m = ModbusClient(
        host, port, writer=InfluxClient(
            host='localhost', port=8086,
            user='eugene', password='7vT4g#1@K',
            dbname='home'
        )
    )
    # m = ModbusClient(host, port, )
    # m._write_one_register(0, 20)
    m.write_to_db()
    res = m.read_registers()
    print(res)


if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port)
