import pandas as pd
import numpy as np
import urllib.request


def get_data(access_saved=True):
  merged = None
  if access_saved:
    merged = pd.read_csv("full_data.csv")

  else:
    urllib.request.urlretrieve("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv", "us-counties.csv")
    urllib.request.urlretrieve("https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv", "us-states.csv")

    census_data = pd.read_csv("2018_est_census_data.csv")
    census_data["County"] = census_data["County"].str.replace(" County", "", case=False)
    census_data["State"] = census_data["State"].str.strip()
    census_states = census_data["State"].unique()
    us_counties = pd.read_csv("us-counties.csv")
    us_counties["date"] = pd.to_datetime(us_counties['date'])
    corona_states = us_counties['state'].unique()
    intersection = list(set(census_states).intersection(set(corona_states)))
    cens_st = census_data.groupby('State')
    cor_st = us_counties.groupby('state')
    us_counties["population"] = float('inf')
    for state in intersection:
      state_data_cens = cens_st.get_group(state)
      state_data_cor = cor_st.get_group(state)
      count_data_cor = state_data_cor.groupby("county")
      counties_exist_both_sets = list(set(count_data_cor.groups).intersection(set(state_data_cens["County"])))

      for county_name in counties_exist_both_sets:
        pop = state_data_cens.loc[state_data_cens["County"] == county_name]["Total"].values[0]
        us_counties.loc[(us_counties["state"] == state) & (us_counties["county"] == county_name), "population"] = pop
    us_counties['cases_per_capita'] = us_counties.apply(lambda row: row.cases / row.population, axis=1)
    us_counties['deaths_per_capita'] = us_counties.apply(lambda row: row.deaths / row.population, axis=1)

    us_states = pd.read_csv("us-states.csv")
    us_states["date"] = pd.to_datetime(us_states['date'])

    merged = pd.merge(left=us_counties, right=us_states, how='inner', on=["date", "state"], suffixes=("", "_state"))

    merged['cases_per_state'] = merged.apply(lambda row: 0 if row.cases_state == 0 else row.cases / row.cases_state, axis=1)
    merged['deaths_per_state'] = merged.apply(lambda row: 0 if row.deaths_state == 0 else row.deaths / row.deaths_state, axis=1)

    merged.to_csv("full_data.csv")

  return merged

if __name__ == "__main__":
  us_counties = get_data(False)
  print(list(us_counties))
