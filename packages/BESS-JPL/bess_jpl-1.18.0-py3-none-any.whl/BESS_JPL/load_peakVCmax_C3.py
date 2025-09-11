from os.path import join, abspath, dirname

import rasters as rt
from rasters import Raster, RasterGeometry

import numpy as np

def load_peakVCmax_C3(geometry: RasterGeometry = None, resampling: str = "nearest") -> Raster:
    filename = join(abspath(dirname(__file__)), "peakVCmax_C3.tif")
    image = Raster.open(filename, geometry=geometry, resampling=resampling, nodata=np.nan)

    return image
