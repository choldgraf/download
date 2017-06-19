# download
A quick helper module to download files online. This draws heavily from
MNE-python's `_fetch_file` function. It will attempt to be smart about
not downloading data that's already there, checking to make sure that
there were no errors in fetching data, automatically unzipping the contents
of downloaded zipfiles (if desired), and displaying a progress bar with
statistics.

# Installation

Either clone this repository and install with `python setup.py install`

or, simply install with `pip`:

`pip install download`
