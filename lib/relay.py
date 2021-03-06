import RPi.GPIO as GPIO
import time
from functools import wraps
import logging
import argparse

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()


class Decorators(object):
    @classmethod
    def cleaning_up(cls, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            GPIO.setmode(GPIO.BCM)
            try:
                func(*args, **kwargs)
            except KeyboardInterrupt:
                GPIO.cleanup()
        return wrapped


class Pump:
    def __init__(self, channel=12, auto_turn_off=5):
        # GPIO.cleanup()
        self.channel = channel
        self.turn_off_time = auto_turn_off
        self.gpio_set()

    def gpio_set(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.channel, GPIO.OUT)

    def gpio_clean(self):
        GPIO.cleanup()

    @Decorators.cleaning_up
    def turn_off(self):
        # self.gpio_set()
        GPIO.output(self.channel, GPIO.HIGH)

    @Decorators.cleaning_up
    def turn_on(self):
        # self.gpio_set()
        GPIO.output(self.channel, GPIO.LOW)
        # time.sleep(self.turn_off_time)

    # def __del__(self):
    #     GPIO.cleanup()


def gpio_clean():
    channel = 12
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(channel, GPIO.OUT)
    GPIO.cleanup()


def parse_args():
    parser = argparse.ArgumentParser(
        description='turn pump on')
    parser.add_argument('--time', type=float, required=False,
                        default=60,
                        help='turn on time')
    return parser.parse_args()


if __name__ == '__main__':
    # arguments = parse_args()
    # pump = Pump(auto_turn_off=arguments.time)
    # pump.gpio_set()
    # pump.turn_off()
    # GPIO.cleanup()

    fan = Pump(13)
    fan.turn_on()

