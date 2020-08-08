from lib.meas_lib_new import parse_args, DHTTemp
from lib.influx.influx_lib import InfluxClient


def main(host, port):
    m = DHTTemp(
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
            print(res)
            m.write_to_db(res)
        except KeyboardInterrupt:
            print('Interrupted by user.')
            break


if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port)
