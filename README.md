# New York Times COVID-19 Data Visualization

## Project Information
This project provides Visualizations (using a Bokeh Server) of current New York Times Covid-19 data. 

Data is auto-loaded and live updated (no need to restart server) every 6 hours.

## Installing Dependencies

This project works thanks to the wonderful open-source packages [Pandas](https://pandas.pydata.org/) and [Bokeh](https://bokeh.org/).

To install `Pandas` follow these [instructions](https://pandas.pydata.org/docs/getting_started/install.html).
To install `Bokeh` follow these [instructions](https://docs.bokeh.org/en/latest/docs/user_guide/quickstart.html#userguide-quickstart).

## Launching Project
Bokeh Server can be run using `bokeh serve --show main.py`

If you would like to change the default comparison county run  `bokeh serve --show main.py --args "state" "county"`

Data can be updated manually by running `python population_stats pull_data`

## Using Project

Two drop down menus allow you to select the state and county of Covid-19 cases. This data will be compared to the state and county with which you launched the program.

Lines can be muted (reduced to 20% opacity) and unmuted by clicking the line in the legend to the right of the graph.

Panning the graphs can be done by clicking and dragging the graph within its borders.

Zomming in on parts of the graph can either be done using square selection or using the scroll wheel on your mouse. The option to zoom must be selected in the Bokeh toolbar in the upper right corner of the page.


## Data Sources and Accuracy
Data used in this project is not perfect since the names of counties did not always match between the the New York Times and Census datasets.

### New York Times COVID-19 Dataset
[NYT](https://github.com/nytimes/covid-19-data) 

### US Census Dataset
[US Census Data from 2018](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html).

## Screenshots
![screenshot](visualization.jpg)

## Disclaimer
I have no affiliation with the New York Times or the United States Census Bureua. All data used in this project was publically available. I am not responsible for any inference, decision, or determination, made from using this data.

If either sources would like that this project be taken down please contact me at my [email](mailto:otoledan@ucsd.edu).

