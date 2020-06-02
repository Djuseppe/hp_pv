# import board
# import digitalio
# import busio
from RPi import GPIO as gpio
import time
import sys


channel = 20
gpio.setmode(gpio.BCM)
gpio.setup(channel, gpio.OUT, initial=gpio.LOW)

def motor_off(pin):
    gpio.output(pin, gpio.HIGH)  # Turn motor on


def motor_on(pin):
    gpio.output(pin, gpio.LOW)  # Turn motor off


if __name__ == '__main__':
	if len(sys.argv) > 1:
		sleep_time = int(sys.argv[1]) * 3600
	else:
		sleep_time = 1 * 3600
	
	print('Relay has been initialized for {} hours.'
	.format(int(sleep_time / 3600)))
    
	try:
		motor_on(channel)
		time.sleep(sleep_time)
		motor_off(channel)
		time.sleep(0.5)
		gpio.cleanup()
	except KeyboardInterrupt:
		gpio.cleanup()
	# 
