import argparse
from lib.influx.influx_lib import InfluxClient
from lib.modbus_lib import ModbusClient


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
            dbname='uceeb'
        )
    )
    m.start_reading()


if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port)
