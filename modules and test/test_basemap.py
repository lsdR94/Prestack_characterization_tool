# Modules
import segyio
import basemap
import utils
import numpy as np
import pandas as pd
import holoviews as hv
from holoviews import opts, dim
from bokeh.models import HoverTool
hv.extension('bokeh')

# PATHS
seismic_path = '../data/NS2950-2180_3000-2230.sgy'
wells_path = '../data/wells_info.txt'
seismic_survey = 'POSEIDON 3D'

# DATAFRAMES
wells_dataframe = utils.wells_data_organization(wells_path)
trace_dataframe = utils.cube_data_organization(seismic_path,1)

# BASEMAP FUNCTIONS

# 1) test_step_validation(input_value, max_value)
def test_step_validation_string():
    input_step = basemap.step_validation("THESIS 2019!",10)
    assert (input_step == False)
def test_step_validation_zero():
    input_step = basemap.step_validation(0,10)
    assert (input_step == False)
def test_step_validation_greater():
    input_step = basemap.step_validation(11,10)
    assert (input_step == False)
def test_step_validation():
    input_step = basemap.step_validation(1,10)
    assert (str(type(input_step)) == "<class 'int'>")

# 2.1)test_step_compute_without_inputs(trace_dataframe,nput)
def test_step_computation_without_inputs():
    step = basemap.step_computation_without_inputs(trace_dataframe,"tracf",1)
    assert (step == 1)
def test_step_computation_without_inputs_false():
    step = basemap.step_computation_without_inputs(trace_dataframe,"tracf","Anything")
    assert (step == False)

# 3.1) test_step_selection_without_inputs(cube_dataframe, str )
def test_step_selection_without_inputs_false():
    step = basemap.step_selection_without_inputs(trace_dataframe, "Something", 5)
    assert (step == False)
def test_step_selection_without_inputs_false2():
    step = basemap.step_selection_without_inputs(trace_dataframe, "Something", "Somethin2")
    assert (step == False)
def test_step_selection_without_inputs():
    step = basemap.step_computation_without_inputs(trace_dataframe, "tracf", 1)
    assert (step == 1)

# 4) polygon_building(cube_dataframe)
def test_polygon_building_shape():
    polygon = basemap.polygon_building(trace_dataframe)
    assert (polygon.shape == (5,5))
def test_polygon_building_zero_iline():
    polygon = basemap.polygon_building(trace_dataframe)
    if (polygon['cdp_iline'] is not None) and (polygon['cdp_iline'] is not None):
        ans =  True
    else: 
        ans = False

    assert ans == True
def test_polygon_building_output_type():
    polygon = basemap.polygon_building(trace_dataframe)
    assert (str(type(polygon)) == "<class 'pandas.core.frame.DataFrame'>")

# 5) wells_plot(wells_dataframe)
def test_wells_plot():
    basemap_output = basemap.wells_plot(wells_dataframe)
    assert str(type(basemap_output)) == "<class 'holoviews.element.chart.Scatter'>"

# 6) polygon_plot(cube_dataframe)
def test_polygon_plot():
    pol = basemap.polygon_plot(trace_dataframe)
    assert (str(type(pol)) == "<class 'holoviews.element.chart.Curve'>")

# 7) trace_plot(cube_dataframe, t_step)
def test_trace_plot():
    trace = basemap.trace_plot(trace_dataframe,100)
    assert (str(type(trace)) == "<class 'holoviews.element.chart.Scatter'>")

# 8) inline_plot(cube_dataframe, i_step)
def test_inline_plot ():
    inline = basemap.inline_plot(trace_dataframe,10)
    assert (str(type(inline)) == "<class 'holoviews.core.overlay.Overlay'>")

# 9) xline_plot(cube_dataframe, x_step) 
def test_xline_plot ():
    xline = basemap.xline_plot(trace_dataframe,10)
    assert (str(type(xline)) == "<class 'holoviews.core.overlay.Overlay'>")

# 10.1) basemap_without_inputs(cube_dataframe, wells_dataframe)
def test_basemap_without_inputs():
    output = basemap.basemap_without_inputs(trace_dataframe, wells_dataframe,50)
    assert (str(type(output)) == "<class 'holoviews.core.overlay.Overlay'>")

# 11) test_to_test_number_of_lines_for_window(nput)
def test_number_of_lines_for_window_without_inputs():
    number_lines = basemap.number_of_lines_for_window_without_inputs(5)
    assert (str(type(number_lines)) == "<class 'int'>")
def test_number_of_lines_for_window_without_inputs_false():
    number_lines = basemap.number_of_lines_for_window_without_inputs('HAHAHA')
    assert (number_lines == False)

# 12.1) window_selection_dataframe_without_inputs(inline, crossline, dataframe)
def window_selection_dataframe_without_inputs():
    window = basemap.window_selection_dataframe_without_inputs(2998,2203, trace_dataframe, 15)
    assert (window.shape == (961, 5))





