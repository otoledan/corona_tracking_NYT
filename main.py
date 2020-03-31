from datetime import datetime

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Legend
from bokeh.layouts import gridplot
from bokeh.models.widgets import Dropdown, Select
from bokeh.plotting import curdoc
from population_stats import *
import sys
from tornado import gen
import time
from functools import partial
from threading import Thread
import bokeh.server

line_width = 3
click_policy = "mute"
muted_alpha = 0.2


def gen_figure_1():
  global p1, r0, r1, r2, r3, r4, r5
  p1 = figure(x_axis_type="datetime", title="Cases and Deaths as compared to " + county_name + ", " + state_name,
              plot_height=350, plot_width=800)
  p1.xaxis.axis_label = 'Time'
  p1.yaxis.axis_label = 'People'
  r0 = p1.line('date', 'cases', source=source, line_width=line_width, muted_alpha=muted_alpha)
  r1 = p1.line('date', 'deaths', source=source, color="red", line_width=line_width, muted_alpha=muted_alpha)
  r2 = p1.line('date', 'cases', source=source1, line_dash="dashed", line_width=line_width, muted_alpha=muted_alpha)
  r3 = p1.line('date', 'deaths', source=source1, color="red", line_dash="dashed", line_width=line_width,
               muted_alpha=muted_alpha)
  r4 = p1.line('date', 'cases_state', source=source, line_dash="dotted", line_width=line_width, muted_alpha=muted_alpha)
  r5 = p1.line('date', 'deaths_state', source=source, color="red", line_dash="dotted", line_width=line_width,
               muted_alpha=muted_alpha)


def gen_figure_2():
  global p2, s0, s1, s2, s3
  p2 = figure(x_axis_type="datetime",
              title="Cases and Deaths per Capita as compared to " + county_name + ", " + state_name, plot_height=350,
              plot_width=800)
  p2.xaxis.axis_label = 'Time'
  p2.yaxis.axis_label = 'Percent People'
  s0 = p2.line('date', 'cases_per_capita', source=source, line_width=line_width, muted_alpha=muted_alpha)
  s1 = p2.line('date', 'deaths_per_capita', source=source, color="red", line_width=line_width, muted_alpha=muted_alpha)
  s2 = p2.line('date', 'cases_per_capita', source=source1, line_dash="dashed", line_width=line_width,
               muted_alpha=muted_alpha)
  s3 = p2.line('date', 'deaths_per_capita', source=source1, color="red", line_dash="dashed", line_width=line_width,
               muted_alpha=muted_alpha)


def gen_figure_3():
  global p3, t0, t1, t2, t3
  p3 = figure(x_axis_type="datetime", title="Cases and Deaths over Total Cases and Deaths in State as compared to "
                                            + county_name + ", " + state_name, plot_height=350,
              plot_width=800)
  p3.xaxis.axis_label = 'Time'
  p3.yaxis.axis_label = 'Percent People'
  t0 = p3.line('date', 'cases_per_state', source=source, line_width=line_width, muted_alpha=muted_alpha)
  t1 = p3.line('date', 'deaths_per_state', source=source, color="red", line_width=line_width, muted_alpha=muted_alpha)
  t2 = p3.line('date', 'cases_per_state', source=source1, line_dash="dashed", line_width=line_width,
               muted_alpha=muted_alpha)
  t3 = p3.line('date', 'deaths_per_state', source=source1, color="red", line_dash="dashed", line_width=line_width,
               muted_alpha=muted_alpha)


def gen_legend_1():
  global legend1
  legend1 = Legend(items=[
    ("Cases in State", [r4]),
    ("Deaths in State", [r5]),
    ("Cases", [r0]),
    ("Deaths", [r1]),
    ("Cases in " + county_name + ", " + state_name, [r2]),
    ("Deaths in " + county_name + ", " + state_name, [r3]),
  ], location=(0, 0))
  legend1.click_policy = click_policy


def gen_legend_2():
  global legend2
  legend2 = Legend(items=[
    ("Cases per Capita", [s0]),
    ("Deaths per Capita", [s1]),
    ("Cases per Capita in " + county_name + ", " + state_name, [s2]),
    ("Deaths per Capita in " + county_name + ", " + state_name, [s3]),
  ], location=(0, 0))
  legend2.click_policy = click_policy


