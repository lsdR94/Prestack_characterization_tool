# Data accessing
import os

# Math
import numpy as np

# Data management
import pandas as pd

# SEGY files management
import segyio

# Visualization
import holoviews as hv
from holoviews import opts
from bokeh.models import HoverTool
import panel as pn
hv.extension('bokeh')


def point_validation(cube_dataframe):
    
    """

        (Currently on development)
    Validates the given (pandas) DataFrame for any method used to make it:
    1) By Scanning the SEG-Y files.
    2) By giving some initial cordinates.
    
    Arguments
    ---------
    dataframe : (Pandas)Dataframe
        Source of the points to use.
        
    Return
    ------
    polygon_dataframe : (Pandas)Dataframe
        A matrix composed by the outer points of the survey:
            - iline: inline coordinate.
            - xline: crossline coordinate.
            - utmx: horizontal axis of the Universal Transversal Mercator coordinate system.
            - utmy: vertical axis of the Universal Transversal Mercator coordinate system. 

    See also
    --------
        1) utils.cube_data_organization
        2) polygon_plot

    """
    
    x1, y1 = cube_dataframe["utmx"].iloc[0], cube_dataframe["utmy"].iloc[0]
    x2, y2 = cube_dataframe["utmx"].iloc[1], cube_dataframe["utmy"].iloc[1]
    x3, y3 = cube_dataframe["utmx"].iloc[2], cube_dataframe["utmy"].iloc[2]
    x4, y4 = cube_dataframe["utmx"].iloc[3], cube_dataframe["utmy"].iloc[3]
    
    if cube_dataframe["utmx"].iloc[0] == 0:
        cube_dataframe["utmx"].iloc[0], cube_dataframe["utmy"].iloc[0] = x4 - x3 + x2, y4 - y3 + y2  
        
    if cube_dataframe["utmx"].iloc[1] == 0:
        cube_dataframe["utmx"].iloc[1], cube_dataframe["utmy"].iloc[1] = x1 - x4 - x3, y1 - y4 - y3
        
    if cube_dataframe["utmx"].iloc[2] == 0:
        cube_dataframe["utmx"].iloc[2], cube_dataframe["utmy"].iloc[2] = x4 - x1 - x2, y4 - y1 - y2   
        
    if cube_dataframe["utmx"].iloc[3] == 0:
        cube_dataframe["utmx"].iloc[3], cube_dataframe["utmy"].iloc[3] = x1 - x2 + x3, y1 - y2 + y3
    
    # Re-evaluating the dataframe (I DON'T WANT TO LOOSE THIS CODE yet)
    utmx_min = cube_dataframe.iloc[cube_dataframe["utmx"].idxmin()]
    utmx_max = cube_dataframe.iloc[cube_dataframe["utmx"].idxmax()]
    utmy_min = cube_dataframe.iloc[cube_dataframe["utmy"].idxmin()]
    utmy_max = cube_dataframe.iloc[cube_dataframe["utmy"].idxmax()]
    
    # Rebuilding the given dataframe
    polygon_dataframe = pd.concat([utmx_min,utmy_min,utmx_max,utmy_max,utmx_min],
                                   ignore_index = True, axis = "columns").transpose()
    
    polygon_dataframe.iline = polygon_dataframe.iline.astype(int)
    polygon_dataframe.xline = polygon_dataframe.xline.astype(int)
    
    return(polygon_dataframe)

def polygon_plot(seismic_dataframe):
    
    """
    
    Plots the boundaries of the Seismic Survey using Holoview's bokeh backend.
    
    Arguments
    ---------
    seismic_dataframe : (Pandas) DataFrame. 
        A matrix compounded by the coordinates of the edge points of a survey.

    Return
    ------
    polygon_dataframe : (Pandas)DataFrame
        A matrix composed by the trace header information of interest: coordinates of the traces along
        the Survey's polygon.
        
    pol : Holviews element [Curve]
        Polygon that represents the boundaries of the Seismic Survey.
        
    See Also
    --------
        1) get_basemap
    
    """
    
    # Loading the polygon dataframe.
    polygon_dataframe = point_validation(seismic_dataframe)
    
    #Plotting the boundaries of the Seismic Survey. Holoviews Curve element
    pol = hv.Curve(polygon_dataframe,["utmx","utmy"], label = "Polygon")
    pol.opts(line_width=2, color="black", tools = ['pan','wheel_zoom','reset'], default_tools=[])
    
    return [pol, polygon_dataframe]

