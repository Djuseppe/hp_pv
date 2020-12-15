from lib.meas_lib_new import TempMeasMAX31865 as Sensor
import board
import time


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


def temp_test():
    m = Sensor(input_list=[board.D18, board.D24], interval=5, therm_names=['se_1', 'se_2'])
    # m = Sensor(input_list=[board.D23], interval=5, therm_names=['se_23'])

    while True:
        try:
            res = m.make_measurement()
            print(time.time(), '\t'*2, res)
            # m.write_to_db(res)
        except KeyboardInterrupt:
            print('Interrupted by user.')
            break


if __name__ == '__main__':
    # args = parse_args()
    # main(host=args.host, port=args.port)
    # main()
    temp_test()
