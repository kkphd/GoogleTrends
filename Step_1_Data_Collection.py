import pandas as pd
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
        self.df2 = None
        self.df = None
        self.symptoms1_df()
        self.symptoms2_df()
        analysis_date = datetime.now()
        print('Data was collected on ' + analysis_date.strftime("%B %d, %Y") + ' at ' +
              analysis_date.strftime("%H:%M:%S"))

    def symptoms1_df(self):
        kw_list1 = ['concussion', 'mild traumatic brain injury', 'mTBI', 'post-concussion syndrome', 'ding']
        pytrend.build_payload(kw_list1, timeframe=self.time_period)
        self.df1 = pytrend.interest_over_time()

    def symptoms2_df(self):
        kw_list2 = ['dinged', 'bell-ringer', 'bell rung', 'football', 'NFL']
        pytrend.build_payload(kw_list2, timeframe=self.time_period)
        self.df2 = pytrend.interest_over_time()

    def merge_df(self):
        self.df = pd.concat([self.df1, self.df2])

    def adjust_df(self):
        df = pd.DataFrame.drop('isPartial')

        # Combine columns of similar content or rename variables.
        df['mTBI'] = df['mild traumatic brain injury'] + df['mTBI']
        df['pcs'] = df['post-concussion syndrome']
        df['ding'] = df['ding'] + df['dinged']
        df['bell'] = df['bell-ringer'] + df['bell rung']




# Example
start_date = "2015-07-01"
end_date = "2020-07-01"
t = Trend(start_date, end_date)