def wells_plot(polygon_dataframe, wells_dataframe):
    
    """
    
    Plots the wells inside the Seismic Survey's polygon using Holoview's bokeh backend.
    
    The function plots only the wells inside the Seismic Survey given, therefore every well outside the this
    will be excluded from the final output.
    
    Arguments
    ---------
    polygon_dataframe : (Pandas)DataFrame
        A matrix composed by the trace header information of interest: coordinates of the 
        Seismic traces.
    
    wells_dataframe : (Pandas)DataFrame.
        A matrix formed by the information of each well inside the Seismic Survey.
    
    Return
    ------
    wells : Holviews element [Scatter]. 
        A plot of the wells inside the Seismic Survey.
    
    See also
    --------
        1) utils.wells_data_organization
        2) polygon_plot

    """
   
    # Plotting Wells. Holoviews Scatter element
    wells = hv.Scatter(wells_dataframe,["utmx","utmy"],
                       ["name","cdp_iline", "cdp_xline"], 
                       label = "Wells")
    wells.opts(line_width = 1,
               color = "green",size = 7 ,marker = "^",
               padding = 0.1, width=600, height=400, show_grid=True, 
               tools = ['pan','wheel_zoom','reset'], default_tools=[])
    
    # Adjusting the number of wells according to the outer polygon_building(cube_dataframe)
    l1 = polygon_dataframe["utmx"].loc[polygon_dataframe["utmx"].idxmin()]
    l2 = polygon_dataframe["utmx"].loc[polygon_dataframe["utmx"].idxmax()]
    l3 = polygon_dataframe["utmy"].loc[polygon_dataframe["utmy"].idxmin()]
    l4 = polygon_dataframe["utmy"].loc[polygon_dataframe["utmy"].idxmax()]
    
    return (wells[l1:l2,l3:l4])

def seismic_lines_dataframe(polygon_dataframe):
    
    """
    
    Builds two dataframes that contains the coordinates of the points belonging to the first 
    inline and first crossline.
    
    Argument
    --------
    polygon_dataframe : (Pandas)DataFrame
        A matrix composed by the trace header information of interest: coordinates of the traces along
        the Survey's polygon.
    
    Return
    ------
    list_of_dataframes : (Pandas)DataFrame
        A list of two dataframes, where the first one contains all the coordinates of the points within
        the first crossline and the second one, all the coordinates of the points inside the first inline.

    See also
    --------
        1) polygon_plot
        2) seismic_line_plot
        3) seismic_intersection 
        4) gather_box
        5) get_basemap

    """
    
    # Less stresful to read the code
    df = polygon_dataframe

    # Computing the diference between min/max of the seismic lines
    dif_ilines = abs(df["iline"].min() - df["iline"].max()) + 1
    dif_xlines = abs(df["xline"].min() - df["xline"].max()) + 1
    
    # array of point's coordinates inside the first inline (based on dif_ilines)
    x_utmx = np.linspace(float(df[df["utmy"] == df["utmy"].min()]["utmx"]), 
                         df["utmx"].min(), 
                         num = dif_xlines, endpoint = True)

    x_utmy = np.linspace(df["utmy"].min(), 
                         float(df[df["utmx"] == df["utmx"].min()]["utmy"][0]), 
                         num = dif_xlines, endpoint = True)
    
    # Array of lines across the inline direction
    xlines = np.arange(df["xline"].min(), 
                       df["xline"].max() + 1, 
                       1)
    
    # array of point's coordinates inside the first xline (based on dif_xlines)
    i_utmx = np.linspace(float(df[df["utmy"] == df["utmy"].min()]["utmx"]), 
                         df["utmx"].max(), 
                         num = dif_ilines, endpoint = True)

    i_utmy = np.linspace(df["utmy"].min(), 
                         float(df[df["utmx"] == df["utmx"].max()]["utmy"]), 
                         num = dif_ilines, endpoint = True)
    
    # Array of lines across the crossline direction
    ilines = np.arange(df["iline"].min(), 
                       df["iline"].max() + 1,
                       1)
    
    # Making dataframes to ease further calculations
    xline_dataframe = pd.DataFrame({"iline": df["iline"].min(),
                                     "xline": xlines,
                                     "utmx": x_utmx, "utmy": x_utmy})
    iline_dataframe = pd.DataFrame({"iline": ilines,
                                     "xline": df["xline"].min(),
                                     "utmx": i_utmx, "utmy": i_utmy})

    return([iline_dataframe, xline_dataframe])

