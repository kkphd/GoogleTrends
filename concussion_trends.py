import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import parse
from pytrends.request import TrendReq
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import seaborn as sns
import json
import folium
import webbrowser

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
        self.df1_rel_queries = None
        self.df2 = None
        self.cols2 = None
        self.df2_metro = None
        self.df2_rel_queries = None
        self.agreement = None
        self.df = None
        self.agreement_geo = None
        self.df_geo = None
        self.terms_mean = None
        self.terms_sum = None
        self.df_T = None
        self.geo_us = None
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
        self.df1_rel_queries = pytrend.related_queries()

    def symptoms2_df(self):
        kw_list2 = ['dinged', 'bell-ringer', 'bell rung', 'football', 'NFL']
        pytrend.build_payload(kw_list2, timeframe=self.time_period)
        self.df2 = pytrend.interest_over_time()
        self.cols2 = pd.DatetimeIndex.to_frame(self.df2.axes[0])
        self.df2.insert(loc=0, column='Date', value=self.cols2)
        self.df2_metro = pytrend.interest_by_region(resolution='DMA', inc_geo_code=True)
        self.df2_rel_queries = pytrend.related_queries()

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
        # *Unfortunately, I am restricted to a maximum of 200 total scaled search counts total per row.*
        self.df['mTBI'] = self.df['mild traumatic brain injury'] + self.df['mTBI']
        self.df.drop(['mild traumatic brain injury'], axis=1, inplace=True)

        self.df['ding'] = self.df['ding'] + self.df['dinged']
        self.df.drop(['dinged'], axis=1, inplace=True)

        self.df['bell'] = self.df['bell-ringer'] + self.df['bell rung']
        self.df.drop(['bell-ringer'], axis=1, inplace=True)
        self.df.drop(['bell rung'], axis=1, inplace=True)

        self.df = self.df.rename(columns={'post-concussion syndrome': 'pcs'})

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

        self.df_geo['mTBI'] = self.df_geo['mild traumatic brain injury'] + self.df_geo['mTBI']
        self.df_geo.drop(['mild traumatic brain injury'], axis=1, inplace=True)

        self.df_geo['ding'] = self.df_geo['ding'] + self.df_geo['dinged']
        self.df_geo.drop(['dinged'], axis=1, inplace=True)

        self.df_geo['bell'] = self.df_geo['bell-ringer'] + self.df_geo['bell rung']
        self.df_geo.drop(['bell-ringer'], axis=1, inplace=True)
        self.df_geo.drop(['bell rung'], axis=1, inplace=True)

        self.df_geo = self.df_geo.rename(columns={'post-concussion syndrome': 'pcs'})

    def data_prep(self):
        self.terms_mean = pd.DataFrame(self.df.mean())
        self.terms_sum = pd.DataFrame(self.df.sum())

        self.df_T = self.df.T
        self.df_T['Sum'] = self.df_T[1:13].sum(axis=1)
        self.df_T = self.df_T.reset_index()

        self.df_copy = self.df
        self.df_copy = self.df_copy.set_index('Date')

        # Subset data frame to selected only locations in the United States.
        # It appears that US cities are represented by integer values so those will be retained.
        self.geo_us = self.df_geo
        self.geo_us['geoCode'] = pd.to_numeric(self.geo_us['geoCode'], downcast='signed', errors='coerce')
        self.geo_us = self.geo_us.dropna()
        geo_us = self.geo_us
        return geo_us

    def histogram_terms(self):
        colors = ['violet', 'blue', 'red', 'green', 'black', 'orange', 'yellow']
        start_date_new = parse(start_date).strftime('%B %d, %Y')
        end_date_new = parse(end_date).strftime('%B %d, %Y')
        self.df_T = self.df_T.iloc[1:, ]
        self.df_T.sort_values('Sum', ascending=False, inplace=True)
        plt.figure(figsize=(12, 9))
        sns.barplot(x='index', y='Sum', data=self.df_T, palette=colors)
        plt.title(label=('Total Concussion-related Google Search Trends from ' +
                         start_date_new + ' to ' + end_date_new), loc='center', fontsize=16)
        plt.xlabel('Search Terms', fontsize=14)
        plt.xticks(rotation=45, fontsize=12)
        plt.ylabel('Sum', fontsize=14)
        plt.yticks(fontsize=12)

    def time_terms(self):
        plt.figure(figsize=(16, 8))
        sns.set_style('whitegrid')

        # The color sequence for the histogram is: blue (football), orange (ding), green (concussion), and
        # red (NFL), so I will follow that some structure for the lineplot.
        colors = ['violet', 'blue', 'red', 'green', 'black', 'orange', 'yellow']
        sns.lineplot(data=self.df_copy, dashes=False, palette=colors)
        plt.title('Concussion-related Google Search Trends over Time', fontsize=20)
        plt.xlabel('Time', fontsize=14)
        plt.xticks(rotation=45, fontsize=12)
        plt.ylabel('Degree of Interest (Scaled)', fontsize=14)
        plt.yticks(fontsize=12)

    # Use latitude and longitude coordinates to map the DMAs in the US.
    # Credit to Mrk-Nguyen for the .json file containing the region codes:
    # https://github.com/Mrk-Nguyen/dmamap/blob/master/nielsengeo.json
    def prep_json(self):
        coord = open('nielsengeo.json')
        data = json.load(coord)

        coord_dict = []
        for feature in data['features']:
            city = feature['properties']['dma1']
            lat = feature['properties']['latitude']
            long = feature['properties']['longitude']
            dictionary = {
                'Location': city,
                'lat': lat,
                'long': long
            }
            coord_dict.append(dictionary)

        coord_dict = pd.DataFrame(coord_dict)
        return coord_dict


