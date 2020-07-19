import Step_1_Data_Collection
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


def histogram_terms(self):
    plt.figure(figsize=(14, 10))
    sns.barplot(x='index', y='Sum', data=self.df_T)
    plt.title(label=('Total Concussion-Related Google Search Trends from ' +
                     self.start_date + ' to ' + self.end_date), loc='center', fontsize=14)
    plt.xlabel('Search Terms', fontsize=10)
    plt.ylabel('Sum', fontsize=10)
    plt.xticks(rotation=60)


# Create a line plot using the copied data frame.
# Y-values are adjusted so terms have a minimum of 0, a median of 50, and a maximum of 100.
# Zero means there weren't any values available for the search term.
def time_terms(self):
    plt.figure(figsize=(30, 10))
    sns.set_style('darkgrid')
    sns.lineplot(data=self.df_copy, dashes=False, palette='bright')
    plt.title('Concussion-Related Google Search Trends over Time', fontsize=14)
    plt.xlabel('Time', fontsize=10)
    plt.xticks(rotation=60)
    plt.ylabel('Degree of Interest (Scaled)', fontsize=10)
