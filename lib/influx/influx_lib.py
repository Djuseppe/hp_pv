from abc import ABC
from datetime import datetime
import numpy as np
import pandas as pd
import pytz
import logging
import influxdb
from influxdb import InfluxDBClient, DataFrameClient
from influxdb.exceptions import InfluxDBClientError, InfluxDBServerError

# set logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('in module %(name)s, in func %(funcName)s, '
                              '%(levelname)-8s: [%(filename)s:%(lineno)d] %(message)s')
file_handler = logging.FileHandler('../influx_local_client.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


class InfluxInterface(ABC):
    def write(self, *args, **kwargs):
        pass

    def read(self, *args):
        pass


class InfluxClient(InfluxInterface):
    def __init__(
            self, host='127.0.0.1', port=8086,
            user=None, password=None,
            dbname='db0'
    ):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.ssl = False
        self.verify_ssl = False
        # self.ssl = True if self.host != '127.0.0.1' else False
        # self.verify_ssl = True if self.host != '127.0.0.1' else False
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

    @staticmethod
    def create_json(time_val, tags, measurement, **kwargs):
        json_body = [
            {
                "measurement": measurement,
                "tags": tags,
                "time": time_val,
                "fields": kwargs,
            }
        ]
        return json_body

    def create_db(self, db_name):
        self.client.create_database(db_name)

    def get_meas_list(self):
        return self.client.get_list_measurements()

    def write(self, time_val, tags, measurement, **kwargs):
        self.client.write_points(self.create_json(time_val, tags, measurement, **kwargs))
        # return self.create_json(time_val, **kwargs)

    def testing(self, *args, **kwargs):
        return self.create_json(*args, **kwargs)

    def read(self, measurement):
        query = 'SELECT * FROM {}'.format(measurement)
        try:
            result = self.client.query(query, database=self.dbname)
        except influxdb.client.InfluxDBClientError as error:
            logger.error('Error while trying to query DB: {}'.format(error))
            result = None
        return result

    def time_query(self, measurement='outdoor_weather', time_shift='1h'):
        query = "SELECT * FROM {} WHERE time > now() - {} AND time < now()".format(measurement, time_shift)
        try:
            result = self.client.query(query, database=self.dbname)
        except influxdb.client.InfluxDBClientError as error:
            logger.error('Error while trying to query DB: {}'.format(error))
            result = None
        return result


class InfluxDataFrameReader:
    def __init__(
        self, host='127.0.0.1', port=8086,
        user=None, password=None,
        dbname='db0'
    ):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.ssl = False
        self.verify_ssl = False
        # self.ssl = True if self.host != '127.0.0.1' else False
        # self.verify_ssl = True if self.host != '127.0.0.1' else False
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

    def time_query(self, measurement='outdoor_weather', time_shift='1h'):
        query = "SELECT * FROM {} WHERE time > now() - {} AND time < now()".format(measurement, time_shift)
        try:
            result = self.client.query(query, database=self.dbname)
        except influxdb.client.InfluxDBClientError as error:
            logger.error('Error while trying to query DB: {}'.format(error))
            result = None
        return result


class DataFrameProcessor:
    def __init__(self, df=None, tz=pytz.timezone('Europe/Prague')):
        self.df = df
        self.tz = tz

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        if isinstance(df, pd.core.frame.DataFrame):
            self._df = df
        else:
            self._df = None
            logger.error('DF passed is not pd.DataFrame object.')

    def convert_tz(self):
        self.df.index = self.df.index.tz_convert(self.tz)


# def main():
#     tz_prague = pytz.timezone('Europe/Prague')
#     time_format = '%Y-%m-%dT%H:%M:%S.%z'
#     client = InfluxClient()
#     t = datetime.now(tz_prague).strftime(time_format)
#     # print(client.create_json(
#     #     time_val=t, temperature=30.1, humidity=66.4
#     # ))
#     # print(client.write(
#     #     time_val=t, temperature=30.1, humidity=66.4
#     # ))
#     # print(client.read())
#     # print(client.get_meas_list())
#     # print(client.get_meas_list())
#     # client.write(
#     #     time_val=t, temperature=30.5, humidity=66.8
#     # )
#     print(client.time_query(time_shift='1h'))
#     print()
def main():
    # client = InfluxClient(
    #     host=r'vpn.feramat.com', port=8086,
    #     user='user', password='b3WDCGoyCsiUTk9pX1dd',
    #     dbname='db0'
    # )
    # client = InfluxClient(
    #     host=r'192.168.4.190', port=8086,
    #     user='eugene', password='7vT4g#1@K',
    #     dbname='home'
    # )

    # client = DataFrameClient(
    #     host=r'192.168.4.190', port=8086,
    #     username='eugene', password='7vT4g#1@K',
    #     database='home'
    # )

    # client = InfluxClient(
    #     host=r'localhost', port=8086,
    #     dbname='home'
    # )
    client = DataFrameClient(
        host=r'localhost', port=8086,
        database='home'
    )

    tz_prague = pytz.timezone('Europe/Prague')
    # tz_utc = pytz.timezone('utc')
    time_format = '%Y-%m-%dT%H:%M:%S.%z'
    t = datetime.now(tz_prague).strftime(time_format)
    # res = client.read()
    # res = client.time_query('hp_measurement', '1d')
    query = "SELECT * FROM {} WHERE time > now() - {} AND time < now()".format('hp_measurement', '1d')
    df = client.query(query, database='home')['hp_measurement']
    pd_processor = DataFrameProcessor(df)
    pd_processor.convert_tz()
    print(type(df))
    print(df)
    # print(client.create_json(
    #     time_val=t,
    #     tags=dict(project='home', type='measurement'),
    #     fields=dict(temperature=55, humidity=77)
    # ))
    # print(type(d), '\n', d)
    # client.client.create_database('testing_2')
    # print(client.client.get_list_database())
    # client.write(
    #     time_val=t,
    #     db_name='outdoor_weather',
    #     tags=dict(project='new_project', type='measurement'),
    #     fields=dict(temperature=30.5, humidity=66.8)
    # )

    # res = client.query("select * from {}".format('outdoor_weather'), database='home')
    # print(res['outdoor_weather'])
    # print(client.query('outdoor_weather'))
    # print(client.read())
    # rs = client.time_query(time_shift='3h')
    # points = list(rs.get_points(measurement='cpu', tags={'host_name': 'influxdb.com'}))
    # points = list(rs.get_points(measurement='outdoor_weather'))
    # print(points[0]['time'], '\t'*2, points[0]['temperature'], '\t'*2, points[0]['humidity'])
    # query = 'SELECT * FROM "outdoor_weather" WHERE time >= {} AND time <= {} GROUP BY time({})'.\
    #     format(
    #         datetime(2019, 4, 19, 5, tzinfo=tz_prague).strftime(time_format),
    #         datetime(2019, 4, 19, 6, tzinfo=tz_prague).strftime(time_format),
    #         '10m')
    #
    # query = 'SELECT * FROM "outdoor_weather" WHERE time >= {} AND time <= {}'.\
    #     format(
    #         datetime(2019, 4, 19, 5, tzinfo=tz_prague).strftime(time_format),
    #         datetime(2019, 4, 19, 6, tzinfo=tz_prague).strftime(time_format))
    # client.write(time_val=t, temperature=float(150), humidity=float(-20))
    # print(client.read())

    # query = 'SELECT * FROM "outdoor_weather" WHERE time >= {}'.\
    #     format('2019-04-19T05:00:00Z')
    # # '2015-08-18T00:00:00Z'
    # print(query)
    # # COUNT("temperature")
    # try:
    #     rs = client.client.query(query=query)
    # except InfluxDBClientError as error:
    #     logger.error('Infludb query error: {}'.format(error))
    #     rs = None
    # print(rs)


if __name__ == '__main__':
    main()
