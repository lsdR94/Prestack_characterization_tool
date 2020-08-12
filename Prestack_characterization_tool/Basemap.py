# Dependencies
# file management
import os
from shutil import copyfile

# Calc
import numpy as np
import pandas as pd

# Visualization
import holoviews as hv
from holoviews import opts
from bokeh.models import HoverTool
from holoviews import streams
import panel as pn 

# Visualization platform
hv.extension('bokeh')

# Code

class BasemapModule:

    """
    NAME
    ----
        BasemapModule

    DESCRIPTION
    -----------
        Blueprint for Basemap objects.
        
        Plots seismic survey elements such as polygon, wells, lines and the intersection of these 
        lines while providing interactive tools to improve the experience between data and users. 
        These plots are not images but objects that can be modified by the user and exported as 
        images.
    
    ATTRIBUTES
    ----------
        basemap_dataframe : (Pandas)DataFrame
            Matrix compounded by the coordinates and lines of the seismic survey's corners. 
            Empty by default.

        wells_dataframe : (Pandas)DataFrame
            Matrix compounded by wells related information. Empty by default.

        polygon : Holviews element [Curve]
            Plot of the seismic survey polygon.

        wells : Holviews element [Scatter]
            Plot of the wells inside the seismic survey.

        seismic_lines : Holviews element [Overlay]
            Plot of the seismic lines (Inline referred as iline and Crossline referred as xline) 
            and its intersection.
            
        basemap : Holviews element [Overlay]
            Combination of the plots: polygon, wells and seismic_lines.
        
    METHODS
    -------
        polygon_plot(**kwargs)
            Constructs the polygon attribute.

        wells_plot(**kwargs)
            Constructs the wells attribute.   

        seismic_line_plot(**kwargS)
            Constructs the seismic_lines attribute.

        get_basemap(**kwargs)
            Constructs the Basemap attribute and provides interactive methods to
            inspect the plotted data.
            
    LIBRARIES
    ---------
        Holoviews: BSD open source Python library designed to simplify the visualization of data.
                    More information available at:
                        http://holoviews.org/

	Numpy: BSD licensed package for scientific computing with Python. More information
               available at:
                   https://numpy.org/
    
        Pandas: BSD 3 licensed open source data analysis and manipulation tool, built on top of
                the Python programming language. More information available at:
                    https://pandas.pydata.org/
                     
        Panel: BSD open source Python library that allows to create custom interactive dashboards 
               by connecting user defined widgets to plots. More information available at:
                    https://panel.holoviz.org/index.html
       
    ON PROGRESS
    -----------
        Include a GIS element into plots.
    """ 
        
    # Holoviews default config
    plot_tools = ['pan','wheel_zoom','reset']
    font_s = {"title": 16, "labels": 14, "xticks": 10, "yticks": 10}
    opts.defaults(opts.Curve(tools = plot_tools, default_tools=[],
                             xformatter = '%.0f', yformatter = '%.0f',
                             fontsize = font_s,
                             height = 400, width = 400, padding = 0.1,
                             toolbar = 'right'),
                  opts.Scatter(tools = plot_tools, default_tools=[],
                               xformatter = '%.0f', yformatter = '%.0f', 
                               fontsize = font_s,
                               height = 400, width = 400, padding = 0.1,
                               toolbar = 'right',
                               framewise = True, show_grid = True),
                  opts.GridSpace(fontsize = font_s,
                                 shared_yaxis = True,
                                 plot_size = (120, 380),
                                 toolbar = "left"),
                  opts.Overlay(xformatter = '%.0f', yformatter = '%.0f',
                               fontsize = font_s,
                               toolbar = "left",
                               show_grid = True),
                  opts.Points(tools=['box_select', 'lasso_select'], default_tools=[], active_tools = ["box_select"],
                              size = 3, width = 500, height = 400, padding = 0.01,
                              fontsize = {'title': 16, 'ylabel': 14, 'xlabel': 14, 'ticks': 10},
                              framewise = True, show_grid = True),
                              toolbar = "left")
    
    def __init__(self, basemap_dataframe, wells_dataframe):
        
        """
        DESCRIPTION
        -----------
            Instantiates BasemapModule's attributes. For more information, please refer to 
            BasemapModule's docstring.
        
        """
        
        self.basemap_dataframe = basemap_dataframe
        self.wells_dataframe = wells_dataframe
        self.iline_step = 1
        self.xline_step = 1
        self.hover_format = [("Utmx", "$x{(0.00)}"), ("Utmy", "$y{(0.00)}")]
        self.hover_attributes = {"show_arrow": True, 
                                 "point_policy": "follow_mouse", 
                                 "anchor": "bottom_right", 
                                 "attachment": "above", 
                                 "line_policy": "none"} 
    
    def polygon_plot(self):

        """
        NAME
        ----
            polygon_plot
        
        DESCRIPTION
        -----------
            Constructs the polygon attribute.
            
            Plots the boundaries of the seismic survey using Holoviews and bokeh as backend.
                   
        ARGUMENTS
        ---------
            BasemapModule.basemap_dataframe : (Pandas)DataFrame
                Matrix compounded by the coordinates and lines of the seismic survey's corners.
        
        RETURN
        ------
            BasemapModule.polygon : Holviews element [Curve] instance attribute
                Plot of the seismic survey polygon.
        
        """

        #Plotting the boundaries of the Seismic Survey. Holoviews Curve element
        BasemapModule.polygon = hv.Curve(self.basemap_dataframe,["utmx","utmy"], label = "Polygon")
        BasemapModule.polygon.opts(line_width=2, color = "black")
        
        return BasemapModule.polygon
 
    def wells_plot(self):

        """
        NAME
        ----
            wells_plot
        
        DESCRIPTION
        -----------
            Constructs the wells attribute

            Plots the wells inside the Seismic Survey's polygon using Holoviews and bokeh as
            backend.

        ARGUMENTS
        ---------
            BasemapModule.wells_dataframe : (Pandas)DataFrame
                Matrix compounded by wells related information.
            
            
        RETURN
        ------
            BasemapModule.wells : Holviews element [Scatter] instance attribute
                Plot of the wells inside the seismic survey.
            
        """
        
        # Declaring the Hover tools (each line will use one)
        wells_hover = HoverTool(tooltips=[("Well", "@name")] + self.hover_format + [("Depth", "@depth{(0)}")])
        
        # Plotting Wells. Holoviews Scatter element
        BasemapModule.wells = hv.Scatter(self.wells_dataframe,["utmx","utmy"],
                                                   ["name","cdp_iline", "cdp_xline", "depth"], 
                                                   label = "Wells")
        BasemapModule.wells.opts(line_width = 1, color = "green", size = 10 ,marker = "^") 
        return (BasemapModule.wells)                
            
    def seismic_line_plot(self, iline_number, xline_number):

        """
        NAME
        ----
            seismic_line_plot
            
        DESCRIPTION
        -----------
            Constructs the seismic_lines attribute.

            Plots seismic lines (given a set of inline and crossline numbers) and the intersection of
            these using Holoviews and bokeh as backend.
            
        ARGUMENTS
        ---------
            iline_number : int
                Number of the chosen inline. The value can be given manually or by Panel's slider 
                widget.

            xline_number : int
                Number of the chosen crossline. The value can be given manually or by Panel's slider 
                widget.

        RETURN
        ------
            BasemapModule.seismic_lines : Holviews element [Overlay] instance attribute
                Plot of the seismic lines and its intersection.
        
        FUNCTIONS
        ---------
            seismic_lines_dataframe(**kwargs)
                Builds a DataFrame for the first line either along inline or crossline direction.

            seismic_intersection(**kwargs)
                Computes the coordinates and tracf of the intersection between two seismic lines.
        
        REFERENCES
        ----------
            bokeh.pydata.org. Change the attributes of the hover tool. Online document:
        https://bokeh.pydata.org/en/latest/docs/reference/models/tools.html#bokeh.models.tools.HoverTool.point_policy
            
        """
        
        def seismic_lines_dataframe(line_direction, perpendicular_direction):

            """
            NAME
            ----
                seismic_lines_dataframe
                
            DESCRIPTION
            -----------
                Builds a DataFrame for the first line either along inline or crossline direction.

                The coordinates represent the lower end of a seismic line; therefore, these shall be used to
                draft seismic lines after the computation of the higher end. If the users want to plot a line 
                along inline direction, the code will compute the coordinates of the traces within the first 
                crossline and vice versa.

            ARGUMENTS
            ---------
            basemap_dataframe : (Pandas)DataFrame
                Matrix compounded by the coordinates and lines of the seismic survey's corners.

            line_direction : str
                Seismic line direction.

            perpendicular_direction : str
                Direction in which the points are going to be calculated. Is perpendicular to line_direction 
                argument.


            RETURN
            ------
                dlines : (Pandas)DataFrame
                    Contains the trace coordinates within the first seismic line.
                    
            """

            # Less stresful to read the code
            df, ld, p_d = self.basemap_dataframe, line_direction, perpendicular_direction


            #Measure the amount of perpendicular lines within line_direction
            dif_lines = abs(int(df[f"{perpendicular_direction}"].min() - df[f"{perpendicular_direction}"].max())) +1

            #Computing the coordinates of each
            utmx = np.linspace(float(df[(df[ld]==df[ld].min()) & (df[p_d]==df[p_d].min())]["utmx"].unique()), 
                                float(df[(df[ld]==df[ld].min()) & (df[p_d]==df[p_d].max())]["utmx"].unique()), 
                                num = dif_lines, endpoint = True)

            utmy =  np.linspace(float(df[(df[ld]==df[ld].min()) & (df[p_d]==df[p_d].min())]["utmy"].unique()), 
                                 float(df[(df[ld]==df[ld].min()) & (df[p_d]==df[p_d].max())]["utmy"].unique()), 
                                 num = dif_lines, endpoint = True)

            #Array of perpendiculars
            array = np.arange(df[f"{p_d}"].min(),
                              df[f"{p_d}"].max() + 1,
                              1)

            # Making dataframes to ease further calculations
            dlines = pd.DataFrame({ld: df[f"{ld}"].min(),
                                   p_d: array,
                                   "utmx": utmx, "utmy": utmy})

            return(dlines)

        
        def seismic_intersection(iline_df, xline_df, iline_number, xline_number):
            
            """
            NAME
            ----
                seismic_intersection
                
            DESCRIPTION
            -----------
                Computes the coordinates and tracf of the intersection between two seismic lines.

                The computation of the intersection uses vector differences.

            ARGUMENTS
            ---------
                iline_df : (Pandas)DataFrame
                    Coordinates of the traces within the first crossline.

                xline_df : (Pandas)DataFrame
                    Coordinates of the traces within the first inline.

                iline_number : int
                    Number of the chosen inline. 

                xline_number : int
                    Number of the chosen crossline. 

            RETURN
            ------
                list
                    List of tracf and coordinates of the intersection.
        
            """
            # Amount of CDP within crosslines
            dif_lines = abs(self.basemap_dataframe["xline"].max() - self.basemap_dataframe["xline"].min()) + 1

            # tracf
            tracf = (iline_number - self.basemap_dataframe["iline"].min()) * dif_lines + (xline_number - self.basemap_dataframe["xline"].min()) + 1

            # vector diferences. Formula utm = b - a + c
            tutmx = float(xline_df[xline_df["xline"] == xline_number]["utmx"]) - xline_df["utmx"].iloc[0] + float(iline_df[iline_df["iline"] == iline_number]["utmx"])
            tutmy = float(xline_df[xline_df["xline"] == xline_number]["utmy"]) - xline_df["utmy"].iloc[0] + float(iline_df[iline_df["iline"] == iline_number]["utmy"])

            return [int(tracf), tutmx, tutmy]
        
        
        df = self.basemap_dataframe
        # Assigning a variable for each dataframe in seismic_lines_dataframe
        ilines, xlines = seismic_lines_dataframe(df.keys()[1], df.keys()[0]), seismic_lines_dataframe(df.keys()[0], df.keys()[1])
        
        # Extracting the intersection coordinates
        intersection = seismic_intersection(ilines, xlines, iline_number, xline_number)
        
        # Computing the second point to plot the seismic lines (By using vector differences)
        ## This can be refactored
        iutmx = float(xlines["utmx"].iloc[-1] - xlines["utmx"].iloc[0] + ilines[ilines["iline"] == iline_number]["utmx"])
        iutmy = float(xlines["utmy"].iloc[-1] - xlines["utmy"].iloc[0] + ilines[ilines["iline"] == iline_number]["utmy"])
        xutmx = float(ilines["utmx"].iloc[-1] - ilines["utmx"].iloc[0] + xlines[xlines["xline"] == xline_number]["utmx"])
        xutmy = float(ilines["utmy"].iloc[-1] - ilines["utmy"].iloc[0] + xlines[xlines["xline"] == xline_number]["utmy"])
        
        # hovers for lines and interception
        iline_hover = HoverTool(tooltips=[("Inline", f"{iline_number}")] + self.hover_format)
        xline_hover = HoverTool(tooltips=[("Crossline", f"{xline_number}")] + self.hover_format)
        int_hover = HoverTool(tooltips=[("Intersection", f"({iline_number}/{xline_number})")] + self.hover_format)
        
        #Updating hover attributes
        for item in [iline_hover, xline_hover, int_hover]:
            item._property_values.update(self.hover_attributes)
            
        # Plotting the Inline. Holoviews Curve element
        iline = hv.Curve([(float(ilines[ilines["iline"] == iline_number]["utmx"]), 
                            float(ilines[ilines["iline"] == iline_number]["utmy"])),
                           (iutmx, iutmy)], label = "I-Line")

        # Plotting the Crossline. Holoviews Curve element
        xline = hv.Curve([(float(xlines[xlines["xline"] == xline_number]["utmx"]), 
                            float(xlines[xlines["xline"] == xline_number]["utmy"])),
                           (xutmx, xutmy)], label = "C-Line")
        
         # Plot the intersection. Holovies Scatter element.
        intersection = hv.Scatter((intersection[1], intersection[2]), label = "Intersection")

        # Adding the hover tool in to the plots
        iline.opts(line_width = 2, color = "red", tools = self.plot_tools + [iline_hover])
        xline.opts(line_width = 2, color = "blue", tools = self.plot_tools + [xline_hover])
        intersection.opts(size = 7, line_color = "black", line_width = 2, color = "yellow", tools = self.plot_tools + [int_hover])

        # Making the overlay of the seismic plot to deploy
        BasemapModule.seismic_lines = iline * xline * intersection
        return BasemapModule.seismic_lines 
 
    def get_basemap(self):
    
        """
        NAME
        ----
            get_basemap
        
        DESCRIPTION
        -----------
            Constructs the basemap attribute and provides interactive methods to inspect the plotted 
            data.
            
            Merges polygon, wells and seismic_lines attributes into one object using Holoviews and 
            bokeh as backend. It also includes Panel's widgets and methods to add elements that ease 
            data management.
        
        ARGUMENTS
        ---------
            BasemapModule.basemap_dataframe : (Pandas)DataFrame
                Matrix compounded by the coordinates and lines of the seismic survey's corners.

            Survey.survey_name : str
                Name of the seismic survey.

        RETURN
        ------
            Panel Layout [Row]
                Container of the following indexed elements:
                    [0] WidgetBox
                    [0] Markdown for Survey.survey_name
                    [1] IntSlider for inline number selection
                    [2] IntSlider for crossline number selection
                    [3] Select for well selection
                    [1] basemap attribute
                     
        FUNCTIONS
        ---------
            basemap_plot(**kwargs)
                Constructs the basemap attribute.

            update_plot(**kwargs)
                Links Panel's selection widgets to the basemap attribute.
        
        """

        df = self.basemap_dataframe
        
        # Widgets
        iline_number = pn.widgets.IntSlider(name = "Inline number",
                                            start = int(df["iline"].min()),
                                            end = int(df["iline"].max()),
                                            step = self.iline_step,
                                            value = int(df["iline"].min()))

        xline_number = pn.widgets.IntSlider(name = "Crossline number",
                                            start = int(df["xline"].min()),
                                            end = int(df["xline"].max()),
                                            step = self.xline_step,
                                            value = int(df["xline"].min()))

        select_well = pn.widgets.Select(name = "Select the well to inspect", 
                                        options = ["None"] + list(self.wells_dataframe["name"]),
                                        value = "None")

        @pn.depends(iline_number.param.value, xline_number.param.value, select_well.param.value)
        def basemap_plot(iline_number, xline_number, select_well):
            
            """
            NAME
            ----
                basemap_plot
            
            DESCRIPTION
            -----------
                Constructs the basemap attribute.

                Merges seismic survey related plots using Holoviews and bokeh as backend.
                
            ARGUMENTS
            ---------
                Arguments are given by Panel's widgets through the panel's depend decorator:

                iline_number : int
                    Number of the chosen inline.

                xline_number : int
                    Number of the chosen crossline.
                    
                select_well : str
                    Automatically gives well's line numbers when selected.

            RETURN
            ------
                basemap : Holviews element [Overlay] instance attribute
                    Combination of the plots: polygon, wells and seismic_lines.
            
            """
            #new attributes
            WiggleModule.inline_number = iline_number
            WiggleModule.crossline_number = xline_number
            
            # First element
            BasemapModule.polygon = BasemapModule.polygon_plot(self)
            # Second element
            BasemapModule.wells = BasemapModule.wells_plot(self)

            # Third element
            BasemapModule.seismic_lines = BasemapModule.seismic_line_plot(self, iline_number, xline_number)
            
            # Final Overlay
            BasemapModule.basemap = BasemapModule.polygon * BasemapModule.wells * BasemapModule.seismic_lines
            BasemapModule.basemap.opts(legend_position = 'top', height = 600, width = 600)

            return(BasemapModule.basemap)

        widgets = pn.WidgetBox(f"## {Survey.survey} Basemap", iline_number, xline_number, select_well)
        
        def update_plot(event):
            
            """
            NAME
            ----
                update_plot
                
            DESCRIPTION
            -----------
                Links Panel's selection widgets to the basemap attribute.

                Modifies the target plot when a well is selected through Panel's selector widget.
                
                
            ARGUMENTS
            ---------
                event : str
                    Panel's selector widget value.
                     
            RETURN
            ------
                basemap : Holviews element [Overlay] instance attribute
                    Combination of the plots: polygon, wells and seismic_lines.
            
            """
            
            if select_well.value != "None":
                iline_number.value = int(self.wells_dataframe["cdp_iline"].loc[str(select_well.value)])
                xline_number.value = int(self.wells_dataframe["cdp_xline"].loc[str(select_well.value)])
                WiggleModule.inline_number = iline_number.value
                WiggleModule.crossline_number = xline_number.value

        select_well.param.watch(update_plot, 'value')
        
        return pn.Row(widgets, basemap_plot).servable()
