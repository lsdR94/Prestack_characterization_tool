# Dependencies

# Segyio
import segyio

# Scipy
import numpy as np
from scipy.interpolate import interp1d

# Pandas
import pandas as pd

# Pyviz
import holoviews as hv
from holoviews import opts, dim
from bokeh.models import HoverTool
import panel as pn
import hvplot.pandas
import panel.widgets as pnw
hv.extension('bokeh')



def min_max_seismic_lines(df, button, iline_number, xline_number, number_of_gathers_to_display):
    
    """
    
    min_max_seismic_lines(df, button, iline_number, xline_number, number_of_gathers_to_display)

    Makes a list of seismic lines (min/max coordinates) to be use as the argument of segyIO's GATHER 
    function.
    
    Arguments
    ---------
    df : (Pandas) DataFrame
        A matrix compounded by the trace header information of interest: coordinates of the 
        Seismic traces.
    
    button : str
        Seismic direction used to read and plot the information related to the gathers. The value comes 
        from Panel's select widget: RadioButtonGroup located in the get_wiggle function. 
        Default value: "Inline".
    
    iline_number : int
        Number of the seismic line along the inline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    xline_number : int
        Number of the seismic line along the crossline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
        
    number_of_gathers_to_display : int
        The amount of gathers to display along with the main given point which is the intersection of 
        the iline_number and xline_number. Default value = 2.
        
    Return
    ------
    list_of_seismic_coordinates : list
        A list compounded by the minimum and maximum values of the seismic lines coordinates to be 
        used by segyIO's GATHER function to extract the amplitude array from the SEG-Y file.

    Note1:
        The segyIO's GATHER function uses as its argument the inline and crossline coordinates to 
        store/extract the amplitudes with the SEG-Y file. The intersection of these lines results in 
        the TRACF header.
    
    """ 
    
    if button == "Inline":
        iline_step = 0
        xline_step = 1
        xline_min = xline_number - xline_step * number_of_gathers_to_display // 2
        xline_max = xline_number + xline_step * number_of_gathers_to_display // 2   
        
        # Solving boundaries issues for inline direction
        if xline_min < df['cdp_xline'].min():
            xline_max = xline_max + abs(xline_min - df['cdp_xline'].min())
            return[iline_number, iline_number, df['cdp_xline'].min(), xline_max]
        
        if xline_max > df['cdp_xline'].max():
            xline_min = xline_min - abs(xline_max - df['cdp_xline'].max()) 
            return[iline_number, iline_number, xline_min, df['cdp_xline'].max()]
        
        else:
            return[iline_number, iline_number, xline_min, xline_max]
        
    
    else:
        iline_step = 1
        xline_step = 0
        iline_min = iline_number - iline_step * number_of_gathers_to_display // 2
        iline_max = iline_number + iline_step * number_of_gathers_to_display // 2 
         
        # Solving boundaries issues for crossline direction    
        if iline_min < df['cdp_iline'].min():
            iline_max = iline_max + abs(iline_min - df['cdp_iline'].min())
            return[df['cdp_iline'].min(), iline_max, xline_number, xline_number]
        
        if iline_max > df['cdp_iline'].max():
            iline_min = iline_min - abs(iline_max - df['cdp_iline'].max()) 
            return[iline_min, df['cdp_iline'].max(), xline_number, xline_number]
        
        else:     
            return[iline_min, iline_max, xline_number, xline_number]

def scaling_fact(list_of_gathers):
    
    """
    scaling_fact(list_of_gathers)
    
    Computes the maximum absolute value of the amplitudes within the SEG-Y files.
    
    Argument
    --------
    list_of_gathers : list
        A list compounded by the path of each partial angle stack file to be used.
        
    Return
    ------
    scaling_fac : float
        Value to be used to scale the axis related to the amplitudes, therefore these will bounded 
        between [-1,1].

    """
    
    scaling_fac = 0
    for file in list_of_gathers:
        with segyio.open(file,'r') as segy:
            something = abs(segyio.tools.collect(segy.trace[:]))   
            if something.max() > scaling_fac:
                scaling_fac = something.max()
                
    return (float(scaling_fac))

