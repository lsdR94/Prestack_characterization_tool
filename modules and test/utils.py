
# Modules
import os
import segyio
import pandas as pd
import numpy as np

# AUXILIARY FUNCTIONS

# 1) path_validation(path)
def path_validation(path):
       
    """
  
    A function that validates the existance of a file by giving it's path.
    
    Argument:
    path : String. Path where the file to test is located.
    
    Return:
    True/False : Boolean. If the file exist then the output will be True, else False.
                 
    """
    
    # FIrst validation: does the file exist in the given rout?
    if os.path.isfile(path) == True:
        
        # If the file trylu exist, then return True
        return (True)
    else:
        # If it doesn't exist, then go False
        return (False)

# 2) check_file_extension (wells_path)
def check_file_extension(file_path):
    """
    
    A function that validates the extension of the input file to build the wells DataFrame
    
    Argument:
    file_path : String. Path where the file either .txt or .sgy is located.
                 
    Return:
    True/False : Boolean. If the extesion is a .txt or .sgy file then the output will be True, else False.
    
    """
    # First validation: is it a TEXT or SEG-Y file?
    file, ext = os.path.splitext(file_path)
    
    # If the file is one of both extensions mentionen above, then return true
    if ext.lower() == (".txt") or ext.lower() == (".sgy"):
        return (True)
    
    # if is not, return false
    else: 
        return (False)

# 3) wells_data_organization (wells_path)
def wells_data_organization(wells_path):
    
    """
    
    A function that builds a DataFrame using the well's information within the Seismic Survey. 
    
    Argument:
    wells_path : String. Path where the text file is located. Default path: wells_info.txt
                 located in the data folder.
    
    Return:
    well_dataframe : (Pandas) DataFrame. Default columns: 
                     {'name','utmx','utmy','cdp_iline','cdp_xline','depth'}
    
    """   
     
    if (path_validation(wells_path) == True) and (check_file_extension(wells_path) == True):
    
        well_dataframe = pd.read_csv(wells_path,
                            sep=" ",
                            header = None, 
                            names= ["name","utmx","utmy","cdp_iline","cdp_xline","depth"])
    
        return(well_dataframe)
    
    else:
        return(("WARNING: the input file is not a text file"))
  
# 4)cube_file_segy_format_validation (seismic_path,step)
def cube_file_segy_format_validation (seismic_path,step):

    """
    
    A function that validates if the input file is a standard SEG-Y file or not.
    
    Arguments:
    seismic_path : String. Path of the standard SEG-Y file. Default: POSEIDON 3D SURVEY located
                   inside the data folder.
                   
    step : Integer. Reading interval between the data. Default: 1.
    
    Return:
    True/False : Boolean. If the input file is a SEG-Y standard file the output will return True, else False. 
    
    """
    
    # Validation 2: is it a SEG-Y standard file?  
    with segyio.open(seismic_path,'r') as segyfile:
        for i in range(0,len(segyfile.header[step].keys()),1):
               
        # segyio.tracefield.keys returns a dictionary of keys.
        # list(segyio.tracefield.keys.keys()) make a list from the dictionary only with the keys within it
            segyio_header = list(segyio.tracefield.keys.keys())
   
            # segyfile.header[0].keys() returns a list of the header keys of the trace 0. 
            # Only matters the trace dist.
            file_header = segyfile.header[step].keys()

            # comparison of both headers. if a == b then b is a standard SEG-Y and return true
            if str(segyio_header[i]) == str(file_header[i]):
                return (True)
                
            # If not: a != b then the file is not standard and return false
            else:
                return (False)   

# 5) cube_file_step_validation(seismic_path, step)
def cube_file_step_validation(seismic_path, step):
    
    """
    
    A function that validates if the given step is bounded between the minimum and maximum value of the survey
    
    Arguments:
    seismic_path : String. Path of the standard SEG-Y file. Default: POSEIDON 3D SURVEY located
                   inside the data folder.
                   
    step : Integer. Reading interval between the data. Default: 1.
    
    Return:
    True/False : Boolean. If the input step is inside the range between [min-max] values then the output will
                 be True, else False.
    
    """
    # Cube validation 3: is the given step a valid one?
    with segyio.open(seismic_path,'r') as segy:
        tracf_min = segy.attributes(segyio.TraceField.TRACE_SEQUENCE_FILE)[:].min()
        tracf_max = segy.attributes(segyio.TraceField.TRACE_SEQUENCE_FILE)[:].max()
        
        # If the step is bounded between trac_min - trac_max return True
        if step >= tracf_min and step <= tracf_max:
            return (True)
        
        # If is not bounded, then return False
        else:
            return (False)

