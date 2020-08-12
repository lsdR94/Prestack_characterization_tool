# Dependencies
# file management
import os
from shutil import copyfile

# Calc
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from scipy import stats

# SEG-Y file management
import segyio

# Visualization
import holoviews as hv
from holoviews import opts
from bokeh.models import HoverTool
from holoviews import streams
import panel as pn 

# parallel execution of processes
from multiprocessing import Pool

# Visualization platform
hv.extension('bokeh')

# Import a class from other module
from Wiggle import WiggleModule

class AVOModule(WiggleModule):
    
    """
    NAME
    ----
        AVOModule.

    DESCRIPTION
    -----------
        Blueprint for AVO objects.

        Computes and stores AVO attributes (intercept & gradient) and statistic parameters (correlation 
        coefficient, p-value, standard error) in brand new SEG-Y files.

        Plots crossplots of stored attributes and seismic lines while providing interactive tools to
        improve the experience between data and users. These plots are not images but objects
        that can be modified by the user and exported as images. To plot seismic lines, this class 
        iherited WiggleModule methods.
    
    ATTRIBUTES
    ----------
        inlines : list
            List of inlines (numbers) within the survey. Empty by default.

        crosslines : list
            List of crosslines (numbers) within the survey. Empty by default.
        
    METHODS
    -------
        files_from_np(**kwargs)
            Creates brand new SEG-Y files to store attributes.

        attributes_computation(**kwargs)
            Computes and stores AVO attributes and statistic parameters.

        index_generator(**kwargs)
            Creates a generator to dynamically provide attributes_computation's arguments
            to be able to use multiprocessing methods.     

        multiprocess_attributes_computation(**kwargs)
            Employs all machine cores to execute attributes_computation.

        attributes_organization(**kwargs)
            Slices and stores AVO attributes and statistic parameters.

        crossplot(**kwargs)
            Plots crossplots using AVO attributes and statistic parameters as axis/legends
            and a map. 

        avo_visualization(**kwargs)
            Plot crossplots, a map and seismic lines while providing interactive methods to
            inspect the plotted data.

    INHERITANCE
    -----------
        WiggleModule.
        
    LIBRARIES
    ---------
        Holoviews: BSD open source Python library designed to simplify the visualization of data.
                   More information available at:
                        http://holoviews.org/
        
        Multiprocessing: a package that supports spawning processes. Allows to fully leverage
                        multiple processors on a given machine. More information available at: 
                            https://docs.python.org/3.4/library/multiprocessing.html?highlight=process

        Numpy: BSD licensed package for scientific computing with Python. More information
               available at:
                   https://numpy.org/
        
        Pandas: BSD 3 licensed open source data analysis and manipulation tool, built on top of
                the Python programming language. More information available at:
                    https://pandas.pydata.org/
                    
        Panel: BSD open source Python library that allows to create custom interactive dashboards 
               by connecting user defined widgets to plots. More information available at:
                    https://panel.holoviz.org/index.html
                    
        SegyIO: LGPL licensed library for easy interaction with SEG-Y and Seismic Unix formatted 
                seismic data, with binding for Python and Matlab. Made by Kvalsvik Jørgen in 
                2014. Code Available at:
                    https://github.com/equinor/segyio.
            
    """     
    
    
    def __init__(self, inlines, crosslines):
        """
        DESCRIPTION
        -----------
            Instantiates AVOModule's attributes. For more information, please refer to AVOModule's 
            docstring.
            
        """
        self.inlines = inlines
        self.crosslines = crosslines
        
    def files_from_np(self):
        
        """
        NAME
        ----
            files_from_np
            
        DESCRIPTION
        -----------
            Creates brand new SEG-Y files to store attributes.

            Constructs from ndarrays brand new SEG-Y files to store: gradient, intercept, correlation 
            coefficient, p-value and standard error. To ease handling and memory usage optimization,
            new SEG-Y files will only contain attributes as trace data field and the following trace
            headers:
                - SourceGroupScalar: bytes 71-72
                - Cdp X: bytes 181-184
                - Cdp Y: bytes 185-188
                - Inline 3D: bytes 189-192
                - Crossline 3D: bytes 193-196
                
        ARGUMENTS
        ---------
            inlines : list instance attribute 
                List of inlines (numbers) within the survey.

            crosslines : list instance attribute
                List of crosslines (numbers) within the survey. 

            WiggleModule.samples_per_trace : int instance attribute
                Amount of samples in a trace. Extracted and stored in this object by 
                Survey.cube_data_organization function.

            Survey.merge_path : str class attribute
                Path where the merge of the PAS is located.

            Survey.gradient_path : str class attribute
                Path where the computation of the "Gradient" will be stored.

            Survey.intercept_path : str class attribute
                Path where the computation of the "Intercept" will be stored.

            Survey.rvalue_path : str class attribute
                Path where the computation of the "Correlation Coefficient" will be stored.

            Survey.pvalue_path : str class attribute
                Path where the computation of the "P Value" will be stored.

            Survey.stderr_path : str class attribute
                Path where the computation of the "Standard Error" will be stored.

        RETURN
        ------
            str
                A message describing the finalization of the process.
                
        REFERENCES
        ----------
            Kvalsvik, J. (2014). Segyio's documentation. Available at:
                https://segyio.readthedocs.io/en/latest/segyio.html
        """
        
        # 3D array to build the segy file
        triD_array = np.zeros((len(self.inlines), len(self.crosslines), WiggleModule.samples_per_trace))
        
        # Create the segy file from array
        segyio.tools.from_array3D(Survey.gradient_path, triD_array)
        
        # Extracting coordinates and scalar for traces with the same offset. By default offset[0]
        with segyio.open(Survey.merge_path) as segy_file:
            staked_trace_index = np.arange(0, segy_file.tracecount, len(segy_file.offsets)) 
            utmx = segy_file.attributes(segyio.TraceField.CDP_X)[staked_trace_index]
            utmy = segy_file.attributes(segyio.TraceField.CDP_Y)[staked_trace_index]
            scalar = segy_file.attributes(segyio.TraceField.SourceGroupScalar)[staked_trace_index]
            
        # Setting lines for future segyio indexing
        trace_counter = 0
        with segyio.open(Survey.gradient_path, "r+") as g:
            for iline in range(self.inlines[0], self.inlines[-1] + 1):
                for xline in range(self.crosslines[0], self.crosslines[-1] + 1):
                    g.header[trace_counter] = {segyio.su.scalco: scalar[trace_counter],
                                               segyio.su.cdpx: utmx[trace_counter],
                                               segyio.su.cdpy: utmy[trace_counter],
                                               segyio.su.iline: iline,  # 189
                                               segyio.su.xline: xline}  # 193
                    
                    trace_counter += 1

        print(f"Successful construction. Gradient file path: ({Survey.gradient_path})")
                    
        # Making copies of the new segy
        copyfile(Survey.gradient_path, Survey.intercept_path)
        print(f"Successful construction. Intercept file path: ({Survey.intercept_path})")
        copyfile(Survey.gradient_path, Survey.rvalue_path)
        print(f"Successful construction. Correlation coeficient file path: ({Survey.rvalue_path})")
        copyfile(Survey.gradient_path, Survey.pvalue_path)
        print(f"Successful construction. Pvalue file path: ({Survey.pvalue_path})")
        copyfile(Survey.gradient_path, Survey.stderr_path)
        print(f"Successful construction. Standard Deviation file path: ({Survey.stderr_path})")

        return ("Files constructed successfully")
    
    def attributes_computation(index_args):
        
        """
        NAME
        ----
            attributes_computation
            
        DESCRIPTION
        -----------
            Computes and stores AVO attributes and statistic parameters.

            AVO attributes can be computed through Zoeppritz equations (1), linear approximations 
            such as Aki Richards (2), Wiggins (3), Shuey (4) and many more. Due to Shuey's assumptions,
            AVO attributes can be estimated from seismic data applying a linear regression to those 
            traces which shows a linear change of amplitude with the square sin of the angle of 
            incidence. Therefore, Shuey's should be only applicable over a limited range of angles, 
            which is generally around 30*. Thus, Shuey's approximation is used to compute AVO
            attributes just for the purpose of describing seismic amplitude variation according 
            to the following statements:
                - Angle range of the data is lower than 30*.
                - Lack of a dense volume of seismic data (traces per gather).
            
            The linear regression will be made by samples using Scipy's linear regression method that
            allows to compute statistic parameters such as correlation coefficient, p-value and standard
            error along with gradient and intercept attributes. After the computation, results are stored 
            in the trace field of the respective SEG-Y file.
        
        ARGUMENTS
        ---------
            The following arguments can be given manually but it's recommended to use the
            generator of the index_generator function. Arguments: 

                Survey.merge_path : str class attribute
                    Path where the merge of the PAS is located.

                Survey.gradient_path : str class attribute
                    Path where the computation of the "Gradient" will be stored.

                Survey.intercept_path : str class attribute
                    Path where the computation of the "Intercept" will be stored.

                Survey.rvalue_path : str class attribute
                    Path where the computation of the "Correlation Coefficient" will be
                    stored.

                Survey.pvalue_path : str class attribute
                    Path where the computation of the "P Value" will be stored.

                Survey.stderr_path : str class attribute
                    Path where the computation of the "Standard Error" will be stored.

                Survey.angle_list : list class attribute
                    List of the average angle of each PAS. None by default. If the value it's 
                    different from none, a constructor will create the list by using
                    angle_interval and the amount of files in gathers_path.

                inlines : list instance attribute 
                    List of inlines (numbers) within the survey.

                crosslines : list instance attribute
                    List of crosslines (numbers) within the survey. 

                trace_index : int
                    Number of the trace within the SEG-Y file.
                
        RETURN
        ------
            str
                A message describing the finalization of the process.           
        
        """
        
        merge_path, gradient_path, intercept_path, rvalue_path, pvalue_path, stderr_path, angle_list, iline_number, xline_number, trace_index = index_args
        
        # sin(angle) list - Extract from this function
        sins = [np.sin(np.radians(angle)) * np.sin(np.radians(angle)) for angle in angle_list]
        
        # Sin array
