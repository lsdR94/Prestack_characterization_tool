# Data accessing
import os

# Math
import numpy as np
from scipy import stats

# Data management
import pandas as pd
from shutil import copyfile
import time

# SEGY files management
import segyio

# MUltiproccessing 
from multiprocessing import Pool

def file_validation(file_path):
    
    """

    Validates the input files.
    
    This functions validates the input data answering this questions:
    1) Does the file exist in the provided folder?
    2) Does the file has a .txt, .segy, -sgy extension?
    3) In case the input file is a SEG-Y: is the file a standard SEG-Y?
    
    
    Argument
    --------
    file_path : str
        Path where the text or SEG-Y file to validate is located.
                 
    Return
    ------
    True : bool
        If the validations are True the output will be True, else a str.
    str
        If the validations (one at least) are False the output will be a Warning specifiying 
        why the function can't work with the given data.
        
        
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

    # First validation: does the file exist?
    if os.path.isfile(file_path):
        file, ext = os.path.splitext(file_path)
        
        # Second validation: does the file has a .txt, .sgy or .segy extension?
        if ext.lower() == (".txt") or ext.lower() == (".sgy") or ext.lower() == (".segy") :
            
            # Third validation: does the SEG-Y file is a standard SEG-Y data?
            if ext.lower() == (".sgy") or ext.lower() == (".segy"):
                with segyio.open(file_path,'r') as segyfile:
                    segyio_header = list(segyio.tracefield.keys.keys())
                    file_header = segyfile.header[0].keys()

                    # Comparing the trace header within the SEG-Y file with the ones in segyIO 
                    for i in range(0,len(segyfile.header[0].keys()),1):
                        if str(segyio_header[i]) == str(file_header[i]):

                            # If the list of headers is the same, return True
                            return(True)

                        # If the SEG-Y is not standard, return text: SEG-Y is not standard
                        else:
                            return(f"SEG-Y provided does not fulfill the requirements")

            # For both validation == True while not a SEG-Y, then return true
            else:
                return(True)
        
        # If not, return text: not a valid one
        else:
            return(f"The file extension in not valid.")
    
    # If not, return text: file does not exist
    else:
        return(f"The given file does not exist.")

def merging_stacks(list_of_gathers, merged_file_path, list_of_angles):
    
    """
    
     Makes a new SEG-Y file by merging the given partial angle stacks.

     The function makes use of Segyio module to scan the metadata of the given files
     to create a SEG-Y file from scratch. The merging process takes advantages of the
     geometry, where the coordinates of the traces are the same for any array of angles
     therefore, there will be only one pair of coordinates (and headers) for each trace 
     regardless of the amount of angles given. To sort the different amplitude arrays
     of each file inside one, the offset header of each file has been modified according
     to the angle of incidence of each file. This aproach will multiply the amount of
     traces within the output file according to the amount of files given and more 
     importantly, these are new traces are sorted by: Inline > Crossline > Angle.
    
    Arguments
    ---------
    list_of_gathers : list
        Contains the path of each partial angle stack file to be used.

    merged_file_path : str
        Path of the new file to be made.

    list_of_angles : list
        Contains the angles of each partial angle stack to be used.
                 
    Return
    ------
    str
        A message wether the merging was successful or not.
            
    Notes
    -----
        Normally, the traces within SEG-Y files are sorted by Inline > Crossline. These
        configuration determines how traces are laid out. Adding the angle to the sorting
        formula would make the file looks for one Inline, for Crossline and then for all 
        the angles before searching another Crossline until this reach the last one
        in order to move to the next Inline.
    
    References
    ----------
    Kvalsvik Jørgen. Segyio. A Fast Python library for SEGY files. Online document:
    https://github.com/equinor/segyio.

    Childs:
        source1: https://github.com/equinor/segyio/blob/master/python/examples/make-file.py
        source2: https://github.com/equinor/segyio/blob/master/python/segyio/tracefield.py
    
    """
    
    # Validating the files
    for file in list_of_gathers:
        if file_validation(file) == True:
            print(f"{file} has been validated")
        else:
            return(f"Unsuccessful validation: {file_validation(file)}")
    
    # Making the offset array
    offsts = np.array(list_of_angles)

    # Initializing the stacks
    with segyio.open(list_of_gathers[0]) as f, segyio.open(list_of_gathers[1]) as g, segyio.open(list_of_gathers[2]) as h:
        
        # Spec function to build the new segy
        spec = segyio.spec()
        spec.sorting = f.sorting
        spec.format = 1
        spec.samples = f.samples
        spec.ilines = f.ilines
        spec.xlines = f.xlines
        spec.offsets = offsts

        # Initializing the merged one
        with segyio.create(merged_file_path, spec) as s:
        
            # Index for the merge headers and trace
            merge_index = 0
            # Index for the original file's headers and trace
            stack_index = 0
            # For loop to set parameters according to the seismic lines and offset
            for il in spec.ilines:
                for xl in spec.xlines:
                    for offset in spec.offsets:
                        # Assigning headers [byte]
                        s.header[merge_index] = {segyio.su.tracl  : f.header[stack_index][1],
                                                 segyio.su.tracr  : f.header[stack_index][5],
                                                 segyio.su.fldr   : f.header[stack_index][9],
                                                 segyio.su.cdp    : f.header[stack_index][21],
                                                 segyio.su.cdpt   : f.header[stack_index][25],
                                                 segyio.su.offset : offset, # 37
                                                 segyio.su.scalco : f.header[stack_index][71],
                                                 segyio.su.ns     : f.header[stack_index][115],
                                                 segyio.su.dt     : f.header[stack_index][117],
                                                 segyio.su.cdpx   : f.header[stack_index][181],
                                                 segyio.su.cdpy   : f.header[stack_index][185],
                                                 segyio.su.iline  : il,  # 189
                                                 segyio.su.xline  : xl}  # 193
                        if offset == list_of_angles[0]:
                            stack = f # near
                        if offset == list_of_angles[1]:
                            stack = g # mid
                        if offset == list_of_angles[2]:
                            stack = h # far                   
                        
                        # Copying the amplitudes from each stack
                        s.trace[merge_index] = stack.trace[stack_index]
                        
                        merge_index += 1
                    stack_index += 1
                
    return (f"Successful merge. New SEG-Y file path: {merged_file_path}")

def wells_data_organization(wells_path):
    
    """

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
        return(file_validation(wells_path))

