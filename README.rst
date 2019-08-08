.. image:: https://codecov.io/gh/choldgraf/download/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/choldgraf/download
  :align: left

.. image:: https://travis-ci.org/choldgraf/download.svg?branch=master
  :align: left

Download
--------
A no-frills tool to download files from the web. It will
attempt to be smart about not downloading data that's
already there, checking to make sure that
there were no errors in fetching data, automatically unzipping the contents
of downloaded zipfiles (if desired), and displaying a progress bar with
statistics.

.. note::

    This draws heavily from the
    `MNE-python <https://martinos.org/mne>`_ ``_fetch_file`` function.

Installation
------------

Either clone this repository and install with::

  python setup.py install

or, simply install with ``pip``::

  pip install download

Usage
-----

Download a file on the web is as easy as::

  from download import download
  path = download(url, file_path)

a file called ``file_name`` will be downloaded to the folder of ``file_path``.

File types
^^^^^^^^^^

If your file is a zip file, you can add the flag::

  path = download(url, file_path, kind="zip")

in this case, the file will be downloaded, and then unzipped into the folder
specified by `file_name`.

Supported formats are `'file', 'zip', 'tar', 'tar.gz'`
Defaults to `file`.

Progress bar
^^^^^^^^^^^^

Whether to display a progress bar during file download.
Defaults to `True`::

  path = download(url, file_path, progressbar=True)
  
Replace
^^^^^^^

If `True` and the URL points to a single file, overwrite the old file if possible.
Defaults to `False`::

  path = download(url, file_path, replace=False)
  
Timeout
^^^^^^^

The URL open timeout in seconds.
Defaults to 10 seconds::

  path = download(url, file_path, timeout=10)
  
Verbose
^^^^^^^

Whether to print download status to the screen.
Defaults to `True`::

  path = download(url, file_path, verbose=True)
