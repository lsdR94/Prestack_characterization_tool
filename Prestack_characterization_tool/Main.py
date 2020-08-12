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

# Import classes of other modules
from Basemap import BasemapModule
from Wiggle import WiggleModule
from AVO import AVOModule

# Code

class Survey:
    
    """
    NAME
    ----     
        Survey

    DESCRIPTION
    -----------
    Main class of the Prestack Characterization Tool.

    Works as the container of the main objects and its data: Basemap, Wiggle and AVO. The
    data is stored as class attributes to improve its scope of use and to avoid inheritance 
    between objects.

    ATTRIBUTES
    ----------
        survey_name : str
            Name of the seismic survey.

        gathers_path : list
            List of the paths where the SEG-Y files (Partial Angle Stacks, PAS in short) are
            located.

        wells_path : list
            List of the paths where wells txt files are located.

        merge_path : str
            Path where the merge of the PAS will be stored.

        gradient_path : str
            Path where the computation of the "Gradient" will be stored.

        intercept_path : str
            Path where the computation of the "Intercept" will be stored.

        rvalue_path : str
            Path where the computation of the "Correlation Coefficient" will be stored.

        pvalue_path : str
            Path where the computation of the "P Value" will be stored.

        stderr_path : str
            Path where the computation of the "Standard Error" will be stored.

        angle_interval : int
            Interval between PAS.

        angle_list : list
            List of the average angle of each PAS. None by default. If the value it's different
            from None, a constructor will create the list by using angle_interval and the 
            amount of files in gathers_path.

        cube_validation : bool
            Whether the seismic files are suitable to work with. False by default.

        wells_validation : bool
            Whether the well files are suitable to work with. False by default.

        basemap_dataframe : (Pandas)DataFrame
            Matrix compounded by the coordinates and lines of the seismic survey's corners. 
            Empty by default.

        wells_dataframe : (Pandas)DataFrame
            Matrix compounded by wells related information. Empty by default.

        inlines : list
            List of inlines (numbers) within the survey. Empty by default.

        crosslines : list
            List of crosslines (numbers) within the survey. Empty by default.

        Basemap : object
            Basemap object. 

        Wiggle : object
            Wiggle object.

        AVO : object
            AVO object.


    METHODS
    -------
        validation(**kwargs)
            Validates de incoming files: seismic files (PAS) and wells txt files.

        merge(**kwargs)
            Creates a pseudo Prestack file by merging all given PAS.   

        cube_data_organization(**kwargS)
            Extracts and stores cube's general information; such as: lines, coordinates and
            trace parameters.

        wells_data_organization(**kwargs)
            Creates well's information matrix. 

    LIBRARIES
    ---------
        Numpy: BSD licensed package for scientific computing with Python. More information
               available at:
                   https://numpy.org/

        Pandas: BSD 3 licensed open source data analysis and manipulation tool, built on top of
                the Python programming language. More information available at:
                    https://pandas.pydata.org/

        SegyIO: LGPL licensed library for easy interaction with SEG-Y and Seismic Unix formatted 
                seismic data, with binding for Python and Matlab. Made by Kvalsvik Jørgen in 
                2014. Code Available at:
                    https://github.com/equinor/segyio.

    """ 

    def __init__(self, survey_name, 
                 gathers_path, wells_path, merge_path, 
                 gradient_path, intercept_path, rvalue_path, pvalue_path, stderr_path,
                 angle_interval, angle_list = None):
        
        """
        DESCRIPTION
        -----------
            Instantiates Survey's class attributes. For more information, please refer to Survey's 
            docstring.
            
        """
        
        # Name of the survey
        Survey.survey = survey_name
        # Files
        Survey.gathers_path = gathers_path
        Survey.wells_path = wells_path
        Survey.merge_path = merge_path
        # AVO files
        Survey.gradient_path = gradient_path
        Survey.intercept_path = intercept_path
        Survey.rvalue_path = rvalue_path
        Survey.pvalue_path = pvalue_path
        Survey.stderr_path = stderr_path
        # Partial angle stacks angles
        Survey.angle_interval = angle_interval
        if angle_list == None:
            Survey.angle_list = [i*Survey.angle_interval for i in range(1, len(Survey.gathers_path)+1)]
        else: 
            Survey.angle_list = angle_list  
        Survey.cube_validation = False
        Survey.wells_validation = False
        # Empty attributes to initialize empty objects
        Survey.basemap_dataframe = pd.DataFrame([])
        Survey.wells_dataframe = pd.DataFrame([])
        Survey.inlines = []
        Survey.crosslines = []
            
    # Setters for each object
    @property
    def BasemapModule(self):
        
        """
        NAME
        ----
            Basemap
        
        DESCRIPTION
        -----------
            Dynamically instantiates the Basemap object. For more information, please refer to
            BasemapModule class.
        
        """
        
        return BasemapModule(self.basemap_dataframe, self.wells_dataframe)
    
    @property
    def WiggleModule(self):
        
        """
        NAME
        ----
            Wiggle
        
        DESCRIPTION
        -----------
            Dynamically instantiates the Wiggle object. For more information, please refer to 
            WiggleModule class.
        
        """
        return WiggleModule(self.inlines, self.crosslines)
    
    @property
    def AVOModule(self):
        
        """
        NAME
        ----
            AVO
        
        DESCRIPTION
        -----------
            Dynamically instantiates the AVO object. For more information, please refer to
            AVOModule class.
            
        """
        
        return AVOModule(self.inlines, self.crosslines)
      
    def __repr__(self):
        print(f"PAS given:")
        for file in self.gathers_path:
            print(f"        - {file}")
        print(f"These files will be merged following the name&path: {self.merge_path}")
        print(f"Wells given: ")
        for well in self.wells_path:
            print(f"        - {well}")
        print(f"Interval between the angle gathers = {self.angle_interval}")
        print(f"Angle list based on the angle interval and que amount of files given = {self.angle_list}")
        print(f"Brand new SEG-Y files name&path: ")
        for file in [self.gradient_path, self.intercept_path, self.rvalue_path, self.pvalue_path, self.stderr_path]:
            print(f"        - {file}")
        print(f"inlines: {self.inlines}")
        print(f"crosslines: {self.crosslines}")
        print(f"Basemap dataframe: {self.basemap_dataframe}")
        print(f"Wells dataframe: {self.wells_dataframe}")
        print(f"Basemap object: {self.BasemapModule}")
        print(f"Wiggle object: {self.WiggleModule}")
        print(f"AVO object: {self.AVOModule}")       
        return(f"Previous parameters have been stored successfully")
   
    def validation(self):
            
        """
        NAME
        ----
            validation
            
        DESCRIPTION
        -----------
            Validates the input files. Stores True/False in cube_validation & wells_validation
            attributes whether the files are suitable for execution.

            The validation process goes by answering this questions:
            1) Does the file exist?
            2) Does the file has a .txt, .segy or .sgy extension?
            3) In case the input file is a SEG-Y: is the file a standard SEG-Y? [On progress]



        ARGUMENTS
        ---------
            Survey.gathers_path : list
                List of the paths where the SEG-Y files are located.

            Survey.wells_path : list
                List of the paths where well txt files are located.

        RETURN
        ------
            Survey.cube_validation : bool class attribute
                True if the files finish the validation process. False if the file is not suitable for
                execution.


            Survey.wells_validation : bool class attribute
                True if the files finish the validation process. False if the file is not suitable for
                execution.
            
            str
                Short description of why the file is not appropriate for work.

        ON PROGRESS
        -----------
            To add a third validation able to identify standard SEG-Y files. This will be done by
            comparing the byte distribution of files with the ones used by SegyIO. Standard SEG-Y
            files follows SEG Technical Standards Committee (2017).

        REFERENCES
        ----------
        SEG Technical Standards Committee. (2017). SEG-Y_r2.0: SEG-Y revision 2.0 Data Exchange format.
            Document Online. Available at: 
            https://seg.org/Portals/0/SEG/News%20and%20Resources/Technical%20Standards/seg_y_rev2_0-mar2017.pdf
        """
        
        #Cube validation
        for file in self.gathers_path:

            # First validation: does the file exist?
            if os.path.isfile(file):
                file, ext = os.path.splitext(file)

                # Second validation: does the file has a .sgy or .segy extension?
                if ext.lower() == (".sgy") or ext.lower() == (".segy"):
                    print(f"Cube file: '{file}' has been validated")
                    self.cube_validation = True

                # If not, return text: not a valid one
                else:
                    self.cube_validation = False
                    return(f"Cube file: '{file}' extension in not valid.")

            # If not, return text: file does not exist
            else:
                self.cube_validation = False
                return(f"Cube file: '{file}' does not exist.")
            
            
        #Wells validation
        for doc in self.wells_path:
            if os.path.isfile(doc):
                file, ext = os.path.splitext(doc)
                if ext.lower() == (".txt"):
                    print(f"Wells file: '{doc}' has been validated")
                    self.wells_validation = True
                else:
                    self.wells_validation = False
                    return(f"Wells file '{doc}' extension in not valid.")
            else:
                self.wells_validation = False
                return(f"Wells file '{doc}' does not exist.")
       
    def merge(self):
        
        """
        NAME
        ----
            merge
        
        DESCRIPTION
        -----------
            Creates a pseudo Prestack file by merging all given PAS.
            
            The new SEG-Y will be constructed using the metadata, the headers of one file and the
            amplitude content of each trace within PAS. To simulate a Prestack file, the byte 37 of
            each trace header(offset) will be used to store a value equal to the average of the angle
            range used in the stacking process. This will allow SegyIO methods (gather) to sort &
            fetch data by Inline - Crossline – Angle.
        
        ARGUMENTS
        ---------
            Survey.gathers_path : list
                List of the paths where the SEG-Y files are located.

            Survey.cube_validation : bool
                Whether the seismic files are suitable to work with.

            Survey.merge_path : str
                Path where the merge of the PAS will be stored.

            Survey.angle_list : list
                List of the average angle of each PAS.
                
        RETURN
        ------    
            str
                A message whether the merging was successful or not.
        
        REFERENCES
        ----------
        Kvalsvik Jørgen. Segyio. A Fast Python library for SEGY files. Online document:
            https://github.com/equinor/segyio.

            Childs:
        source1: https://github.com/equinor/segyio/blob/master/python/examples/make-file.py
        source2: https://github.com/equinor/segyio/blob/master/python/segyio/tracefield.py

        """
        Survey.validation(self)
        if self.cube_validation == True:
       

            # Making the offset array
            offsts = np.array(self.angle_list)

            # Initializing the stacks
            with segyio.open(self.gathers_path[0]) as f:

                # Spec function to build the new segy
                spec = segyio.spec()
                spec.sorting = f.sorting
                spec.format = 1
                spec.samples = f.samples
                spec.ilines = f.ilines
                spec.xlines = f.xlines
                spec.offsets = offsts

                # Initializing the merged one
                with segyio.create(self.merge_path, spec) as s:

                    # Index for the merge headers and trace
                    merge_index = 0
                    # Index for the original file's headers and trace
                    stack_index = 0
                    # For loop to set parameters according to the seismic lines and offset
                    for il in spec.ilines:
                        for xl in spec.xlines:
                            for offset in spec.offsets:
                                # Assigning headers [byte]
                                s.header[merge_index] = {segyio.su.tracl: f.header[stack_index][1],
                                                         segyio.su.tracr: f.header[stack_index][5],
                                                         segyio.su.fldr: f.header[stack_index][9],
                                                         segyio.su.cdp: f.header[stack_index][21],
                                                         segyio.su.cdpt: f.header[stack_index][25],
                                                         segyio.su.offset: offset,  # 37
                                                         segyio.su.scalco: f.header[stack_index][71],
                                                         segyio.su.ns: f.header[stack_index][115],
                                                         segyio.su.dt: f.header[stack_index][117],
                                                         segyio.su.cdpx: f.header[stack_index][181],
                                                         segyio.su.cdpy: f.header[stack_index][185],
                                                         segyio.su.iline: il,  # 189
                                                         segyio.su.xline: xl}  # 193

                                # Extracts the index of the angle which match with the file's index
                                file_index = self.angle_list.index(offset)

                                # Openning the file asociated with the angle in offset
                                with segyio.open(self.gathers_path[file_index], "r") as stack:

                                    # Copying the amplitudes from each stack
                                    s.trace[merge_index] = stack.trace[stack_index]

                                merge_index += 1
                            stack_index += 1

            return (f"Successful merge. New SEG-Y file path: {self.merge_path}")
        
        else:
            return("The provided files are not suitable for characterization")
        
    def cube_data_organization(self):
    
        """
        NAME
        ----
            cube_data_organization
        
        DESCRIPTION
        -----------
            Extracts and stores cube's general information; such as: 
                1) Numbers of all inlines and crosslines within the survey.
                2) Sample interval and samples per trace.
                3) Coordinates and lines of the traces located at the survey's corners.
            
        ARGUMENTS
        ---------
            Survey.cube_validation : bool
                Whether the seismic files are suitable to work with.

            Survey.merge_path : str
                Path where the pseudo Prestack file is located.
        
        RETURN
        ------
            Survey.inlines : list class attribute
                Inlines within the survey.

            Survey.crosslines : list class attribute
                Crosslines within the survey.

            WiggleModule.sample_interval : int instance attribute
                Sample interval in ms.

            WiggleModule.samples_per_trace : int instance attribute
                Amount of samples in a trace.

            WiggleModule.trace_length : list instance attribute
                Range of trace's time axis.
                
            Survey.basemap_dataframe : (Pandas)DataFrame class attribute
                A matrix compounded by the coordinates of the seismic survey's corners. The information
                is structured by the following columns:
                    - iline: inline number of the line where the corner is located.
                    - xline: crossline number of the line where the corner is located.
                    - utmx: horizontal coordinates Universal Transversal Mercator coordinate system.
                    - utmy: vertical coordinates Universal Transversal Mercator coordinate system.
                            
        ON PROGRESS
        -----------
            1) Approximate any polygon (survey) into a rectangle.
            2) Compute the forth corner of a rectangle by giving three points.
        
        NOTE
        ----
            The function optimizes the usage of SEG-Y files by opening the these once.

        """    
        
        if self.cube_validation == True:
            if self.basemap_dataframe.empty:
                with segyio.open(self.merge_path, "r") as segy:

                    #Accessing & storing line numbers
                    self.inlines = segy.ilines
                    self.crosslines = segy.xlines

                    #Accessing & storing WiggleModule attributes: sample interval, samples per trace, lenght of traces
                    WiggleModule.sample_interval = int(segy.attributes(segyio.TraceField.TRACE_SAMPLE_INTERVAL)[0]/1000)
                    WiggleModule.samples_per_trace = int(segy.attributes(segyio.TraceField.TRACE_SAMPLE_COUNT)[0]) 
                    WiggleModule.trace_length = [0, 
                                                 WiggleModule.sample_interval * WiggleModule.samples_per_trace - WiggleModule.sample_interval]

                    # Array to extract the min/max coordinates
                    utmx = segy.attributes(segyio.TraceField.CDP_X)[:] 
                    utmy = segy.attributes(segyio.TraceField.CDP_Y)[:] 

                    # Extracting the points
                    corners = [utmx.argmin(), utmy.argmin(), utmx.argmax(), utmy.argmax()]

                    # Making a Dataframe from the coordinates in corners
                    for index in corners:
                        series = {"iline": segy.attributes(segyio.TraceField.INLINE_3D)[index], 
                                        "xline": segy.attributes(segyio.TraceField.CROSSLINE_3D)[index],
                                        "utmx": segy.attributes(segyio.TraceField.CDP_X)[index], 
                                        "utmy": segy.attributes(segyio.TraceField.CDP_Y)[index],
                                        "scalar" : segy.attributes(segyio.TraceField.SourceGroupScalar)[index]}
                        self.basemap_dataframe = pd.concat([self.basemap_dataframe, 
                                                            pd.DataFrame(series)], ignore_index = True, axis="rows")

                    # Adapting the coordinates to the segy's scalar value
                    self.basemap_dataframe['utmx'] = np.where(self.basemap_dataframe['scalar'] == 0, 
                                                              self.basemap_dataframe['utmx'],
                                                    np.where(self.basemap_dataframe['scalar'] > 0,
                                                             self.basemap_dataframe['utmx'] * self.basemap_dataframe['scalar'],
                                                             self.basemap_dataframe['utmx'] / abs(self.basemap_dataframe['scalar'])))

                    self.basemap_dataframe['utmy'] = np.where(self.basemap_dataframe['scalar'] == 0,
                                                              self.basemap_dataframe['utmy'],
                                                    np.where(self.basemap_dataframe['scalar'] > 0, 
                                                             self.basemap_dataframe['utmy'] * self.basemap_dataframe['scalar'],
                                                             self.basemap_dataframe['utmy'] / abs(self.basemap_dataframe['scalar'])))

                    # Dropping the scalar column
                    self.basemap_dataframe = self.basemap_dataframe.drop(["scalar"], axis = 1)

                    # Concatenating the first row once again to close the survey's polygon
                    first_row = pd.DataFrame(self.basemap_dataframe.iloc[0]).transpose()
                    self.basemap_dataframe = pd.concat([self.basemap_dataframe, first_row], ignore_index = True, axis = 0)
                
                return self.basemap_dataframe
            
        else:
            return(Survey.validation(self))
        
    def wells_data_organization(self, index=0):
       
        """
        NAME
        ----
            wells_data_organization
            
        DESCRIPTION
        -----------
            Creates well's information matrix.

            The function will only take the wells inside the survey. The txt files must be structured 
            by the following order, where each item has to be separated by a single space:
                - "well name"
                - "inline coordinate"
                - "xline coordinate"
                - "utmx coordinate"
                - "utmy coordinate"
                - "depth"
                
        ARGUMENTS
        ---------      
            Survey.wells_validation : bool
                Whether the well files are suitable to work with.

            Survey.wells_path : list
                List of the paths where well txt files are located.

            Survey.basemap_dataframe : (Pandas)DataFrame
                Matrix compounded by the coordinates and lines of the seismic survey's corners.
        
        RETURN
        ------
            Survey.wells_dataframe : (Pandas)DataFrame class attribute
                A matrix compounded by the information related to each well inside the survey. 
                The information is structured by the following columns:
                    - name: well's name
                    - cdp_iline: inline number.
                    - cdp_xline: crossline number.
                    - utmx: horizontal axis of the Universal Transversal Mercator coordinate system.
                    - utmy: vertical axis of the Universal Transversal Mercator coordinate system.
                    - depth: depth reached.

        """
        
        if self.wells_validation == True:

            self.wells_dataframe = pd.read_csv(self.wells_path[index],
                                sep=" ",
                                header = None, 
                                names= ["name","cdp_iline","cdp_xline","utmx","utmy", "depth"])

            self.wells_dataframe["index"] = self.wells_dataframe["name"]
            self.wells_dataframe.set_index("index", inplace = True)

            # Adjusting the dataframe according to the survey
            self.wells_dataframe = self.wells_dataframe[(self.wells_dataframe.cdp_iline >= self.basemap_dataframe.iline.min()) &
                                                        (self.wells_dataframe.cdp_iline <= self.basemap_dataframe.iline.max()) &
                                                        (self.wells_dataframe.cdp_xline >= self.basemap_dataframe.xline.min()) &
                                                        (self.wells_dataframe.cdp_xline <= self.basemap_dataframe.xline.max())]
            return(self.wells_dataframe)
        
        else:
            return(Survey.validation(self))       
