import board
import time
import logging
# from lib.meas_lib_new import parse_args, DHTTemp
# from lib.influx.influx_lib import InfluxClient
from relay import Pump as Relay
from lib.meas_lib_new import DHTTemp

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("'in module %(name)s, in func %(funcName)s, @ %(asctime)s; %(levelname)s; %(message)s",
                              "%Y-%m-%d %H:%M:%S.%z")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

f_handler = logging.FileHandler('lib/heater_clt.log')
f_handler.setLevel(logging.DEBUG)
f_handler.setFormatter(formatter)
logger.addHandler(f_handler)

# if not len(logger.handlers):
logger.addHandler(stream_handler)
logger.propagate = True
# logger.addHandler(f_handler)
# logger.propagate = False


class HeatingSystem:
    def __init__(self, hea_set=20, hyster=5, cool_set=25,
                 thermometer=DHTTemp(interval=10, board_ch=board.D20),
                 interval=10, cooler=Relay(19), heater=Relay(13)):
        self.hea_set = hea_set
        self.cool_set = cool_set
        self.hyster = hyster
        self.interval = interval
        # init instances
        self.heater = heater
        self.cooler = cooler
        self.thermometer = thermometer

        self.heater.turn_off()
        self.cooler.turn_off()

    def clean(self):
        self.heater.gpio_clean()
        self.cooler.gpio_clean()

    def temp_meas(self):
        return self.thermometer.make_measurement().get('amb_temp', 20)

    def run(self):
        while True:
            try:
                temp = self.temp_meas()
                if temp <= self.hea_set:
                    self.heater.turn_on()
                    while temp <= self.hea_set + self.hyster:
                        logger.info(f'Heater is running @ temp = {temp:.1f} [C]')
                        temp = self.temp_meas()
                        # time.sleep(1)
                else:
                    self.stop()
                    logger.info(f'Current temperature = {temp:.1f} [C]')
                    time.sleep(1)
                self.clean()
            except KeyboardInterrupt:
                self.clean()
                print('Interrupted by user.')
                break


if __name__ == '__main__':
    HeatingSystem().run()
