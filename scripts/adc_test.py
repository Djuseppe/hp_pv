import time
import busio
import board
from adafruit_ads1x15 import ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

GAIN = 1

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48, gain=GAIN)

# chan_diff = AnalogIn(ads, ADS.P0, ADS.P1)
ch_0 = AnalogIn(ads, ADS.P0)
ch_1 = AnalogIn(ads, ADS.P1)
ch_2 = AnalogIn(ads, ADS.P2)
ch_3 = AnalogIn(ads, ADS.P3)
# chan_1 = AnalogIn(ads, ADS.P1)

#print("{:>5}\t{:>5}".format('raw', 'v'))

while True:
    # print("diff = {:>5}   {:>5.3f}".format(chan_diff.value,
    # chan_diff.voltage))
    
	# print('channel 0 voltage = {:.3f}'.format(chan_0.voltage))
	# print(chan_1.voltage)
	print('ch_0 = {:.2f}\tch_1 = {:.2f}\tch_2 = {:.2f}\tch_3 = {:.2f}'
	.format(ch_0.voltage, ch_1.voltage, ch_2.voltage, ch_3.voltage))
	time.sleep(1)



