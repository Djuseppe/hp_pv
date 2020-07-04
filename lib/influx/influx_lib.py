from abc import ABC
from datetime import datetime
import pytz
import logging
import pandas as pd
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
# logger.addHandler(file_handler)
# logger.addHandler(stream_handler)
if not len(logger.handlers):
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.propagate = False


class DataFrameProcessor:
    def __init__(self, df_list, tz=pytz.timezone('Europe/Prague')):
        self.tz = tz
        self.df_list = df_list

    @property
    def df_list(self):
        return self._df_list

    @df_list.setter
    def df_list(self, df_list):
        self._df_list = list()
        # self._df_list = [df for df in df_list if isinstance(df, pd.core.frame.DataFrame)]
        for df in df_list:
            if isinstance(df, pd.core.frame.DataFrame):
                df.index = df.index.tz_convert(self.tz)
                df_resampled = df.resample('1min').mean()
                self._df_list.append(df_resampled)

    def process(self):
        if self.df_list:
            d = pd.concat(self.df_list, axis=1)
        else:
            d = None
        return d


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
        dbname='db0',
        interval='10m'
    ):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.ssl = False
        self.verify_ssl = False
        self.interval = interval
        # self.ssl = True if self.host != '127.0.0.1' else False
        # self.verify_ssl = True if self.host != '127.0.0.1' else False
        self.client = DataFrameClient(
            host=self.host, port=self.port, database=self.dbname,
            username=self.user, password=self.password,
            ssl=self.ssl, verify_ssl=self.verify_ssl
        )
        try:
            self._ver = self.client.ping()
            logger.info('Connected to DB {} version = {}'.format(self.dbname, self._ver))
        except Exception as error:
            self._ver = False
            logger.error('Connection error: {}'.format(error))

    def time_query(self, measurement='outdoor_weather', time_shift='1h'):
        if not self._ver:
            result = None
        else:
            query = "SELECT * FROM {} WHERE time > now() - {} AND time < now()".format(measurement, time_shift)
            try:
                result = self.client.query(query, database=self.dbname).get(measurement)
            except influxdb.client.InfluxDBClientError as error:
                logger.error('Error while trying to query DB: {}'.format(error))
                result = None
        return result

    def read_results(self):
        _df_pv = self.time_query('pv_measurement', self.interval)
        _df_hp = self.time_query('hp_measurement', self.interval)
        df_pv = _df_pv.loc[:, ['power']]
        df_pv.columns = ['pv_power']
        df_hp = _df_hp.loc[
                :, ['0_set_temp', '1_sens_on', '2_sens_off',
                    '3_hp_on_off', '4_hysteresis_on', '5_hysteresis_off']]
        return df_pv, df_hp


class DBReader(InfluxDataFrameReader):
    def __init__(
            self, host='10.208.8.93', port=8086,
            dbname='uceeb', username='eugene', password='7vT4g#1@K',
            interval='10m'):
        super().__init__(host, port, username, password, dbname)
        self.interval = interval

    def get_data_from_db(self):
        df_pv = self.time_query('pv_measurement', self.interval)
        df_hp = self.time_query('hp_measurement', self.interval)
        df = DataFrameProcessor([
            df_pv.loc[:, ['power']],
            df_hp.loc[:, ['0_set_temp', '1_sens_on', '2_sens_off',
                          '3_hp_on_off', '4_hysteresis_on', '5_hysteresis_off']]]).process()
        return df.power.mean(), df.iloc[:-1, :]


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
    client = InfluxDataFrameReader(
        host=r'localhost', port=8086,
        dbname='home'
    )

    tz_prague = pytz.timezone('Europe/Prague')
    # tz_utc = pytz.timezone('utc')
    time_format = '%Y-%m-%dT%H:%M:%S.%z'
    t = datetime.now(tz_prague).strftime(time_format)
    # res = client.read()
    result = client.time_query('hp_measurement', '1d').get('hp_measurement')
    # query = "SELECT * FROM {} WHERE time > now() - {} AND time < now()".format('hp_measurement', '1d')
    # result = client.query(query, database='home')
    print(result)


if __name__ == '__main__':
    main()
