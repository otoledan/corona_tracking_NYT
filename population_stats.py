import os
import time

import pandas as pd
import sys
import urllib.request
import numpy as np

from queue import Queue
from threading import Thread

np.warnings.filterwarnings('ignore')

def get_data(access_saved=True):
  merged = None
  if access_saved and os.path.exists("full_data.csv"):
    merged = pd.read_csv("full_data.csv")
  else:
    urllib.request.urlretrieve("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv", "us-counties.csv")
    urllib.request.urlretrieve("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv", "us-states.csv")

    census_data = pd.read_csv("2018_est_census_data.csv")
    census_data["State"] = census_data["State"].str.strip()
    census_data["County"] = census_data["County"].str.replace(" County", "", case=False)
    census_data["County"] = census_data["County"].str.replace(" Parish", "", case=False)

    census_states = census_data["State"].unique()
    us_counties = pd.read_csv("us-counties.csv")
    us_counties["date"] = pd.to_datetime(us_counties['date'])
    corona_states = us_counties['state'].unique()
    intersection = list(set(census_states).intersection(set(corona_states)))
    cens_st = census_data.groupby('State')
    cor_st = us_counties.groupby('state')
    us_counties["population"] = float('inf')
    #us_counties["cases_trend_lin"] = 0
    us_counties["cases_trend_log"] = 0
    #us_counties["deaths_trend_lin"] = 0
    us_counties["deaths_trend_log"] = 0

    q = Queue(maxsize=0)

    for state in intersection:
      state_data_cens = cens_st.get_group(state)
      state_data_cor = cor_st.get_group(state)
      count_data_cor = state_data_cor.groupby("county")
      counties_exist_both_sets = list(set(count_data_cor.groups).intersection(set(state_data_cens["County"])))

      for county_name in counties_exist_both_sets:
        pop = state_data_cens.loc[state_data_cens["County"] == county_name]["Total"].values[0]
        us_counties.loc[(us_counties["state"] == state) & (us_counties["county"] == county_name), "population"] = pop

        county = us_counties[(us_counties["state"] == state) & (us_counties["county"] == county_name)]
        cases = np.array(county["cases"])
        deaths = np.array(county["deaths"])

        trend_county_cases_log = make_trend_line(cases, 7)
        trend_county_deaths_log = make_trend_line(deaths, 7)

        us_counties.loc[(us_counties["state"] == state) & (us_counties["county"] == county_name), "cases_trend_log"] = trend_county_cases_log
        us_counties.loc[(us_counties["state"] == state) & (us_counties["county"] == county_name), "deaths_trend_log"] = trend_county_deaths_log


    us_counties['cases_per_capita'] = us_counties.apply(lambda row: row.cases / row.population, axis=1)
    us_counties['deaths_per_capita'] = us_counties.apply(lambda row: row.deaths / row.population, axis=1)

    us_states = pd.read_csv("us-states.csv")
    us_states["date"] = pd.to_datetime(us_states['date'])

    merged = pd.merge(left=us_counties, right=us_states, how='inner', on=["date", "state"], suffixes=("", "_state"))

    merged['cases_per_state'] = merged.apply(lambda row: 0 if row.cases_state == 0 else row.cases / row.cases_state, axis=1)
    merged['deaths_per_state'] = merged.apply(lambda row: 0 if row.deaths_state == 0 else row.deaths / row.deaths_state, axis=1)

    merged.to_csv("full_data.csv")

  return merged

def make_trend_line(y, deg):
  act_len = len(y)

  length = len(np.argwhere(y > 0))
  x = range(1, length+1)
  prepend = np.array([0]*(act_len - length))

  if len(prepend) != act_len:
    y_log = y[-1 * (act_len - len(prepend)):]
    y_log = np.log(y_log)

    trend = np.polyfit(x, y_log, deg)
    trend = np.poly1d(trend)
    trend_log = np.exp(trend(x))

    trend_log = np.append(prepend, trend_log)

  else:
    trend_log = prepend

  return trend_log


if __name__ == "__main__":
  if len(sys.argv) == 2 and sys.argv[1] == "pull_data":
    print("Downloading Data...")
    us_counties = get_data(False)
    print("Data Downloaded")
    print("Data Columns:", list(us_counties))

  else:
    print("Using old Data")
    us_counties = get_data(True)
    print("Data Columns:", list(us_counties))
