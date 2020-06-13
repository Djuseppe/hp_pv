import RPi.GPIO as GPIO
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()


class Decorators(object):
    @classmethod
    def cleaning_up(cls, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            GPIO.cleanup()
            func(*args, **kwargs)
            GPIO.cleanup()
            # return res
        return wrapped


class Pump:
    def __init__(self, channel=12, auto_turn_off=5):
        self.channel = channel
        self.turn_off_time = auto_turn_off
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.channel, GPIO.OUT)

    @staticmethod
    def clean():
        GPIO.cleanup()

    @Decorators.cleaning_up
    def turn_off(self):
        GPIO.output(self.channel, GPIO.HIGH)

    @Decorators.cleaning_up
    def turn_on(self):
        GPIO.output(self.channel, GPIO.LOW)
        time.sleep(self.turn_off_time)


if __name__ == '__main__':
    pump = Pump()
    pump.turn_on()
    
    # try:
    #     motor_on(channel)
    #     time.sleep(1)
    #     motor_off(channel)
    #     time.sleep(1)
    #     GPIO.cleanup()
    # except KeyboardInterrupt:
    #     GPIO.cleanup()
