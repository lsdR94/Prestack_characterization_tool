# Dependencies
import os
import segyio
import numpy as np
import pandas as pd
import holoviews as hv
from holoviews import opts, dim
from bokeh.models import HoverTool
hv.extension('bokeh')
# Panel and Hvplot
import panel as pn
import hvplot.pandas
import panel.widgets as pnw
# Basemap functions
default_tools = ['pan','wheel_zoom','reset']

# 1) Computing function: limits of the plot
def polygon_building(cube_dataframe):
    
    """
    polygon_building(cube_dataframe)
    
    Computes the limit of the Seismic Survey given a DataFrame.
    
    Argument
    --------
    cube_dataframe : (Pandas) DataFrame
        A matrix compounded by the trace header information of interest: coordinates of the 
        Seismic traces.
        
    Return
    ------
    polygon : (Pandas) DataFrame
        A matrix compounded only by the coordinates of the polygon's edges. Default columns:
        {"utmx_min","utmy_min","utmx_max", "utmy_max","utmx_min"}
                  
    Note
    ----
    One column is repeated in order to close the polygon further in the plot functions.
    
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

# 2) Plotting function: limits of the plot
def polygon_plot(cube_dataframe):
    
    """
    polygon_plot(cube_dataframe)
    
    Plots the boundaries of the Seismic Survey using Holoview's bokeh backend.
    
    Arguments
    ---------
    cube_dataframe : (Pandas) DataFrame. 
        A matrix compounded by the trace header information of interest: coordinates of the 
        Seismic traces.

    Return
    ------
    pol : Holviews element [Curve]
        Polygon that represents the boundaries of the Seismic Survey.
        
    See Also
    --------
    Plot functions:
        1) polygon_building(cube_dataframe)
    
    """
    
    # Loading the polygon dataframe.
    polygon = polygon_building(cube_dataframe)
    
    #Plotting the boundaries of the Seismic Survey. Holoviews curve element
    pol = hv.Curve(polygon,"utmx","utmy", label = "Polygon")
    pol.opts(line_width=2, color="black", tools = default_tools, default_tools=[])
    
    return (pol)

# 3) Plotting function: wells
def wells_plot(cube_dataframe, wells_dataframe):
    
    """
    wells_plot(cube_dataframe, wells_dataframe)
    
    Plots the wells inside the Seismic Survey polygon using Holoview's bokeh backend.
    
    The function plots only the wells inside the Seismic Survey given. Every well outside the area
    mentioned before will be deleated from the final output.
    
    Arguments
    ---------
    wells_dataframe : (Pandas) DataFrame.
        A matrix compounded by the information of each well inside the Seismic Survey.
    
    cube_dataframe : (Pandas) DataFrame
        A matrix compounded by the trace header information of interest: coordinates of the 
        Seismic traces.
    
    Return
    ------
    wells : Holviews element [Scatter]. 
        A plot of the collection of wells inside the Seismic Survey.
    
    """
    # Plotting Wells. Holoviews scatter element
    wells = hv.Scatter(wells_dataframe,["utmx","utmy"],["name"], label = "Wells")
    wells.opts(line_width=1,
           color="green",size = 10 ,marker = "triangle",
           padding=0.1, width=600, height=400, show_grid=True, 
           tools= [HoverTool(tooltips=[("Pozo", "@name")])] + ['pan','wheel_zoom','reset'], default_tools=[])
    
    # Adjusting the number of wells according to the outer polygon_building(cube_dataframe)
    l1 = cube_dataframe["utmx"].iloc[cube_dataframe["utmx"].idxmin()]
    l2 = cube_dataframe["utmx"].iloc[cube_dataframe["utmx"].idxmax()]
    l3 = cube_dataframe["utmy"].iloc[cube_dataframe["utmy"].idxmin()]
    l4 = cube_dataframe["utmy"].iloc[cube_dataframe["utmy"].idxmax()]
    
    return (wells[l1:l2,l3:l4])

# 4) Plotting function: traces
def trace_plot(cube_dataframe):
    
    """
    trace_plot(cube_dataframe)
    
    Plots the traces of the Seismic Survey using Holoview's bokeh backend.
    
    Argument
    --------
    cube_dataframe : (Pandas) DataFrame
        A matrix compounded by the trace header information of interest: coordinates of the 
        Seismic traces.
       
    Return
    ------
    traces : Holviews element [Scatter]
        A plot of the collection of the Seismic traces inside the Survey.
    
    """
    # Less stressful to read
    df = cube_dataframe
    
    # Plotting traces inside the cube according to it's utm coordinates. Holoviews scatter element
    traces = hv.Scatter(df,["utmx", "utmy"],["tracf","cdp_xline","cdp_iline"], 
                        label= f"Trace (tracf)")
    traces.opts(line_width=0.2, color="grey",size = 2, height=500, width=500, 
                tools = default_tools, default_tools=[])
    
    return (traces)

# 5) Plotting function: seismic lines
def seismic_lines(cube_dataframe, iline_number, xline_number):
    
    """
    seismic_lines(cube_dataframe, iline_number, xline_number)
    
    Plots the seismic lines using Holoview's bokeh backend.
    
    Arguments
    ---------
    cube_dataframe : (Pandas) DataFrame
        A matrix compounded by the trace header information of interest: coordinates of the 
        Seismic traces.
    
    inline_number : int
        Number of the line along the inline axis to plot. Comes from Panel's slider widget.
    
    xline_number : int
        Number of the line along the crossline axis to plot. Comes from Panel's slider widget.
      
    Return
    ------
    traces : Holviews element [Scatter]. 
        A collection of the seismic lines inside the Survey.
        
    See Also
    --------
    Plot functions:
        1) get_basemap(cube_dataframe, wells_dataframe)
    
    """
    # Less stressful to read
    df = cube_dataframe
    
    # Computing the min and max cdp in for both directions
    iline_max = df["cdp_iline"].unique().max()
    iline_min = df["cdp_iline"].unique().min()
    xline_max = df["cdp_xline"].unique().max()
    xline_min = df["cdp_xline"].unique().min()
    
    # Plotting the lines according to the selected step. Holoviews curve element 
    iline = hv.Curve(df[df["cdp_iline"]==iline_number], ["utmx", "utmy"],
                          ["tracf"], label = f"Inline")
    iline.opts(line_width=2, color="red", height=500, width=500, 
               tools = [HoverTool(tooltips=[("Tracf", "@tracf")])] + default_tools, default_tools=[])
    xline = hv.Curve(df[df["cdp_xline"]==xline_number], ["utmx", "utmy"],
                          ["tracf"], label = f"Crossline")
    xline.opts(line_width=2, color="blue", height=500, width=500, 
               tools = [HoverTool(tooltips=[("Tracf", "@tracf")])] + default_tools, default_tools=[])
    
    return (iline * xline)

# 6) Plotting function: basemap 
def get_basemap(cube_dataframe, wells_dataframe, seismic_survey):

    """
    
    Plots the basic information of a Seismic Survey. 
    
    This function integrates the previous plots into one while combining it with Panel's widgets to improve
    the interaction between human-tool. 
    
    Arguments
    ---------
    wells_dataframe : (Pandas) DataFrame.
        A matrix compounded by the information of each well inside the Seismic Survey.
    
    cube_dataframe : (Pandas) DataFrame
        A matrix compounded by the trace header information of interest: coordinates of the 
        Seismic traces.
      
    Return
    ------
    basemap : Holviews element [Overlay]. 
        The output is the combination of the seismic survey polygon, the seismic traces, the lines along 
        the survey and the wells inside of it, a tool to show the coordinates and the identification of 
        each element have been implemented to the plot (Hover Tool) and Panel's widgets listed as 
        controls:
            - A track bar to modify each seismic line displayed.
            - A checkbox to display the traces around the seismic lines.
              
    See Also
    --------
    Plot functions:
        1) polygon_plot(cube_dataframe)
        2) wells_plot(cube_dataframe, wells_dataframe)
        4) trace_plot(cube_dataframe)
        3) seismic_lines(cube_dataframe, iline_number, xline_number)
    
    Notes
    -----
    This function combines Panel's widgets with the Holoviews plot elements. So the code distribution is
    delicate. Refactory must be done carefully in order to avoid bugs and malfunctions.
    
    References
    ----------
    Panel contributors. (2019). Temperature distribution. Document Online. Available at:
    https://panel.pyviz.org/gallery/simple/temperature_distribution.html#gallery-temperature-distribution

    """
    

    # Making the cube argument less stressful to read
    df = cube_dataframe
    
    # Declaration of widgets
    iline_number = pn.widgets.IntSlider(name = "Inline number", 
                                        start = int(df["cdp_iline"].unique().min()), 
                                        end = int(df["cdp_iline"].unique().max()), 
                                        step = 1, 
                                        value = int(df["cdp_iline"].unique().min()))
    
    xline_number = pn.widgets.IntSlider(name = "Crossline number", 
                                        start = int(df["cdp_xline"].unique().min()), 
                                        end = int(df["cdp_xline"].unique().max()), 
                                        step = 1, 
                                        value = int(df["cdp_xline"].unique().min()))
    
    display_traces = pn.widgets.Checkbox(name = "Show traces")    
    
    # Decorator to mess up with the API
    @pn.depends(iline_number.param.value, xline_number.param.value, display_traces.param.value)
    
    # A function must follow the decorator
    def basemap(iline_number, xline_number, display_traces):
        
        # First element of the Basemap: wells
        wells = wells_plot(cube_dataframe, wells_dataframe)

        # Second element of the Basemap: boundary polygon
        polygon = polygon_plot(cube_dataframe)

        # third element of the Basemap: seismic lines
        s_lines = seismic_lines(cube_dataframe, iline_number, xline_number)

        # Fourth element of the Basemap: traces
        traces = trace_plot(cube_dataframe)
        
        # Overlaying the elements. Setting the basemap element
        if display_traces:
            basemap = polygon * traces *  wells * s_lines
        else:
            basemap = polygon * wells * s_lines

        # Setting options and formats to the final plot    
        basemap.opts(padding = 0.1,height=500, width=500,
                     title = f"Seismic Survey: {seismic_survey}",
                     fontsize = {"title": 16, "labels": 14, "xticks": 8, "yticks": 8},
                     xlabel = "Coordenadas UTM X (m)", ylabel = "Coordenadas UTM Y (m)", 
                     legend_position = "top",
                     xformatter = "%f", yformatter="%f",
                     tools=['pan','wheel_zoom','reset'], default_tools=[])
        
        return (basemap)
    
    widgets = pn.WidgetBox(f"## Seismic lines ", iline_number, xline_number, display_traces)

    return(pn.Row(widgets, basemap).servable())
























