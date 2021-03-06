from datetime import datetime
from os import remove
from os.path import isfile

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Legend, LegendItem, Paragraph, Panel, Tabs
from bokeh.layouts import gridplot
from bokeh.models.widgets import Select
from bokeh.plotting import curdoc
from population_stats import *
import sys
from tornado import gen
import time
from functools import partial
from threading import Thread
import bokeh.server
from bokeh.settings import settings


def gen_figure_1(y_axis_type="linear"):
  title = gen_html_paragraph(text="Cases and Deaths", weight="bold")
  p1 = figure(x_axis_type="datetime", plot_height=500, sizing_mode="stretch_width", y_axis_type=y_axis_type)
  p1.xaxis.axis_label = 'Time'
  p1.yaxis.axis_label = 'People'
  r2 = p1.line('date', 'cases', source=source, line_width=line_width, muted_alpha=muted_alpha)
  r3 = p1.line('date', 'deaths', source=source, color="red", line_width=line_width, muted_alpha=muted_alpha)
  r4 = p1.line('date', 'cases', source=source1, line_dash="dashed", line_width=line_width, muted_alpha=muted_alpha)
  r5 = p1.line('date', 'deaths', source=source1, color="red", line_dash="dashed", line_width=line_width,
               muted_alpha=muted_alpha)
  #r0 = p1.line('date', 'cases_state', source=source2, line_dash="dotted", line_width=line_width, muted_alpha=muted_alpha)
  #r1 = p1.line('date', 'deaths_state', source=source2, color="red", line_dash="dotted", line_width=line_width,
  #             muted_alpha=muted_alpha)
  r0_trend_log = p1.line("date", "cases_trend_log", source=source, line_width=line_width - 2, color="orange", muted_alpha=0)
  r1_trend_log = p1.line("date", "deaths_trend_log", source=source, line_width=line_width - 2, color="green", muted_alpha=0)

  return p1, r2, r3, r4, r5, r0_trend_log, r1_trend_log, title


def gen_figure_2(y_axis_type="linear"):
  title = gen_html_paragraph(text="Cases and Deaths per Capita", weight="bold")
  p2 = figure(x_axis_type="datetime", plot_height=500, sizing_mode="stretch_width", y_axis_type=y_axis_type)
  p2.xaxis.axis_label = 'Time'
  p2.yaxis.axis_label = 'Percent People'
  s0 = p2.line('date', 'cases_per_capita', source=source, line_width=line_width, muted_alpha=muted_alpha)
  s1 = p2.line('date', 'deaths_per_capita', source=source, color="red", line_width=line_width, muted_alpha=muted_alpha)
  s2 = p2.line('date', 'cases_per_capita', source=source1, line_dash="dashed", line_width=line_width,
               muted_alpha=muted_alpha)
  s3 = p2.line('date', 'deaths_per_capita', source=source1, color="red", line_dash="dashed", line_width=line_width,
               muted_alpha=muted_alpha)
  s0_trend_log = p2.line('date', 'cases_per_capita_trend_log', source=source, line_width=line_width - 2, color="orange", muted_alpha=0)
  s1_trend_log = p2.line('date', 'deaths_per_capita_trend_log', source=source, line_width=line_width - 2, color="green", muted_alpha=0)

  return p2, s0, s1, s2, s3, s0_trend_log, s1_trend_log, title


def gen_figure_3():
  title = gen_html_paragraph(text="Cases and Deaths over Total Cases and Deaths in State", weight="bold")
  p3 = figure(x_axis_type="datetime",
              plot_height=500, sizing_mode="stretch_width")
  p3.xaxis.axis_label = 'Time'
  p3.yaxis.axis_label = 'Percent People'
  t0 = p3.line('date', 'cases_per_state', source=source, line_width=line_width, muted_alpha=muted_alpha)
  t1 = p3.line('date', 'deaths_per_state', source=source, color="red", line_width=line_width, muted_alpha=muted_alpha)
  t2 = p3.line('date', 'cases_per_state', source=source1, line_dash="dashed", line_width=line_width,
               muted_alpha=muted_alpha)
  t3 = p3.line('date', 'deaths_per_state', source=source1, color="red", line_dash="dashed", line_width=line_width,
               muted_alpha=muted_alpha)

  return p3, t0, t1, t2, t3, title


def gen_legend_1(q2, q3, q4, q5, q0_trend, q1_trend):
  legend1 = Legend(items=[
    ("Cases in " + first_county + ", " + first_state, [q2]),
    ("Deaths in " + first_county + ", " + first_state, [q3]),
    ("Cases in " + county_name + ", " + state_name, [q4]),
    ("Deaths in " + county_name + ", " + state_name, [q5]),
    ("Cases Trendline", [q0_trend]),
    ("Deaths Trendline", [q1_trend])
  ], location="top_left")
  legend1.click_policy = click_policy

  return legend1


