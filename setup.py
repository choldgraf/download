#! /usr/bin/env python
#
# Copyright (C) 2015 Chris Holdgraf
# <choldgraf@gmail.com>
#
# Adapted from MNE-Python

import os
import setuptools
from setuptools import setup
from download import __version__


descr = """A quick module to help downloading files using python."""

DISTNAME = "download"
DESCRIPTION = descr
MAINTAINER = "Chris Holdgraf"
MAINTAINER_EMAIL = "choldgraf@gmail.com"
URL = "https://github.com/choldgraf/download"
LICENSE = "BSD (3-clause)"
DOWNLOAD_URL = "https://github.com/choldgraf/download"
VERSION = __version__
with open("./README.rst", "r") as ff:
    LONG_DESCRIPTION = ff.read()

if __name__ == "__main__":
    if os.path.exists("MANIFEST"):
        os.remove("MANIFEST")

    setup(
        name=DISTNAME,
        maintainer=MAINTAINER,
        include_package_data=False,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/x-rst",
        license=LICENSE,
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        zip_safe=False,  # the package can run out of an .egg file
        classifiers=[
            "Intended Audience :: Science/Research",
            "Intended Audience :: Developers",
            "License :: OSI Approved",
            "Programming Language :: Python",
            "Topic :: Software Development",
            "Topic :: Scientific/Engineering",
        ],
        platforms="any",
        packages=["download"],
        package_data={},
        scripts=[],
        install_requires=["tqdm", "six", "requests"],
        extras_require={
            "dev": ["numpy", "codecov", "pytest", "pytest-cov"],
            "sphinx": ["matplotlib", "pandas", "sphinx", "sphinx-gallery", "pillow"],
        },
    )