def merge_geos(g, coords):
    g = g.drop(['geoCode'], axis=1)
    coords['Location'] = coords.Location.str.replace(',', '')

    # Merge 'geo' and 'coordinates' on 'Location', which should be nearly, if not completely, identical.
    geo_coord = pd.merge(left=g, right=coords, on='Location', how='outer')

    # Manually enter the missing ('NaN') values with corresponding values from the 'coordinates'
    # and 'geo' data frames. If they are not available, approximate coordinates by identifying
    # their location with a Google search.
    geo_coord.at[geo_coord['Location'] == 'Anchorage AK', 'lat'] = 61.2181
    geo_coord.at[geo_coord['Location'] == 'Anchorage AK', 'long'] = -149.9003

    geo_coord.at[geo_coord['Location'] == 'Birmingham AL', 'lat'] = 33.50310
    geo_coord.at[geo_coord['Location'] == 'Birmingham AL', 'long'] = -86.86964

    geo_coord.at[geo_coord['Location'] == 'Birmingham (Anniston and Tuscaloosa) AL', 'lat'] = 33.5031
    geo_coord.at[geo_coord['Location'] == 'Birmingham (Anniston and Tuscaloosa) AL', 'long'] = -86.86964

    geo_coord.at[geo_coord['Location'] == 'Boston MA-Manchester NH', 'lat'] = 42.50102
    geo_coord.at[geo_coord['Location'] == 'Boston MA-Manchester NH', 'long'] = -71.46049

    geo_coord.at[geo_coord['Location'] == 'Fairbanks AK', 'lat'] = 64.8378
    geo_coord.at[geo_coord['Location'] == 'Fairbanks AK', 'long'] = -147.7164

    geo_coord.at[geo_coord['Location'] == 'Florence-Myrtle Beach SC', 'lat'] = 34.29878
    geo_coord.at[geo_coord['Location'] == 'Florence-Myrtle Beach SC', 'long'] = -79.41977

    geo_coord.at[geo_coord['Location'] == 'Greenville-Spartanburg SC-Asheville NC-Anderson SC', 'lat'] = 35.05266
    geo_coord.at[geo_coord['Location'] == 'Greenville-Spartanburg SC-Asheville NC-Anderson SC', 'long'] = -82.69770

    geo_coord.at[geo_coord['Location'] == 'Honolulu HI', 'lat'] = 21.3069
    geo_coord.at[geo_coord['Location'] == 'Honolulu HI', 'long'] = -157.8583

    geo_coord.at[geo_coord['Location'] == 'Juneau AK', 'lat'] = 58.3019
    geo_coord.at[geo_coord['Location'] == 'Juneau AK', 'long'] = -134.4197

    geo_coord.at[geo_coord['Location'] == 'Miami-Ft. Lauderdale FL', 'lat'] = 25.43902
    geo_coord.at[geo_coord['Location'] == 'Miami-Ft. Lauderdale FL', 'long'] = -80.94063

    geo_coord.at[geo_coord['Location'] == 'Montgomery (Selma) AL', 'lat'] = 32.05068
    geo_coord.at[geo_coord['Location'] == 'Montgomery (Selma) AL', 'long'] = -86.76757

    geo_coord.at[geo_coord['Location'] == 'Paducah KY-Cape Girardeau MO-Harrisburg-Mount Vernon IL', 'lat'] = 37.23529
    geo_coord.at[geo_coord['Location'] == 'Paducah KY-Cape Girardeau MO-Harrisburg-Mount Vernon IL', 'long'] = -89.49733

    geo_coord.at[geo_coord['Location'] == 'Sioux Falls(Mitchell) SD', 'lat'] = 44.01338
    geo_coord.at[geo_coord['Location'] == 'Sioux Falls(Mitchell) SD', 'long'] = -98.73520

    geo_coord.at[geo_coord['Location'] == 'Wichita-Hutchinson KS', 'lat'] = 33.90593
    geo_coord.at[geo_coord['Location'] == 'Wichita-Hutchinson KS', 'long'] = -99.03978

    geo_coord.at[geo_coord['Location'] == 'Wichita Falls TX & Lawton OK', 'lat'] = 33.90593
    geo_coord.at[geo_coord['Location'] == 'Wichita Falls TX & Lawton OK', 'long'] = -99.03978

    # The rows with latitude and longitude coordinates but without Google search counts are already
    # counted in the cases I modified above. Therefore, the cases deemed 'NaN' will be dropped.
    geo_coord.dropna(inplace=True)
    geo_coord['total'] = geo_coord.iloc[:, 3:9].sum(axis=1)
    return geo_coord


