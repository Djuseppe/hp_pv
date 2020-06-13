import time
import math
import busio
import board
import digitalio
import sys
import RPi.GPIO as GPIO

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D21)
mcp = MCP.MCP3008(spi, cs)

ratio = 10 / 2
# if len(sys.argv) > 1:
# 	ch_num = sys.argv[1]
# else:
# 	ch_num = ;;
ch3 = AnalogIn(mcp, MCP.P3)
ch4 = AnalogIn(mcp, MCP.P4)
ch5 = AnalogIn(mcp, MCP.P5)
while True:
	# print('Raw ADC Value: ', channel.value)

	print('ch3 = {:.2f}, ch4 = {:.2f}, ch5 = {:.2f}'.format(ch3.voltage, ch3.voltage, ch5.voltage))
	# print('ADC Voltage: {:.3f} V = {:.3f} V'.format(ch_volt, ch_volt * ratio))
	time.sleep(1)
