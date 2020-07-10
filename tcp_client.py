from lib.tcp_lib import Client


def main():
    host = '10.208.8.106'
    port = 65432
    c = Client(host, port)
    data = 'off'
    c.send(data)


if __name__ == '__main__':
    main()
