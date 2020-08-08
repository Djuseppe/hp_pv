from lib.meas_lib_new import TempMeasMAX31865 as Sensor
import board


def main(host=None, port=None):
    # m = Sensor(input_list=list(board.D16))
    m = Sensor()
#
    while True:
        try:
            res = m.make_measurement()
            print(res)
            # m.write_to_db(res)
        except KeyboardInterrupt:
            print('Interrupted by user.')
            break


if __name__ == '__main__':
    # args = parse_args()
    # main(host=args.host, port=args.port)
    main()
