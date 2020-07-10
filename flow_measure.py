from lib.influx.influx_lib import InfluxClient
from lib.meas_lib_new import parse_args
from lib.flow_lib import AnalogDeviceMPC


def main(host, port):
    m = AnalogDeviceMPC(
        writer=InfluxClient(
            host=host, port=port,
            user='eugene', password='7vT4g#1@K',
            dbname='uceeb'
        )
    )

    while True:
        try:
            power, flows = m.make_measurement()
            print(power, flows)
            m.write_to_db(power, flows)
        except KeyboardInterrupt:
            print('Interrupted by user.')
            break


if __name__ == '__main__':
    args = parse_args()
    main(host=args.host, port=args.port)
