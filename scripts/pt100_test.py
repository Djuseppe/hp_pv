import busio
import board
import digitalio
import adafruit_max31865
import time


spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs = digitalio.DigitalInOut(board.D21)
sensor = adafruit_max31865.MAX31865(spi, cs, wires=4)


for i in range(61):
	print('Temperature = {:.2f}'.format(sensor.temperature))
	time.sleep(1)