def seismic_line_plot(polygon_dataframe, iline_number, xline_number):
    
    """
    
    Plots the seismic lines given set of inline and crossline coordinates using Holoview's bokeh backend.
    
    Arguments
    ---------
    polygon_dataframe : (Pandas)DataFrame
        A matrix composed by the trace header information of interest: coordinates of the traces along
        the Survey's polygon.
        
    iline_number : int
        Number of the seismic line along the inline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    xline_number : int
        Number of the seismic line along the crossline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
        
    Return
    ------   
    seismic_lines : Holviews element [Overlay]
        A collection seismic lines inside the survey.
    
    References
    ----------
        bokeh.pydata.org. Change the attributes of the hover tool. Online document:
        https://bokeh.pydata.org/en/latest/docs/reference/models/tools.html#bokeh.models.tools.HoverTool.point_policy
    
    See also
    --------
        1) polygon_plot
        2) seismic_lines_dataframe
        3) seismic_intersection
        4) get_basemap

    """

    # Assigning a variable for each dataframe in seismic_lines_dataframe
    ilines, xlines = seismic_lines_dataframe(polygon_dataframe)
    
    # Declaring the Hover tools (each line will use one)
    iline_hover = HoverTool(tooltips=[("Inline", f"{iline_number}"),
                                      ("Utmx", "$x{(0.00)}"),
                                      ("Utmy", "$y{(0.00)}")])

    xline_hover = HoverTool(tooltips=[("Crossline", f"{xline_number}"),
                                      ("Utmx", "$x{(0.00)}"),
                                      ("Utmy", "$y{(0.00)}")])
    
    # Changing the attributes of the hover tool
    iline_hover.show_arrow, xline_hover.show_arrow = False, False
    iline_hover.point_policy, xline_hover.point_policy = "follow_mouse", "follow_mouse"
    iline_hover.anchor, xline_hover.anchor = "bottom_right", "bottom_right"
    iline_hover.attachment, xline_hover.attachment = "right", "right"
    iline_hover.line_policy, xline_hover.line_policy = "interp", "interp"
    
    # Computing the second point to plot the seismic lines (By using vector differences)
    ## This can be refactored
    iutmx = float(xlines["utmx"].iloc[-1] - xlines["utmx"].iloc[0] + ilines[ilines["iline"] == iline_number]["utmx"])
    iutmy = float(xlines["utmy"].iloc[-1] - xlines["utmy"].iloc[0] + ilines[ilines["iline"] == iline_number]["utmy"])
    xutmx = float(ilines["utmx"].iloc[-1] - ilines["utmx"].iloc[0] + xlines[xlines["xline"] == xline_number]["utmx"])
    xutmy = float(ilines["utmy"].iloc[-1] - ilines["utmy"].iloc[0] + xlines[xlines["xline"] == xline_number]["utmy"])

    # Plotting the Inline. Holoviews Curve element
    iline = hv.Curve([(float(ilines[ilines["iline"] == iline_number]["utmx"]), 
                        float(ilines[ilines["iline"] == iline_number]["utmy"])),
                       (iutmx, iutmy)])
    
    # Plotting the Crossline. Holoviews Curve element
    xline = hv.Curve([(float(xlines[xlines["xline"] == xline_number]["utmx"]), 
                        float(xlines[xlines["xline"] == xline_number]["utmy"])),
                       (xutmx, xutmy)])
    
    # Adding the hover tool in to the plots
    iline.opts(line_width = 2, color = "red", 
               tools = [iline_hover] + ['pan','wheel_zoom','reset'], default_tools=[])
    xline.opts(line_width = 2, color = "blue", 
               tools = [xline_hover] + ['pan','wheel_zoom','reset'], default_tools=[])
    
    # Making the overlay of the seismic plot to deploy
    seismic_lines = iline * xline
    
    return seismic_lines