def time_axis(one_gather_file):
    
    """
    
    time_axis(one_gather_file)
    
    Builds the time axis of the plot based on the sample interval and the number of samples
    per trace stored within the SEG-Y file.
    
    Argument
    --------
    one_gather_file : str
        Path of a partial angle stack file to extract the information inside the trace headers.
        
    Return
    ------
    time_array : np.array
        An array compounded by the time samples of each trace in the SEG-Y file.
        
    Note:
        Partial angle stacks shares geometry, therefore only one is needed to calculate the vertical 
        axis of the plot.
    
    """
    
    # Every trace has the same sample interval so as the samples per trace
    first_trace = 0
    with segyio.open(one_gather_file,'r') as segy:     
        # Extracting the sample interval and the amount of amplitudes from the header. Also us to s
        sample_interval = float(segy.attributes(segyio.TraceField.TRACE_SAMPLE_INTERVAL)[first_trace]/1000000)
        samples_per_trace = int(segy.attributes(segyio.TraceField.TRACE_SAMPLE_COUNT)[first_trace])
        
        time_array = np.arange(first_trace,sample_interval * samples_per_trace,sample_interval)
        
    return (time_array)

def spline_storepolation (iline_number, xline_number, list_of_gathers, time_interval, angle_bet_gathers):
    
    """
    spline_storepolation (iline_number, xline_number, list_of_gathers, time_interval)
    
    Makes and stores (Pandas DataFrame) a spline interpolation of amplitudes and time samples for
    a given interval.
    
    This function is used to smooth the wiggle plot: the sampling inside the SEG-Y files is not good 
    enough to recreate the shape of a zero phase wavelet, hence this function approximates the data to 
    a seismic wavelet and not to a sismological wave.
    
    Arguments
    ---------
    iline_number : int
        Number of the seismic line along the inline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    xline_number : int
        Number of the seismic line along the crossline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    list_of_gathers : list
        A list compounded by the path of each partial angle stack file to be used.
        
    time_array : np.array
        An array compounded by the time samples of each trace in the SEG-Y file. Y axis of the plot.

    angle_bet_gathers : int
        The reason of the media of each gather.
        
    Return
    ------
    amp_dataframe : (Pandas) DataFrame
        A matrix made of amplitude arrays for each angle gather loaded.
        
    Note:
        The amplitude array has been separated in two series: positive_amplitude and negative_amplitude 
        for each angle loaded. These will be used along with the Holoviews Area element in order to 
        apply the usual polarity displayed in gathers. The result of the previous element simulates 
        matplotlib's fill_in_between function using bokeh.
    
    """
    
    # Initializing the dataframe and angle
    amp_dataframe = pd.DataFrame([])
    angle = angle_bet_gathers
    
    # Making the Y axis
    t_axis = time_axis(list_of_gathers[0])
    
    #Interpolate to:
    new_time = np.arange(t_axis[0],t_axis[-1] + time_interval, time_interval)
    
    amp_dataframe["time_axis"] = new_time
    
    # Extracting the amplitude array from the SEG-Y file
    for file in list_of_gathers:
        with segyio.open(file,'r') as segy:
            amp = segy.gather[iline_number, xline_number][0] # [0] because is an ndarray of a ndarray

        # Spline interpolation
        f_spline = interp1d(t_axis, amp, kind = "cubic")
        new_amp = f_spline(new_time)
    
        # Making two more series: Negative amplitude and positive amplitude
        amp_dataframe[f"amplitude_{angle}"] = new_amp
        amp_dataframe[f"positive_amplitude_{angle}"] = new_amp
        amp_dataframe[f"negative_amplitude_{angle}"] = new_amp
        
        # Separating the values of the amplitudes for Area element
        amp_dataframe.loc[amp_dataframe[f"positive_amplitude_{angle}"] < 0 , f"positive_amplitude_{angle}"] = 0
        amp_dataframe.loc[amp_dataframe[f"negative_amplitude_{angle}"] > 0 , f"negative_amplitude_{angle}"] = 0
        
        # Taking control of the angle related to the amplitude to store it in a dataframe
        angle = angle + angle_bet_gathers
            
    return (amp_dataframe.round(4))  

