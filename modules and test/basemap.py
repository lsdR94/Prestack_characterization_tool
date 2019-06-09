# ===================================================================================================
# TEG: "Desarrollo de una herramienta computacional para la caracterización de yacimientos empleando
#       sísmica preapilada"
# Luisdaniel Rivera
# ===================================================================================================

# Modules
import segyio
import utils
import numpy as np
import pandas as pd
import holoviews as hv
from holoviews import opts, dim
from bokeh.models import HoverTool

hv.extension('bokeh')

seismic_survey = 'POSEIDON 3D'
# BASEMAP FUNCTIONS

# NOTE: float functions are those who has been modified because of the
#       input method within the code.

# FUNCTIONS that have to be refactorized are: 2 (i repeat stuff), 11 (doesn't have any shield) 

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
    while True:
        # First validation: the input value isn't a string nor symbol
        try:
            step = int(input_value)
        except ValueError:
            print(f"The step can't be a symbol, nor 0 nor greater than {max_value}. Please, introduce a valid data ")
            return (False)     

        # Second validation: if the input value isn't a symbol, then check if it's 0 or greater than max_value
        if int(input_value) == 0 or (int(input_value) > int(max_value)):
            print(f"The step can't be a symbol, nor 0 nor greater than {max_value}. Please, introduce a valid data ")
            return (False)
        else:
            return (step)

# 2) step_compute(cube_dataframe) [Refactored]
def step_computation(cube_dataframe, str ):
    
    """
    
    A function that allows the user to choose the step of a DataFrame's key (columns names).
    
    Argument:
    cube_dataframe : (Pandas)DataFrame. Source of the input keys and the range of values than can be chosen as
                      the step.
    
    str : String. Name of the DataFrame's column to compute the step.
    
    Return:
    item_step : Integer. An integer to be used as the step by the basemap function.
    
    """
    # Computation of boundaries of the str range   
    step_min = int(cube_dataframe[str].iloc[0])
    step_max = int(cube_dataframe[str].iloc[-1])
        
    # While loop to shield the input step 
    while True:
        item_step = step_validation(input(f" Select a step from the {str} range [{int(step_min/step_min)},{step_max - step_min}] to plot the traces: "),step_max)
        if item_step == False:
            print(" ")
        else: 
            print(" ")
            break
            
    return (item_step)
# 2.1) step_computation_without_inputs(cube_dataframe, str, nput)
def step_computation_without_inputs(cube_dataframe, str, nput):
    
    """
    
    TESTING FUNCTION: STEP_COMPUTE WITHOUT INPUT METHODS
    
    """

    # Computation of boundaries of the str range   
    step_min = int(cube_dataframe[str].iloc[0])
    step_max = int(cube_dataframe[str].iloc[-1])
        
    # While loop to shield the input step 
    while True:
        item_step = step_validation(nput,step_max)
        if item_step == False:
            print(" ")
            break
        else: 
            print(" ")
            break
            
    return (item_step)

# 3) step_selection(cube_dataframe, str ) [Refactored]
def step_selection(cube_dataframe, str ):
    
    """
    
    A function that validates the string argument of the step_computation function.
    
    Argument:
    cube_dataframe : (Pandas)DataFrame. Source of the input keys and the range of values than can be chosen as
                      the step.
    
    str : String. Name of the DataFrame's column to compute the step.
    
    Return:
    step : Integer. An integer to be used as the step by the basemap function.
    
    """
    
    # if the given string is NOT one of the columns do:
    if str not in cube_dataframe.keys():  
        
        # while loop to shield the input
        while True:
            str = input(f" Introduce a proper column name: ")
            
            # Again: if is not one of the keys: start the cycle 
            if str not in cube_dataframe.keys(): 
                print("  ")
            
            # If not, go computing the step
            else:
                step = step_computation(cube_dataframe, str )
                return(step)
                break
            
    # If the initial argument is an actual column name, then start the calculations
    else:
        step = step_computation(cube_dataframe, str )
        return (step)

# 3.1) step_selection_without_inputs
def step_selection_without_inputs(cube_dataframe, str, nput):
        
    """
    
    TESTING FUNCTION: STEP_SELECTION WITHOUT INPUT METHODS
    
    """
    
    # if the given string is NOT one of the columns do:
    if str not in cube_dataframe.keys():  
        
        # while loop to shield the input          
        return (False)
            
    # If not, go computing the step
            
    # If the initial argument is an actual column name, then start the calculations
    else:
        step = step_computation_without_inputs(cube_dataframe, str, nput)
        return (step)

