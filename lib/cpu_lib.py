from gpiozero import CPUTemperature
import RPi.GPIO as GPIO
import time
import numpy as np
import functools


def wait(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        wait_time = 10
        start = time.time()
        res = func(*args, **kwargs)
        stop = time.time()
        if stop - start < wait_time:
            time.sleep(wait_time - (stop - start))
        return res
    return wrapped


class CoolingSystem:
    def __init__(self, setpoint=45, hyster=5, interval=10, channel=23):
        self.hyster = hyster
        self.setpoint = setpoint
        self.interval = interval
        self.channel = channel
        self.cpu = CPUTemperature()
        self._setmode()
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(self.channel, GPIO.OUT)

    def _setmode(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.channel, GPIO.OUT)

    def cool(self):
        self._setmode()
        GPIO.output(self.channel, GPIO.LOW)

    def stop(self):
        self._setmode()
        GPIO.output(self.channel, GPIO.HIGH)

    @staticmethod
    def clean():
        GPIO.cleanup()

    def measure(self):
        return self.cpu.temperature

    @wait
    def make_measurement(self):
        temp_arr = np.zeros(self.interval, dtype=float)
        for i in range(self.interval):
            temp_arr[i] = self.measure()
            time.sleep(0.9)
        return temp_arr[~np.isnan(temp_arr)].mean()

    def run(self):
        self.clean()
        while True:
            try:
                temp = self.make_measurement()
                if temp >= self.setpoint:
                    self.cool()
                    while temp >= self.setpoint - self.hyster:
                        print('Current temperature = {:.1f}'.format(temp))
                        temp = self.make_measurement()
                        # time.sleep(1)
                else:
                    self.stop()
                    print('Current temperature = {:.1f}'.format(temp))
                    time.sleep(1)
                self.clean()
            except KeyboardInterrupt:
                self.clean()
                print('Interrupted by user.')
                break


def main():
    cooler = CoolingSystem()
    cooler.run()


if __name__ == '__main__':
    main()
