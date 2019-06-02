import auxiliary
import segyio
import pandas as pd
import os.path

# Default location
seismic_path = "../data/NS2900-2200_3000-2300.sgy" #POSEIDON 3D
wells_path = "../data/wells_info.txt"

# 1) test_wells_file_validation
def test_wells_file_validation():
    ext = auxiliary.wells_file_validation(wells_path)
    assert (ext == True)

# 2) test_wells_data_organization
def test_wells_data_organization_columns():
    well_dataframe = auxiliary.wells_data_organization(wells_path)
    assert (len(well_dataframe.columns) == 6)
def test_wells_data_organization_first_well():
    well_dataframe = auxiliary.wells_data_organization(wells_path)
    assert (well_dataframe['name'][1] == 'Kronos_1')

# 3) test_cube_file_extension_validation
def test_cube_file_extension_validation ():
    ext = auxiliary.cube_file_extension_validation(seismic_path, 1)
    assert (ext == True)

# 4) cube_file_segy_format_validation FALTA GENERAR UN SEGYI CON SEGYIO PARA FALSE
def cube_file_format_file_validation():
    standard = auxiliary.cube_file_format_file_validation(seismic_path,1)
    assert (standard == True)

# 5) cube_file_step_validation(seismic_path, step)
def test_cube_file_step_validation():
    step = auxiliary.cube_file_step_validation(seismic_path,69)
    assert (step == True)

# 6) test_cube_file_validation
def test_cube_file_validation():
    cube_file = auxiliary.cube_file_validation(seismic_path,13)
    assert (cube_file == True)

# 7) test_cube_data_organization
def test_cube_wells_data_organization_columns(): 
    cube_dataframe = auxiliary.cube_data_organization(seismic_path)
    assert (cube_dataframe.shape == (10201, 5))
def test_cube_wells_data_organization_tracf(): 
    cube_dataframe = auxiliary.cube_data_organization(seismic_path)
    assert (cube_dataframe['tracf'][0]== 1)