def wiggle_plot(amp_df, iline_number, xline_number, list_of_gathers, time_slice_top, angle_bet_gathers):
    
    """
    wiggle_plot (df, list_of_gathers, iline_number, xline_number, time_slice_top)
    
    Plots the amplitude matrix into the shape of a zero phase wavelet.
    
    Arguments
    ---------
    amp_df : (Pandas) DataFrame
        A matrix compounded by the trace header information of interest: coordinates of the 
        Seismic traces.
    
    iline_number : int
        Number of the seismic line along the inline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    xline_number : int
        Number of the seismic line along the crossline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    list_of_gathers : list
        A list compounded by the path of each partial angle stack file to be used.
    
    time_slice_top : int
        A value that controls the top of the Y axis (time) displayed. The value comes from Panel's slider
        widget inside get_widget function of the wiggle module.
    
    Return
    ------
    wiggle_display : Holviews element [Overlay]
        A collection zero phase wavelets of the given partial angle stacks and inline/crossline.
    
    
    Note:
        The plot combines the Curve and Area elements, both of Holoviews. The first one is responsible 
        of ensuring the layout of the seismic zero fase wavelet of a gather and the deployment of the 
        information through a hover tool. The second one is responsible of showing the amplitudes 
        polarity along the time axis, where:
            - Positive values = Blue
            - Negative values = Red
            - Null values (0) = Black
    
    """
    
    # Initializing the plot and the angle variable
    wiggle_display = hv.Curve((0,0))
    angle = angle_bet_gathers

    # Computing scale factor for the X axis
    scale_f = scaling_fact(list_of_gathers)
    s_factor = 0
    xticks = [] 
    
    # making the data to plot according a scaled value
    for file in list_of_gathers:
        
        amp_df[f"s_amplitude_{angle}"] = amp_df[f"amplitude_{angle}"] + s_factor
        amp_df[f"s_negative_amplitude_{angle}"] = amp_df[f"negative_amplitude_{angle}"] + s_factor
        amp_df[f"s_positive_amplitude_{angle}"] = amp_df[f"positive_amplitude_{angle}"] + s_factor
        
        # Hover designation
        hover_w= HoverTool(tooltips=[('Time', '@time_axis'),
                                     ('Amplitude', f"@amplitude_{angle}"),
                                     ("Angle",f"{angle}")])  
         
        # Plotting the wiggle
        wiggle = hv.Curve(amp_df, ["time_axis", f"s_amplitude_{angle}"], 
                              [f"amplitude_{angle}"])
        wiggle.opts(color = "black", line_width = 2, tools = [hover_w])
          
        # Making the area plot more comfortable
        x = amp_df["time_axis"]
        y = s_factor
        y2 = amp_df[f"s_negative_amplitude_{angle}"]
        y3 = amp_df[f"s_positive_amplitude_{angle}"]
        
        # Fill in between: Holoviews Element
        negative = hv.Area((x, y, y2), vdims=['y', 'y2']).opts(color = "red", line_width = 0)
        positive = hv.Area((x, y, y3), vdims=['y', 'y3']).opts(color = "blue", line_width = 0)        
        fill_in_between = negative * positive
        
        # Overlying the colored areas +  the zero phase wavelet
        wiggle_display = wiggle_display * wiggle * fill_in_between
        
        # For next iteration
        xticks = xticks + [(s_factor, angle)]
        angle = angle + angle_bet_gathers
        s_factor = s_factor + scale_f
        
        # Adding final customizations
        wiggle_display.opts(height = 500, width = 150, padding = 0.1,
                            show_grid = True, xaxis = "top", invert_axes = True, invert_yaxis=True,
                            fontsize={"title": 10, "labels": 14, "xticks": 8, "yticks": 8},
                            ylabel = f"{iline_number}/{xline_number}", xlabel = "Time [s]",
                            xformatter = "%f", yformatter = "%.1f", xticks = xticks,
                            xlim = (time_slice_top, time_slice_top + 1),
                            active_tools = ["pan", "wheel_zoom"])
        
    return(wiggle_display)

