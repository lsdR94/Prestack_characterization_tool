# Dependencies
# file management
import os
from shutil import copyfile

# Calc
import numpy as np
import pandas as pd

# SEG-Y file management
import segyio

# Visualization
import holoviews as hv
from holoviews import opts
from bokeh.models import HoverTool
from holoviews import streams
import panel as pn 

# Visualization platform
hv.extension('bokeh')

# Code

class WiggleModule:
    
    """
    NAME
    ----
        WiggleModule.

    DESCRIPTION
    -----------
        Blueprint for Wiggle objects.

        Reconstructs and plots angle gathers while providing interactive tools to improve the 
        experience between data and users. These plots are not images but objects that can be 
        modified by the user and exported as images.
    
    ATTRIBUTES
    ----------
        inlines : list
            List of inlines (numbers) within the survey. Empty by default.

        crosslines : list
            List of crosslines (numbers) within the survey. Empty by default.

        sample_interval : int instance attribute
            Sample interval in ms. Extracted and stored in this object by 
            Survey.cube_data_organization function.

        samples_per_trace : int instance attribute
            Amount of samples in a trace. Extracted and stored in this object by
            Survey.cube_data_organization function.

        trace_length : list instance attribute
            Range of trace's time axis. Extracted and stored in this object by
            Survey.cube_data_organization function.

        interpolation : bool
            Whether the amplitudes will be interpolated to improve wiggle display. False by
            default.

        time_axis : (Numpy) ndarray
            Time axis for angle gather plot. Units in ms.

        interpolation_time : (Numpy) ndarray
            Interpolated time axis if interpolation attribute equal True.

        scaling_factor : int
            highest amplitude value to scale angle gather plots. Does not affect amplitude
            content of the traces.


    METHODS
    -------
        scaling_factor(**kwargs)
            Computes the scaling factor attribute.

        time(**kwargs)
            Constructs time_axis attribute.

        amp_dataframe(**kwargs)
            Builds a DataFrame compounded by the amplitudes of the single gather that will be plotted.

        wiggle_plot(**kwargs)
            Plots the amplitudes of a single angle gather.

        get_wiggle(**kwargs)
            Plots the amplitude content of angle gathers and provides interactive methods to inspect 
            the plotted data.
                     
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
                    
        SegyIO: LGPL licensed library for easy interaction with SEG-Y and Seismic Unix formatted 
                seismic data, with binding for Python and Matlab. Made by Kvalsvik Jørgen in 
                2014. Code Available at:
                    https://github.com/equinor/segyio.
                             
    """
    def __init__(self, inlines, crosslines):
        
        """
        DESCRIPTION
        -----------
            Instantiates WiggleModule's attributes. For more information, please refer to
            WiggleModule's docstring.

        """
        
        self.inlines = inlines
        self.crosslines = crosslines
        self.interpolation = False
        
    def scaling_factor(self, amp_array):
        
        """
        NAME
        ----
            scaling_factor.
        
        DESCRIPTION
        -----------
            Computes the scaling factor attribute.

            The seismic data is scanned in order to extract the highest absolute value of amplitude.
            
        
        ARGUMENTS
        ---------
            amp_array : (Numpy)ndarray
                Array of cube's amplitudes.
        
        RETURN
        ------
            scaling_factor : int instance attribute
                highest amplitude value to scale angle gather plots. Does not affect amplitude
                content of the traces.
                
        """
        
        factor = abs(amp_array)
        WiggleModule.scaling_fac = factor.max()

        return self.scaling_fac

    def time(self, time_interval):
        
        """
        NAME
        ----
            time
        
        DESCRIPTION
        -----------
            Constructs time_axis attribute.

            sample_interval and samples_per_trace attributes are needed to make the time array.
            If the time_interval is different from cube's sample interval (sample_interval attribute),             
            the function will resample the first array mentioned according to the sample given by 
            time_interval.

        ARGUMENTS
        ---------
            time_interval : int
                Chosen time interval. The value can be given manually or by Panel's slider widget.

            WiggleModule.sample_interval : int instance attribute
                Sample interval in ms. Extracted and stored in this object by
                Survey.cube_data_organization function.

            WiggleModule.samples_per_trace : int instance attribute
                Amount of samples in a trace. Extracted and stored in this object by 
                Survey.cube_data_organization function.

        RETURN
        ------
            interpolation : bool instance attribute 
                False if time_interval equal to WiggleModule.sample_interval, else True.

            time_axis : (Numpy) ndarray instance attribute
                Time axis for angle gather plot. Units in ms.

            interpolation_time : (Numpy) ndarray instance attribute
                Interpolated time_axis if interpolation attribute equal True.
                
        """
        
        #f.samples returns all the array
        
        WiggleModule.time_axis = np.arange(0, self.sample_interval * self.samples_per_trace, self.sample_interval)

        if time_interval != self.sample_interval:
            self.interpolation = True
            WiggleModule.interpolation_time = np.arange(self.time_axis[0], self.time_axis[-1] + time_interval, time_interval)
            return (self.interpolation_time)
        return (self.time_axis)
        
    def amp_dataframe(self, gather, time_slice, wiggle_buttons):
        
        """
        NAME
        ----
            amp_dataframe.
        
        DESCRIPTION
        -----------
            Builds a DataFrame compounded by the amplitudes of the single gather that will be plotted.
    
            Amplitudes in the DataFrame will vary according to the following parameters:
                - time_slice will set the time window for the DataFrame.
                - If interpolation is False, DataFrame's amplitudes will be the same as the cube.
                - If interpolation is True, the amplitude content will be resampled by using
                  Scipy's cubic spline interpolation method and the resampled time axis given 
                  by time function.           
                - If interpolation is True and wiggle_button is not "Wavelet", the DataFrame will
                  contain positive and negative amplitudes separately.

        ARGUMENTS
        ---------
            gather : (Numpy)ndarray
                Amplitude array given by Segyio's gather method. Can be given manually.

            time_slice : list
                Time slice of interest. Can be given manually or by Panel's range slider widget.

            wiggle_buttons : str
                Desired amplitude's plot type. Can be given manually or by Panel's radio button
                widget. "Wavelet" will plot amplitudes using only a sine curve, "Black wiggle"
                will fill with black the area between the sin curve and time_axis and "Colored
                wiggle", will fill with blue/red the positive/negative area between the sin curve
                and time_axis.
            
            WiggleMethod.interpolation : bool
                Whether the amplitudes will be interpolated to improve wiggle display or not.
                False by default.
            
        RETURN
        ------     
            amp_dfe : (Pandas)DataFrame
                Amplitude matrix of the desire gather. The information is structured by the
                following columns:
                    - time_axis: plot's time axis. Concur with trace axis.
                    - amplitude_{angle}: amplitude for a given trace of the gather.
                    ** optional **
                    - positive_amplitude_{angle}: positive amplitude values for a given trace of the 
                                                  gather.
                    - negative_amplitude_{angle}: negative amplitude values for a given trace of the 
                                                  gather.
                                                  
        """
        amp_df = pd.DataFrame([])
        s_factor = 0

        for trace in range(gather.shape[0]):
            if self.interpolation == True:
                f_spline = interp1d(self.time_axis, gather[trace], kind="cubic")
                amp = f_spline(self.interpolation_time)
                # Extract this from the cicle
                amp_df["time_axis"] = self.interpolation_time
            else:
                amp = gather[trace]
                # Extract this from the cicle
                amp_df["time_axis"] = self.time_axis

            # Making two more series: Negative amplitude and positive amplitude
            amp_df[f"amplitude_{Survey.angle_list[trace]}"] = amp
            # Scalating amplitudes for plot
            amp_df[f"s_amplitude_{Survey.angle_list[trace]}"] = amp_df[f"amplitude_{Survey.angle_list[trace]}"] + s_factor

            if wiggle_buttons != "Wavelet":  #Might give delay to the plot
            
                amp_df[f"positive_amplitude_{Survey.angle_list[trace]}"] = amp_df[f"amplitude_{Survey.angle_list[trace]}"]
                amp_df[f"negative_amplitude_{Survey.angle_list[trace]}"] = amp_df[f"amplitude_{Survey.angle_list[trace]}"]

                # Separating for polarity
                amp_df.loc[amp_df[f"positive_amplitude_{Survey.angle_list[trace]}"]
                           < 0, f"positive_amplitude_{Survey.angle_list[trace]}"] = 0
                amp_df.loc[amp_df[f"negative_amplitude_{Survey.angle_list[trace]}"]
                           > 0, f"negative_amplitude_{Survey.angle_list[trace]}"] = 0

                # Scalating amps for polarity
                amp_df[f"s_negative_amplitude_{Survey.angle_list[trace]}"] = amp_df[
                    f"negative_amplitude_{Survey.angle_list[trace]}"] + s_factor
                amp_df[f"s_positive_amplitude_{Survey.angle_list[trace]}"] = amp_df[
                    f"positive_amplitude_{Survey.angle_list[trace]}"] + s_factor

            s_factor += self.scaling_fac

        return (amp_df[(amp_df.time_axis >= time_slice[0]) & (amp_df.time_axis <= time_slice[1])])

    def wiggle_plot(self, gather, time_slice, wiggle_buttons):
        
        """
        NAME
        ----
           wiggle_plot.
        
        DESCRIPTION
        -----------
            Plots the amplitudes of a single angle gather.

            The plot will vary according to the following parameters:
                - time_slice will set the time window for the plot.
                - wiggle_button value will modify the way the amplitudes are displayed. More
                  details in wiggle_buttons argument.

        ARGUMENTS
        ---------
            gather : (Numpy)ndarray
                Amplitude array given by Segyio's gather method. Can be given manually.
            
            time_slice : list
                Time slice of interest. Can be given manually or by Panel's range slider widget.
            
            wiggle_buttons : str
                Desired amplitude's plot type. Can be given manually or by Panel's radio button
                widget. "Wavelet" will plot amplitudes using only a sine curve, "Black wiggle"
                will fill with black the area between the sin curve and time_axis and "Colored
                wiggle", will fill with blue/red the positive/negative area between the sin curve
                and time_axis.
            
            WiggleMethod.interpolation : bool
                Whether the amplitudes will be interpolated to improve wiggle display or not. 
                False by default.
            
        RETURN
        ------   
            wiggle_display : Holviews element [Overlay]
                Compilation of traces within the angle gather.
                                                  
        """
        amp_df = WiggleModule.amp_dataframe(self, gather, time_slice, wiggle_buttons)

        # Initializing the plot
        wiggle_display = hv.Curve((0, 0))

        # Computing scale factor for the X axis
        WiggleModule.plot_xticks = [(angle_position * self.scaling_fac,
                            Survey.angle_list[angle_position]) for angle_position in range(len(Survey.angle_list))]

        # making the data to plot according a scaled value
        for trace in range(gather.shape[0]):

            # Hover designation
            hover_w = HoverTool(tooltips=[('Time', '@time_axis'),
                                          ('Amplitude', f"@amplitude_{Survey.angle_list[trace]}"),
                                          ("Angle", f"{Survey.angle_list[trace]}")])

            # Plotting the wiggle
            wiggle = hv.Curve(amp_df, ["time_axis", f"s_amplitude_{Survey.angle_list[trace]}"],
                                      [f"amplitude_{Survey.angle_list[trace]}"], label="W")
            wiggle.opts(color="black", line_width=2, tools=[hover_w])
            
            if wiggle_buttons != "Wavelet":
            
                if wiggle_buttons == "Black wiggle":
                    WiggleModule.positive_amp, WiggleModule.negative_amp = "black", "black"
                else: 
                    WiggleModule.positive_amp, WiggleModule.negative_amp = "blue", "red"

                # Making the area plot more comfortable
                x = amp_df["time_axis"]
                y = self.scaling_fac * trace
                y2 = amp_df[f"s_negative_amplitude_{Survey.angle_list[trace]}"]
                y3 = amp_df[f"s_positive_amplitude_{Survey.angle_list[trace]}"]

                # Fill in between: Holoviews Element
                negative = hv.Area((x, y, y2), vdims=['y', 'y2'], label="-").opts(color=self.negative_amp, line_width=0)
                positive = hv.Area((x, y, y3), vdims=['y', 'y3'], label="+").opts(color=self.positive_amp, line_width=0)

                # Overlying the colored areas +  the zero phase wavelet
                wiggle_display *= wiggle * negative * positive
            
            else:
                wiggle_display *= wiggle
                
            # Adding final customizations
            wiggle_display.opts(xaxis="top", invert_axes = True, invert_yaxis = True,                                
                                xlabel = "Time [ms]", ylabel = " ",
                                xticks = self.plot_xticks, xlim = (time_slice[0], time_slice[-1]))

        return(wiggle_display)

    def get_wiggle(self):
        
        """
        NAME
        ----
            wiggle_plot.
        
        DESCRIPTION
        -----------
            Plots the amplitude content of angle gathers and provides interactive methods to inspect 
            the plotted data.

            Stacks gathers into a grid using Holoviews and bokeh as backend. It also includes Panel's
            widgets and methods to add elements that ease data management.
     
        ARGUMENTS
        ---------
            WiggleModule.inlines : list **instance attribute**
                List of inlines (numbers) within the survey. Empty by default.

            WiggleModule.crosslines : list instance attribute
                List of crosslines (numbers) within the survey. Empty by default.  

            WiggleModule.sample_interval : int instance attribute
                Sample interval in ms. Extracted and stored in this object by
                Survey.cube_data_organization function.

            WiggleModule.trace_length : list instance attribute
                Range of trace's time axis. Extracted and stored in this object by
                Survey.cube_data_organization function.
                
        RETURN
        ------
            Panel Layout [Row]
                Container of the following indexed elements:
                [0] WidgetBox
                    [0] Markdown for element identification.
                    [1] StaticText for element identification.
                    [2] StaticText for element identification.
                    [3] RadioButtonGroup for the selection of a seismic direction.
                    [4] IntSlider for inline number selection.
                    [5] IntRangeSlider for the selection of a range of crosslines.
                    [6] IntSlider for crossline number selection.
                    [7] IntRangeSlider for the selection of a range of inlines.
                    [8] StaticText for element identification.
                    [9] IntRangeSlider for the selection of a time slice.
                    [10] IntSlider for sample interval selection.
                    [11] RadioButtonGroup for the selection of the desired wiggle display.
                [1] Angle gather display.
                     
        FUNCTIONS
        ---------
            gather_plot(**kwargs)
                Constructs a grid of angle gathers.

            bg_widgets(**kwargs)
                Links widget's color to seismic direction buttons in order to ease the
                identification of widgets.
            
        """

        # Display string
        line_input = pn.widgets.StaticText(name='Line input',
                                           value=f"Default lines: Basemap ({self.inline_number}/{self.crossline_number})")

        trace_input = pn.widgets.StaticText(name='Trace input', value="")

        gather_direction = pn.widgets.StaticText(value=" Plot direction")

        # Buttons
        seismic_buttons = pn.widgets.RadioButtonGroup(name='Radio Button Group',
                                                      options=['Inline', 'Crossline'],
                                                      button_type='success')
        
        wiggle_buttons = pn.widgets.RadioButtonGroup(name='Radio Button Group',
                                                     options=['Wavelet', 'Black wiggle', 'Colored wiggle'], button_type='success')
        # Sliders
        seismic_iline = pn.widgets.IntSlider(name='Inline',
                                             start = int(self.inlines[0]),
                                             end = int(self.inlines[-1]),
                                             value = self.inline_number,
                                             step = 1,
                                             bar_color =  "#47a447")

        traces_iline = pn.widgets.IntRangeSlider(name='Traces along Inline',
                                                 start = int(self.crosslines[0]),
                                                 end = int(self.crosslines[-1]),
                                                 value = (int(self.crosslines[0]), int(self.crosslines[0]) + 1),
                                                 step = 1,
                                                 bar_color =  "#47a447")
        
        seismic_xline = pn.widgets.IntSlider(name='Crossline',
                                             start = int(self.crosslines[0]),
                                             end = int(self.crosslines[-1]),
                                             value = self.crossline_number,
                                             step = 1,
                                             bar_color ="#e6e6e6")

        traces_xline = pn.widgets.IntRangeSlider(name='Traces along Crossline',
                                                 start = int(self.inlines[0]),
                                                 end = int(self.inlines[-1]),
                                                 value = (int(self.inlines[0]), int(self.inlines[0]) + 1),
                                                 step = 1,
                                                 bar_color ="#e6e6e6")

        time_slice = pn.widgets.IntRangeSlider(name='Time slice [ms]',
                                               start=WiggleModule.trace_length[0],
                                               end=WiggleModule.trace_length[-1],
                                               value=(0, int(WiggleModule.trace_length[-1]/10)),
                                               step=int(WiggleModule.trace_length[-1]/10))

        time_interval = pn.widgets.IntSlider(name="Sample interval [ms]",
                                               start=int(WiggleModule.sample_interval/WiggleModule.sample_interval),
                                               end=WiggleModule.sample_interval,
                                               step=int(WiggleModule.sample_interval/WiggleModule.sample_interval),
                                               value=WiggleModule.sample_interval)

        # Decorator to mess up with the API
        @pn.depends(seismic_buttons.param.value, wiggle_buttons.param.value,
                    seismic_iline.param.value, traces_iline.param.value,
                    seismic_xline.param.value, traces_xline.param.value,
                    time_slice.param.value, time_interval.param.value)
        def gather_plot(seismic_buttons, wiggle_buttons,
                        seismic_iline,traces_iline, 
                        seismic_xline, traces_xline,
                        time_slice, time_interval):
            
            """
            NAME
            ----
                gather_plot
            
            DESCRIPTION
            -----------
                Constructs a grid of angle gathers.

                Collects angle gathers into one plot given a range of lines by using Holoviews
                and bokeh as backend.
                
            ARGUMENTS
            ---------
                Arguments are given by Panel's widgets through the panel's depend decorator:

                    seismic_buttons : str
                        Seismic direction to base the amplitude plotting.

                    wiggle_buttons : str
                        Desired amplitude's plot type. Can be given manually or by Panel's
                        radio button widget. "Wavelet" will plot amplitudes using only a sine
                        curve, "Black wiggle" will fill with black the area between the sin curve
                        and time_axis and "Colored wiggle", will fill with blue/red the positive/negative 
                        area between the sin curve and time_axis.
                              
                    seismic_iline : int
                        Inline number selection.

                    traces_iline : tuple
                        Range of crosslines to be intersected with seismic_iline.

                    seismic_xline : int
                        Crossline number selection.

                    traces_xline : tuple
                        Range of inlines to be intersected with seismic_xline.

                    time_slice : list
                        Time slice of interest. 

                    time_interval : int
                        Chosen time interval.

                    Survey.merge_path : str
                        Path where the merge of the PAS is located.
  
                                          
            RETURN
            ------
                GridSpace : Holviews element [GridSpace]
                    Angle gathers.
            
            """
            
            # f.gather[2405, 2664, :] array // f.gather[2405:2408, 2664:2667, :] generator!! Presents errores while giving atributes
                #When is not hardcoded
            
            #Opening seismic file (once)
            with segyio.open(Survey.merge_path) as segy:  
                
                gather_dict = {}
                # Storing scaling fac
                WiggleModule.scaling_factor(self, segyio.tools.collect(segy.trace[:]))

                # Storing time array
                WiggleModule.time(self, time_interval)
                
                # Segyio gather Generator
                if seismic_buttons == "Inline":
                    trace_counter = traces_iline[0]
                    for gather in segy.gather[seismic_iline, traces_iline[0]:traces_iline[-1] + 1, :]:
                        gather_dict[f"{seismic_iline}/{trace_counter}"] = WiggleModule.wiggle_plot(self, 
                                                                                                   gather, 
                                                                                                   time_slice, 
                                                                                                   wiggle_buttons)
                        trace_counter += 1
                elif seismic_buttons == "Crossline":
                    trace_counter = traces_xline[0]
                    for gather in segy.gather[traces_xline[0]:traces_xline[1] + 1, seismic_xline, :]:
                        gather_dict[f"C{trace_counter}/{seismic_xline}"] = WiggleModule.wiggle_plot(self, 
                                                                                                    gather, 
                                                                                                    time_slice, 
                                                                                                    wiggle_buttons)
                        trace_counter += 1

                # Gathers
                GridSpace = hv.GridSpace(gather_dict, kdims=['Trace'])
                return(GridSpace)
                    
                
                column = pn.Column('# Column', w1, w2, background='WhiteSmoke')
        
        widgets = pn.WidgetBox(f"## Gathers display menu",
                               line_input, gather_direction, seismic_buttons,
                               seismic_iline, traces_iline,
                               seismic_xline, traces_xline,
                               trace_input, time_slice, time_interval, wiggle_buttons)

        def bg_widgets(event):
            
            """
            NAME
            ----
                bg_widgets.
            
            DESCRIPTION
            -----------
                Links widget's color to seismic direction buttons in order to ease the identification of
                widgets.
                
            ARGUMENTS
            ---------
                event : str
                    Seismic radio buttons value.
                     
            RETURN
            ------
                [0] WidgetBox
                    [4] IntSlider color.
                    [5] IntRangeSlider color.
                    [6] IntSlider color.
                    [7] IntRangeSlider color.

            """
            
            if seismic_buttons.value == "Crossline":
                seismic_iline.bar_color = "#e6e6e6"
                traces_iline.bar_color = "#e6e6e6"
                seismic_xline.bar_color = "#47a447"
                traces_xline.bar_color = "#47a447"

            else:
                seismic_iline.bar_color = "#47a447"
                traces_iline.bar_color = "#47a447"
                seismic_xline.bar_color = "#e6e6e6"
                traces_xline.bar_color = "#e6e6e6"
                
            

        seismic_buttons.param.watch(bg_widgets, 'value')

        return((pn.Row(widgets, gather_plot).servable()))