def seismic_intersection(polygon_dataframe, iline_number, xline_number):
    
    """
    
    Computes the intersection of the seismic lines.
    
    Arguments
    ---------
    polygon_dataframe : (Pandas)DataFrame
        A matrix composed by the trace header information of interest: coordinates of the traces along
        the Survey's polygon.
        
    iline_number : int
        Number of the seismic line along the inline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    xline_number : int
        Number of the seismic line along the crossline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
        
    Return
    ------
    trac_list : list
        A list of the information of the seismic intersection:
            - tracf: trace number within the original field record.
            - utmx: horizontal axis of the Universal Transversal Mercator coordinate system.
            - utmy: vertical axis of the Universal Transversal Mercator coordinate system.  
     
    Formula
    -------
        To calculate the tracf given the geometry data:
        
            tracf = ΔLine(inline direction) * #CDP + ΔXline + 1
            
            where:
            - ΔLine(inline direction) is the amount of lines between the first inline and the given one.
            - #CDP the amount of CDP per crosslines.
            - ΔXline the difference between the given xline number and the first one.
            - +1 to count the first point (offten forgotten)

    See also
    --------
        1) polygon_plot
        2) seismic_lines_dataframe
        3) seismic_line_plot
        4) gather_box
        5) get_basemap
         
    """
    
    # Assigning a variable for each dataframe in seismic_lines_dataframe
    ilines, xlines = seismic_lines_dataframe(polygon_dataframe)
    
    # Computing the amount of CDP along the crosslines 
    dif_xlines = abs(polygon_dataframe["xline"].max() - polygon_dataframe["xline"].min()) + 1
    
    # Tracf computation
    tracf_number = (iline_number - polygon_dataframe["iline"].min()) * dif_xlines + (xline_number - polygon_dataframe["xline"].min()) + 1
    
    # Tracf coordinates computation
    bx = float(xlines[xlines["xline"] == xline_number]["utmx"])
    by = float(xlines[xlines["xline"] == xline_number]["utmy"])
    ax = xlines["utmx"].iloc[0]
    ay = xlines["utmy"].iloc[0]
    cx = float(ilines[ilines["iline"] == iline_number]["utmx"])
    cy = float(ilines[ilines["iline"] == iline_number]["utmy"])
    
    tutmx = bx - ax + cx
    tutmy = by - ay + cy
    
    trac_list = [int(tracf_number), tutmx, tutmy]
    return (trac_list)

def seismic_intersection_plot(polygon_dataframe, iline_number, xline_number):
    
    """
    
    Plots the intersection of the seismic lines using Holoview's bokeh backend.
    
    Arguments
    ---------    
    polygon_dataframe : (Pandas)DataFrame
        A matrix composed by the trace header information of interest: coordinates of the traces along
        the Survey's polygon.
        
    iline_number : int
        Number of the seismic line along the inline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    xline_number : int
        Number of the seismic line along the crossline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
        
    Return
    ------
    tracf_plot : Holviews element [Scatter]
        A plot of the interseccion of the seismic lines.
    
    See also
    --------
        1) seismic_intersection
        2) get_basemap

    """
    
    tracf_list = seismic_intersection(polygon_dataframe, 
                                      iline_number, xline_number)
    
    # Declaring the Hover tools (each line will use one)
    tracf_hover = HoverTool(tooltips=[("Tracf", f"{tracf_list[0]}"),
                                      ("(I/X)", f"({iline_number}/{xline_number})"),
                                      ("(Utmx, Utmy)", "($x{(0.00)},$y{(0.00)}")])

    # Changing the attributes of the hover tool
    tracf_hover.show_arrow = False
    tracf_hover.point_policy = "follow_mouse"
    tracf_hover.anchor = "bottom_right"
    tracf_hover.attachment = "right"
    tracf_hover.line_policy = "interp"
    
    
    # Plot the intersection. Holovies Scatter element.
    tracf_plot = hv.Scatter((tracf_list[1], tracf_list[2]))
    tracf_plot.opts(size = 7, line_color = "black", line_width = 2, color = "yellow",
               tools = [tracf_hover] + ['pan','wheel_zoom','reset'], default_tools=[])
    
    return(tracf_plot)

