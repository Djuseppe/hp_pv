import time
import math
import busio
import board
import digitalio
import sys

import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
cs = digitalio.DigitalInOut(board.D5)
mcp = MCP.MCP3008(spi, cs)

ratio = 300 / 2
# if len(sys.argv) > 1:
# 	ch_num = sys.argv[1]
# else:
# 	ch_num = 
channel = AnalogIn(mcp, MCP.P7)
while True:
	# print('Raw ADC Value: ', channel.value)
	ch_volt = channel.voltage
	print('Channel voltage = {:.2f}'.format(ch_volt))
	# print('ADC Voltage: {:.3f} V = {:.3f} V'.format(ch_volt, ch_volt * ratio))
	time.sleep(1)
