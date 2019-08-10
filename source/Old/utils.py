# Dependencies
import os
import segyio
import pandas as pd
import numpy as np

# Utility functions

# 1) Validation function: existance
def path_validation(path):
    
    """
    path_validation(path)
    
    Validates the existance of a file by giving it's path.
    
    Argument
    --------
    path : str
        Path where the file to validate is located.
    
    Return
    ------
    True/False : bool
        If the file exist the output will be True, else False.
                 
    """
    
    # FIrst validation: does the file exist in the given route?
    if os.path.isfile(path) == True:
    
        # If the file truly exist, then return True
        return (True)
    else:
        # If it doesn't exist, then go False
        return (False)


# 2) Validation function: file extension (TXT, SEG-Y)
def check_file_extension(file_path):
    
    """
    check_file_extension(file_path)
    
    Validation of the input file's extension. Whether the function is a .txt or .sgy file.
    
    Argument
    --------
    file_path : str 
        Path where the file to validate is located.
                 
    Return
    ------
    True/False : bool 
        If the extesion is a .txt or .sgy file the output will be True, else False.
    
    """
    
    # First validation: is it a TEXT or SEG-Y file?
    file, ext = os.path.splitext(file_path)
    
    # If the file is one of both extensions mentionen above, then return true
    if ext.lower() == (".txt") or ext.lower() == (".sgy"):
        return (True)
    
    # if is not, return false
    else: 
        return (False)


# 3) Validation function: standard SEG-Y file
def cube_file_segy_format_validation(seismic_path):

    """
    cube_file_segy_format_validation(seismic_path)

    Validation whether the input file is a standard SEG-Y file or not.
    
    Argument
    ---------
    seismic_path : str
        Path where the seg-y file to validate is located.
                   
    Return
    ------
    True/False : bool
        If the input file is a SEG-Y standard file the output will be True, else False. 
        
    Notes
    -----
    This function compares the byte distribution of the given file and the ones used by segyIO. These 
    follows the Technical Standards Committee (2017) of the SEG.
    
    References
    ----------
    SEG Technical Standards Committee. (2017). SEG-Y_r2.0: SEG-Y revision 2.0 Data Exchange format.
        Document Online. Available at: 
        https://seg.org/Portals/0/SEG/News%20and%20Resources/Technical%20Standards/seg_y_rev2_0-mar2017.pdf
    
    
    """
    
    # Validation 2: is it a SEG-Y standard file?  
    with segyio.open(seismic_path,'r') as segyfile:
        for i in range(0,len(segyfile.header[0].keys()),1):
               
        # segyio.tracefield.keys returns a dictionary of keys.
        # list(segyio.tracefield.keys.keys()) make a list from the dictionary only with the keys within it
            segyio_header = list(segyio.tracefield.keys.keys())
   
            # segyfile.header[0].keys() returns a list of the header keys of the trace 0. 
            # Only matters the trace dist.
            file_header = segyfile.header[0].keys()

            # comparison of both headers. if a == b then b is a standard SEG-Y and return true
            if str(segyio_header[i]) == str(file_header[i]):
                return (True)
                
            # If not: a != b then the file is not standard and return false
            else:
                return (False) 


# 4) Collection of validation fuctions for SEG-Y files
def cube_file_validation(seismic_path):
    
    """
    cube_file_validation(seismic_path)

    Collection of previous validations to test whether the seg-y file is suitable for the following functions
    
    Argument
    --------
    seismic_path : str
        Path where the seg-y file to validate is located.
                 
    Return
    ------
    True : bool
        If the previous validations are True the output will be True, else a str.
    str
        If one the previous validations (at least) is False the output will a Warning specifiying why the
        function can't work with the data.
        
        
    See Also
    --------
    Validation functions:
        1) path_validation(path)
        2) check_file_extension(file_path)
        3) cube_file_segy_format_validation(seismic_path)
    
    """
    
    if (path_validation(seismic_path) == True) and (check_file_extension(seismic_path) == True):
        if cube_file_segy_format_validation(seismic_path) == True:
            return (True)
        else:
            return(f"WARNING: the SEG-Y is not standard") # Second validation
    else:
        return(f"WARNING: the input file is not a valid one") # First two validation


