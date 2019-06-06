
import utils
import segyio
import pandas as pd
import os

# Default location
seismic_path = "../data/NS2950-2180_3000-2230.sgy" #POSEIDON 3D
wells_path = "../data/wells_info.txt"

# 1) test_path_validation
def test_path_validation_wells_file():
    path = utils.path_validation(wells_path)
    assert (path == True)
def test_path_validation_seismic_file():
    path = utils.path_validation(seismic_path)
    assert (path == True)
def test_path_validation_false():
    path = utils.path_validation("LA VERDAD DEL UNIVERSO")
    assert (path == False)

# 2) test_check_file_extension
def test_check_file_extension_wells():
    ext = utils.check_file_extension(wells_path)
    assert (ext == True)
def test_check_file_extension_segy():
    ext = utils.check_file_extension(seismic_path)
    assert (ext == True)
def test_check_file_extension_false():
    ext = utils.check_file_extension("LA VERDAD DEL UNIVERSO")
    assert (ext == False)

# 3) test_wells_data_organization
def test_wells_data_organization_columns():
    well_dataframe = utils.wells_data_organization(wells_path)
    assert (len(well_dataframe.columns) == 6)
def test_wells_data_organization_first_well():
    well_dataframe = utils.wells_data_organization(wells_path)
    assert (well_dataframe["name"][1] == "Kronos_1")
def test_wells_data_organization_output_type():
    well_dataframe = utils.wells_data_organization(wells_path)
    assert (str(type(well_dataframe)) == "<class 'pandas.core.frame.DataFrame'>")   
def test_wells_data_organization_false():
    well_dataframe = utils.wells_data_organization("RED WOMAN")
    assert (str(type(well_dataframe)) == "<class 'str'>")

# 4) cube_file_segy_format_validation FALTA GENERAR UN SEGYI CON SEGYIO PARA FALSE
def cube_file_format_file_validation():
    standard = utils.cube_file_format_file_validation(seismic_path,1)
    assert (standard == True)
#def cube_file_format_file_validation_false()

# 5) cube_file_step_validation(seismic_path, step)
def test_cube_file_step_validation():
    step = utils.cube_file_step_validation(seismic_path,69)
    assert (step == True)
def test_cube_file_step_validation():
    step = utils.cube_file_step_validation(seismic_path,9999999)
    assert (step == False)

# 6) test_cube_file_validation
def test_cube_file_validation():
    cube_file = utils.cube_file_validation(seismic_path,13)
    assert (cube_file == True)
def test_cube_file_validation_false_1():
    cube_file = utils.cube_file_validation("TUPAC IS ALIVE",13)
    assert (str(type(cube_file)) == "<class 'str'>")
#def test_cube_file_validation_false_2():
#    cube_file = utils.cube_file_validation("TUPAC IS ALIVE",13)
#    assert (cube_file == False)
def test_cube_file_validation_false_3():
    cube_file = utils.cube_file_validation("TUPAC IS ALIVE",99999)
    assert (str(type(cube_file)) == "<class 'str'>")

# 7) test_cube_data_organization
def test_cube_data_organization_columns(): 
    cube_dataframe = utils.cube_data_organization(seismic_path)
    assert (cube_dataframe.shape == (2601, 5))
def test_cube_data_organization_tracf(): 
    cube_dataframe = utils.cube_data_organization(seismic_path)
    assert (cube_dataframe['tracf'][0]== 1)
def test_cube_data_organization_output_type():
    cube_dataframe = utils.cube_data_organization(seismic_path)
    assert (str(type(cube_dataframe)) == "<class 'pandas.core.frame.DataFrame'>")
def test_cube_data_organization_false(): 
    cube_dataframe = utils.cube_data_organization("CHOCOLATE TIME!")
    assert (str(type(cube_dataframe)) == "<class 'str'>")


