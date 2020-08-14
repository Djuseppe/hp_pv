import board
import pandas as pd
import numpy as np
import time
import argparse
from lib.relay import Pump as Fan
from lib.meas_lib_new import parse_args, DHTTemp, Decorators
# from lib.influx.influx_lib import InfluxClient
import adafruit_dht as dht_lib
import board


def parse_args():
    """Parse the args from main."""
    parser = argparse.ArgumentParser(
        description='set setoint temp and hum')
    parser.add_argument('--temp', type=float, required=False,
                        default=25,
                        help='setpoint temperature')
    parser.add_argument('--hum', type=float, required=False,
                        default=55,
                        help='setpoint humidity')
    return parser.parse_args()


def print_res(res_dict):
    print(f"temp = {res_dict.get('temp'):.2f} C    |    hum = {res_dict.get('hum'):.2f} %")


class DHTTempModified(DHTTemp):
    def __init__(self, board_ch):
        super().__init__(board_ch=board_ch)

    @Decorators.wait
    def make_measurement(self):
        df = pd.DataFrame(
            np.zeros((self.interval, 2), dtype=float),
            columns=['temp', 'hum'], index=range(self.interval))
        for i, (ind, _) in zip(range(self.interval), df.iterrows()):
            df.loc[ind, :] = self.measure()
            time.sleep(0.9)
        return df.mean().round(2).to_dict()


def test_temp():
    m = DHTTempModified(board_ch=board.D5)
#
    while True:
        try:
            res = m.make_measurement()
            print(res)
            # m.write_to_db(res)
        except KeyboardInterrupt:
            print('Interrupted by user.')
            break


def dht_test():
    dht = dht_lib.DHT22(board.D5)
    print(dht.temperature)


def main(temp_set, hum_set):
    temp_hyster, hum_hyster = 5, 5
    # init temp sensor & fan
    m = DHTTempModified(board_ch=board.D20)
    big_fan = Fan(channel=13)  # big fan channel

    # run ctrl
    while True:
        try:
            res = m.make_measurement()
            temp, hum = res.values()
            print_res(res)
            if temp >= temp_set or hum >= hum_set:
                # start cooling
                big_fan.turn_on()
                while (temp >= temp_set - temp_hyster) and (hum >= hum_set - hum_hyster):
                    print_res(res)
                    res = m.make_measurement()
                    temp, hum = res.values()
            else:
                # stop cooling
                big_fan.turn_off()
                print_res(res)
                time.sleep(1)
        except KeyboardInterrupt:
            print('Interrupted by user.')
            big_fan.turn_off()
            big_fan.gpio_clean()
            break


def stop_fan():
    big_fan = Fan(channel=13)  # big fan channel
    big_fan.turn_off()
    big_fan.gpio_clean()


if __name__ == '__main__':
    # args = parse_args()
    # main(temp_set=args.temp, hum_set=args.hum)

    # test_temp()
    dht_test()
    # stop_fan()

    # main()
    # fan = Fan(channel=19)
    # fan = Fan(channel=13)  # big fan channel
    # # fan.turn_on()
    # fan.turn_off()
