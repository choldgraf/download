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

If your file is a zip file, you can add the flag::

  path = download(url, file_path, zipfile=True)

in this case, the file will be downloaded, and then unzipped into the folder
specified by `file_name`.
