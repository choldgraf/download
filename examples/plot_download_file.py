"""
Downloading files and zipfiles
------------------------------

This example shows off how to download a file, and optionally unzip it.
"""
from download import download
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import cartopy as cp
import os.path as op
import numpy as np

###############################################################################
# Downloading a file simply requires that you have a URL.

url = "https://ndownloader.figshare.com/files/7010681"
path = download(url, './downloaded/boulder-precip.csv', replace=True)
data = pd.read_csv(path)
ax = data.plot('DATE', 'PRECIP')
ax.set(title="Precipitation over time in Boulder, CO")
plt.setp(ax.get_xticklabels(), rotation=45)
plt.tight_layout()

###############################################################################
# You can optionally unzip the file to the directory of your choice
# using ``zipfile=True``.

url = "http://www2.census.gov/geo/tiger/GENZ2016/shp/cb_2016_us_county_20m.zip"
path = download(url, './downloaded/counties/', replace=True, zipfile=True)
shapes = gpd.read_file(op.join(path, 'cb_2016_us_county_20m.shp'))
shapes = shapes.query('STATEFP == "08"')
bounds = np.array(shapes.total_bounds)[[0, 2, 1, 3]]

fig, ax = plt.subplots(subplot_kw={'projection': cp.crs.PlateCarree()})
ax.add_geometries(shapes['geometry'], crs=cp.crs.PlateCarree(),
                  facecolor='darkgray', edgecolor='k', linewidth=3)
ax.set_extent(np.array(shapes.total_bounds)[[0, 2, 1, 3]])
ax.set(title="Counties in Colorado")
ax.set_axis_off()

plt.show()