def get_wiggle(df, iline_number, xline_number, list_of_gathers, angle_bet_gathers):
    
    """
    get_wiggle(df, iline_number, xline_number, list_of_gathers)
    
    Plots an interactive gather for a given partial angle stacks and inline/crossline coordinates.
    
    Arguments
    ---------
    df : (Pandas) DataFrame
        A matrix compounded by the trace header information of interest: coordinates of the 
        Seismic traces.
    
    iline_number : int
        Number of the seismic line along the inline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    xline_number : int
        Number of the seismic line along the crossline direction. The value could be given manually
        or by Panel's slider widget inside the get_basemap function of the basemap module.
    
    list_of_gathers : list
        A list compounded by the path of each partial angle stack file to be used.

    angle_bet_gathers : int
        The reason of the media of each gather.
    
    Return
    ------
    NdLayout : Panel layout element [Row]
        A collection of gathers and Panel's widgets listed as controls:
            - A track bar to modify the amount of gathers displayed.
            - A button to change the between the seismic directions: Inline or Crossline.
            - Two track bars to make time slices (at least by one second).
            - A track bar to change the sample interval used by the spline_storepolation function.
            
    See also
    --------
        wiggle plot functions:
            1) min_max_seismic_lines(df, button, iline_number, xline_number, number_of_gathers_to_display)
            2) scaling_fact(list_of_gathers)
            3) time_axis(one_gather_file)
            4) spline_storepolation (iline_number, xline_number, list_of_gathers, time_interval)
            5) wiggle_plot(df, iline_number, xline_number, list_of_gathers, time_slice_top)

    """
    
    # Display
    display_iline_number = pn.widgets.StaticText(name = 'Selected Inline', value = str(iline_number))
    
    display_xline_number = pn.widgets.StaticText(name = 'Selected Crossline', value = str(xline_number))
    
    gather_direction = pn.widgets.StaticText(value = " Direction to plot the gathers")
    
    display_controls = pn.widgets.StaticText(value = "Display controls")
    
    # Buttons
    seismic_buttons = pn.widgets.RadioButtonGroup(name='Radio Button Group', 
                                                  options=['Inline', 'Crossline'], button_type='success')
    
    
    # Sliders
    time_slice_top = pn.widgets.IntSlider(name = "Survey's top [s]", 
                                          start = int(time_axis(list_of_gathers[0])[0]), 
                                          end = int(time_axis(list_of_gathers[0])[-1] - 1), 
                                          step = 1, 
                                          value = 0)
    time_slice_base = pn.widgets.IntSlider(name = "Survey's base [s]", 
                                           start = int(time_axis(list_of_gathers[0])[0] + 1), 
                                           end = int(time_axis(list_of_gathers[0])[-1]), 
                                           step = 1, 
                                           value = 6)
    
    sample_interval = pn.widgets.FloatSlider(name = "Sample interval [s]", 
                                            start = 0.001, 
                                            end = 0.004, 
                                            step = 0.001, 
                                            value = 0.004)
    
    number_gather_display = pn.widgets.IntSlider(name = "Extra gathers to display", 
                                                 start = 2, 
                                                 end = 6, 
                                                 step = 2, 
                                                 value = 2)
       
    # Decorator to mess up with the API
    @pn.depends(time_slice_top.param.value, time_slice_base.param.value,
                sample_interval.param.value,seismic_buttons.param.value, number_gather_display.param.value)
    
    def gather_plot(time_slice_top, time_slice_base, sample_interval ,seismic_buttons, number_gather_display):
        
        scale_factor = scaling_fact(list_of_gathers)
        s_f = 0

        # Initializing dictionary for holoviews layout element
        angle_gather_dict = {}
        
        max_min_gathers = min_max_seismic_lines(df, seismic_buttons, iline_number, xline_number, number_gather_display)
        
        for inline in range(max_min_gathers[0], max_min_gathers[1] + 1, 1):
            for crossline in range(max_min_gathers[2], max_min_gathers[3] + 1, 1):

        # Making the dataframe
                amp_dataframe = spline_storepolation(inline, crossline, 
                                                     list_of_gathers, sample_interval, angle_bet_gathers)

        # Cropping the dataframe according to the time_variant variable. when t_w = 0, no crop is done
                amp_dataframe = amp_dataframe[(amp_dataframe.time_axis >= time_slice_top) &
                                              (amp_dataframe.time_axis <= time_slice_base)]

                # Plotting the wiggle from the top chosen with the slider to the previous + 1
                gather = wiggle_plot (amp_dataframe, inline, crossline, list_of_gathers, 
                                      time_slice_top, angle_bet_gathers)

                # Changing some parameters of the plot: y axis label + y axis line
                if (inline == max_min_gathers[0]) and (crossline == max_min_gathers[2]):
                    gather.opts(xlabel = "Time [s]", width = 200)
                else:
                    gather.opts(xlabel = " ", yaxis = None, width = 150)
                    
                angle_gather_dict[f"{inline}/{crossline}"] = gather

            # NdLayout for the dictionary
        NdLayout = hv.NdLayout(angle_gather_dict, kdims = f"Angle Gather (I/X)")
        return(NdLayout)
    
    widgets = pn.WidgetBox(f"## Gathers display Panel", display_iline_number,
                                                             display_xline_number, 
                                                             pn.Spacer(height = 10),
                                                             number_gather_display,
                                                             pn.Spacer(height = 10),
                                                             gather_direction,
                                                             seismic_buttons,
                                                             pn.Spacer(height = 10),
                                                             display_controls,
                                                             time_slice_top,
                                                             time_slice_base,
                                                             sample_interval)
                        
    return((pn.Row(widgets, gather_plot).servable()))
 















