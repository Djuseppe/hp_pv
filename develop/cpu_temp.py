from gpiozero import CPUTemperature
import time

cpu = CPUTemperature()

while True:
    try:
        print('cpu temp = {:.2f}'.format(cpu.temperature))
        time.sleep(1)
    except KeyboardInterrupt:
        print('Exiting')
        break