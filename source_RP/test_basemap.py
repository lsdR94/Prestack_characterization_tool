import pytest
import numpy as np
import basemap



# @pytest.fixture()
# def setup():
#     path = "../data/NS2990-2200_3000-2210.sgy"
#
#     return path


def test_read_segy_xy():
    path = "../data/NS2990-2200_3000-2210.sgy"
    val = basemap.read_segy_xy(path)
    val = val.iloc[0, :].values
    exp = np.array([1.0000000e+00, 2.2000000e+03, 2.9900000e+03, 4.2408170e+05, 8.4900492e+06])
    assert np.array_equal(val, exp)