# 6) cube_file_validation(seismic_path, step)
def cube_file_validation(seismic_path, step):
    
    """

    Collection of validation functions to test whether the input file is suitable for the following functions.
    
    Argument:
    seismic_path : String. Path of the standard SEG-Y file. Default: POSEIDON 3D SURVEY located 
                   inside the data folder.
                 
    Return:
    True/False : Boolean. If the previous validations (extension of the file, type of file and the step given)
                 are True, then the output will return True, else False.
    
    """
    
    if check_file_extension(seismic_path) == True:
        if cube_file_segy_format_validation(seismic_path,step) == True:
            if cube_file_step_validation(seismic_path, step):
                return (True)
            else:
                return(f"WARNING: the step is not a valid one") # Third validation
        else:
            return(f"WARNING: the SEG-Y is not standard") # Second validation
    else:
        return(f"WARNING: the input file is not a valid one") # First validation

# 7) cube_data_organization (seismic_path, step)
def cube_data_organization(seismic_path, step = 1):

    """
    
    A function that builds a DataFrame using the information within the trace headers of a 
    standard SEG-Y file. 
    
    Arguments:
    seismic_path : String. Path of the standard SEG-Y file. Default: POSEIDON 3D SURVEY located 
                   inside the data folder.
                   
    step : Integer. Reading interval between the data. Default: 1.
        
    Return:
    trace_coordinates : (Pandas) DataFrame. Default headers as columns:
                        {'tracf','(CDP)utmx','(CDP)utmy','(CDP)iline','(CDP)xline'}
    
    """        
    
    if cube_file_validation(seismic_path, step) == True:
    
        # Initializing the DataFrame
        trace_coordinates = pd.DataFrame() 

        # Opening the seismic file
        with segyio.open(seismic_path,'r') as segy:

            # Declaring variables to slice the array given by segyio
            fta = 0 # fti stands for: First Trace of the Array
            lta = segy.tracecount # lti stands for: Last Trace of the Array     

            # # Adding the columns to the DataFrame for each header of interest 
            trace_coordinates['tracf'] = segy.attributes(segyio.TraceField.TRACE_SEQUENCE_FILE)[fta:lta:step] #b(5-8)
            trace_coordinates['utmx'] = segy.attributes(segyio.TraceField.CDP_X)[fta:lta:step] #b(181-184)
            trace_coordinates['utmy'] = segy.attributes(segyio.TraceField.CDP_Y)[fta:lta:step] #b(185-188)
            trace_coordinates['cdp_iline'] = segy.attributes(segyio.TraceField.INLINE_3D)[fta:lta:step] #b(189-192)
            trace_coordinates['cdp_xline'] = segy.attributes(segyio.TraceField.CROSSLINE_3D)[fta:lta:step] #b(193-196)

            # A scalar (bytes 71-72) are usually aplied to the cdp coordinates in the trace headers:
            scalar = segy.attributes(segyio.TraceField.SourceGroupScalar)[fta:lta:step] # b (71-72)
            trace_coordinates['utmx'] = np.where(scalar == 0, trace_coordinates['utmx'],
                                            np.where(scalar > 0, trace_coordinates['utmx'] * scalar, 
                                                                    trace_coordinates['utmx'] / abs(scalar)))
            trace_coordinates['utmy'] = np.where(scalar == 0, trace_coordinates['utmy'],
                                            np.where(scalar > 0, trace_coordinates['utmy'] * scalar, 
                                                                    trace_coordinates['utmy'] / abs(scalar)))

            return (trace_coordinates)
        
    else:
        return(f"WARNING: the input data is not valid")