# import adafruit_ads1x15 as adс
# from adafruit_ads1x15 import ads1x15 as adc
# from adafruit_ads1x15 import analog_in
import time
import busio
import board
from adafruit_ads1x15 import ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1015(i2c)
chan = AnalogIn(ads, ADS.P0)

print("{:>5}\t{:>5}".format('raw', 'v'))

while True:
    print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))
    time.sleep(0.5)

# print(dir(analog_in.AnalogIn()))

# analog_in.AnalogIn()


# GAIN = 1
# a = adc
#
# print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(4)))
# print('-' * 37)
# # Main loop.
# while True:
#     # Read all the ADC channel values in a list.
#     values = [0]*4
#     for i in range(4):
#         # Read the specified ADC channel using the previously set gain value.
#         values[i] = a.read_adc(i, gain=GAIN)
#
#     print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))
#     # Pause for half a second.
#     time.sleep(0.5)
