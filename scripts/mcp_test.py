import time
import math
import busio
import board
import digitalio
import sys
import RPi.GPIO as GPIO

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn


def apply_correction(u, u_base=.6, ratio=2000 / (5 - 1)):
	# ratio = 2000 / (5 - .6)
	u_calc = u - u_base
	if u - u_base > 0.05:
		return (u + u_base) * ratio
	else:
		return 0


def main():
	spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
	cs = digitalio.DigitalInOut(board.D21)
	mcp = MCP.MCP3008(spi, cs)

	coeff = 400
	coeff_i, coeff_u = 10/2, 300/2
	ch_u = AnalogIn(mcp, MCP.P6)
	ch_i = AnalogIn(mcp, MCP.P7)

	ch3 = AnalogIn(mcp, MCP.P3)
	ch4 = AnalogIn(mcp, MCP.P4)
	ch5 = AnalogIn(mcp, MCP.P5)

	# while True:
	# 	# print('Raw ADC Value: ', channel.value)
	#
	# 	# print('eva = {:.2f}, cond = {:.2f}, cold_wat = {:.2f}'.format(
	# 	# 	ch3.voltage, ch4.voltage, ch5.voltage))
	#
	# 	# print('eva = {:.2f}, cond = {:.2f}, cold_wat = {:.2f}'.format(
	# 	# 	ch3.voltage*coeff, ch4.voltage*coeff, ch5.voltage*coeff))
	#
	# 	u_eva, u_cond = apply_correction(ch3.voltage, ratio=2000 / (5 - .9)), apply_correction(ch4.voltage, ratio=2000 / (5 - 1))
	# 	u_cw = apply_correction(ch5.voltage)
	# 	print('eva = {:.2f}, cond = {:.2f}, cold_wat = {:.2f}'.format(u_eva, u_cond, u_cw))
	#
	# 	# print('ADC Voltage: {:.3f} V = {:.3f} V'.format(ch_volt, ch_volt * ratio))
	# 	time.sleep(1)

	while True:

		print('ch0 = {:.2f}, ch1 = {:.1f}'.format(
			ch_u.voltage*coeff_u, ch_i.voltage*coeff_i))
		time.sleep(1)


if __name__ == '__main__':
	main()