def gen_legend_2(s0, s1, s2, s3, s0_trend, s1_trend):
  legend2 = Legend(items=[
    ("Cases per Capita in " + first_county + ", " + first_state, [s0]),
    ("Deaths per Capita in " + first_county + ", " + first_state, [s1]),
    ("Cases per Capita in " + county_name + ", " + state_name, [s2]),
    ("Deaths per Capita in " + county_name + ", " + state_name, [s3]),
    ("Cases per Capita Trendline", [s0_trend]),
    ("Deaths per Capita Trendline", [s1_trend])
  ], location="top_left")
  legend2.click_policy = click_policy

  return legend2


def gen_legend_3(t0, t1, t2, t3):
  legend3 = Legend(items=[
    (first_county + " Cases/" + first_state + " Cases", [t0]),
    (first_county + " Deaths/" + first_state + " Deaths", [t1]),
  ], location=(0, 20))
  legend3.click_policy = click_policy

  legend4 = Legend(items=[
    (county_name + " Cases/" + state_name + " Cases", [t2]),
    (county_name + " Deaths/" + state_name + " Deaths", [t3]),
  ], location=(0, 40))
  legend4.click_policy = click_policy

  return legend3, legend4


def gen_select_state_county(state_name, county_name):
  state_list = list(us_counties["state"].unique())
  state_list.sort()
  counties_in_states = list(us_counties.loc[us_counties["state"] == state_name]['county'].unique())
  counties_in_states.sort()
  select_state = Select(title="State:", value="foo", options=state_list)
  select_county = Select(title="County:", value="foo", options=counties_in_states)

  select_state.value = state_name
  select_county.value = county_name

  return select_state, select_county


def when_changing_state(attr, old, new):
  state = select_state.value
  counties_in_states = list(us_counties.loc[us_counties["state"] == state]['county'].unique())
  counties_in_states.sort()
  select_county.options = counties_in_states

  state_name = select_state.value
  county_name = select_county.value

  set_legend1_1(legend1, county_name, state_name, q2, q3)
  set_legend1_1(legend1_log, county_name, state_name, q2_log, q3_log)

  set_legend2_1(legend2, county_name, state_name, s0, s1)
  set_legend2_1(legend2_log, county_name, state_name, s0_log, s1_log)

  state = us_counties.groupby("state").get_group(state_name)
  res = state.groupby("county")
  county = res.get_group(counties_in_states[0])
  select_county.value = counties_in_states[0]
  source.data = county


def when_changing_county(attr, old, new):
  state_name = select_state.value
  county_name = select_county.value

  set_legend1_1(legend1, county_name, state_name, q2, q3)
  set_legend1_1(legend1_log, county_name, state_name, q2_log, q3_log)

  set_legend2_1(legend2, county_name, state_name, s0, s1)
  set_legend2_1(legend2_log, county_name, state_name, s0_log, s1_log)

  legend3.items[0] = LegendItem(label=county_name + " Cases/" + state_name + " Cases", renderers=[t0])
  legend3.items[1] = LegendItem(label=county_name + " Deaths/" + state_name + " Deaths", renderers=[t1])

  state = us_counties.groupby("state").get_group(state_name)
  res = state.groupby("county")
  county = res.get_group(county_name)

  source.data = county
  source2.data = res.get_group(" All Counties")


def set_legend2_1(legend, county_name, state_name, s0, s1):
  legend.items[0] = LegendItem(label="Cases per Capita in " + county_name + ", " + state_name, renderers=[s0])
  legend.items[1] = LegendItem(label="Deaths per Capita in " + county_name + ", " + state_name, renderers=[s1])


def set_legend1_1(legend, county_name, state_name, q2, q3):
  legend.items[0] = LegendItem(label="Cases in " + county_name + ", " + state_name, renderers=[q2])
  legend.items[1] = LegendItem(label="Deaths in " + county_name + ", " + state_name, renderers=[q3])


def when_changing_state_2(attr, old, new):
  state = select_state_2.value
  counties_in_states = list(us_counties.loc[us_counties["state"] == state]['county'].unique())
  counties_in_states.sort()
  select_county_2.options = counties_in_states

  state_name = select_state_2.value
  county_name = select_county_2.value

  set_legend1_2(legend1, county_name, state_name, q4, q5)
  set_legend1_2(legend1_log, county_name, state_name, q4_log, q5_log)

  set_legend2_2(legend2, county_name, state_name, s2, s3)
  set_legend2_2(legend2_log, county_name, state_name, s2_log, s3_log)

  state = us_counties.groupby("state").get_group(state_name)
  res = state.groupby("county")
  county = res.get_group(counties_in_states[0])
  select_county_2.value = counties_in_states[0]
  source1.data = county


