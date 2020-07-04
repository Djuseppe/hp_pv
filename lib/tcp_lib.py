import socket
from datetime import datetime
import logging
import argparse

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


def parse_args():
    parser = argparse.ArgumentParser(
        description='parse data to be sent to tcp server')
    parser.add_argument('--data', type=str, required=True,
                        default='Hello world!',
                        help='data')
    return parser.parse_args()


class Server:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.socket = self._start()

    def _start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen()
        return s

    def send_reply(self, reply):
        while True:
            conn, addr = self.socket.accept()
            with conn:
                print('Connected by', addr)
                _ = conn.recv(4096)
                # print(data.decode())
                now = datetime.now()
                time_now = '-'.join([str(i) for i in [now.hour, now.minute, now.second]])
                conn.sendall(bytes('time is ' + time_now, 'utf-8'))

    # def run(self):
    #     # init a measurement class
    #     m = Measurement(interval=2)
    #     while True:
    #         conn, addr = self.socket.accept()
    #         with conn:
    #             print('Connected by', addr)
    #             _ = conn.recv(1024)
    #             _res = m.measure()
    #             res = _res if isinstance(_res, (float, int)) else np.nan
    #
    #             conn.sendall(
    #                 bytes(
    #                     '{}\t{:.2f}'.format(time.strftime(m.time_format), res), 'utf-8'
    #                 ))
                # time = time.now()
                # now = datetime.now()
                # time_now = ':'.join([str(i) for i in [now.hour, now.minute, now.second]])
                # conn.sendall(bytes('time = {}, res = {:.2f}'.format(time_now, res), 'utf-8'))


class Client:
    def __init__(self, host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        # self.socket = self._start()

    def send(self, data=None):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(bytes(data, 'utf-8'))


def main():
    s = Server()
    try:
        while True:
            conn, addr = s.socket.accept()
            # loop serving the new client
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print(f'data received: {data}')
                if data == bytes('on', 'utf-8'):
                    print('get it, pump on!')
                elif data == bytes('off', 'utf-8'):
                    print('get it, pump off!')
                else:
                    logger.debug(f'Command to rp42n was not understood: {data}')

                # Echo back the same data you just received
                # s.send(data)
            conn.close()
    except KeyboardInterrupt:
        logger.info('Interrupted by user: exiting')
    finally:
        s.socket.close()


def send_data(data):
    c = Client()
    c.send(data)


if __name__ == '__main__':
    args = parse_args()
    send_data(args.data)
    # main()
