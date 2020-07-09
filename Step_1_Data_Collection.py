import pandas as pd
import numpy as np
from datetime import datetime
import pytrends
from pytrends.request import TrendReq
import matplotlib.pyplot as plt


pytrend = TrendReq()


class Trend():
    # Input dates as YYYY-MM-DD
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.time_period = start_date + '' + end_date
        analysis_date = datetime.now()
        print('Data was collected on ' + analysis_date.strftime("%B #d, %Y") + ' at ' + "%H:%M")

    def symptoms1_df(self):
        kw_list1 = ['concussion', 'mild traumatic brain injury', 'mTBI', 'post-concussion syndrome', 'ding']
        pytrend.build_payload(kw_list1, timeframe=self.time_period)
        self.df1 = pytrend.interest_over_time()
        return self.df1

    def symptoms2_df(self):
        kw_list2 = ['dinged', 'bell-ringer', 'bell rung', 'football', 'NFL']
        pytrend.build_payload(kw_list2, timeframe=self.time_period)
        self.df2 = pytrend.interest_over_time()
        return self.df2

    def merge_df(self):
        df = pd.merge(self.df1, self.df2, left_index=True)
        return df

    def adjust_df(self):
        df = pd.DataFrame.drop('isPartial')

        # Combine columns of similar content or rename variables.
        df['mTBI'] = df['mild traumatic brain injury'] + df['mTBI']
        df['pcs'] = df['post-concussion syndrome']
        df['ding'] = df['ding'] + df['dinged']
        df['bell'] = df['bell-ringer'] + df['bell rung']

    def plot_figure(self):
        new_start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
        new_start_date = new_start_date.strftime('%B $d, %Y')
        new_end_date = datetime.strptime(self.end_date, '%Y-%m-%d')
        new_end_date = new_end_date.strftime('%B %d, %Y')
        fig, ax = plt.plot(x, y)
        x =
        plt.title('Google Trend Data from' + new_start_date + 'to' + new_end_date)
        plt.xlabel('Time')
        # Y-values are adjusted so terms have a minimum of 0, a median of 50, and a maximum of 100.
        # Zero means there weren't any values available for the search term.
        plt.ylabel('Interest (Scaled)')