# 4) polygon_building(cube_dataframe) 
def polygon_building(cube_dataframe):
    
    """
    
    A function that computes the limit of the Seismic Survey given a DataFrame.
    
    Argument:
    cube_dataframe : (Pandas) DataFrame. Source of the Seismic Survey boundary coordinates. 
    
    Return:
    polygon : (Pandas) DataFrame. Default columns: the edges of the polygon
              {"utmx_min","utmy_min","utmx_max", "utmy_max","utmx_min"}
    
    """  
    
    # Survey's bounds plotting
    ## Taking the index of the min/max coordinates
    utmx_min_ind = cube_dataframe["utmx"].idxmin()
    utmx_max_ind = cube_dataframe["utmx"].idxmax()
    utmy_min_ind = cube_dataframe["utmy"].idxmin()
    utmy_max_ind = cube_dataframe["utmy"].idxmax()
    
    ## Extracting the min/max data from dataframe
    utmx_min = cube_dataframe.iloc[utmx_min_ind]
    utmx_max = cube_dataframe.iloc[utmx_max_ind]
    utmy_min = cube_dataframe.iloc[utmy_min_ind]
    utmy_max = cube_dataframe.iloc[utmy_max_ind]
    
    ## Building a new DataFrame for further plot
    polygon = pd.concat([utmx_min,utmy_min,utmx_max,utmy_max,utmx_min],
                         ignore_index=True, axis="columns").transpose()
    
    return (polygon)

# 5) wells_plot(wells_dataframe)
def wells_plot(wells_dataframe):
    
    """
    
    A function that plots the wells inside the dataframe using Holoview's bokeh backend.
    
    Arguments:
    wells_dataframe : (Pandas) DataFrame. Source of the wells information. 
    
    Return:
    wells : Holviews element [Scatter]. Collection of wells inside the Seismic Survey.
    
    """
    
    #Hover tool designation    
    hover_w = HoverTool(tooltips=[("Pozo", "@name"),
                                  ("Utmx", "@utmx{int}"),
                                  ("Utmy", "@utmy{int}"),
                                  ("Inline", "@cdp_iline"),
                                  ("Xnline","@cdp_xline")])
    
    # Plotting Wells. Holoviews scatter element
    wells = hv.Scatter(wells_dataframe,["utmx","utmy"],["name","depth","cdp_iline", "cdp_xline"], 
                       label = "Wells")
    wells.opts(line_width=1,
           color="green",size = 7 ,marker = "triangle",
           padding=0.1, width=600, height=400, show_grid=True, tools=[hover_w])
    
    return (wells)

# 6) polygon_plot(cube_dataframe)
def polygon_plot(cube_dataframe):
    
    """
    
    A function that plots the boundaries of the Seismic Survey using Holoview's bokeh backend.
    
    Arguments:
    cube_dataframe : (Pandas) DataFrame. Source of the Seismic parameters to compute and plot. 
    
    Return:
    pol : Holviews element [Curve]. Polygon that represents the boundaries of the Seismic Survey.
    
    """
    
    # Loading the polygon dataframe.
    polygon = polygon_building(cube_dataframe)
    
    #Plotting the boundaries of the Seismic Survey. Holoviews curve element
    pol = hv.Curve(polygon,"utmx","utmy", label = "Polygon")
    pol.opts(line_width=0.5, color="black")
    
    return (pol)

# 7) trace_plot(cube_dataframe, t_step)
def trace_plot(cube_dataframe, t_step):
    
    """
    
    A function that plots the traces of the Seismic Survey using Holoview's bokeh backend.
    
    Arguments:
    cube_dataframe : (Pandas) DataFrame. Source of the Seismic parameters to compute and plot. 
    
    t_step : Integer. Value to use as the interval for each trace to be plotted.
    
    Return:
    traces : Holviews element [Scatter]. Collection of the Seismic traces inside the Survey.
    
    """
    
    #Hover tool designation
    hover_t= HoverTool(tooltips=[("Tracf", "@tracf"),
                                 ("Inline", "@cdp_iline{int}"),
                                 ("Crossline", "@cdp_xline{int}")])
    
    # Less stressful to read
    df = cube_dataframe
    
    # Plotting traces inside the cube according to it's utm coordinates. Holoviews scatter element
    traces = hv.Scatter(df[0:len(df)+t_step:t_step],["utmx", "utmy"],["tracf","cdp_xline","cdp_iline"], 
                        label= f"Trace (tracf)")
    traces.opts(line_width=1, color="black",size = 2, height=500, width=500, tools=[hover_t])
    
    return (traces)

