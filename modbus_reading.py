import time
import os
import argparse
from lib.modbus_lib import ModbusClient
from lib.influx.influx_lib import InfluxClient
from apscheduler.schedulers.background import BackgroundScheduler


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
    m.write_to_db()
    print(res)
    m.client.close()


def main(host, port, interval):
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
            time.sleep(5*60)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()


if __name__ == '__main__':
    args = parse_args()
    main(args.host, args.port, args.interval)
