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

def wells_data_organization(wells_path):
    
    """
    wells_data_organization(wells_path)
    
    Builds a DataFrame using the well's information within the Seismic Survey.
    
    The function builds a (Pandas) DataFrame based on the information contained by the given text file
    related to wells. The data inside the file must be structured in a very specific way in order to be
    readen by the function. Each of the items listed below have to be separated by one space: 
        "well name" "utmx coordinate" "utmy coordinate" "inline coordinate" "xline coordinate" "depth"
    
    
    Argument
    --------
    wells_path : str
        Path where the well information file is located. Default path: '../data/wells_info.txt'
    
    Return
    ------
    well_dataframe : (Pandas) DataFrame. 
        A matrix compounded by the information related to each well. The information distribution is 
        controlled by the following columns:
            - name: well's name
            - cdp_iline: inline coordinate.
            - cdp_xline: crossline coordinate.
            - utmx: horizontal axis of the Universal Transversal Mercator coordinate system.
            - utmy: vertical axis of the Universal Transversal Mercator coordinate system.
            - depth: depth reached by the well.
    
    str
        If the previous validations (one at least) are False the output will be a Warning specifiying 
        why the function can't work with the data.
        
    """   
     
    if file_validation(wells_path) == True:
    
        well_dataframe = pd.read_csv(wells_path,
                            sep=" ",
                            header = None, 
                            names= ["name","cdp_iline","cdp_xline","utmx","utmy", "depth"])
        
        well_dataframe["index"] = well_dataframe["name"]
        well_dataframe.set_index("index", inplace = True)
        
        return(well_dataframe)
    
    else:
        return("WARNING: the input file is not a text file")