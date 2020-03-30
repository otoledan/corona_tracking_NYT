# corona_tracking_NYT

This project provides Visualizations (using a Bokeh Server) of current New York Times Covid-19 data. 

Data can be updated by running `python population_stats pull_data`

Bokeh Server can be run using `bokeh serve --show main.py`

If you would like to change the default comparison county run  `bokeh serve --show main.py --args "state" "county"`

Data is not perfect since the names of counties did not always match between the [NYT](https://github.com/nytimes/covid-19-data) and [US Census Data from 2018](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html).

