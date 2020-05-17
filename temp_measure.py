from lib.meas_lib_new import parse_args, TemperatureMeasurementDevice
from lib.influx.influx_lib import InfluxClient


def main(host, port):
    m = TemperatureMeasurementDevice(
        writer=InfluxClient(
            host=host, port=port,
            user='eugene', password='7vT4g#1@K',
            dbname='uceeb'
        )
    )
#
    while True:
        try:
            res = m.make_measurement()
            print(res, end='')
            m.write_to_db(res)
        except KeyboardInterrupt:
            print('Interrupted by user.')
            break


if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port)