def cube_data_organization(file_path):
    
    """
    
    Builds a DataFrame using the trace headers information within the SEG-Y file.
    
    Argument
    ---------
    seismic_path : str
        Path of the standard SEG-Y file.
        
    Return
    ------
    trace_coordinates : (Pandas) DataFrame
        A matrix compounded by the coordinates of each trace. The information 
        distribution is controlled by the following columns:
            - iline: inline coordinate.
            - xline: crossline coordinate.
            - utmx: horizontal axis of the Universal Transversal Mercator coordinate system.
            - utmy: vertical axis of the Universal Transversal Mercator coordinate system. 
    str
        If the previous validations (one at least) are False the output will be a Warning specifiying 
        why the function can't work with the data.
    
    """
    if file_validation(file_path) == True:
        df = pd.DataFrame([])
        corners = []
        with segyio.open(file_path, "r") as segy:
            df = pd.DataFrame([])
            
            # Array to extract the min/max coordinates
            utmx = segy.attributes(segyio.TraceField.CDP_X)[:] 
            utmy = segy.attributes(segyio.TraceField.CDP_Y)[:] 
            
            # Extracting the points
            corners += [utmx.argmin(), utmx.argmax(), utmy.argmin(), utmy.argmax()]
            
            # Making a Dataframe from the coordinates in corners
            for index in corners:
                series = {"iline": segy.attributes(segyio.TraceField.INLINE_3D)[index], 
                        "xline": segy.attributes(segyio.TraceField.CROSSLINE_3D)[index],
                        "utmx": segy.attributes(segyio.TraceField.CDP_X)[index], 
                        "utmy": segy.attributes(segyio.TraceField.CDP_Y)[index],
                        "scalar" : segy.attributes(segyio.TraceField.SourceGroupScalar)[index]}
                df = pd.concat([df, pd.DataFrame(series)], 
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
            
            # Concatenating the first row once again to close the survey's polygon
            #first_row = pd.DataFrame(df.iloc[0]).transpose()
            #df = pd.concat([df, first_row], ignore_index = True, axis = 0)
            
            return df

    else:
        return(file_validation(file_path))

def avo_storing_files(list_of_gathers, gradient_path, intercept_path, rvalue_path, pvalue_path, stderr_path): 
    
    """

    Makes SEG-Y files to store the AVO attributes.

    This function makes SEG-Y files using the metadata and trace information of the original SEG-Y files. The AVO 
    attributes, which are calculated by the samples of each traces, will be store in the same place where
    amplitudes are stored in order to control these attributes by depth.
    
    Arguments
    ---------
    list_of_gathers : list
        Contains the path of each partial angle stack file to be used.
    
    gradient_path : str
        Path of the file to be created where the Gradient (AVO attribute) will be stored.
    
    intercept_path : str
        Path of the file to be created where the Interpcet (AVO attribute) will be stored.
        
    rvalue_path : str
        Path of the file to be created where the Correlation Coeficient (AVO attribute's statistiscs) will be stored.
    
    pvalue_path : str
        Path of the file to be created where Gradient = 0 hypothesis (AVO attribute's statistiscs) will be stored.
    
    stderr_path : str
        Path of the file to be created where the Standard Deviation (AVO attribute's statistiscs) will be stored.
        
    Return
    ------
    str
        Whether the creation is successful or not and the entire path where the file got created in case the first
        is true.
    
    See also
    --------
    1) avo.AVO_attributes_computation_2

    """
    
    
    # Initializing the stacks
    with segyio.open(list_of_gathers[0]) as f:
        
        # Spec function to build the new segy
        spec = segyio.tools.metadata(f)

        # Initializing the merged one
        with segyio.create(gradient_path, spec) as gradient:

            # Assigning headers [byte]
            gradient.text[0] = f.text[0]
            gradient.bin = f.bin
            gradient.header = f.header
            gradient.trace = f.trace
            
        print(f"Successful construction. Gradient path: ({gradient_path})")
            
    
    # Making copies of the new segy
    copyfile(gradient_path, intercept_path)
    print(f"Successful construction. Intercept path: ({intercept_path})")
    copyfile(gradient_path, rvalue_path)
    print(f"Successful construction. Correlation coeficient path: ({rvalue_path})")
    copyfile(gradient_path, pvalue_path)
    print(f"Successful construction. Pvalue path: ({pvalue_path})")
    copyfile(gradient_path, stderr_path)
    print(f"Successful construction. Standard Deviation path: ({stderr_path})")

    return ()


















