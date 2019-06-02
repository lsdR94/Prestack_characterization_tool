# ===================================================================================================
# TEG: "Desarrollo de una herramienta computacional para la caracterización de yacimientos empleando
#       sísmica preapilada"
# Luisdaniel Rivera
# ===================================================================================================

# Modules
import segyio
import numpy as np
import pandas as pd
import holoviews as hv
from holoviews import opts, dim
from bokeh.models import HoverTool
hv.extension('bokeh')

# BASEMAP FUNCTIONS

# 1) step_validation(input_value, max_value)
def step_validation(input_value, max_value):
    
    """
    
    A function that validates the step fo either traces, inline and crosslines introduced by the user 
    through an input method.
    
    Arguments:
    input_value : String. Value introduced by the input method: the step_selection function.
 
    max_value : Integer. Upper limit of the element to plot: traces, inline and crosslines. Value introduced 
                by the input method: the step_selection function.
    
    Return:
    step : Integer. Value used by the basemap function to plot the elements of the Seismic Survey with a 
           distance between each one equal to this function output.

    """
    
    # First validation: the input value isn't a string nor symbol
    try:
        step = int(input_value)
    except ValueError:
        print(f"The step can't be a symbol, nor 0 nor greater than {max_value}. Please, introduce a valid data ")
        return (False)     
    
    # Second validation: if the input value isn't a symbol, then check if it's 0 or greater than max_value
    if int(input_value) == 0 or (int(input_value) >= int(max_value)):
        print(f"The step can't be a symbol, nor 0 nor greater than {max_value}. Please, introduce a valid data ")
        return (False)
    else:
        return (True)

# 2) step_compute(cube_dataframe)
def step_compute(cube_dataframe):
    
    """
    
    A function that allows the user to introduce the step between the elements of the Seismic Survey.
    
    Argument:
    cube_dataframe : (Pandas)DataFrame. Source of the values to compute the range of each element to plot:
                      traces, inline and crossline range.
    
    Return:
    steps : List. A list of integer values to be used as the step by the basemap function.
    
    """
    
    tracf_min = int(cube_dataframe['tracf'].iloc[0])
    tracf_max = int(cube_dataframe['tracf'].iloc[-1])
    trace_step = step_validation(input(f'Select a step from the trace range [{tracf_min},{tracf_max}] to plot the traces: '),tracf_max)
    
    iline_min = int(cube_dataframe['cdp_iline'].iloc[0])
    iline_max = int(cube_dataframe['cdp_iline'].iloc[-1])
    iline_step = step_validation(input(f'Select a step from the inline range [1,{iline_max - iline_min}] to plot the inlines: '),iline_max - iline_min)
    
    xline_min = int(cube_dataframe['cdp_xline'].iloc[0])
    xline_max = int(cube_dataframe['cdp_xline'].iloc[-1])
    xline_step = step_validation(input(f'Select a step from the crossline range [1,{xline_max - xline_min}] to plot the crosslines: '),xline_max - xline_min)
    
    steps = [int(trace_step),int(iline_step), int(xline_step)]
    
    return (steps)

# 3) polygon_building(cube_dataframe) 
def polygon_building(cube_dataframe):
    
    """
    
    A function that computes the limit of the Seismic Survey given a DataFrame.
    
    Argument:
    cube_dataframe : (Pandas) DataFrame. Source of the Seismic Survey boundary coordinates. 
                      Default: trace_dataframe.
    
    Return:
    polygon : (Pandas) DataFrame. Default columns: the edges of the polygon
              {'utmx_min','utmy_min','utmx_max','utmy_max','utmx_min'}
    
    """  
    
    # Survey's bounds plotting
    ## Taking the index of the min/max coordinates
    utmx_min_ind = cube_dataframe['utmx'].idxmin()
    utmx_max_ind = cube_dataframe['utmx'].idxmax()
    utmy_min_ind = cube_dataframe['utmy'].idxmin()
    utmy_max_ind = cube_dataframe['utmy'].idxmax()
    
    ## Extracting the min/max data from dataframe
    utmx_min = cube_dataframe.iloc[utmx_min_ind]
    utmx_max = cube_dataframe.iloc[utmx_max_ind]
    utmy_min = cube_dataframe.iloc[utmy_min_ind]
    utmy_max = cube_dataframe.iloc[utmy_max_ind]
    
    ## Building a new DataFrame for further plot
    polygon = pd.concat([utmx_min,utmy_min,utmx_max,utmy_max,utmx_min],
                         ignore_index=True, axis='columns').transpose()
    
    return (polygon)

