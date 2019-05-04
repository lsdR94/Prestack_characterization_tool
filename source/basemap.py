import os
import numpy as np
import pandas as pd
import segyio


def read_segy_xy(path):
    """
    Return pandas dataframe with segy coordinates
    (tracf, utm_x, utm_y, cdp_inline, cdp_xline)

    Input:
    path: File path
    """
    xy = pd.DataFrame()
    xy = pd.DataFrame()
    with segyio.open(path, 'r') as segy:
        xy['tracf'] = segy.attributes(segyio.TraceField.TRACE_SEQUENCE_FILE)[:]
        xy['cdp_xline'] = segy.attributes(segyio.TraceField.CROSSLINE_3D)[:]
        xy['cdp_iline'] = segy.attributes(segyio.TraceField.INLINE_3D)[:]

        xy_scalar = segy.attributes(segyio.TraceField.SourceGroupScalar)[:]
        xy['utmx'] = segy.attributes(segyio.TraceField.CDP_X)[:]
        xy['utmy'] = segy.attributes(segyio.TraceField.CDP_Y)[:]

        # Apply coordinate scalar to coordinates
        xy['utmx'] = np.where(xy_scalar == 0, xy['utmx'],
                              np.where(xy_scalar > 0, xy['utmx'] * xy_scalar, xy['utmx'] / abs(xy_scalar)))
        xy['utmy'] = np.where(xy_scalar == 0, xy['utmy'],
                              np.where(xy_scalar > 0, xy['utmy'] * xy_scalar, xy['utmy'] / abs(xy_scalar)))

    return xy