#         sina = np.full((len(segy_file.samples), len(segy_file.offsets)), sins)
        
        with segyio.open(merge_path) as segy_file:
    
            # Array to store regression
            gradient = np.zeros([len(segy_file.samples), ], dtype = "float32")
            intercept = np.zeros([len(segy_file.samples), ], dtype = "float32")
            rvalue = np.zeros([len(segy_file.samples), ], dtype = "float32")
            pvalue = np.zeros([len(segy_file.samples), ], dtype = "float32")
            stderr = np.zeros([len(segy_file.samples), ], dtype = "float32")
     
            # From gather to matrix
            for angle in angle_list:

                # First angle shall initialize the matrix from segyio
                if angle == angle_list[0]:
                    amp = segy_file.gather[iline_number, xline_number, angle].reshape(len(segy_file.samples), 1)

                # The rest of the angles, concatenate the amplitudes into the matrix.
                else:
                    amp = np.concatenate((amp, segy_file.gather[iline_number, xline_number, angle].reshape(len(segy_file.samples), 1)),
                                         axis=1)
                
        # Calculation of intercept, gradient and statistical parameters
        # To do: vectorize this function
        for row in range(amp.shape[0]):
            gradient[row], intercept[row], rvalue[row], pvalue[row], stderr[row] = stats.linregress(sins, amp[row])
        
        # Store in segys whatever was computed before
        with segyio.open(gradient_path, "r+") as gradient_segy:
            gradient_segy.trace[trace_index] = gradient

        with segyio.open(intercept_path, "r+") as intercept_segy:
            intercept_segy.trace[trace_index] = intercept

        with segyio.open(rvalue_path, "r+") as rvalue_segy:
            rvalue_segy.trace[trace_index] = rvalue

        with segyio.open(pvalue_path, "r+") as pvalue_segy:
            pvalue_segy.trace[trace_index] = pvalue

        with segyio.open(stderr_path, "r+") as stderr_segy:
                stderr_segy.trace[trace_index] = stderr
        
        print(f"AVO attributes for trace number {trace_index}, [{iline_number},{xline_number}], has been stored successfully")
        return("Seismic attributes computation ended successfully")
      
    def index_generator(self):
        
        """
        NAME
        ----
            index_generator
            
        DESCRIPTION
        -----------
            Creates a generator to dynamically provide attributes_computation's arguments
            to be able to use multiprocessing methods.    
            
        ARGUMENTS
        ---------
            Survey.merge_path : str class attribute
                Path where the merge of the PAS is located.

            Survey.gradient_path : str class attribute
                Path where the computation of the "Gradient" will be stored.

            Survey.intercept_path : str class attribute
                Path where the computation of the "Intercept" will be stored.

            Survey.rvalue_path : str class attribute
                Path where the computation of the "Correlation Coefficient" will be stored.

            Survey.pvalue_path : str class attribute
                Path where the computation of the "P Value" will be stored.

            Survey.stderr_path : str class attribute
                Path where the computation of the "Standard Error" will be stored.

            Survey.angle_list : list class attribute
                List of the average angle of each PAS. None by default. If the value it's different
                from none, a constructor will create the list by using angle_interval and the
                amount of files in gathers_path.

            inlines : list instance attribute 
                List of inlines (numbers) within the survey.

            crosslines : list instance attribute
                List of crosslines (numbers) within the survey. 

            trace_index : int
                Number of the trace within the SEG-Y file.
                
        YIELDS
        ------
            list
                List of arguments for attributes_computation method.
        """
        
        trace_index = 0
        for iline_number in self.inlines:
            for xline_number in self.crosslines:
                    yield [Survey.merge_path, Survey.gradient_path, Survey.intercept_path, 
                           Survey.rvalue_path, Survey.pvalue_path, Survey.stderr_path, 
                           Survey.angle_list, iline_number, xline_number, trace_index]
                    trace_index += 1   
    
    def multiprocess_attributes_computation(self):
        
        """
        NAME
        ----
            multiprocess_attributes_computation.
        
        DESCRIPTION
        -----------
            Employs all machine cores to execute attributes_computation.

            Acts as a process manager. Executes attributes_computation method in
            parallel using machine cores.
        
        RETURN
        ------
            str
                A message describing the finalization of the process.   

        
        """
        index_args = AVOModule.index_generator(self)

        if __name__ == "__main__":
            p = Pool(maxtasksperchild = 1)
            p.map(AVOModule.attributes_computation, index_args, chunksize=1)
                
        return(f"Seismic attributes computation ended successfully")
        
    def attributes_organization(self, inline_range, crossline_range, time_window):
        
        """
        NAME
        ----
            attributes_organization.
            
        DESCRIPTION
        -----------
            Slices and stores in a DataFrame AVO attributes and statistic parameters.
            
        ARGUMENTS
        ---------
            Survey.gradient_path : str class attribute
                Path where the computation of the "Gradient" will be stored.

            Survey.intercept_path : str class attribute
                Path where the computation of the "Intercept" will be stored.

            Survey.rvalue_path : str class attribute
                Path where the computation of the "Correlation Coefficient" will be stored.

            Survey.pvalue_path : str class attribute
                Path where the computation of the "P Value" will be stored.

            Survey.stderr_path : str class attribute
                Path where the computation of the "Standard Error" will be stored.

            inline_range : tuple
                Range of inlines samples to be plotted. Can be given manually or by Panel's
                range slider widget.

            crossline_range : tuple
                Range of crosslines samples to be plotted. Can be given manually or by Panel's
                range slider widget. 

            time_window : tuple
                Time slice of interest. Can be given manually or by Panel's range slider widget.
            
        RETURN
        ------
            df : (Pandas)DataFrame
                Matrix compounded by AVO attributes and statistic parameters. The information is
                structured by the following columns:
                    - inline : number of the chosen inline.
                    - crossline : number of the chosen crossline.
                    - utmx: horizontal coordinates Universal Transversal Mercator coordinate system.
                    - utmy: vertical coordinates Universal Transversal Mercator coordinate system.
                    - time_slice : plot's time axis. Concur with trace axis.
                    - gradient : gradient AVO attribute.
                    - intercept : intercept AVO attribute.
                    - rvalue : correlation coefficient statistic parameter.
                    - pvalue : p-value statistic parameter.
                    - serror : standard error statistic parameter.
            
        """
        
        with segyio.open(Survey.gradient_path, "r") as g, segyio.open(Survey.intercept_path, "r") as f:
            with segyio.open(Survey.rvalue_path, "r") as r, segyio.open(Survey.pvalue_path, "r") as p:
                with segyio.open(Survey.stderr_path, "r") as s:
                
                    # Making an array of inlines and crosslines following the trace sorting
                    ilines = g.attributes(segyio.TraceField.INLINE_3D)[:] 
                    xlines = g.attributes(segyio.TraceField.CROSSLINE_3D)[:]

                    # Extracting the index of those traces within the line range
                    ilines = np.array(np.where((ilines >= inline_range[0]) & (ilines <= inline_range[-1])))
                    xlines = np.array(np.where((xlines >= crossline_range[0]) & (xlines <= crossline_range[-1])))

                    # Intersection of traces between both ranges
                    trace_index = np.intersect1d(ilines, xlines)
                    
                    # index of the time window
                    time_slice = np.where((g.samples>=time_window[0]) & (g.samples<=time_window[-1]))
                    
                    # dataframe for seismic and statistic data
                    df = pd.DataFrame([])
                    for trace in trace_index:
                        df = pd.concat([df, pd.DataFrame({"inline":g.header[trace][189],
                                                          "crossline": g.header[trace][193],
                                                          "utmx":g.header[trace][181], 
                                                          "utmy":g.header[trace][185],
                                                          "time_slice":g.samples[time_slice],
                                                          "gradient":g.trace[trace][time_slice],
                                                          "intercept":f.trace[trace][time_slice],
                                                          "rvalue":r.trace[trace][time_slice],
                                                          "pvalue":p.trace[trace][time_slice], 
                                                          "serror":s.trace[trace][time_slice],
                                                          "scalar" : g.header[trace][71]})],
                                               ignore_index = True, axis="rows")
               
            # Adapting the coordinates to the segy's scalar value
            df['utmx'] = np.where(df['scalar'] == 0, df['utmx'],
                                    np.where(df['scalar'] > 0, df['utmx'] * df['scalar'], 
                                                                df['utmx'] / abs(df['scalar'])))
            df['utmy'] = np.where(df['scalar'] == 0, df['utmy'],
                                    np.where(df['scalar'] > 0, df['utmy'] * df['scalar'], 
                                                                df['utmy'] / abs(df['scalar'])))

            # Dropping the scalar column
            df = df.drop(["scalar"], axis = 1)                        
       
            return df
        
    def crossplot(self, dataframe, x_column, y_column, scale_select_value):
        
        """
        NAME
        ----
            crossplot.
            
        DESCRIPTION
        -----------
            Plots crossplots using AVO attributes and statistic parameters as axis/legends and a map. 

            The map will show whatever gets selected in the crossplot using the available tools for
            selection. Both plots are made by using Holoviews and bokeh as backend.
            
        ARGUMENTS
        ---------
            dataframe : (Pandas)DataFrame
                Matrix compounded by AVO attributes and statistic parameters.

            x_column : str
                X axis name of the crossplot. The name must coincide with one of the DataFrames's 
                columns. Can be given manually or by Panel's selector. Map's x axis is utmx by 
                default.

            y_column : str
                Y axis name of the crossplot. The name must coincide with one of the DataFrames's 
                columns. Can be given manually or by Panel's selector. Map's y axis is utmy by 
                default.

            scale_select_value : str
                Color bar of the crossplot. The name must coincide with one of the DataFrames's
                columns. Can be given manually or by Panel's selector.
            
        RETURN
        ------
            layout : Holviews element [NdLayout]
                Crossplot and map of the points selected in the crossplot.
        
        FUNCTIONS
        ---------
            selected_info(**kwargs)
                Plots a location map based on the selected points in the crossplot. Empty by
                default.

        """
        
        # Scale for the crossplot
        levels = np.linspace(dataframe[scale_select_value].min(),
                             dataframe[scale_select_value].max(), 100,
                             endpoint = True).tolist()

        # Preparing the data's plot
        data = hv.Points(dataframe, [x_column, y_column], vdims = scale_select_value)
        data.opts(title = f"{x_column} vs {y_column}",
                  color = scale_select_value, color_levels = levels, cmap = "fire", colorbar = True)

        # Axis of plot
        x_axis = hv.Curve([(0,dataframe[y_column].min()), (0,dataframe[y_column].max())])
        x_axis.opts(color = "black", line_width = 0.5)
        y_axis = hv.Curve([(dataframe[x_column].min(), 0), (dataframe[x_column].max(), 0)])
        y_axis.opts(color = "black", line_width = 0.5)

        # Declare points as source of selection stream
        selection = streams.Selection1D(source = data)

        # Write function that uses the selection indices to slice points and compute stats
        def selected_info(index):
            
            """
            NAME
            ----
                selected_info.
                
            DESCRIPTION
            -----------
                Plots a location map based on the selected samples in the crossplot. Empty by default.
                
            ARGUMENTS
            ---------
                hc : (Pandas)DataFrame
                    DataFrame made by converting selected samples of the crossplot.
            
            RETURN
            ------
                plot : Holviews element [Scatter]
                        Map of the selected samples in the crossplot.
                
            """
            
            hc = dataframe.iloc[index]
            plot = hv.Scatter(hc, ["utmx","utmy"])
            plot.opts(color = "red", size = 5, 
                      fontsize = {"title": 16, "labels": 14, "xticks": 7, "yticks": 7},
                      title = f"Position of the selected traces",
                      tools = [HoverTool(tooltips=[('Trace [I/X]', f"@inline/@crossline"),
                                                   ('Time [ms]', f"@time_slice")])])

            return plot

        dynamic_map = hv.DynamicMap(selected_info, streams = [selection])

        # Combine points and DynamicMap
        layout = ((data * x_axis * y_axis) + dynamic_map).opts(merge_tools=False)

        return (layout)
           
    def avo_visualization(self):
        
        """
        NAME
        ----
            avo_visualization.
            
        DESCRIPTION
        -----------
            Creates a Column layout with the result of the crossplot function and a seismic line while 
            providing interactive methods to inspect the plotted data.

            Displays the mentioned plots along Panel's widgets to ease data manipulation.
            
        ARGUMENTS
        ---------
            inlines : list instance attribute 
                List of inlines (numbers) within the survey.

            crosslines : list instance attribute
                List of crosslines (numbers) within the survey. 

            WiggleModule.samples_per_trace : int instance attribute
                Amount of samples in a trace. Extracted and stored in this object by
                Survey.cube_data_organization function.
                
        RETURN
        ------
            Panel Layout [Column]
                Container of the following indexed elements:
                    [0] Row
                        [0] WidgetBox
                            [0] Markdown for element identification.
                            [1] StaticText for element identification.
                            [2] IntRangeSlider for selection of a range of inlines.
                            [3] IntRangeSlider for selection of a range of crosslines.
                            [4] IntRangeSlider for selection of a time slice.
                            [5] Select for selection of crossplot's x axis.
                            [6] Select for selection of crossplot's y axis.
                            [7] Select for selection of crossplot's color bar.
                        [1] Crossplot and map.
                    [1] Row
                        [0] WidgetBox
                            [0] Markdown for element identification.
                            [1] Checkbox to enable line display.
                            [2] RadioButtonGroup for the selection of a seismic direction.
                            [3] TextInput for input of inline number.
                            [4] TextInput for input of crossline number.
                        [1] Lines.
                        
        FUNCTIONS
        ---------
            avo_stuff(**kwargs)
                Plots crossplot and a map of crossplot selected data.

            line_stuff(**kwargs)
                Plots a chosen seismic line. Inherited from WiggleModule class.

            bg_widgets(**kwargs)
                Links widget's color to seismic direction buttons in order to ease the
                identification of widgets.
        
        """
        
        df = pd.DataFrame(columns = ["inline","crossline","time_slice",
                                     "gradient","intercept","rvalue","pvalue","serror"])
        
        # Window Selection
        inst = pn.widgets.StaticText(name = "Window to work with", value = "")

        iline_range = pn.widgets.IntRangeSlider(name = 'Inline range',
                                                start = int(self.inlines.min()), 
                                                end = int(self.inlines.max()), 
                                                value = (int(self.inlines.min()), int(self.inlines.min())+1), 
                                                step = 1)

        xline_range = pn.widgets.IntRangeSlider(name = 'Crossline range',
                                                start = int(self.crosslines.min()), 
                                                end = int(self.crosslines.max()), 
                                                value = (int(self.crosslines.min()), int(self.crosslines.min())+1), 
                                                step = 1)

        # Time slice selection
        time_slice = pn.widgets.IntRangeSlider(name = 'Time slice [ms]',
                                                 start = WiggleModule.trace_length[0], 
                                                 end = WiggleModule.trace_length[-1], 
                                                 value = (WiggleModule.trace_length[-1]//2, 
                                                          WiggleModule.trace_length[-1]//2 + WiggleModule.trace_length[-1]//10), 
                                                 step = 100)

        # Crossplot parameters
        axis = pn.widgets.StaticText(name = "Crossplots", value = "")
        x_axis = pn.widgets.Select(name = "X axis", 
                                  options = list(df.columns),
                                  value = "intercept")
        y_axis = pn.widgets.Select(name = "Y axis", 
                                  options = list(df.columns),
                                  value = "gradient")

        # Scale selection
        select_scale = pn.widgets.Select(name = "Color scale", 
                                        options = list(df.columns),
                                        value = "serror")

        # Buttons
        seismic_buttons = pn.widgets.RadioButtonGroup(name='Radio Button Group', 
                                                  options=['Inline', 'Crossline'], button_type='success')

        # Line entry
        iline_input = pn.widgets.TextInput(name = 'Inline number',
                                           value= str(iline_range.value[0]),
                                           background = "#47a447")
        xline_input = pn.widgets.TextInput(name = 'Crossline number',
                                           value= str(xline_range.value[0]),
                                           background = "WhiteSmoke")

        # display line
        checkbox = pn.widgets.Checkbox(name = "Check to display a line")


        # Decorator to mess up with the API
        @pn.depends(iline_range.param.value, xline_range.param.value,
                    time_slice.param.value,
                    x_axis.param.value, y_axis.param.value,
                    select_scale.param.value)
        def avo_stuff(iline_range, xline_range, time_slice,
                      x_axis, y_axis, select_scale):
            
            """
            NAME
            ----
                avo_stuff.
                
            DESCRIPTION
            -----------
                Plots crossplot and map of crossplot selected data.
                
            ARGUMENTS
            ---------
                Arguments are given by Panel's widgets through the panel's depends decorator:
                
                    inline_range : tuple
                        Range of inlines samples to be plotted.

                    crossline_range : tuple
                        Range of crosslines samples to be plotted.

                    time_window : tuple
                        Time slice of interest. 
                        
                    x_column : str
                        X axis name of the crossplot. The name must coincide with one of the DataFrames's 
                        columns. 
                        
                    y_column : 
                        Y axis name of the crossplot. The name must coincide with one of the DataFrames's 
                        columns. 
                        
                    scale_select_value : str
                        Color bar of the crossplot. The name must coincide with one of the DataFrames's
                        columns.

            RETURN
            ------
                crossplots : Holviews element [NdLayout]
                    A plot compounded by a crossplot and a map of crossplot selected data.
            
            """
            
            attribute_dataframe = AVOModule.attributes_organization(self, iline_range, xline_range, time_slice)
#             # Crossplot stuff
            crossplots = AVOModule.crossplot(self, attribute_dataframe, x_axis, y_axis, select_scale)

            return(crossplots).opts(merge_tools=False)
        
        @pn.depends(time_slice.param.value,
                    seismic_buttons.param.value,
                    iline_input.param.value, xline_input.param.value,
                    checkbox.param.value)
        def line_stuff(time_slice, seismic_buttons, iline_input, xline_input, checkbox):
            
            """
            NAME
            ----
                line_stuff.
                
            DESCRIPTION
            -----------
                Plots a chosen seismic line. Inherited from WiggleModule class.

                The detected anomalies in the crossplot shall be compared with the amplitude display of 
                a gather.
                
            ARGUMENTS
            ---------
                seismic_buttons : str
                     Seismic direction to base the amplitude plotting.

                wiggle_buttons : str
                     Hardcoded to "Colored wiggle".

                seismic_iline : int
                     Inline number selection.

                traces_iline : tuple
                     Range of crosslines to be intersected with seismic_iline.

                seismic_xline : int
                     Crossline number selection.

                traces_xline : tuple
                    Range of inlines to be intersected with seismic_iline.

                time_slice : list
                     Time slice of interest. 

                Survey.merge_path : str
                    Path where the merge of the PAS is located.
            
            RETURN
            ------
                GridSpace : Holviews element [GridSpace]
                    A grid compounded by angle gathers.
            
            """
            
            if checkbox:
                with segyio.open(Survey.merge_path) as segy:
                    self.interpolation = False
                    gather_dict = {}
                    # Storing scaling fac
                    self.scaling_factor = WiggleModule.scaling_factor(self, segyio.tools.collect(segy.trace[:]))

                    # Storing time array
                    WiggleModule.time(self, int(segy.attributes(segyio.TraceField.TRACE_SAMPLE_INTERVAL)[0]/1000))

                    # Line visualization
                    if seismic_buttons == "Inline":
                        trace_counter = self.crosslines[0]
                        for gather in segy.gather[int(iline_input),:, :]:
                            gather_dict[f"{int(iline_input)}/{trace_counter}"] = WiggleModule.wiggle_plot(self, 
                                                                                                          gather, time_slice, 
                                                                                                          "Colored wiggle")
                            trace_counter += 1

                    else: 
                        trace_counter = self.inlines[0]
                        for gather in segy.gather[:, int(xline_input), :]:
                            gather_dict[f"C{trace_counter}/{int(xline_input)}"] = WiggleModule.wiggle_plot(self, 
                                                                                                           gather, time_slice, 
                                                                                                           "Colored wiggle")
                            trace_counter += 1
                
                grid = hv.GridSpace(gather_dict, kdims=['Trace'])
                grid.opts(fontsize = {"title": 16, "labels": 14, "xticks": 8, "yticks": 8},
                          plot_size = (60, 240))
                
                return grid

        # Widget construction    
        avo_widgets = pn.WidgetBox(f"## AVO visualization", 
                                      inst, iline_range, xline_range, time_slice, x_axis, y_axis, select_scale,
                                  width = 250)
    
        line_widgets = pn.WidgetBox(f"## Line visualization", 
                                       checkbox, seismic_buttons, iline_input, xline_input,
                                   width = 250)
        
        def bg_widgets(event):
            
            """
            NAME
            ----
                bg_widgets
            
            DESCRIPTION
            -----------
                Links widget's color to seismic direction buttons in order to
                ease the identification of widgets.
                
            ARGUMENTS
            ---------
                event : str
                    Seismic radio buttons value.
                     
            RETURN
            ------
                [1] Row
                    [0] WidgetBox
                        [3] TextInput color
                        [4] TextInput color.
            """
            
            if seismic_buttons.value == "Crossline":
                iline_input.background = "WhiteSmoke"
                xline_input.background = "#47a447"
            else:
                iline_input.background = "#47a447"
                xline_input.background = "WhiteSmoke"
                  
        seismic_buttons.param.watch(bg_widgets, 'value')
        
        avo = pn.Row(avo_widgets, avo_stuff).servable()
        line = pn.Row(line_widgets, line_stuff).servable()
        
        return pn.Column(avo, line)
