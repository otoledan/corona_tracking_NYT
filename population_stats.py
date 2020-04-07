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

    time1 = time.clock()

    census_data = pd.read_csv("2018_est_census_data.csv")
    census_data["State"] = census_data["State"].str.strip()
    census_data["County"] = census_data["County"].str.replace(" County", "", case=False)
    census_data["County"] = census_data["County"].str.replace(" Parish", "", case=False)

    census_states = census_data["State"].unique()
    us_counties = pd.read_csv("us-counties.csv")
    us_counties["date"] = pd.to_datetime(us_counties['date'])

    us_states = pd.read_csv("us-states.csv")
    us_states["date"] = pd.to_datetime(us_states['date'])

    us_states["county"] = " All Counties"
    us_counties = us_counties.append(us_states, ignore_index=True)

    corona_states = us_counties['state'].unique()
    intersection = list(set(census_states).intersection(set(corona_states)))

    cens_st = census_data.groupby('State')
    cor_st = us_counties.groupby('state')

    us_counties["population"] = float('inf')
    us_counties["cases_trend_log"] = 0
    us_counties["deaths_trend_log"] = 0

    population_index = 6
    cases_trend_log_index = 7
    deaths_trend_log_index = 8

    us_numpy = us_counties.to_numpy()
    all_cases = np.array(us_numpy[:, 4], float)
    all_deaths = np.array(us_numpy[:, 5], float)

    deg = 5

    time2 = time.clock()

    for state in intersection:
      state_data_cens = cens_st.get_group(state)
      state_data_cor = cor_st.get_group(state)
      count_data_cor = state_data_cor.groupby("county")
      counties_exist_both_sets = list(set(count_data_cor.groups).intersection(set(state_data_cens["County"])))

      for county_name in counties_exist_both_sets:
        state_indexes = np.argwhere(us_numpy[:, 2] == state)
        county_indexes = np.argwhere(us_numpy[:, 1] == county_name)
        intersection_state_county_indexes = np.intersect1d(county_indexes, state_indexes, assume_unique=False)

        pop = state_data_cens.loc[state_data_cens["County"] == county_name]["Total"].values[0]
        us_counties.iloc[intersection_state_county_indexes, population_index] = pop
        #us_counties.loc[(us_counties["state"] == state) & (us_counties["county"] == county_name), "population"] = pop

        cases = all_cases[intersection_state_county_indexes]
        deaths = all_deaths[intersection_state_county_indexes]

        trend_county_cases_log = make_trend_line(cases, deg)
        trend_county_deaths_log = make_trend_line(deaths, deg)

        us_counties.iloc[intersection_state_county_indexes, cases_trend_log_index] = trend_county_cases_log
        us_counties.iloc[intersection_state_county_indexes, deaths_trend_log_index] = trend_county_deaths_log

    time3 = time.clock()

    us_counties['cases_per_capita'] = us_counties.apply(lambda row: row.cases / row.population, axis=1)
    us_counties['deaths_per_capita'] = us_counties.apply(lambda row: row.deaths / row.population, axis=1)

    us_counties["cases_per_capita_trend_log"] = 0
    us_counties["deaths_per_capita_trend_log"] = 0

    cases_per_capita_trend_log_index = 11
    deaths_per_capita_trend_log_index = 12

    us_numpy = us_counties.to_numpy()
    all_cases_per_capita = np.array(us_numpy[:, 9], float)
    all_deaths_per_capita = np.array(us_numpy[:, 10], float)

    time4 = time.clock()

    for state in intersection:
      state_data_cens = cens_st.get_group(state)
      state_data_cor = cor_st.get_group(state)
      count_data_cor = state_data_cor.groupby("county")
      counties_exist_both_sets = list(set(count_data_cor.groups).intersection(set(state_data_cens["County"])))

      for county_name in counties_exist_both_sets:
        state_indexes = np.argwhere(us_numpy[:, 2] == state)
        county_indexes = np.argwhere(us_numpy[:, 1] == county_name)
        intersection_state_county_indexes = np.intersect1d(county_indexes, state_indexes, assume_unique=False)

        cases_per_capita = all_cases_per_capita[intersection_state_county_indexes]
        deaths_per_capita = all_deaths_per_capita[intersection_state_county_indexes]

        trend_county_cases_per_capita_log = make_trend_line(cases_per_capita, deg)
        trend_county_deaths_per_capita_log = make_trend_line(deaths_per_capita, deg)

        us_counties.iloc[intersection_state_county_indexes, cases_per_capita_trend_log_index] = trend_county_cases_per_capita_log
        us_counties.iloc[intersection_state_county_indexes, deaths_per_capita_trend_log_index] = trend_county_deaths_per_capita_log

    time5 = time.clock()

    merged = pd.merge(left=us_counties, right=us_states, how='inner', on=["date", "state"], suffixes=("", "_state"))

    merged['cases_per_state'] = merged.apply(lambda row: 0 if row.cases_state == 0 else row.cases / row.cases_state, axis=1)
    merged['deaths_per_state'] = merged.apply(lambda row: 0 if row.deaths_state == 0 else row.deaths / row.deaths_state, axis=1)

    merged.to_csv("full_data.csv")

    time6 = time.clock()

    '''
    l = [time1, time2, time3, time4, time5, time6]
    for i in range(len(l) - 1):
      print("time" + str(i + 2) + " - time" + str(i+1) + ":", l[i+1] - l[i])
    '''

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