# 8) inline_plot(cube_dataframe, i_step)
def inline_plot(cube_dataframe, i_step):
    
    """
    
    A function that plots the inlines of the Seismic Survey using Holoview's bokeh backend.
    
    Arguments:
    cube_dataframe : (Pandas) DataFrame. Source of the Seismic parameters to compute and plot.
    
    i_step : Integer. Value to use as the interval for each line to be plotted.
    
    Return:
    traces : Holviews element [Scatter]. Collection of the inlines inside the Survey.
    
    """
    
    #Hover tool designation
    hover_i = HoverTool(tooltips=[("Inline", "@cdp_iline"),
                                  ("CDP","@cdp_xline"),
                                  ("Tracf", "@tracf")])
    
    # Less stressful to read
    df = cube_dataframe
    
    # Computing the min and max cdp in inline  direction
    inline_max = df["cdp_iline"].unique().max()
    inline_min = df["cdp_iline"].unique().min()
    
    # Initializing the plot (else the for loop doesn't work)
    inline = hv.Curve(df[df["cdp_iline"]==inline_min], ["utmx", "utmy"])
    inline.opts(line_width = 0.5, color = "white")
    
    # Plotting inlines according to the selected step. Holoviews curve element
    for i in range(inline_min, inline_max + i_step, i_step):   
        inlines = hv.Curve(df[df["cdp_iline"]==i], ["utmx", "utmy"],["cdp_iline","cdp_xline","tracf"])
        inlines.opts(line_width=1, color="red", height=500, width=500, tools=[hover_i])
        
        inline = inline * inlines
        
    return (inline)

# 9) xline_plot(cube_dataframe, x_step) 
def xline_plot(cube_dataframe, x_step):
    
    """
    
    A function that plots the crosslines of the Seismic Survey using Holoview's bokeh backend.
    
    Arguments:
    cube_dataframe : (Pandas) DataFrame. Source of the Seismic parameters to compute and plot.
    
    x_step : Integer. Value to use as the interval for each line to be plotted.
    
    Return:
    traces : Holviews element [Scatter]. Collection of the crosslines inside the Survey.
    
    """

    #Hover tool designation   
    hover_x = HoverTool(tooltips=[("Crossline", "@cdp_xline"),
                                  ("CDP","@cdp_iline"),
                                  ("Tracf", "@tracf")])
    # Less stressful to read
    df = cube_dataframe
    
    #Computing the min and max cdp in crossline direction.
    xline_max = df["cdp_xline"].unique().max()
    xline_min = df["cdp_xline"].unique().min()
    
    # Initializing the plot (else the for loop doesn't work)
    xline = hv.Curve(df[df["cdp_xline"]==xline_min], ["utmx", "utmy"])
    xline.opts(line_width = 0.5, color = "white")
    
    # Plotting Xlines  according to the selected step. Holoviews curve element
    for x in range(xline_min, xline_max + x_step, x_step):   
        xlines = hv.Curve(df[df["cdp_xline"]==x], ["utmx", "utmy"],["cdp_xline","cdp_iline","tracf"])
        xlines.opts(line_width=1, color="blue", height=500, width=500, tools=[hover_x])
        
        xline = xline * xlines
    
    return (xline)