# 5) Database function: wells information
def wells_data_organization(wells_path):
    
    """
    wells_data_organization(wells_path)
    
    Builds a DataFrame using the well's information within the Seismic Survey.
    
    The function builds a pandas DataFrame based on the information contained by the given text file
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
        A matrix compounded by the following columns and the information related to each well: 
        {"index", "name","utmx","utmy","cdp_iline","cdp_xline"}
    
    str
        If the previous validations (one at least) are False the output will be a Warning specifiying 
        why the function can't work with the data.
        
    See Also
    --------
    Validation functions:
        1) path_validation(path)
        2) check_file_extension(file_path)
    """   
     
    if (path_validation(wells_path) == True) and (check_file_extension(wells_path) == True):
    
        well_dataframe = pd.read_csv(wells_path,
                            sep=" ",
                            header = None, 
                            names= ["name","utmx","utmy","cdp_iline","cdp_xline","depth"])
        
        well_dataframe["index"] = well_dataframe["name"]
        well_dataframe.set_index("index", inplace = True)
        
        return(well_dataframe)
    
    else:
        return("WARNING: the input file is not a text file")


# 6) Database function: cube information
def cube_data_organization(seismic_path):

    """
    cube_data_organization(seismic_path)
    
    Builds a DataFrame using the trace headers information within the seg-y file.
    
    Argument
    ---------
    seismic_path : str
        Path of the standard SEG-Y file
        
    Return
    ------
    trace_coordinates : (Pandas) DataFrame
        A matrix compounded by the following columns and the information related to each trace: 
        {"tracf","CDP",(CDP)utmx","(CDP)utmy","(CDP)iline","(CDP)xline"}
    
    str
        If the previous validations (one at least) are False the output will be a Warning specifiying 
        why the function can't work with the data.
    
    See Also
    --------
    Validation functions:
        1) cube_file_validation(seismic_path)
        2) path_validation(path)
        3) check_file_extension(file_path)
        4) cube_file_segy_format_validation(seismic_path)
    
    """        
    
    if cube_file_validation(seismic_path) == True:
    
        # Initializing the DataFrame
        trace_coordinates = pd.DataFrame() 

        # Opening the seismic file
        with segyio.open(seismic_path,'r') as segy:

            # Declaring variables to slice the array given by segyio
            fta = 0 # fti stands for: First Trace of the Array
            lta = segy.tracecount # lti stands for: Last Trace of the Array     

            # # Adding the columns to the DataFrame for each header of interest 
            trace_coordinates['tracf'] = segy.attributes(segyio.TraceField.TRACE_SEQUENCE_FILE)[:] #b(5-8)
            trace_coordinates['cdp'] = segy.attributes(segyio.TraceField.CDP)[:] # b(21-24)
            trace_coordinates['utmx'] = segy.attributes(segyio.TraceField.CDP_X)[:] #b(181-184)
            trace_coordinates['utmy'] = segy.attributes(segyio.TraceField.CDP_Y)[:] #b(185-188)
            trace_coordinates['cdp_iline'] = segy.attributes(segyio.TraceField.INLINE_3D)[:] #b(189-192)
            trace_coordinates['cdp_xline'] = segy.attributes(segyio.TraceField.CROSSLINE_3D)[:] #b(193-196)

            # A scalar (bytes 71-72) are usually aplied to the cdp coordinates in the trace headers:
            scalar = segy.attributes(segyio.TraceField.SourceGroupScalar)[:] # b (71-72)
            trace_coordinates['utmx'] = np.where(scalar == 0, trace_coordinates['utmx'],
                                            np.where(scalar > 0, trace_coordinates['utmx'] * scalar, 
                                                                    trace_coordinates['utmx'] / abs(scalar)))
            trace_coordinates['utmy'] = np.where(scalar == 0, trace_coordinates['utmy'],
                                            np.where(scalar > 0, trace_coordinates['utmy'] * scalar, 
                                                                    trace_coordinates['utmy'] / abs(scalar)))

            return (trace_coordinates)
        
    else:
        return(cube_file_validation(seismic_path))








