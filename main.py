from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Legend
from bokeh.layouts import gridplot
from bokeh.models.widgets import Dropdown, Select
from bokeh.plotting import curdoc
from population_stats import *
import sys


def gen_figure_1():
  global p1, r0, r1, r2, r3, r4, r5
  p1 = figure(x_axis_type="datetime", title="Cases and Deaths as compared to " + county_name + ", " + state_name,
              plot_height=350, plot_width=800)
  p1.xaxis.axis_label = 'Time'
  p1.yaxis.axis_label = 'People'
  r0 = p1.line('date', 'cases', source=source)
  r1 = p1.line('date', 'deaths', source=source, color="red")
  r2 = p1.line('date', 'cases', source=source1, line_dash="dotted")
  r3 = p1.line('date', 'deaths', source=source1, color="red", line_dash="dotted")
  r4 = p1.line('date', 'cases_state', source=source, line_dash="dashed")
  r5 = p1.line('date', 'deaths_state', source=source, color="red", line_dash="dashed")


def gen_figure_2():
  global p2, s0, s1, s2, s3
  p2 = figure(x_axis_type="datetime",
              title="Cases and Deaths per Capita as compared to " + county_name + ", " + state_name, plot_height=350,
              plot_width=800)
  p2.xaxis.axis_label = 'Time'
  p2.yaxis.axis_label = 'Percent People'
  s0 = p2.line('date', 'cases_per_capita', source=source)
  s1 = p2.line('date', 'deaths_per_capita', source=source, color="red")
  s2 = p2.line('date', 'cases_per_capita', source=source1, line_dash="dotted")
  s3 = p2.line('date', 'deaths_per_capita', source=source1, color="red", line_dash="dotted")


def gen_figure_3():
  global p3, s4, s5
  p3 = figure(x_axis_type="datetime", title="Cases and Deaths over Total Cases and Deaths in State", plot_height=350,
              plot_width=800)
  p3.xaxis.axis_label = 'Time'
  p3.yaxis.axis_label = 'Percent People'
  s4 = p3.line('date', 'cases_per_state', source=source)
  s5 = p3.line('date', 'deaths_per_state', source=source, color="red", )


def gen_legend_1():
  global legend1
  legend1 = Legend(items=[
    ("Cases", [r0]),
    ("Deaths", [r1]),
    ("Cases in " + county_name + ", " + state_name, [r2]),
    ("Deaths in " + county_name + ", " + state_name, [r3]),
    ("Cases in State", [r4]),
    ("Deaths in State", [r5]),
  ], location=(0, 0))


def gen_legend_2():
  global legend2
  legend2 = Legend(items=[
    ("Cases per Capita", [s0]),
    ("Deaths per Capita", [s1]),
    ("Cases per Capita in " + county_name + ", " + state_name, [s2]),
    ("Deaths per Capita in " + county_name + ", " + state_name, [s3]),
  ], location=(0, 0))


def gen_legend_3():
  global legend3
  legend3 = Legend(items=[
    ("County Cases/State Cases", [s4]),
    ("County Deaths/State Deaths", [s5]),
  ], location=(0, 0))


def set_default_state_county_dropdowns():
  global select_state, select_county
  state_list = list(us_counties["state"].unique())
  state_list.sort()
  counties_in_states = list(us_counties.loc[us_counties["state"] == "Alabama"]['county'].unique())
  counties_in_states.sort()
  select_state = Select(title="State:", value="foo", options=state_list)
  select_county = Select(title="County:", value="foo", options=counties_in_states)

def when_changing_state(attr, old, new):
  state = select_state.value
  counties_in_states = list(us_counties.loc[us_counties["state"] == state]['county'].unique())
  counties_in_states.sort()
  select_county.options = counties_in_states

  state_name = state

  state = us_counties.groupby("state").get_group(state_name)
  res = state.groupby("county")
  county = res.get_group(counties_in_states[0])

  source.data = county


def when_changing_county(attr, old, new):
  state_name = select_state.value
  county_name = select_county.value

  state = us_counties.groupby("state").get_group(state_name)
  res = state.groupby("county")
  county = res.get_group(county_name)

  source.data = county

###############################################################

#Default Comparison County
state_name = "California"
county_name = "Los Angeles"

if len(sys.argv) == 3:
  state_name = sys.argv[1]
  county_name = sys.argv[2]

us_counties = get_data()
us_counties["date"] = pd.to_datetime(us_counties['date'])

state = us_counties.groupby("state").get_group(state_name)
res = state.groupby("county")
county = res.get_group(county_name)

source = ColumnDataSource(county)
source1 = ColumnDataSource(county)

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

curdoc().title = "COVID-19 Charts"
curdoc().add_root(select_state)
curdoc().add_root(select_county)
curdoc().add_root(p)