# 4) basemap
def basemap_plot(cube_dataframe, wells_dataframe):
    
    """
    
    A function to plot the basic information of a Seismic Survey. 
    
    Argument:
    cube_dataframe : (Pandas) DataFrame. Source of the Seismic Survey coordinates for all traces
                      and lines within the input file. Default: trace_dataframe.
    
    wells_dataframe : (Pandas) DataFrame. Source of the wells information. 
                       Default: wells_dataframe
    
    Note:
    A new DataFrame is made in order to solve the issue related to the inability of the 
    Holoviews Scatter element to use loops for a step implementation.
    
    Return:
    basemap : Holviews element [Overlay]. The output is the combination of the seismic survey 
              polygon, the seismic traces, the lines along the survey and the Wells inside of it. A tool 
              to show the coordinates and the identification of each element have been implemented to the 
              plot (Hover Tool)
    
    """

    #Hover tool designation
    hover_t= HoverTool(tooltips=[('Tracf', '@tracf'),
                                 ('Inline', '@cdp_iline{int}'),
                                 ('Crossline', '@cdp_xline{int}')])
    
    hover_i = HoverTool(tooltips=[('Inline', '@cdp_iline'),
                                  ('CDP','@cdp_xline'),
                                  ('Tracf', '@tracf')])
    
    hover_x = HoverTool(tooltips=[('Crossline', '@cdp_xline'),
                                  ('CDP','@cdp_iline'),
                                  ('Tracf', '@tracf')])
    
    hover_w = HoverTool(tooltips=[('Pozo', '@name'),
                                  ('Utmx', '@utmx{int}'),
                                  ('Utmy', '@utmy{int}'),
                                  ('Inline', '@cdp_iline'),
                                  ('Xnline','@cdp_xline')])
      
    # Making the cube argument less stressful to read
    df = cube_dataframe
    
    # Computing the step list to extract the step for traces and lines
    step = step_compute(df)
    t_step, ix_step = step[0], step[1]
    
    # Loading the polygon dataframe + Plotting the boundaries of the data. Holoviews curve element
    polygon = polygon_building(df)
    pol = hv.Curve(polygon,'utmx','utmy', label = 'Polygon')
    pol.opts(line_width=0.5, color='black')
     
    # Plotting traces inside the cube according to it's utm coordinates. Holoviews scatter element
    traces = hv.Scatter(df[0:len(df)+t_step:t_step],['utmx', 'utmy'],['tracf','cdp_xline','cdp_iline'], 
                        label='Trace (Tracf)')
    traces.opts(line_width=1, color='black',size = 2, height=500, width=500, tools=[hover_t])
        
    ## Adding traces to the final output through loop   
    basemap = pol * traces
       
    # Plotting inlines. Holoviews curve element
    ## Computing the min and max cdp in inline  direction
    inline_max = df['cdp_iline'].unique().max()
    inline_min = df['cdp_iline'].unique().min()
 
    for i in range(inline_min, inline_max + ix_step, ix_step):   
        inline = hv.Curve(df[df['cdp_iline']==i], ['utmx', 'utmy'],['cdp_iline','cdp_xline','tracf'])
        inline.opts(line_width=1, color='red', height=500, width=500, tools=[hover_i])
        
    ## Adding traces to the final output through loop   
        basemap = basemap * inline        
    
    # Plotting Xlines. Holoviews curve element
    ## Computing the min and max cdp in crossline direction
    xline_max = df['cdp_xline'].unique().max()
    xline_min = df['cdp_xline'].unique().min()

    for x in range(xline_min, xline_max + ix_step, ix_step):   
        xnline = hv.Curve(df[df['cdp_xline']==x], ['utmx', 'utmy'],['cdp_xline','cdp_iline','tracf'])
        xnline.opts(line_width=1, color='blue', height=500, width=500, tools=[hover_x])
        
    ## Adding traces to the final output through loop
        basemap = basemap * xnline
    
    # Plotting Wells. Holoviews scatter element
    wells = hv.Scatter(wells_dataframe,['utmx','utmy'],['name','depth','cdp_iline', 'cdp_xline'], label = 'Wells')
    wells.opts(line_width=1,
           color='green',size = 7 ,marker = 'triangle',
           padding=0.1, width=600, height=400, show_grid=True, tools=[hover_w])
        
    
    # Overlaying boundaries, traces, inlines, xlines and wells plots
    basemap = basemap * wells
    
    # Setting options and formats to the final plot
        
    basemap.opts(padding = 0.1,height=500, width=500,
                 title = 'Seismic Survey: '+ seismic_survey,
                 fontsize={'title': 16, 'labels': 14, 'xticks': 8, 'yticks': 8},
                 xlabel = 'Coordenadas UTM X (m)', ylabel = 'Coordenadas UTM Y (m)', 
                 legend_position='top_left',
                 xformatter='%f', yformatter='%f')
    
    return (basemap)