from abc import ABC
from datetime import datetime
import pytz
import logging
from influxdb.client import InfluxDBClientError
from influxdb import InfluxDBClient

# set logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('in module %(name)s, in func %(funcName)s, '
                              '%(levelname)-8s: [%(filename)s:%(lineno)d] %(message)s')
file_handler = logging.FileHandler('influx_lib.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)
if not len(logger.handlers):
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.propagate = False


class InfluxInterface(ABC):
    def write(self, *args, **kwargs):
        pass

    def read(self):
        pass


class InfluxClient(InfluxInterface):
    def __init__(
            self, host='127.0.0.1', port=8086,
            user=None, password=None,
            dbname='db0', tech_ind=0
    ):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.tech_ind = tech_ind
        self.user = user
        self.password = password
        self.ssl = False
        self.verify_ssl = False
        self.client = InfluxDBClient(
            host=self.host, port=self.port, database=self.dbname,
            username=self.user, password=self.password,
            ssl=self.ssl, verify_ssl=self.verify_ssl
        )
        try:
            _ver = self.client.ping()
            logger.info('Connected to DB {} version = {}'.format(self.dbname, _ver))
        except Exception as error:
            logger.error('Connection error: {}'.format(error))

    def create_json(self, time_val, tags, measurement, **kwargs):
        json_body = [
            {
                "measurement": measurement,
                "tags": tags,
                "time": time_val,
                "fields": kwargs,
            }
        ]
        # return json.dumps(json_body)
        return json_body

    def create_db(self, db_name):
        self.client.create_database(db_name)

    def get_meas_list(self):
        return self.client.get_list_measurements()

    def write(self, time_val, **kwargs):
        self.client.write_points(self.create_json(time_val, **kwargs))
        # return self.create_json(time_val, **kwargs)

    def read(self):
        query = 'SELECT * FROM {}'.format('outdoor_weather')
        try:
            result = self.client.query(query, database=self.dbname)
        except InfluxDBClientError as error:
            logger.error('Error while trying to query DB: {}'.format(error))
            result = None
        return 'result = {}'.format(result)


def main():
    tz_prague = pytz.timezone('Europe/Prague')
    time_format = '%Y-%m-%dT%H:%M:%S.%z'
    client = InfluxClient()
    t = datetime.now(tz_prague).strftime(time_format)
    # print(client.create_json(
    #     time_val=t, temperature=30.1, humidity=66.4
    # ))
    # print(client.write(
    #     time_val=t, temperature=30.1, humidity=66.4
    # ))
    # print(client.read())
    # print(client.get_meas_list())
    # print(client.get_meas_list())
    # client.write(
    #     time_val=t, temperature=30.5, humidity=66.8
    # )
    print(client.read())
    print()


def vpn():
    client = InfluxClient(
        host=r'vpn.feramat.com', port=8086,
        user='user', password='b3WDCGoyCsiUTk9pX1dd',
        dbname='db0'
    )
    tz_prague = pytz.timezone('Europe/Prague')
    time_format = '%Y-%m-%dT%H:%M:%S.%z'
    t = datetime.now(tz_prague).strftime(time_format)
    # client.write(
    #     time_val=t, temperature=30.5, humidity=66.8
    # )
    print(client.read())


if __name__ == '__main__':
    # main()
    vpn()