def gather_box(polygon_dataframe, iline_number, xline_number, number_of_gathers_to_display, inline_step, crossline_step):
    
    """
    
    Builds points (Pandas)Dataframes of the traces around the intesection of the given lines.
    
    This function calculates the tracf and the coordinates of the traces around the interseccion within
    a window which dimensions are equal to the square of the number_of_gathers_to_display arguement.
    
    Arguments
    ---------     
    polygon_dataframe : (Pandas)DataFrame
        A matrix composed by the trace header information of interest: coordinates of the traces along
        the Survey's polygon.
        
    iline_number : int
        Number of the seismic line along the inline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    xline_number : int
        Number of the seismic line along the crossline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
        
    number_of_gathers_to_display : int
        Number of points to be calculated, plot and displayed around the intersection of the seismic lines.
        
    Return
    ------
    [df, iline_gathers, xline_gathers] : list of (Pandas)Dataframe
        List of three matrix where df is the array with all the traces inside the box and 
        inline_gathers/xline_gathers are the dataframes whose points math the seismic lines given. Each 
        dataframe is compounded by the following columns:
            - tracf: trace number within the original field record.
            - utmx: horizontal axis of the Universal Transversal Mercator coordinate system.
            - utmy: vertical axis of the Universal Transversal Mercator coordinate system. 
            - iline: inline coordinate.
            - xline: crossline coordinate.
    
    See also
    --------
        1) polygon_plot
        2) seismic_lines_dataframe
        3) seismic_intersection
        4) gather_box_plot
        5) get_basemap

    """
    
    # Less stressful to read
    nd = number_of_gathers_to_display
    
    # Tracf number and coordinates
    tracf = seismic_intersection(polygon_dataframe, 
                                 iline_number, xline_number)
    
    # Points of the seismic lines
    ilines = seismic_lines_dataframe(polygon_dataframe)[0]
    xlines = seismic_lines_dataframe(polygon_dataframe)[1]
    
    # number_of_gathers_to_display = 2
    tracf_dataframe = pd.DataFrame(columns = {"tracf","utmx","utmy"})
    tracf_list = []
    
    # max min seismic lines 
    iline_min = iline_number - nd//2 * inline_step
    iline_max = iline_number + nd//2 * inline_step
    xline_min = xline_number - nd//2 * crossline_step
    xline_max = xline_number + nd//2 * crossline_step
    
    # Solving boundary problems
    if iline_min < polygon_dataframe["iline"].min():
        iline_max = iline_max + abs(polygon_dataframe["iline"].min() - iline_min)       
        iline_min = polygon_dataframe["iline"].min()
        
    if iline_max > polygon_dataframe["iline"].max():
        iline_min = iline_min - abs(polygon_dataframe["iline"].max() - iline_max)       
        iline_max = polygon_dataframe["iline"].max()
        
    if xline_min < polygon_dataframe["xline"].min():
        xline_max = xline_max + abs(polygon_dataframe["xline"].min() - xline_min)       
        xline_min = polygon_dataframe["xline"].min()
        
    if xline_max > polygon_dataframe["xline"].max():
        xline_min = xline_min - abs(polygon_dataframe["xline"].max() - xline_max)       
        xline_max = polygon_dataframe["xline"].max()

    # tracs around the intersection
    for inline in range(int(iline_min), int(iline_max) + 1, 1):
        for xline in range(int(xline_min), int(xline_max) + 1, 1):
            tracf_coordinates = seismic_intersection(polygon_dataframe, inline, xline)
            
            tracf_list = tracf_list + [tracf_coordinates + [inline, xline]]
            
    df = pd.DataFrame(tracf_list, columns = ["tracf","utmx","utmy", "iline", "xline"])   
    
    # extracting the possible gathers along the seismic lines
    iline_gathers = df[(df.iline >= iline_min) &
                        (df.iline <= iline_max) & 
                        (df.xline == xline_number)]
    
    xline_gathers = df[(df.xline >= xline_min) &
                        (df.xline <= xline_max) & 
                        (df.iline == iline_number)]
    
    return([df, iline_gathers, xline_gathers])