def map_terms(g_coord):
    # Constants.
    states = 'us-states.json'
    us_lat = 37
    us_long = -102

    # Extract the state from 'Location' so searches conducted within a state can be summed and then mapped
    # in folium. ALthough some cities overlap with different states, for simplicity's sake, I will only
    # map the last state in the cell.
    g_coord['id'] = g_coord['Location'].str[-2:]
    g_coord = g_coord[['Location', 'id', 'concussion', 'mTBI', 'pcs', 'ding', 'football',
                       'NFL', 'bell', 'total']]
    g_coord = g_coord.sort_values('id')

    # 'Washington DC/Hagerstown MD' is incorrected labeled as state 'D)' so I will rename that cell.
    g_coord.loc[g_coord.id == 'D)', 'id'] = 'MD'

    # Since I will aggregate search trends across states, I will make 'id' the key variable.
    # Group search terms by state and sum the total number of searches per term.
    g_coord.drop(['Location'], axis=1, inplace=True)
    g_coord = g_coord.groupby('id', as_index=False).sum()


    # Due to how the DMA locations are coded, Vermont, Rhode Island, New Jersey, and Delaware
    # are not included in the dataframe and are thus whited out.

    # Map 'football.'
    m = folium.Map(
        location=[us_lat, us_long],
        zoom_start=4,
        tiles='cartodbpositron',
    )

    # Map 'football' (purple).
    folium.Choropleth(
        geo_data=states,
        name='Football',
        data=g_coord,
        nan_fill_color='white',
        columns=['id', 'football'],
        key_on='feature.id',
        fill_color='BuPu',
        fill_opacity='0.7',
        line_color='black',
        line_opacity='0.5',
        legend_name='Football (degree of interest)'
    ).add_to(m)

    # Map 'ding' (blue).
    folium.Choropleth(
        geo_data=states,
        name='Ding',
        data=g_coord,
        nan_fill_color='white',
        columns=['id', 'football'],
        key_on='feature.id',
        fill_color='PuBu',
        fill_opacity='0.7',
        line_color='black',
        line_opacity='0.5',
        legend_name='Ding (degree of interest)'
    ).add_to(m)

    # Map 'concussion' (red).
    folium.Choropleth(
        geo_data=states,
        name='Concussion',
        data=g_coord,
        nan_fill_color='white',
        columns=['id', 'concussion'],
        key_on='feature.id',
        fill_color='OrRd',
        fill_opacity='0.7',
        line_color='black',
        line_opacity='0.5',
        legend_name='Concussion (degree of interest)'
    ).add_to(m)

    # Map 'NFL' (green).
    folium.Choropleth(
        geo_data=states,
        name='NFL',
        data=g_coord,
        nan_fill_color='white',
        columns=['id', 'NFL'],
        key_on='feature.id',
        fill_color='YlGn',
        fill_opacity='0.7',
        line_color='black',
        line_opacity='0.5',
        legend_name='NFL (degree of interest)'
    ).add_to(m)


    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    m.save('map.html')
    webbrowser.open('map.html', 2)


# Example
start_date = "2010-07-01"
end_date = "2020-07-01"
t = Trend(start_date, end_date)

t.histogram_terms()
t.time_terms()
plt.show()
geo = t.data_prep()
coordinates = t.prep_json()
geo_coord = merge_geos(geo, coordinates)
map_terms(geo_coord)