def when_changing_county_2(attr, old, new):
  state_name = select_state_2.value
  county_name = select_county_2.value

  set_legend1_2(legend1, county_name, state_name, q4, q5)
  set_legend1_2(legend1_log, county_name, state_name, q4_log, q5_log)

  set_legend2_2(legend2, county_name, state_name, s2, s3)
  set_legend2_2(legend2_log, county_name, state_name, s2_log, s3_log)

  legend4.items[0] = LegendItem(label=county_name + " Cases/" + state_name + " Cases", renderers=[t2])
  legend4.items[1] = LegendItem(label=county_name + " Deaths/" + state_name + " Deaths", renderers=[t3])

  state = us_counties.groupby("state").get_group(state_name)
  res = state.groupby("county")
  county = res.get_group(county_name)

  source1.data = county


def set_legend2_2(legend, county_name, state_name, s2, s3):
  legend.items[2] = LegendItem(label="Cases per Capita in " + county_name + ", " + state_name, renderers=[s2])
  legend.items[3] = LegendItem(label="Deaths per Capita in " + county_name + ", " + state_name, renderers=[s3])


def set_legend1_2(legend, county_name, state_name, q4, q5):
  legend.items[2] = LegendItem(label="Cases in " + county_name + ", " + state_name, renderers=[q4])
  legend.items[3] = LegendItem(label="Deaths in " + county_name + ", " + state_name, renderers=[q5])


def get_county_dataset(state_name, county_name):
  us_counties["date"] = pd.to_datetime(us_counties['date'])
  state = us_counties.groupby("state").get_group(state_name)
  res = state.groupby("county")
  county = res.get_group(county_name)

  return county


@gen.coroutine
def update():
  current_state = select_state.value
  current_county = select_county.value

  temp_source = get_county_dataset(current_state, current_county)
  temp_source1 = get_county_dataset(state_name, county_name)
  temp_source2 = get_county_dataset(current_state, " All Counties")

  source.data = temp_source
  source1.data = temp_source1
  source2.data = temp_source2

  state_list = list(us_counties["state"].unique())
  state_list.sort()
  counties_in_states = list(us_counties.loc[us_counties["state"] == select_state.value]['county'].unique())
  counties_in_states.sort()

  select_state.options = state_list
  select_county.options = counties_in_states


def blocking_task():
  while True:
    global us_counties
    # do some blocking computation
    cur_time = datetime.now()

    last_updated_file = os.path.getmtime("full_data.csv")
    epoch = datetime.utcfromtimestamp(0)
    total_seconds = (cur_time - epoch).total_seconds()

    '''
    print("Current Time:", str(cur_time.hour) + ":" + str(cur_time.minute).zfill(2) + ":"
          + str(cur_time.second).zfill(2))
    '''
    if cur_time.hour % time_every == time_hour and cur_time.minute == time_minute:
      data_download()

    elif cur_time.hour % time_every == time_hour and cur_time.minute == time_minute + 3 \
            and bokeh.server.data_needs_loading and bokeh.server.get_data:
      bokeh.server.data_needs_loading = False
      print("Data Loading")
      bokeh.server.data = get_data()
      us_counties = bokeh.server.data

    elif cur_time.hour % time_every == time_hour and cur_time.minute == time_minute + 5:
      bokeh.server.get_data = False
      if isfile("update.txt"):
        remove("update.txt")

      print("Reset get_data and data_needs_loading flags")
      us_counties = bokeh.server.data
      doc.add_next_tick_callback(partial(update))

    elif (total_seconds - last_updated_file) > (time_every * 60 * 60):
      data_download()

    time.sleep(60)


def data_download():
  if bokeh.server.get_data == False and not isfile("update.txt"):
    bokeh.server.get_data = True
    bokeh.server.data_needs_loading = False

    f = open("update.txt", "w+")
    f.close()

    print("Downloading Data...")
    global us_counties
    bokeh.server.data = get_data(False)
    us_counties = bokeh.server.data
    print("Downloaded")

  elif bokeh.server.get_data == False and isfile("update.txt"):
    bokeh.server.get_data = True
    bokeh.server.data_needs_loading = True
    print("Data Download Initiated on another Server")

def gen_html_paragraph(text, width=800, font_size=13.333, weight="normal"):
  return Paragraph(text=text, width=None, style={"font-size": str(font_size) + "px", "font-weight": weight}, sizing_mode="stretch_width")

