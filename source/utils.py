# Dependencies
import os
import segyio
import pandas as pd
import numpy as np

def file_validation(file_path):
    
    """
    file_validation(file_path)
    
    Validates the input files.
    
    This functions validates the input data answering this questions:
    1) Does the file exist in the provided folder?
    2) Does the file has a .txt, .segy, -sgy extension?
    3) In case the input is a SEG-Y: is the file a standard SEG-Y?
    
    
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
        return(f"The file given does not exist.")