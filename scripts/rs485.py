import time
import serial
from RPi import GPIO as gpio
	
	
	
ser = serial.Serial(
	port='/dev/serial0',
	baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1,
    rtscts=True,
    dsrdtr=True
)

while True:
	val = ser.readline()
	print(val)
	time.sleep(1)
