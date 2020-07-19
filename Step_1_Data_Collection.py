import pandas as pd
import numpy as np
from datetime import datetime
from pytrends.request import TrendReq


pytrend = TrendReq()


class Trend:

    # Input dates as YYYY-MM-DD
    def __init__(self, start_date, end_date):
        self.start_date = str(start_date)
        self.end_date = str(end_date)
        self.time_period = start_date + ' ' + end_date
        self.df1 = None
        self.cols1 = None
        self.df1_metro = None
        self.df2 = None
        self.cols2 = None
        self.df2_metro = None
        self.agreement = None
        self.df = None
        self.agreement_geo = None
        self.df_geo = None
        self.terms_mean = None
        self.terms_sum = None
        self.df_T = None
        self.symptoms1_df()
        self.symptoms2_df()
        self.merge_df()
        self.adjust_df()
        self.merge_geo_df()
        self.data_prep()
        analysis_date = datetime.now()
        print('Data was collected on ' + analysis_date.strftime("%B %d, %Y") + ' at ' +
              analysis_date.strftime("%H:%M:%S") + ' for searches between ' + start_date +
              ' and ' + end_date + '.')

    def symptoms1_df(self):
        kw_list1 = ['concussion', 'mild traumatic brain injury', 'mTBI', 'post-concussion syndrome', 'ding']
        pytrend.build_payload(kw_list1, timeframe=self.time_period)
        self.df1 = pytrend.interest_over_time()
        self.cols1 = pd.DatetimeIndex.to_frame(self.df1.axes[0])
        self.df1.insert(loc=0, column='Date', value=self.cols1)
        self.df1_metro = pytrend.interest_by_region(resolution='DMA', inc_geo_code=True)

    def symptoms2_df(self):
        kw_list2 = ['dinged', 'bell-ringer', 'bell rung', 'football', 'NFL']
        pytrend.build_payload(kw_list2, timeframe=self.time_period)
        self.df2 = pytrend.interest_over_time()
        self.cols2 = pd.DatetimeIndex.to_frame(self.df2.axes[0])
        self.df2.insert(loc=0, column='Date', value=self.cols2)
        self.df2_metro = pytrend.interest_by_region(resolution='DMA', inc_geo_code=True)

    def merge_df(self):
        self.agreement = pd.concat([self.df1.Date, self.df2.Date], axis=1)
        self.agreement['Agree'] = np.where(self.agreement.iloc[:, 0] ==
                                           self.agreement.iloc[:, 1], 1, 0)

        if self.agreement.shape[0] == self.agreement['Agree'].count():
            self.df = pd.merge(left=self.df1, right=self.df2, how='left')
            self.df.set_index(self.df.iloc[:, 0])
        else:
            print("DataFrames' indices do not agree - double check values.")

    def adjust_df(self):
        self.df.drop(['isPartial'], axis=1, inplace=True)
        self.df.set_index('Date')

        # Combine columns of similar content or rename variables.
        self.df['mTBI'] = self.df['mild traumatic brain injury'] + self.df['mTBI']
        self.df['pcs'] = self.df['post-concussion syndrome']
        self.df['ding'] = self.df['ding'] + self.df['dinged']
        self.df['bell'] = self.df['bell-ringer'] + self.df['bell rung']

    def merge_geo_df(self):
        self.agreement_geo = pd.concat([self.df1_metro.geoCode, self.df2_metro.geoCode], axis=1)
        self.agreement_geo['Agree'] = np.where(self.agreement_geo.iloc[:, 0] ==
                                               self.agreement_geo.iloc[:, 1], 1, 0)

        if self.agreement_geo.shape[0] == self.agreement_geo['Agree'].count():
            self.df_geo = pd.merge(left=self.df1_metro, right=self.df2_metro, how='left')
            self.df_geo.set_index(self.df_geo.iloc[:, 0])
            self.df_geo.insert(loc=1, column='Location', value=self.df1_metro.axes[0])
        else:
            print("DataFrames' indices do not agree - double check values.")

    def data_prep(self):
        self.terms_mean = pd.DataFrame(self.df.mean())
        self.terms_sum = pd.DataFrame(self.df.sum())

        self.df_T = self.df.T
        self.df_T['Sum'] = self.df_T[1:13].sum(axis=1)
        self.df_T = self.df_T.reset_index()

# Example
start_date = "2010-07-01"
end_date = "2020-07-01"
t = Trend(start_date, end_date)