# 10) basemap(cube_dataframe, wells_dataframe)
def basemap(cube_dataframe, wells_dataframe):
      
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
    
    # Making the cube argument less stressful to read
    df = cube_dataframe
    
    # Computing the step in each plot line **
    
    # First element of the Basemap: wells
    wells = wells_plot(wells_dataframe)
    
    # Second element of the Basemap: boundary polygon
    polygon = polygon_plot(cube_dataframe)
    
    # Third element of the Basemap: traces
    traces = trace_plot(cube_dataframe, step_selection(cube_dataframe, "tracf", ))
    
    # Fourth element of the Basemap: inlines
    inlines = inline_plot(cube_dataframe, step_selection(cube_dataframe, "cdp_iline" ))
    
    # Fith element of the Basemap: crosslines
    crosslines = xline_plot(cube_dataframe, step_selection(cube_dataframe, "cdp_xline" ))
         
    # Overlaying the elements. Setting the basemap element
    basemap = wells * polygon * traces * inlines * crosslines
    
    # Setting options and formats to the final plot    
    basemap.opts(padding = 0.1,height=500, width=500,
                 title = 'Seismic Survey: '+ seismic_survey,
                 fontsize={'title': 16, 'labels': 14, 'xticks': 8, 'yticks': 8},
                 xlabel = 'Coordenadas UTM X (m)', ylabel = 'Coordenadas UTM Y (m)', 
                 legend_position='top_left',
                 xformatter='%f', yformatter='%f')
    
    return (basemap)

# 10.1) basemap_without_inputs (cube_dataframe, wells_dataframe,steps
def basemap_without_inputs(cube_dataframe, wells_dataframe,nput):
       
    """
    
    TESTING FUNCTION: BASEMAP WITHOUT INPUT METHODS
    
    """
    
    # Making the cube argument less stressful to read
    df = cube_dataframe
    
    # Computing the step in each plot line **
    
    # First element of the Basemap: wells
    wells = wells_plot(wells_dataframe)
    
    # Second element of the Basemap: boundary polygon
    polygon = polygon_plot(cube_dataframe)
    
    # Third element of the Basemap: traces
    traces = trace_plot(cube_dataframe, step_selection_without_inputs(cube_dataframe, "tracf" , nput))
    
    # Fourth element of the Basemap: inlines
    inlines = inline_plot(cube_dataframe, step_selection_without_inputs(cube_dataframe, "cdp_iline", nput))
    
    # Fith element of the Basemap: crosslines
    crosslines = xline_plot(cube_dataframe, step_selection_without_inputs(cube_dataframe, "cdp_xline", nput))
         
    # Overlaying the elements. Setting the basemap element
    basemap = wells * polygon * traces * inlines * crosslines
    
    # Setting options and formats to the final plot    
    basemap.opts(padding = 0.1,height=500, width=500,
                 title = 'Seismic Survey: '+ seismic_survey,
                 fontsize={'title': 16, 'labels': 14, 'xticks': 8, 'yticks': 8},
                 xlabel = 'Coordenadas UTM X (m)', ylabel = 'Coordenadas UTM Y (m)', 
                 legend_position='top_left',
                 xformatter='%f', yformatter='%f')
    
    return (basemap)

# 11)number_of_lines_for_window()
def number_of_lines_for_window():
    
    """
    
    A function that allows the user to select a dimension to build a window from a DataFrame. 
    It's part of the arguments of the window_selection_dataframe function.
    
    Arguments:
    No argument. Instead the function allows the user to choose it through an input method.
     
    Return:
    n_lines : Integer. The amount of lines to be taken in consideration by the 
              window_selection_dataframe function.
       
    """
    while True:
        val1 = step_validation(input('Introduce the amonunt of lines to take around the selected trace to build a subvolumen (20 max) : '),20) 
        if val1 == False:
            print(" ")
        else: 
            print(" ")
            break 

    return (val1)

# 11.1) number_of_lines_for_window_without_inputs()
def number_of_lines_for_window_without_inputs(nput):
        
    """
    
    TESTING FUNCTION: NUMBER OF LINES FOR WINDOW WITHOUT 
    INPUT METHODS
       
    """
    while True:
        val1 = step_validation(nput,20) 
        if val1 == False:
            return False
            break
            print(" ")
        else: 
            print(" ")
            break 

    return (val1)