def gen_legend_3():
  global legend3
  legend3 = Legend(items=[
    ("County Cases/State Cases", [t0]),
    ("County Deaths/State Deaths", [t1]),
    (county_name + " Cases/" + state_name + " Cases", [t2]),
    (county_name + " Deaths/" + state_name + " Deaths", [t3]),
  ], location=(0, 0))
  legend3.click_policy = click_policy


def set_default_state_county_dropdowns():
  global select_state, select_county, first_state, first_county
  state_list = list(us_counties["state"].unique())
  state_list.sort()
  counties_in_states = list(us_counties.loc[us_counties["state"] == state_list[0]]['county'].unique())
  counties_in_states.sort()
  select_state = Select(title="State:", value="foo", options=state_list)
  select_county = Select(title="County:", value="foo", options=counties_in_states)

  select_state.value = state_list[0]
  select_county.value = counties_in_states[0]


def when_changing_state(attr, old, new):
  state = select_state.value
  counties_in_states = list(us_counties.loc[us_counties["state"] == state]['county'].unique())
  counties_in_states.sort()
  select_county.options = counties_in_states

  state_name = state

  state = us_counties.groupby("state").get_group(state_name)
  res = state.groupby("county")
  county = res.get_group(counties_in_states[0])
  select_county.value = counties_in_states[0]
  source.data = county


def when_changing_county(attr, old, new):
  state_name = select_state.value
  county_name = select_county.value

  state = us_counties.groupby("state").get_group(state_name)
  res = state.groupby("county")
  county = res.get_group(county_name)

  source.data = county


def get_county_dataset(state_name, county_name):
  us_counties["date"] = pd.to_datetime(us_counties['date'])
  state = us_counties.groupby("state").get_group(state_name)
  res = state.groupby("county")
  county = res.get_group(county_name)

  return county


###############################################################

# Default Comparison County
state_name = "California"
county_name = "Los Angeles"

if len(sys.argv) == 3:
  state_name = sys.argv[1]
  county_name = sys.argv[2]

us_counties = get_data()

first_state = list(us_counties["state"].unique())[0]
first_county = list(us_counties.loc[us_counties["state"] == first_state]['county'].unique())[0]

source = ColumnDataSource(get_county_dataset(first_state, first_county))
source1 = ColumnDataSource(get_county_dataset(state_name, county_name))

gen_figure_1()
gen_figure_2()
gen_figure_3()
p = gridplot([[p1], [p2], [p3]])

set_default_state_county_dropdowns()

gen_legend_1()
gen_legend_2()
gen_legend_3()

p1.add_layout(legend1, 'right')
p2.add_layout(legend2, 'right')
p3.add_layout(legend3, 'right')

select_state.on_change('value', when_changing_state)
select_county.on_change('value', when_changing_county)

doc = curdoc()

doc.title = "COVID-19 Charts"
doc.add_root(select_state)
doc.add_root(select_county)
doc.add_root(p)


def update():
  temp_source = get_county_dataset(first_state, first_county)
  temp_source1 = get_county_dataset(state_name, county_name)

  source.data = temp_source
  source1.data = temp_source1

  state_list = list(us_counties["state"].unique())
  state_list.sort()
  counties_in_states = list(us_counties.loc[us_counties["state"] == select_state.value]['county'].unique())
  counties_in_states.sort()

  select_state.options = state_list
  select_county.options = counties_in_states


if not hasattr(bokeh.server, "get_data"):
  bokeh.server.get_data = False
  bokeh.server.data = None


def blocking_task():
  while True:
    # do some blocking computation
    cur_time = datetime.now()

    print("Current Time:", str(cur_time.hour) + ":" + str(cur_time.minute).zfill(2) + ":"
          + str(cur_time.second).zfill(2))
    if cur_time.hour % 6 == 0 and cur_time.minute == 0:
      if bokeh.server.get_data == False:
        bokeh.server.get_data = True

        print("Downloading Data...")
        global us_counties
        bokeh.server.data = get_data(False)
        us_counties = bokeh.server.data
        print("Downloaded")

    if cur_time.hour % 6 == 0 and cur_time.minute == 5:
      bokeh.server.get_data = False
      print("Reset get_data Flag")
      us_counties = bokeh.server.data
      doc.add_next_tick_callback(partial(update))

    else:
      print("Data will be updated at:", str((int(cur_time.hour / 6) * 6 + 6) % 24) + ":05:00")
    time.sleep(60)


thread = Thread(target=blocking_task)
thread.start()
