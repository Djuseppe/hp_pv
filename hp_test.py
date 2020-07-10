import time
import os
import argparse
import logging
from lib.modbus_lib import ModbusClient
from lib.influx.influx_lib import InfluxClient, DBReader
from apscheduler.schedulers.background import BackgroundScheduler
from lib.tcp_lib import Client

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


def parse_args():
    """Parse the args from main."""
    parser = argparse.ArgumentParser(
        description='Run modbus registers reader')
    parser.add_argument('--host', type=str, required=False,
                        default='147.32.99.72',
                        help='hostname of heat pump Modbus tcp ip')
    parser.add_argument('--port', type=int, required=False, default=64072,
                        help='port of heat pump Modbus tcp ip')
    parser.add_argument('--interval', type=int, required=False, default=60,
                        help='reading interval in seconds (runs scheduler)')
    return parser.parse_args()


def ctrl(host='147.32.99.72', port=64072):
    m = ModbusClient(
        host, port, writer=InfluxClient(
            host='localhost', port=8086,
            user='eugene', password='7vT4g#1@K',
            dbname='uceeb'
        )
    )
    res = m.read_registers()
    print(res)
    m.client.close()


def main_old(host, port, interval):
    scheduler = BackgroundScheduler()
    scheduler.add_job(ctrl, 'interval', seconds=interval, args=(
        host, port
    ))
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    start = time.time()
    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            print('Still working at time = {:.2f} hour after start'.format((time.time() - start) / 3600))
            time.sleep(5 * 60)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()


def start_hp():
    hp = ModbusClient()
    hp.start_hp()
    hp.client.close()

    # p = Client('10.208.8.106', 65432)
    # p.send('on')


def stop_hp():
    hp = ModbusClient()
    hp.stop_hp()
    hp.client.close()

    # p = Client('10.208.8.106', 65432)
    # p.send('off')


def main():
    t_top, t_bot = 45, 45

    db = DBReader()
    hp = ModbusClient()
    pv_power, res = db.get_data_from_db()
    if pv_power >= 1e3:

        hp.set_bottom_temperature(t_bot)
    else:
        hp.set_upper_temperature(t_top)
    hp.client.close()

    print()


if __name__ == '__main__':
    # pass
    start_hp()

    # stop_hp()
    # main()
