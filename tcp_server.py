from lib.tcp_lib import Server
from lib.relay import Pump
import logging


# set logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('in module %(name)s, in func %(funcName)s, '
                              '%(levelname)-8s: [%(filename)s:%(lineno)d] %(message)s')
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
if not len(logger.handlers):
    logger.addHandler(stream_handler)
    logger.propagate = False


def main():
    s = Server('10.208.8.106')
    pump = Pump(auto_turn_off=2 * 3600)
    try:
        while True:
            conn, addr = s.socket.accept()
            # loop serving the new client
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                # print(f'data received: {data}')
                if data == bytes('on', 'utf-8'):
                    pump.turn_on()
                    logger.info('get it, pump is on!')
                elif data == bytes('off', 'utf-8'):
                    pump.turn_off()
                    logger.info('get it, pump is off!')
                else:
                    logger.info(f'Command to rp42n was not understood: {data}')

                # Echo back the same data you just received
                # s.send(data)
            conn.close()
    except KeyboardInterrupt:
        logger.info('Interrupted by user: exiting')
    finally:
        s.socket.close()
        pump.gpio_clean()


if __name__ == '__main__':
    main()
