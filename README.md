# New York Times COVID-19 Data Visualization

## Project Information
This project provides Visualizations (using a Bokeh Server) of current New York Times Covid-19 data. 

Data is auto-loaded and live updated (no need to restart server) every 6 hours.

## Installing Dependencies
This project was written using Python3.

This project works thanks to the wonderful open-source packages [Pandas](https://pandas.pydata.org/) and [Bokeh](https://bokeh.org/).

### Using a Virtual Environment (Optional)

If you would like to install this project without effecting the other packages on your system you can use a virtual environment.

Run the below which will create and then launch your virtual environment.
```
pip3 install virtualenv
python3 -m venv <myenvname> 
```

Then install the dependencies as specified below.

### Quick Install Dependencies

Run `pip3 install -r requirements.txt` in the main directory to install dependent packages.

### Manual Install Dependencies
Most of the packages in `requirements.txt` are already installed. The main two packages needed are `Pandas` and `Bokeh`.

To install `Pandas` follow these [instructions](https://pandas.pydata.org/docs/getting_started/install.html).
To install `Bokeh` follow these [instructions](https://docs.bokeh.org/en/latest/docs/user_guide/quickstart.html#userguide-quickstart).

## Launching Project

### If using a Virtual environment
Launch your virtual environment first, then follow the below instructions.
```
python3 -m venv <myenvname> 
```

### All Us Cases
This project uses a Bokeh Server to run the site with visualizations locally.

To launch the Bokeh Server run `bokeh serve --show main.py`.

If you would like to change the default comparison county run  `bokeh serve --show main.py --args "state" "county"`.

Data can be updated manually by running `python population_stats pull_data`. This is not needed since data will be 
pulled by the Bokeh server every 6 hours.

## Using Project

Four drop down menus allow you to select the state and county (and comparison state and county) of Covid-19 cases. All 
plots data and legends will be automatically updated to match your selection. 

Some plots can also be viewed on Logarithmic scale (instead of the usual linear scale), this makes understanding the
trends of the plots a little easier.

Lines can be muted (reduced to 20% opacity) and unmuted by clicking the line in the legend to the right of the graph.

Panning the graphs can be done by clicking and dragging the graph within its borders.

Zooming in on parts of the graph can either be done using square selection or using the scroll wheel on your mouse. The 
option to zoom must be selected in the Bokeh toolbar in the upper right corner of the page.

## Data Sources and Accuracy
Data used and calculated in this project is not perfect since the names of counties did not always match between the 
New York Times and Census datasets.

Currently there are 305/21,799 rows of data (as of 3/31/20) where the county does not match the census. The vast 
majority of these cases are a result of the New York Times dataset listing the county as "Unknown".

The census dataset was slightly modified to match the New York Times Dataset, such as combining all the counties of 
New York City to match the New York Times Dataset.
### New York Times COVID-19 Dataset
[NYT](https://github.com/nytimes/covid-19-data) 

### US Census Dataset
[US Census Data from 2018](https://www.census.gov/data/tables/time-series/demo/popest/2010s-counties-detail.html).

## Screenshots
![screenshot](visualization.jpg)

## Disclaimer
I have no affiliation with the New York Times or the United States Census Bureau. All data used in this project was 
publicly available. I am not responsible for any inference, decision, or determination, made using this data.

If either sources would like that this project be taken down please contact me at my [email](mailto:otoledan@ucsd.edu).