# 12) window_selection_dataframe(inline, crossline, dataframe)
def window_selection_dataframe(inline, crossline, dataframe):
    
    """
    
    A function to build a window around the intersection of the given inline and crossline 
    coordinates. The amount of data selected depends on the number of lines (in both seismic 
    directions) choosen through and input method (Number_of_lines_for_window function)
    
    Argument:
    inline : Integer. Inline coordinate set as datum to build the window.
    
    crossline: Integer. Crossline coordinate set as datum to build the window.
    
    dataframe: (Pandas) DataFrame. Source of the coordinates to be computed as the window's limits.

    
    Example:
    If the lines cordinates are: (inline,crossline) = (2900,2200) and the "number_of_lines" 
    output is equal to 5, then this function will extract from the dataframe given the values 
    related to the intersecion of the lines. It will aso extract 5 lines around the 
    trace: 5 lines up and down the intersection selected for both directions: inline and crossline.
    
    Return:
    cropped_dataframe : (Pandas) DataFrame. Window of study which dimensions are equal to:
                        2 * number_of_lines_for_window + 1. Default headers as columns: 
                        {'tracf','(CDP)utmx','(CDP)utmy','(CDP)iline','(CDP)xline'}
    
    """
    
    # Setting the amount of lines to plot around the given trace
    number_of_lines = number_of_lines_for_window()
    
    # Defining the boundaries of the window
    iline_min = inline - number_of_lines
    iline_max = inline + number_of_lines
    xline_min = crossline - number_of_lines
    xline_max = crossline + number_of_lines
    
    # Solving boundarie's problems: this adds more lines either in inline or crossline directions according to
    # how many lines the previous formula exceeds. By default, the amount of lines plotted is 11 (I/X) > 5-1-5 <
    if iline_min < dataframe['cdp_iline'].min():
        iline_max = iline_max + abs(iline_min - dataframe['cdp_iline'].min())
        
    if iline_max > dataframe['cdp_iline'].max():
        iline_min = iline_min - abs(iline_max - dataframe['cdp_iline'].max())    
    
    if xline_min < dataframe['cdp_xline'].min():
        xline_max = xline_max + abs(xline_min - dataframe['cdp_xline'].min()) 
        
    if xline_max > dataframe['cdp_xline'].max():
        xline_min = xline_min - abs(xline_max - dataframe['cdp_xline'].max()) 
        
    # Selecting the data according to the boundaries
    cropped_dataframe = dataframe[(dataframe.cdp_iline >= iline_min) &
                                  (dataframe.cdp_iline <= iline_max) & 
                                  (dataframe.cdp_xline >= xline_min) &
                                  (dataframe.cdp_xline <= xline_max)]
    
    #Reset and delete the index of the dataframe
    cropped_dataframe = cropped_dataframe.reset_index().drop(columns='index')
    
    return (cropped_dataframe)

# 12.1) window_selection_dataframe_without_inputs(inline, crossline, dataframe)
def window_selection_dataframe_without_inputs(inline, crossline, dataframe, number_of_lines):
    
    """
    
    TESTING FUNCTION: WINDOW SELECTION DATAFRAME WITHOUT 
    INPUT METHODS
    
    """
    
    # Setting the amount of lines to plot around the given trace
    number_of_lines = number_of_lines
    
    # Defining the boundaries of the window
    iline_min = inline - number_of_lines
    iline_max = inline + number_of_lines
    xline_min = crossline - number_of_lines
    xline_max = crossline + number_of_lines
    
    # Solving boundarie's problems: this adds more lines either in inline or crossline directions according to
    # how many lines the previous formula exceeds. By default, the amount of lines plotted is 11 (I/X) > 5-1-5 <
    if iline_min < dataframe['cdp_iline'].min():
        iline_max = iline_max + abs(iline_min - dataframe['cdp_iline'].min())
        
    if iline_max > dataframe['cdp_iline'].max():
        iline_min = iline_min - abs(iline_max - dataframe['cdp_iline'].max())    
    
    if xline_min < dataframe['cdp_xline'].min():
        xline_max = xline_max + abs(xline_min - dataframe['cdp_xline'].min()) 
        
    if xline_max > dataframe['cdp_xline'].max():
        xline_min = xline_min - abs(xline_max - dataframe['cdp_xline'].max()) 
        
    # Selecting the data according to the boundaries
    cropped_dataframe = dataframe[(dataframe.cdp_iline >= iline_min) &
                                  (dataframe.cdp_iline <= iline_max) & 
                                  (dataframe.cdp_xline >= xline_min) &
                                  (dataframe.cdp_xline <= xline_max)]
    
    #Reset and delete the index of the dataframe
    cropped_dataframe = cropped_dataframe.reset_index().drop(columns='index')
    
    return (cropped_dataframe)


