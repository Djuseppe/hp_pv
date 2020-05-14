import pandas as pd
import pytz
import logging

# logger config
logging.basicConfig()
logger = logging.getLogger('data_proc')
logger.setLevel(logging.DEBUG)


class DataFrameProcessor:
    def __init__(self, df_list, tz=pytz.timezone('Europe/Prague')):
        self.df_list = df_list
        self.tz = tz

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

    # def convert_tz(self, df):
    #     df.index = df.index.tz_convert(self.tz)

    def process(self):
        if self.df_list:
            d = pd.concat(self.df_list, axis=1)
        else:
            d = None
        return d