###############################################################

# Line Settings
line_width = 4
click_policy = "mute"
muted_alpha = 0.2

# Data Update Settings
time_every = 6
time_hour = 0 % time_every
time_minute = 0

# Default Comparison County
state_name = "California"
county_name = "Los Angeles"

###############################################################

settings.allowed_ws_origin = ["https://www.covidtracking.tk", "www.covidtracking.tk", "covidtracking.tk", "localhost:2001", "localhost:5006"]

if len(sys.argv) == 3:
  state_name = sys.argv[1]
  county_name = sys.argv[2]

if not hasattr(bokeh.server, "get_data"):
  bokeh.server.get_data = False
  bokeh.server.data_needs_loading = False
  bokeh.server.data = get_data()

us_counties = bokeh.server.data

first_state = list(us_counties["state"].unique())
first_state.sort()
first_state = first_state[0]

first_county = list(us_counties.loc[us_counties["state"] == first_state]['county'].unique())
first_county.sort()
first_county = first_county[0]

source = ColumnDataSource(get_county_dataset(first_state, first_county))
source1 = ColumnDataSource(get_county_dataset(state_name, county_name))
source2 = ColumnDataSource(get_county_dataset(first_state, " All Counties"))

p1, q2, q3, q4, q5, q0_trend, q1_trend, title_p1 = gen_figure_1()
p1_log, q2_log, q3_log, q4_log, q5_log, q0_trend_log, q1_trend_log, title_p1_log = gen_figure_1("log")
tab1_lin = Panel(child=p1, title="Linear")
tab1_log = Panel(child=p1_log, title="Logarithmic")
tabs_1 = Tabs(tabs=[tab1_lin, tab1_log], sizing_mode="stretch_width")

p2, s0, s1, s2, s3, s0_trend, s1_trend, title_p2 = gen_figure_2()
p2_log, s0_log, s1_log, s2_log, s3_log, s0_trend_log, s1_trend_log, title_p2_log = gen_figure_2("log")
tab2_lin = Panel(child=p2, title="Linear")
tab2_log = Panel(child=p2_log, title="Logarithmic")
tabs_2 = Tabs(tabs=[tab2_lin, tab2_log], sizing_mode="stretch_width")

p3, t0, t1, t2, t3, title_p3 = gen_figure_3()

p = gridplot([[title_p1],
              [tabs_1],
              [title_p2],
              [tabs_2],
              [title_p3],
              [p3]], sizing_mode="stretch_width")

legend1 = gen_legend_1(q2, q3, q4, q5, q0_trend, q1_trend)
legend2 = gen_legend_2(s0, s1, s2, s3, s0_trend, s1_trend)

legend1_log = gen_legend_1(q2_log, q3_log, q4_log, q5_log, q0_trend_log, q1_trend_log)
legend2_log = gen_legend_2(s0_log, s1_log, s2_log, s3_log, s0_trend_log, s1_trend_log)

legend3, legend4 = gen_legend_3(t0, t1, t2, t3)

p1.add_layout(legend1, "below")
p1_log.add_layout(legend1_log, "below")

p2.add_layout(legend2, "below")
p2_log.add_layout(legend2_log, "below")

p3.add_layout(legend3, "below")
p3.add_layout(legend4, "below")

title = gen_html_paragraph("COVID-19 Cases and Deaths in US Counties", 800, 32)
subtitle = gen_html_paragraph("The following charts represent the data on a county level of COVID-19 cases and can be "
                              "compared to another county in the U.S.", 800, 24)
text_col_select = gen_html_paragraph('Select a State and County', width=300)
text_col_select_2 = gen_html_paragraph('Select a Comparison State and County', width=300)

select_state, select_county = gen_select_state_county(first_state, first_county)
select_state.on_change('value', when_changing_state)
select_county.on_change('value', when_changing_county)

select_state_2, select_county_2 = gen_select_state_county(state_name, county_name)
select_state_2.on_change('value', when_changing_state_2)
select_county_2.on_change('value', when_changing_county_2)

one = bokeh.layouts.layout([
  [text_col_select],
  [select_state],
  [select_county]
], sizing_mode="stretch_width")

two = bokeh.layouts.layout([
  [text_col_select_2],
  [select_state_2],
  [select_county_2]
], sizing_mode="stretch_width")

selection_grid = bokeh.layouts.layout([
    [title],
    [subtitle],
    [one, two]
], sizing_mode="stretch_width")

doc = curdoc()
doc.title = "COVID-19 Charts"
doc.add_root(selection_grid)
doc.add_root(p)

thread = Thread(target=blocking_task)
thread.start()
