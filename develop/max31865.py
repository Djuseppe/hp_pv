import board
import busio
import digitalio
import adafruit_max31865
import time

# create a spi object
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

# allocate a CS pin and set the direction
cs1 = digitalio.DigitalInOut(board.D20)
# cs1.direction = digitalio.Direction.OUTPUT

cs2 = digitalio.DigitalInOut(board.D21)
# cs2.direction = digitalio.Direction.OUTPUT
cs3 = digitalio.DigitalInOut(board.D12)
cs4 = digitalio.DigitalInOut(board.D25)
cs5 = digitalio.DigitalInOut(board.D26)
cs6 = digitalio.DigitalInOut(board.D24)
cs7 = digitalio.DigitalInOut(board.D22)
cs8 = digitalio.DigitalInOut(board.D27)
cs9 = digitalio.DigitalInOut(board.D17)
cs10 = digitalio.DigitalInOut(board.D4)

# create a thermocouple object with the above
thermocouple_1 = adafruit_max31865.MAX31865(spi, cs1, wires=4)
thermocouple_2 = adafruit_max31865.MAX31865(spi, cs2, wires=4)
thermocouple_3 = adafruit_max31865.MAX31865(spi, cs3, wires=4)
thermocouple_4 = adafruit_max31865.MAX31865(spi, cs4, wires=4)
thermocouple_5 = adafruit_max31865.MAX31865(spi, cs5, wires=4)
thermocouple_6 = adafruit_max31865.MAX31865(spi, cs6, wires=4)
thermocouple_7 = adafruit_max31865.MAX31865(spi, cs7, wires=4)
thermocouple_8 = adafruit_max31865.MAX31865(spi, cs8, wires=4)
thermocouple_9 = adafruit_max31865.MAX31865(spi, cs9, wires=4)
thermocouple_10 = adafruit_max31865.MAX31865(spi, cs10, wires=4)
therm_list = [
    thermocouple_1,
    thermocouple_2,
    thermocouple_3,
    thermocouple_4,
    thermocouple_5,
    thermocouple_6,
    thermocouple_7,
    thermocouple_8,
    thermocouple_9,
    thermocouple_10
]

while True:
    try:
        for i, therm in enumerate(therm_list):
            print('t_{} = {:.1f} C\t'.format(i + 1, therm.temperature), end='')
        print()
        # print(
        #     'thermocouple_1 = {:.2f} C,\tthermocouple_2 = {:.2f} C'.format(
        #         thermocouple_1.temperature,
        #         thermocouple_2.temperature
        #     )
        # )
        # print('thermocouple_2 = {:.2f}'.format(thermocouple_2.temperature))
        time.sleep(1)
    except KeyboardInterrupt:
        print('Interrupted by user.')
        break
