# import board
# import digitalio
# import busio
from RPi import GPIO as gpio
import time

# print('Hello blinka!')



gpio.setmode(gpio.BOARD)
gpio.setup(8, gpio.OUT, initial=gpio.LOW)

for i in range(5):
    gpio.output(8, gpio.HIGH)
    time.sleep(1)
    gpio.output(8, gpio.LOW)
    time.sleep(1)

print('Blinking is done.')