def gather_box_plot(gather_box_list):
    
    """
    
    Plots the gather's window, intersection of the seismic lines and the traces around the last one within
    the first.
    
    Argument
    --------
    gather_box_list : llist of (Pandas)Dataframe
        List of three matrix where df is the array with all the traces inside the box and 
        inline_gathers/xline_gathers are the dataframes whose points math the seismic lines given.
    
    Return
    ------
    overlay : Holviews element [Overlay]
        A collection traces inside the gather window.
    
    See also
    --------
        1) gather_box
        2) get_basemap

    """ 
    # Unboxing the list of the gathers points
    df, iline_gathers, xline_gathers = gather_box_list
   
    # Making a polygon that contains the gathers
    polygon_gathers = point_validation(df)
    
    # Setting hovers for the data
    hover = HoverTool(tooltips=[("I/X", f"@iline" + "/" + f"@xline"),
                                ("X/Y", "f@utmx" + "/" + f"@utmy"),
                                ("Trace number", f"@tracf")])

    # Changing the attributes of the hover tool
    hover.show_arrow = False
    hover.point_policy = "follow_mouse"
    hover.anchor = "bottom_right"
    hover.attachment = "right"
    hover.line_policy = "interp"
    
    # Plotting the position of the gathers
    plot_iline_gather = hv.Scatter(iline_gathers, ["utmx", "utmy"], ["tracf", "iline", "xline"]) 
    plot_iline_gather. opts(size = 4, line_color = "black", line_width = 2, color = "red",
                           tools = [hover] + ['pan','wheel_zoom','reset'], default_tools=[])
    plot_xline_gather = hv.Scatter(xline_gathers, ["utmx", "utmy"], ["tracf", "iline", "xline"])
    plot_xline_gather. opts(size = 4, line_color = "black", line_width = 2, color = "blue",
                           tools = [hover] + ['pan','wheel_zoom','reset'], default_tools=[])
    
    # Plotting the gather's cage
    polygon = hv.Curve(polygon_gathers, ["utmx","utmy"]).opts(line_width = 2, line_color = "black")
    points = hv.Scatter(polygon_gathers, ["utmx","utmy"]).opts(size = 3, color = "black")
    
    #Overlay
    overlay = polygon * points * plot_xline_gather * plot_iline_gather
    
    return(overlay)

def get_basemap(seismic_dataframe, wells_dataframe, seismic_survey, inline_step, crossline_step):
    
    """
    
    Plots an interactive basemap for a given geometry and wells data.
    
    Arguments
    ---------
    seismic_dataframe : (Pandas) DataFrame. 
        A matrix compounded by the coordinates of the edge points of a survey.
        
    wells_dataframe : (Pandas)DataFrame.
        A matrix formed by the information of each well inside the Seismic Survey.
           
    Return
    ------
    NdLayout : Panel layout element [Row]
        A Seismic Basemap and Panel's widgets listed as controls:
            - Two track bars to inspect the data by setting different inline and xline numbers.
            - A track bar to modify the amount of gathers displayed.
            - A select panel to choose the Well to inspect.
    
    See also
    --------
        1) polygon_plot
        2) wells_plot
        3) seismic_line_plot
        4) seismic_intersection_plot
        5) gather_box_plot

    """
    
    
    # Widgets
    iline_number = pn.widgets.IntSlider(name = "Inline number",
                                        start = int(seismic_dataframe["iline"].min()),
                                        end = int(seismic_dataframe["iline"].max()),
                                        step = 1,
                                        value = int(seismic_dataframe["iline"].min()))
    
    xline_number = pn.widgets.IntSlider(name = "Crossline number",
                                        start = int(seismic_dataframe["xline"].min()),
                                        end = int(seismic_dataframe["xline"].max()),
                                        step = 1,
                                        value = int(seismic_dataframe["xline"].min()))
    
    gather_display = pn.widgets.IntSlider(name = "Number of gathers to display",
                                          start = 2,
                                          end = 6,
                                          step = 2,
                                          value = 2)
    
    select_well = pn.widgets.Select(name = "Select the well to inspect", 
                                    options = ["None"] + list(wells_dataframe["name"]),
                                    value = "None")
    
    @pn.depends(iline_number.param.value, xline_number.param.value, 
                gather_display.param.value, 
                select_well.param.value)
    
    def basemap_plot(iline_number, xline_number, gather_display, select_well):
        
        if select_well !=  "None":
            iline_number = int(well_dataframe[well_dataframe["name"] == select_well]["cdp_iline"])
            xline_number = int(well_dataframe[well_dataframe["name"] == select_well]["cdp_xline"])
        
        # First element
        seismic_polygon, polygon_dataframe = polygon_plot(seismic_dataframe)

        # Second element
        wells = wells_plot(seismic_dataframe, wells_dataframe)
        
        # Third element
        seismic_lines = seismic_line_plot(polygon_dataframe, 
                                          iline_number, xline_number)

        # Fourth element
        gather = gather_box(polygon_dataframe, 
                            iline_number, xline_number, gather_display, inline_step, crossline_step)
        
        gathers = gather_box_plot(gather)

        # Fifth element dataframe
        tracf = seismic_intersection_plot(polygon_dataframe, 
                                          iline_number, xline_number) 
     
        # Final Overlay
        basemap = seismic_polygon * wells * seismic_lines * gathers * tracf

        return(basemap)
    
    widgets = pn.WidgetBox(f"## {seismic_survey} Basemap", iline_number, xline_number, 
                                          gather_display, select_well)
    
    return pn.Row(widgets, basemap_plot).servable()








