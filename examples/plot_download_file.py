"""
Downloading files and zipfiles
------------------------------

This example shows off how to download a file, and optionally unzip it.
"""
from download import download
import matplotlib.pyplot as plt
import pandas as pd
import os.path as op
from glob import glob

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
print(glob(op.join(path, '*')))

plt.show()
